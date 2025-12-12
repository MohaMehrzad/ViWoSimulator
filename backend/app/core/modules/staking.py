"""
Staking Module - Token staking, APY calculations, and fee discounts.

=== SOLANA STAKING INTEGRATION (November 2025) ===

Built on Solana's high-performance infrastructure:

SPL Token Staking Program:
- Custom Solana program for VCoin staking
- Anchor framework for security
- Rent-exempt stake accounts (~$0.10 per staker)
- Per-block reward calculation (not per-epoch like native SOL)

Technical Details:
- Stake Account: PDA derived from user + pool
- Reward Distribution: Every ~400ms (each block)
- Compound: Automatic or manual claim
- Unstake Cooldown: 1 epoch (~2 days) or instant with penalty

Staking Architecture:
1. User deposits VCoin to stake pool PDA
2. Stake amount tracked on-chain
3. Rewards calculated proportionally per block
4. Fee discounts enforced via on-chain lookup

On-chain Benefits:
- Instant staking (no epoch wait like native SOL)
- Composable with DeFi protocols
- Verifiable APY on-chain
- Gas-efficient batch operations

Cost Structure (November 2025):
- Stake transaction: ~$0.00025
- Claim rewards: ~$0.00025  
- Unstake: ~$0.00025
- Create stake account (one-time): ~$0.10

Governance (Future):
- Realms integration for voting
- Vote-escrowed staking (veVCoin)
- Proposal creation thresholds
"""

from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum
from app.models import SimulationParameters


class StakeAccountState(Enum):
    """State of a Solana stake account"""
    INACTIVE = "inactive"
    ACTIVATING = "activating"
    ACTIVE = "active"
    DEACTIVATING = "deactivating"
    COOLDOWN = "cooldown"


@dataclass
class StakingTier:
    """Staking tier with associated benefits"""
    name: str
    min_stake: float
    fee_discount: float
    voting_power: float
    apy_bonus: float
    # Solana-specific
    priority_fee_discount: float = 0  # Discount on priority fees
    nft_boost_eligible: bool = False  # Can boost with NFT staking


# Default staking tiers (WhitePaper v1.4 - Section 5.4)
STAKING_TIERS = [
    StakingTier(
        name="Bronze", 
        min_stake=1000,      # WhitePaper: 1,000 VCN minimum
        fee_discount=0.10, 
        voting_power=1.0, 
        apy_bonus=0,
        priority_fee_discount=0,
        nft_boost_eligible=False
    ),
    StakingTier(
        name="Silver", 
        min_stake=5000,      # WhitePaper: 5,000 VCN minimum
        fee_discount=0.20, 
        voting_power=2.0, 
        apy_bonus=0.01,
        priority_fee_discount=0.10,
        nft_boost_eligible=False
    ),
    StakingTier(
        name="Gold", 
        min_stake=20000,     # WhitePaper: 20,000 VCN minimum
        fee_discount=0.30, 
        voting_power=5.0, 
        apy_bonus=0.02,
        priority_fee_discount=0.25,
        nft_boost_eligible=True
    ),
    StakingTier(
        name="Platinum", 
        min_stake=100000,    # WhitePaper: 100,000 VCN minimum
        fee_discount=0.50, 
        voting_power=10.0, 
        apy_bonus=0.03,
        priority_fee_discount=0.50,
        nft_boost_eligible=True
    ),
]

# Solana staking constants (November 2025)
SOLANA_STAKE_ACCOUNT_RENT = 0.00203928  # SOL for rent-exempt stake account
SOLANA_EPOCH_DURATION_DAYS = 2  # Approximate epoch duration
SOLANA_BLOCKS_PER_DAY = 216000  # At 400ms per block
STAKE_TX_COST_USD = 0.00025  # Per staking transaction


def get_staking_tier(stake_amount: float) -> Optional[StakingTier]:
    """Get the staking tier for a given stake amount."""
    current_tier = None
    for tier in STAKING_TIERS:
        if stake_amount >= tier.min_stake:
            current_tier = tier
    return current_tier


def calculate_staking_rewards(
    staked_amount: float,
    apy: float,
    duration_months: int = 1,
    tier_bonus: float = 0
) -> float:
    """
    Calculate staking rewards for a given amount and duration.
    
    Args:
        staked_amount: Amount of VCoin staked
        apy: Annual percentage yield (0.10 = 10%)
        duration_months: Staking duration in months
        tier_bonus: Additional APY from tier bonus
    
    Returns:
        Rewards earned in VCoin
    """
    effective_apy = apy + tier_bonus
    monthly_rate = effective_apy / 12
    rewards = staked_amount * monthly_rate * duration_months
    return rewards


def estimate_staking_participation(
    users: int,
    participation_rate: float,
    avg_stake_amount: float,
    token_price: float,
    monthly_emission: float,
    staking_apy: float = 0.10,
    stake_lock_days: int = 30
) -> Dict[str, float]:
    """
    Estimate staking participation based on user-configured parameters.
    
    Now uses configurable participation_rate and avg_stake_amount instead of
    hardcoded maturity-based values. APY and lock days also affect participation.
    
    Args:
        users: Total active users
        participation_rate: Base % of users who stake (from params)
        avg_stake_amount: Average stake per staker in VCoin (from params)
        token_price: Current token price
        monthly_emission: Monthly token emission
        staking_apy: Annual staking APY (higher = more participation)
        stake_lock_days: Lock period in days (lower = more participation)
    """
    # APY modifier: Higher APY attracts more stakers
    # 10% APY = 1.0x, 20% APY = 1.2x, 30% APY = 1.4x
    apy_modifier = 1.0 + (staking_apy - 0.10) * 2
    apy_modifier = max(0.6, min(1.5, apy_modifier))  # Cap between 0.6x - 1.5x
    
    # Lock period modifier: Shorter lock = more participation
    # 30 days = 1.0x, 7 days = 1.3x, 90 days = 0.8x
    lock_modifier = 1.0 - (stake_lock_days - 30) * 0.01
    lock_modifier = max(0.5, min(1.5, lock_modifier))  # Cap between 0.5x - 1.5x
    
    # Apply modifiers to base participation rate
    effective_participation = participation_rate * apy_modifier * lock_modifier
    effective_participation = max(0.01, min(0.60, effective_participation))  # 1-60% cap
    
    stakers = int(users * effective_participation)
    
    # Average stake amount (directly from params, with APY bonus)
    # Higher APY encourages larger stakes
    avg_stake = avg_stake_amount * (1.0 + (staking_apy - 0.10) * 0.5)
    avg_stake = max(100, avg_stake)  # Minimum 100 VCoin
    
    total_staked = stakers * avg_stake
    total_staked_usd = total_staked * token_price
    
    # Staking as % of monthly emission
    staking_ratio = total_staked / monthly_emission if monthly_emission > 0 else 0
    
    return {
        'stakers_count': stakers,
        'participation_rate': effective_participation,
        'avg_stake_amount': avg_stake,
        'total_staked': total_staked,
        'total_staked_usd': total_staked_usd,
        'staking_emission_ratio': staking_ratio,
        'apy_modifier': apy_modifier,
        'lock_modifier': lock_modifier,
    }


def calculate_fee_savings(
    user_monthly_fees: float,
    fee_discount: float
) -> float:
    """Calculate monthly fee savings from staking discount."""
    return user_monthly_fees * fee_discount


def calculate_staking(
    params: SimulationParameters,
    users: int,
    monthly_emission: float,
    circulating_supply: float = 100_000_000,
    five_a_apy_boost: float = 0.0,
    max_staking_budget: float = None,
) -> dict:
    """
    Calculate complete staking metrics for Solana-based staking program.
    
    === SOLANA STAKING PROGRAM (November 2025) ===
    
    On-chain staking with:
    - Per-block reward distribution (~400ms)
    - Automatic compounding option
    - Instant staking (no epoch wait)
    - Minimal gas costs (~$0.00025 per transaction)
    
    === UNIFIED BUDGET CONSTRAINT (December 2025) ===
    
    Staking rewards are now subject to a unified budget constraint:
    - User rewards are calculated first (priority for growth)
    - Staking rewards are capped to remaining budget
    - If staking would exceed budget, effective APY is reduced
    
    Args:
        params: Simulation parameters
        users: Total active users
        monthly_emission: Monthly token emission
        circulating_supply: Current circulating supply
        five_a_apy_boost: Average 5A APY boost across population (0.0-0.5)
        max_staking_budget: Maximum VCoin available for staking rewards (unified budget constraint)
    
    5A Integration (Dec 2025):
    - High 5A stakers get bonus APY (up to +50%)
    - five_a_apy_boost is average boost across staking population
    - Increases effective APY and staking attractiveness
    
    Returns:
        Dict with all staking metrics and Solana-specific data
    """
    # Check if module is enabled
    if not getattr(params, 'enable_staking', True):
        return {
            'enabled': False,
            'revenue': 0,
            'costs': 0,
            'profit': 0,
            'margin': 0,
            'protocol_fee_from_rewards_usd': 0,
            'protocol_fee_from_rewards_vcoin': 0,
            'unstake_penalty_usd': 0,
            'unstake_penalty_vcoin': 0,
            'tx_fee_revenue_usd': 0,
            'tx_fee_revenue_vcoin': 0,
            'total_revenue_vcoin': 0,
            'staking_apy': 0,
            'staking_cap': 0,
            'staking_at_capacity': False,
            'staking_capacity_percent': 0,
            'staker_fee_discount': 0,
            'min_stake_amount': 0,
            'lock_days': 0,
            'stakers_count': 0,
            'participation_rate': 0,
            'avg_stake_amount': 0,
            'total_staked': 0,
            'total_staked_usd': 0,
            'staking_ratio': 0,
            'total_monthly_rewards': 0,
            'total_monthly_rewards_usd': 0,
            'rewards_per_staker': 0,
            'rewards_per_staker_usd': 0,
            'effective_monthly_yield': 0,
            'tier_distribution': {'bronze': 0, 'silver': 0, 'gold': 0, 'platinum': 0},
            'total_fee_savings_usd': 0,
            'locked_supply_percent': 0,
            'reduced_sell_pressure': 0,
            'reduced_sell_pressure_usd': 0,
            'staking_status': 'Disabled',
            'is_healthy': False,
            'annual_rewards_total': 0,
            'annual_rewards_usd': 0,
        }
    
    # Get parameters
    base_staking_apy = params.staking_apy
    # 5A Integration: Apply APY boost from 5A policy
    # High 5A stakers get bonus APY (e.g., avg_boost of 0.05 = +5% effective APY)
    effective_five_a_apy_boost = base_staking_apy * five_a_apy_boost  # e.g., 10% * 0.5 = +5%
    staking_apy = base_staking_apy + effective_five_a_apy_boost
    
    # HIGH-04 Fix: Use maturity-adjusted staking participation rate
    if hasattr(params, 'get_effective_staking_participation'):
        staking_participation_rate = params.get_effective_staking_participation()
    else:
        staking_participation_rate = getattr(params, 'staking_participation_rate', 0.15)
    avg_stake_amount = getattr(params, 'avg_stake_amount', 2000)
    staker_fee_discount = params.staker_fee_discount
    min_stake = params.min_stake_amount
    lock_days = params.stake_lock_days
    token_price = params.token_price
    
    # Estimate participation using maturity-adjusted parameters
    participation = estimate_staking_participation(
        users=users,
        participation_rate=staking_participation_rate,
        avg_stake_amount=avg_stake_amount,
        token_price=token_price,
        monthly_emission=monthly_emission,
        staking_apy=staking_apy,
        stake_lock_days=lock_days
    )
    
    stakers_count = participation['stakers_count']
    total_staked = participation['total_staked']
    avg_stake = participation['avg_stake_amount']
    
    # === DYNAMIC STAKING CAP (December 2025) ===
    # Calculate max tokens that can be staked within budget at current APY
    # Uses 7% APY cap to ensure budget compliance with minimal overflow
    # Grandfather: existing stakes stay, cap only limits new staking
    
    if max_staking_budget is not None and max_staking_budget > 0 and staking_apy > 0:
        # Max staked = budget * 12 / APY
        staking_cap = (max_staking_budget * 12) / staking_apy
        
        # Cap the staked amount to what budget allows
        if total_staked > staking_cap:
            # Over cap - limit to cap (grandfather in monthly progression)
            capped_staked = staking_cap
            staking_at_capacity = True
        else:
            capped_staked = total_staked
            staking_at_capacity = False
        
        # Use capped staked amount for reward calculations
        effective_total_staked = capped_staked
    else:
        # No budget constraint or invalid values
        staking_cap = float('inf')
        staking_at_capacity = False
        effective_total_staked = total_staked
    
    # Calculate staking capacity percentage
    if staking_cap > 0 and staking_cap != float('inf'):
        staking_capacity_percent = (total_staked / staking_cap) * 100
    else:
        staking_capacity_percent = 0
    
    # Calculate total staking rewards with capped staked amount
    total_monthly_rewards = calculate_staking_rewards(
        effective_total_staked,
        staking_apy,
        duration_months=1
    )
    
    # Update total_staked to reflect capped value for downstream calculations
    original_total_staked = total_staked
    total_staked = effective_total_staked
    
    # Rewards per staker
    rewards_per_staker = (
        total_monthly_rewards / stakers_count 
        if stakers_count > 0 else 0
    )
    
    # Calculate staking pool value
    staking_pool_usd = total_staked * token_price
    
    # Staking ratio of circulating supply
    staking_ratio = (
        total_staked / circulating_supply 
        if circulating_supply > 0 else 0
    )
    
    # Effective APY after considering token price
    rewards_usd = total_monthly_rewards * token_price
    effective_monthly_yield = (
        rewards_usd / staking_pool_usd 
        if staking_pool_usd > 0 else 0
    )
    
    # Staking tier distribution (estimated)
    tier_distribution = {
        'bronze': int(stakers_count * 0.60),   # 60% in Bronze
        'silver': int(stakers_count * 0.25),   # 25% in Silver
        'gold': int(stakers_count * 0.12),     # 12% in Gold
        'platinum': int(stakers_count * 0.03), # 3% in Platinum
    }
    
    # Calculate fee savings for platform
    avg_monthly_fees = 5.0  # Estimated $5/month in fees for active user
    total_fee_savings = stakers_count * avg_monthly_fees * staker_fee_discount
    
    # Reduce sell pressure calculation
    locked_supply_percent = staking_ratio * 100
    reduced_sell_pressure = total_staked * 0.30  # 30% would have been sold
    
    # Health indicators
    is_healthy = staking_ratio >= 0.05
    staking_status = (
        "Healthy" if staking_ratio >= 0.10 else
        "Moderate" if staking_ratio >= 0.05 else
        "Low"
    )
    
    # === PLATFORM REVENUE FROM STAKING ===
    
    # Issue #3 Fix: Protocol Fee on Staking Rewards (5% to match rewards.py PLATFORM_FEE_RATE)
    # Changed from 10% to 5% for consistency across all platform fees
    protocol_reward_fee_rate = getattr(params, 'staking_protocol_fee', 0.05)
    protocol_fee_from_rewards = total_monthly_rewards * protocol_reward_fee_rate
    protocol_fee_from_rewards_usd = protocol_fee_from_rewards * token_price
    
    # 2. Unstaking Fees (penalty on early unstakes)
    # Configurable rates for scenario modeling
    early_unstake_rate = getattr(params, 'early_unstake_rate', 0.15)  # 15% default
    early_unstake_penalty_rate = getattr(params, 'early_unstake_penalty_rate', 0.01)  # 1% default
    
    if stakers_count > 0:
        early_unstakers = int(stakers_count * early_unstake_rate)
        unstake_penalty_vcoin = early_unstakers * avg_stake * early_unstake_penalty_rate
        unstake_penalty_usd = unstake_penalty_vcoin * token_price
        
        # 3. Stake/Unstake Transaction Fees (platform keeps small fee per transaction)
        # Platform charges 0.1% on stake/unstake operations
        platform_tx_fee_rate = 0.001  # 0.1% of staked amount per transaction
        monthly_stake_txs = stakers_count * 2  # avg 2 txs per staker per month
        tx_fee_revenue_vcoin = monthly_stake_txs * avg_stake * platform_tx_fee_rate
        tx_fee_revenue_usd = tx_fee_revenue_vcoin * token_price
    else:
        # No stakers = no penalties or transaction fees
        early_unstakers = 0
        unstake_penalty_vcoin = 0
        unstake_penalty_usd = 0
        platform_tx_fee_rate = 0.001  # Keep for reference
        monthly_stake_txs = 0
        tx_fee_revenue_vcoin = 0
        tx_fee_revenue_usd = 0
    
    # Calculate expected early unstake impact on net rewards
    # Note: Early unstakers forfeit their pending rewards (penalty applies to staked amount)
    # The net rewards reported are for stakers who complete the full staking period
    expected_early_unstake_reward_loss = (
        early_unstakers * (total_monthly_rewards / stakers_count) if stakers_count > 0 else 0
    )
    
    # Total Platform Revenue from Staking
    staking_revenue_vcoin = protocol_fee_from_rewards + unstake_penalty_vcoin + tx_fee_revenue_vcoin
    staking_revenue_usd = protocol_fee_from_rewards_usd + unstake_penalty_usd + tx_fee_revenue_usd
    
    # Staking Costs on Solana are MINIMAL
    # - No expensive infrastructure (it's on-chain)
    # - Only cost is Solana tx fees for reward distribution (~$0.00025 per tx)
    # - Smart contract rent is one-time, not monthly
    reward_distribution_txs = stakers_count  # 1 claim per staker per month
    staking_infra_cost_usd = reward_distribution_txs * STAKE_TX_COST_USD * 10  # 10x buffer for operations
    staking_infra_cost_usd = max(0.10, staking_infra_cost_usd)  # Minimum $0.10/month
    
    # Staking Profit (should be positive on Solana due to low costs!)
    staking_profit_usd = staking_revenue_usd - staking_infra_cost_usd
    staking_margin = (staking_profit_usd / staking_revenue_usd * 100) if staking_revenue_usd > 0 else 0
    
    # === SOLANA-SPECIFIC CALCULATIONS ===
    
    # Stake account creation costs (one-time per staker)
    stake_account_rent_sol = SOLANA_STAKE_ACCOUNT_RENT
    stake_account_rent_usd = stake_account_rent_sol * 50  # At $50/SOL
    total_stake_accounts_cost = stakers_count * stake_account_rent_usd
    
    # Transaction costs for staking operations
    # Estimate: 3 txs per staker per month (stake, claim, compound)
    staking_txs_per_month = stakers_count * 3
    total_tx_costs = staking_txs_per_month * STAKE_TX_COST_USD
    
    # Rewards distribution frequency
    blocks_per_month = SOLANA_BLOCKS_PER_DAY * 30
    rewards_per_block = total_monthly_rewards / blocks_per_month
    
    # Compound frequency options
    daily_compound_apy = ((1 + staking_apy / 365) ** 365 - 1)  # With daily compound
    
    # Unstake cooldown
    cooldown_epochs = 1  # 1 epoch = ~2 days
    instant_unstake_penalty = 0.02  # 2% penalty for instant unstake
    
    return {
        # === PLATFORM REVENUE & PROFIT ===
        'revenue': round(staking_revenue_usd, 2),
        'costs': round(staking_infra_cost_usd, 2),
        'profit': round(staking_profit_usd, 2),
        'margin': round(staking_margin, 1),
        
        # Revenue breakdown
        'protocol_fee_from_rewards_usd': round(protocol_fee_from_rewards_usd, 2),
        'protocol_fee_from_rewards_vcoin': round(protocol_fee_from_rewards, 2),
        'unstake_penalty_usd': round(unstake_penalty_usd, 2),
        'unstake_penalty_vcoin': round(unstake_penalty_vcoin, 2),
        'tx_fee_revenue_usd': round(tx_fee_revenue_usd, 2),
        'tx_fee_revenue_vcoin': round(tx_fee_revenue_vcoin, 2),
        'total_revenue_vcoin': round(staking_revenue_vcoin, 2),
        
        # Core metrics
        'staking_apy': round(staking_apy * 100, 1),  # Fixed 7% APY
        'staking_cap': round(staking_cap, 2) if staking_cap != float('inf') else 0,  # Max tokens allowed
        'staking_at_capacity': staking_at_capacity,  # Whether staking pool is full
        'staking_capacity_percent': round(min(staking_capacity_percent, 100), 1),  # Current usage of capacity
        'staker_fee_discount': round(staker_fee_discount * 100, 1),
        'min_stake_amount': min_stake,
        'lock_days': lock_days,
        
        # Participation
        'stakers_count': stakers_count,
        'participation_rate': round(participation['participation_rate'] * 100, 1),
        'avg_stake_amount': round(avg_stake, 2),
        
        # Totals
        'total_staked': round(total_staked, 2),
        'total_staked_usd': round(staking_pool_usd, 2),
        'staking_ratio': round(staking_ratio * 100, 2),
        
        # Rewards (paid to stakers - net after protocol fee)
        'total_monthly_rewards': round(total_monthly_rewards - protocol_fee_from_rewards, 2),
        'total_monthly_rewards_usd': round((total_monthly_rewards - protocol_fee_from_rewards) * token_price, 2),
        'rewards_per_staker': round((total_monthly_rewards - protocol_fee_from_rewards) / stakers_count if stakers_count > 0 else 0, 2),
        'rewards_per_staker_usd': round((total_monthly_rewards - protocol_fee_from_rewards) / stakers_count * token_price if stakers_count > 0 else 0, 2),
        'effective_monthly_yield': round(effective_monthly_yield * 100, 2),
        
        # Tier distribution
        'tier_distribution': tier_distribution,
        
        # Platform impact
        'total_fee_savings_usd': round(total_fee_savings, 2),
        'locked_supply_percent': round(locked_supply_percent, 2),
        'reduced_sell_pressure': round(reduced_sell_pressure, 2),
        'reduced_sell_pressure_usd': round(reduced_sell_pressure * token_price, 2),
        
        # Health
        'staking_status': staking_status,
        'is_healthy': is_healthy,
        
        # Annual projections
        'annual_rewards_total': round(total_monthly_rewards * 12, 2),
        'annual_rewards_usd': round(rewards_usd * 12, 2),
        
        # Early unstake impact tracking
        'early_unstake_rate': round(early_unstake_rate * 100, 1),
        'early_unstake_penalty_rate': round(early_unstake_penalty_rate * 100, 2),
        'early_unstakers_count': early_unstakers,
        'expected_early_unstake_reward_loss': round(expected_early_unstake_reward_loss, 2),
        
        # === SOLANA-SPECIFIC DATA ===
        'network': 'solana',
        'program_type': 'spl_token_staking',
        'framework': 'anchor',
        
        # On-chain costs
        'stake_account_rent_sol': round(stake_account_rent_sol, 6),
        'stake_account_rent_usd': round(stake_account_rent_usd, 4),
        'total_stake_accounts_cost_usd': round(total_stake_accounts_cost, 2),
        'staking_tx_cost_usd': STAKE_TX_COST_USD,
        'monthly_tx_costs_usd': round(total_tx_costs, 4),
        
        # Reward distribution
        'reward_frequency': 'per_block',
        'blocks_per_month': blocks_per_month,
        'rewards_per_block': round(rewards_per_block, 8),
        
        # Compound options
        'auto_compound_enabled': True,
        'daily_compound_apy': round(daily_compound_apy * 100, 2),
        'compound_boost': round((daily_compound_apy - staking_apy) * 100, 2),
        
        # Unstaking
        'cooldown_epochs': cooldown_epochs,
        'cooldown_days': cooldown_epochs * SOLANA_EPOCH_DURATION_DAYS,
        'instant_unstake_available': True,
        'instant_unstake_penalty': round(instant_unstake_penalty * 100, 1),
        
        # Solana advantages
        'eth_equivalent_tx_cost': round(staking_txs_per_month * 5.0, 2),  # ~$5 per ETH staking tx
        'solana_savings': round((staking_txs_per_month * 5.0) - total_tx_costs, 2),
        
        # Governance (future)
        'governance_enabled': False,  # Coming soon
        'governance_platform': 'realms',
        'vote_escrow_planned': True,  # veVCoin coming
        
        # WP-005 & MED-002 Fix: Document staking reward funding source
        # Staking rewards are NOT from platform revenue - they come from emission allocation
        'reward_funding_source': 'emission_allocation',
        'reward_funding_details': (
            "Staking rewards are funded from the 35% Ecosystem & Rewards allocation "
            "(350M VCoin over 60 months = 5.83M VCoin/month). The 10% APY is a target rate "
            "that may require treasury subsidies if staking participation exceeds projections. "
            "Protocol fee (5%) on rewards provides some offset but does not fully fund APY."
        ),
        # Calculate if rewards exceed module fee income (sustainability warning)
        'rewards_exceed_module_income': staking_revenue_usd < (total_monthly_rewards * token_price),
        'sustainability_warning': (
            "WARNING: Staking rewards exceed platform staking revenue. "
            "Difference is subsidized from emission allocation or treasury."
        ) if staking_revenue_usd < (total_monthly_rewards * token_price) else None,
        
        # 5A Integration
        'five_a_apy_boost': round(five_a_apy_boost * 100, 2),
        'five_a_effective_apy_boost': round(effective_five_a_apy_boost * 100, 2),
        'base_staking_apy': round(base_staking_apy * 100, 1),
    }

