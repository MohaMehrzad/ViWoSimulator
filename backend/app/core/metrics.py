"""
Token Metrics Module - Advanced tokenomics calculations.

Provides key token health metrics including:
- Token Velocity (transaction volume / circulating supply)
- Real Yield (revenue-based yield, not emissions)
- Value Accrual Score (0-100 comprehensive score)
- Gini Coefficient (token distribution fairness)
- Treasury Runway (months of operating expenses covered)

Based on DeFi best practices and tokenomics research.
"""

from typing import Dict, Optional
from dataclasses import dataclass
import math


@dataclass
class TokenMetricsConfig:
    """Configuration for token metrics calculations"""
    # Velocity thresholds
    velocity_low: float = 0.5          # Below this is low velocity (bearish for price)
    velocity_high: float = 5.0         # Above this is high velocity (too much selling)
    velocity_optimal_low: float = 1.0  # Optimal range start
    velocity_optimal_high: float = 3.0 # Optimal range end
    
    # Real yield thresholds
    real_yield_min: float = 0.02       # 2% minimum to be meaningful
    real_yield_high: float = 0.15      # 15%+ is exceptional
    
    # Value accrual weights
    weight_burn: float = 0.20
    weight_buyback: float = 0.20
    weight_staking: float = 0.15
    weight_utility: float = 0.25
    weight_governance: float = 0.10
    weight_liquidity: float = 0.10


DEFAULT_METRICS_CONFIG = TokenMetricsConfig()


def calculate_token_velocity(
    transaction_volume: float,
    circulating_supply: float,
    time_period_days: int = 30
) -> Dict[str, float]:
    """
    Calculate token velocity.
    
    Velocity = Transaction Volume / Circulating Supply (over a period)
    
    Interpretation:
    - Low velocity (<1): Tokens are being held (bullish for price)
    - Optimal (1-3): Healthy usage and holding balance
    - High velocity (>5): Too much trading/selling (bearish for price)
    
    Args:
        transaction_volume: Total transaction volume in tokens
        circulating_supply: Current circulating supply
        time_period_days: Time period for measurement (default 30 days)
    
    Returns:
        Dict with velocity metrics
    """
    if circulating_supply <= 0:
        return {
            'velocity': 0,
            'annualized_velocity': 0,
            'interpretation': 'No supply',
            'health_score': 0,
        }
    
    # Calculate velocity
    velocity = transaction_volume / circulating_supply
    
    # Annualize if not already annual
    annualized_velocity = velocity * (365 / time_period_days)
    
    # Determine interpretation
    # MED-02 Fix: Health score measures ECOSYSTEM health, not just price outlook.
    # A healthy ecosystem has balanced velocity - not too low (no utility) or too high (no holding).
    # Low velocity is good for price (holding) but indicates low platform usage.
    # We score low velocity at 80 (not 100) because it suggests underutilization.
    config = DEFAULT_METRICS_CONFIG
    if velocity < config.velocity_low:
        interpretation = 'Low - tokens being held (bullish for price, low utility)'
        health_score = 80  # MED-02: Raised from 70 to 80 for consistency
    elif velocity <= config.velocity_optimal_high:
        interpretation = 'Optimal - healthy balance of usage and holding'
        health_score = 100
    elif velocity <= config.velocity_high:
        interpretation = 'Elevated - active trading (increased sell pressure)'
        health_score = 60
    else:
        interpretation = 'High - excessive selling pressure (bearish)'
        health_score = 30
    
    # Calculate days to turn over supply
    days_to_turnover = time_period_days / velocity if velocity > 0 else float('inf')
    
    return {
        'velocity': round(velocity, 4),
        'annualized_velocity': round(annualized_velocity, 4),
        'interpretation': interpretation,
        'health_score': health_score,
        'days_to_turnover': round(days_to_turnover, 1) if days_to_turnover != float('inf') else 0,
        'transaction_volume': round(transaction_volume, 2),
        'circulating_supply': round(circulating_supply, 2),
        'time_period_days': time_period_days,
    }


def calculate_real_yield(
    protocol_revenue: float,
    staked_supply: float,
    token_price: float,
    exclude_emissions: bool = True
) -> Dict[str, float]:
    """
    Calculate real yield (revenue-based, not emission-based).
    
    Real Yield = Protocol Revenue / Staked Supply Value
    
    This measures yield from actual revenue, not token emissions.
    True sustainable yield should be funded by protocol revenue.
    
    Args:
        protocol_revenue: Monthly protocol revenue in USD
        staked_supply: Total tokens staked
        token_price: Current token price in USD
        exclude_emissions: Whether this excludes emission-based rewards
    
    Returns:
        Dict with real yield metrics
    """
    staked_value = staked_supply * token_price
    
    if staked_value <= 0:
        return {
            'monthly_real_yield': 0,
            'annual_real_yield': 0,
            'interpretation': 'No staked value',
            'is_sustainable': False,
            'yield_per_1000_usd': 0,
        }
    
    monthly_yield = protocol_revenue / staked_value
    annual_yield = monthly_yield * 12
    
    config = DEFAULT_METRICS_CONFIG
    
    if annual_yield >= config.real_yield_high:
        interpretation = 'Exceptional - strong revenue model'
        is_sustainable = True
    elif annual_yield >= config.real_yield_min:
        interpretation = 'Healthy - sustainable yield'
        is_sustainable = True
    elif annual_yield > 0:
        interpretation = 'Low - may need emission subsidies'
        is_sustainable = False
    else:
        interpretation = 'None - no revenue distribution'
        is_sustainable = False
    
    # Calculate yield per $1000 staked
    yield_per_1000 = 1000 * monthly_yield
    
    return {
        'monthly_real_yield': round(monthly_yield * 100, 3),
        'annual_real_yield': round(annual_yield * 100, 2),
        'interpretation': interpretation,
        'is_sustainable': is_sustainable,
        'yield_per_1000_usd': round(yield_per_1000, 2),
        'protocol_revenue': round(protocol_revenue, 2),
        'staked_value_usd': round(staked_value, 2),
        'excludes_emissions': exclude_emissions,
    }


def calculate_value_accrual_score(
    burn_rate: float,
    buyback_rate: float,
    staking_ratio: float,
    utility_score: float,
    governance_participation: float,
    liquidity_ratio: float,
    config: TokenMetricsConfig = DEFAULT_METRICS_CONFIG
) -> Dict[str, any]:
    """
    Calculate comprehensive value accrual score (0-100).
    
    Measures how well token captures value through:
    - Burns (deflationary pressure)
    - Buybacks (market support)
    - Staking (supply lock)
    - Utility (real usage)
    - Governance (engagement)
    - Liquidity (market health)
    
    Args:
        burn_rate: Annual burn rate (0-1)
        buyback_rate: Annual buyback rate (0-1)
        staking_ratio: Staked / circulating supply (0-1)
        utility_score: Utility usage score (0-100)
        governance_participation: Governance participation rate (0-1)
        liquidity_ratio: Liquidity / market cap ratio (0-1)
        config: Metrics configuration
    
    Returns:
        Dict with value accrual score and breakdown
    """
    # Normalize inputs (0-100 scale)
    burn_score = min(100, burn_rate * 1000)  # 10% burn = 100
    buyback_score = min(100, buyback_rate * 1000)  # 10% buyback = 100
    staking_score = min(100, staking_ratio * 200)  # 50% staked = 100
    utility_input = min(100, utility_score)
    # HIGH-002 Fix: Adjusted governance multiplier from 500 to 200
    # Industry benchmarks show 20% participation is already good (Compound, Uniswap)
    # Now: 50% participation = 100 (more realistic threshold)
    # Before: 20% participation = 100 (too easy to max)
    governance_score = min(100, governance_participation * 200)  # 50% participation = 100
    liquidity_score = min(100, liquidity_ratio * 500)  # 20% liquidity = 100
    
    # Calculate weighted score
    total_score = (
        burn_score * config.weight_burn +
        buyback_score * config.weight_buyback +
        staking_score * config.weight_staking +
        utility_input * config.weight_utility +
        governance_score * config.weight_governance +
        liquidity_score * config.weight_liquidity
    )
    
    # Determine grade
    if total_score >= 80:
        grade = 'A'
        interpretation = 'Excellent value accrual'
    elif total_score >= 60:
        grade = 'B'
        interpretation = 'Good value accrual'
    elif total_score >= 40:
        grade = 'C'
        interpretation = 'Moderate value accrual'
    elif total_score >= 20:
        grade = 'D'
        interpretation = 'Weak value accrual'
    else:
        grade = 'F'
        interpretation = 'Poor value accrual'
    
    return {
        'total_score': round(total_score, 1),
        'grade': grade,
        'interpretation': interpretation,
        'breakdown': {
            'burn': round(burn_score, 1),
            'buyback': round(buyback_score, 1),
            'staking': round(staking_score, 1),
            'utility': round(utility_input, 1),
            'governance': round(governance_score, 1),
            'liquidity': round(liquidity_score, 1),
        },
        'weights': {
            'burn': config.weight_burn,
            'buyback': config.weight_buyback,
            'staking': config.weight_staking,
            'utility': config.weight_utility,
            'governance': config.weight_governance,
            'liquidity': config.weight_liquidity,
        },
        'inputs': {
            'burn_rate': burn_rate,
            'buyback_rate': buyback_rate,
            'staking_ratio': staking_ratio,
            'utility_score': utility_score,
            'governance_participation': governance_participation,
            'liquidity_ratio': liquidity_ratio,
        },
    }


def calculate_utility_score(
    users: int,
    identity_result: dict,
    content_result: dict,
    advertising_result: dict,
    exchange_result: dict,
    recapture_result: dict,
    staking_result: dict,
    total_revenue: float,
) -> float:
    """
    Calculate comprehensive utility score (0-100) based on real platform activity.
    
    Components:
    1. Module Engagement (25%) - Active users across modules
    2. Token Velocity (25%) - VCoin being used in ecosystem
    3. Revenue per User (25%) - Real economic activity
    4. Feature Adoption (25%) - Premium features, NFTs, staking
    
    Returns:
        float: Utility score 0-100
    """
    if users <= 0:
        return 0.0
    
    scores = []
    
    # === 1. MODULE ENGAGEMENT (25%) ===
    # How many users are actively engaging with modules
    
    # Identity: upgraded users (not free basic users)
    # HIGH-003 Fix: Calibrated to industry benchmarks
    # Industry reality: 2-5% paid conversion is excellent for freemium apps
    # Now: 4% upgraded = 100 (using * 2500)
    # Before: 20% upgraded = 100 (unrealistic - most platforms never hit 20%)
    identity_breakdown = identity_result.get('breakdown', {})
    upgraded_users = identity_breakdown.get('upgraded_users', 0)
    identity_engagement = min(100, (upgraded_users / max(users, 1)) * 2500)  # 4% upgraded = 100
    
    # Content: creators actively posting
    # HIGH-003 Fix: Calibrated to industry benchmarks
    # Industry reality: 5-15% of users create content (1% rule: 90% lurk, 9% engage, 1% create)
    # Now: 15% creators = 100 (using * 667)
    # Before: 50% creators = 100 (unrealistic - no platform has 50% creators)
    content_breakdown = content_result.get('breakdown', {})
    creators = content_breakdown.get('creators', 0)
    monthly_posts = content_breakdown.get('monthly_posts', 0)
    content_engagement = min(100, (creators / max(users, 1)) * 667)  # 15% creators = 100
    posts_per_creator = monthly_posts / max(creators, 1) if creators > 0 else 0
    content_activity = min(100, posts_per_creator * 5)  # 20 posts/creator = 100
    
    # Advertising: advertisers using platform
    ad_breakdown = advertising_result.get('breakdown', {})
    advertisers = ad_breakdown.get('advertisers', 0)
    ad_engagement = min(100, (advertisers / max(users, 1)) * 1000)  # 10% advertisers = 100
    
    # Exchange: traders using swap
    # Issue #1 fix: Use existing 'active_exchange_users' instead of non-existent 'traders'
    exchange_breakdown = exchange_result.get('breakdown', {})
    active_exchange_users = exchange_breakdown.get('active_exchange_users', 0)
    exchange_engagement = min(100, (active_exchange_users / max(users, 1)) * 500)  # 20% traders = 100
    
    module_engagement = (
        identity_engagement * 0.25 +
        content_engagement * 0.25 +
        content_activity * 0.15 +
        ad_engagement * 0.15 +
        exchange_engagement * 0.20
    )
    scores.append(('module_engagement', module_engagement, 0.25))
    
    # === 2. TOKEN VELOCITY/USAGE (25%) ===
    # How actively VCoin is being transacted
    
    # VCoin flowing through the system
    vcoin_volume = recapture_result.get('total_revenue_source_vcoin', 0)
    
    # Scale: 100K VCoin monthly volume per 1K users = healthy
    expected_volume = users * 100  # 100 VCoin per user per month = baseline
    volume_ratio = vcoin_volume / max(expected_volume, 1)
    token_usage = min(100, volume_ratio * 100)  # 1x expected = 100
    
    # Recapture rate shows tokens being recycled
    recapture_rate = recapture_result.get('recapture_rate', 0)
    recapture_score = min(100, recapture_rate * 300)  # 33% recapture = 100
    
    token_velocity_score = token_usage * 0.6 + recapture_score * 0.4
    scores.append(('token_velocity', token_velocity_score, 0.25))
    
    # === 3. REVENUE PER USER (25%) ===
    # Real economic activity per user
    
    revenue_per_user = total_revenue / max(users, 1)
    # $0.50 per user per month = 50, $1.00 = 100 (capped)
    revenue_score = min(100, revenue_per_user * 100)
    
    scores.append(('revenue_per_user', revenue_score, 0.25))
    
    # === 4. FEATURE ADOPTION (25%) ===
    # Premium features, NFTs, staking participation
    
    # Premium content users - use premium DM users as proxy (10% of users use premium DMs)
    # Issue #1 fix: Use existing breakdown keys instead of non-existent 'premium_content_users'
    premium_dm_users = content_breakdown.get('premium_dms', 0) / 3  # 3 DMs per user
    premium_adoption = min(100, (premium_dm_users / max(users, 1)) * 2000)  # 5% = 100
    
    # NFT minters - estimate from nft_mints (1 creator per ~3 mints on average)
    # Issue #1 fix: Use existing 'nft_mints' instead of non-existent 'nft_creators'
    nft_mints = content_breakdown.get('nft_mints', 0)
    nft_creators_estimate = max(1, nft_mints // 3) if nft_mints > 0 else 0
    nft_adoption = min(100, (nft_creators_estimate / max(users, 1)) * 1000)  # 10% = 100
    
    # Staking participation
    stakers = staking_result.get('stakers_count', 0)
    staking_adoption = min(100, (stakers / max(users, 1)) * 500)  # 20% = 100
    
    # Verified users (premium identity)
    verified_users = identity_breakdown.get('verified_users', 0) + \
                     identity_breakdown.get('premium_users', 0) + \
                     identity_breakdown.get('enterprise_users', 0)
    verified_adoption = min(100, (verified_users / max(users, 1)) * 500)  # 20% = 100
    
    feature_adoption = (
        premium_adoption * 0.25 +
        nft_adoption * 0.25 +
        staking_adoption * 0.25 +
        verified_adoption * 0.25
    )
    scores.append(('feature_adoption', feature_adoption, 0.25))
    
    # === FINAL WEIGHTED SCORE ===
    total_score = sum(score * weight for _, score, weight in scores)
    
    return round(min(100, max(0, total_score)), 1)


def calculate_gini_coefficient(
    holder_balances: list,
    total_supply: float = None
) -> Dict[str, float]:
    """
    Calculate Gini coefficient for token distribution.
    
    Gini = 0: Perfect equality (everyone has same amount)
    Gini = 1: Perfect inequality (one holder has everything)
    
    For tokens:
    - 0.0-0.3: Highly decentralized (rare for tokens)
    - 0.3-0.5: Moderately distributed
    - 0.5-0.7: Concentrated
    - 0.7-1.0: Highly concentrated (typical for early tokens)
    
    Args:
        holder_balances: List of token balances
        total_supply: Total supply (optional, calculated if not provided)
    
    Returns:
        Dict with Gini coefficient and distribution metrics
    """
    if not holder_balances or len(holder_balances) == 0:
        return {
            'gini': 1.0,
            'interpretation': 'No holders',
            'decentralization_score': 0,
        }
    
    n = len(holder_balances)
    sorted_balances = sorted(holder_balances)
    
    if total_supply is None:
        total_supply = sum(sorted_balances)
    
    if total_supply <= 0:
        return {
            'gini': 1.0,
            'interpretation': 'No supply',
            'decentralization_score': 0,
        }
    
    # Calculate Gini using the formula
    cumulative_sum = 0
    weighted_sum = 0
    
    for i, balance in enumerate(sorted_balances):
        cumulative_sum += balance
        weighted_sum += (i + 1) * balance
    
    gini = (2 * weighted_sum) / (n * total_supply) - (n + 1) / n
    gini = max(0, min(1, gini))  # Clamp to 0-1
    
    # Calculate top holder concentrations
    top_1_percent_idx = max(1, int(n * 0.99))
    top_10_percent_idx = max(1, int(n * 0.90))
    
    top_1_concentration = sum(sorted_balances[top_1_percent_idx:]) / total_supply
    top_10_concentration = sum(sorted_balances[top_10_percent_idx:]) / total_supply
    
    # Interpretation
    if gini < 0.3:
        interpretation = 'Highly decentralized'
    elif gini < 0.5:
        interpretation = 'Moderately distributed'
    elif gini < 0.7:
        interpretation = 'Concentrated'
    else:
        interpretation = 'Highly concentrated'
    
    # Decentralization score (inverse of Gini)
    decentralization_score = (1 - gini) * 100
    
    return {
        'gini': round(gini, 4),
        'interpretation': interpretation,
        'decentralization_score': round(decentralization_score, 1),
        'holder_count': n,
        'top_1_percent_concentration': round(top_1_concentration * 100, 2),
        'top_10_percent_concentration': round(top_10_concentration * 100, 2),
    }


def generate_realistic_holder_distribution(
    simulation_month: int,
    active_users: int,
    monthly_rewards_vcoin: float = 0,
    avg_user_balance: float = 0,
) -> list:
    """
    Generate realistic holder balances based on ACTUAL VCoin token allocation.
    
    This models the real-world distribution of tokens at any given month,
    accounting for:
    1. Vesting schedules for each allocation category
    2. Number of holders per category (team members, investors, users, etc.)
    3. Power-law distribution within categories (some holders have more)
    4. User rewards earned through platform participation
    
    Token Allocation (1B Total):
    - Seed Round: 2% (20M) - ~10-15 early investors
    - Private Round: 3% (30M) - ~15-25 VCs/strategic investors  
    - Public Sale: 5% (50M) - ~500-5000 public buyers
    - Team: 10% (100M) - ~20-50 team members
    - Advisors: 5% (50M) - ~10-20 advisors
    - Treasury/DAO: 20% (200M) - 1 governance wallet (excluded from Gini)
    - Ecosystem/Rewards: 35% (350M) - Distributed to users over 60 months
    - Liquidity: 10% (100M) - Protocol-owned in DEX (excluded from Gini)
    - Foundation: 2% (20M) - 1-2 foundation wallets
    - Marketing: 8% (80M) - 2-5 marketing wallets
    
    Args:
        simulation_month: Current simulation month (0 = TGE)
        active_users: Number of active platform users
        monthly_rewards_vcoin: Monthly reward distribution
        avg_user_balance: Average user balance (from staking/rewards)
    
    Returns:
        List of holder balances (VCoin amounts)
    """
    import random
    random.seed(42 + simulation_month)  # Deterministic but varies by month
    
    holder_balances = []
    
    # === VESTING SCHEDULE CALCULATIONS ===
    # Calculate what each category has unlocked by this month
    
    def get_vested_amount(total: int, tge_pct: float, cliff: int, vesting: int, month: int) -> int:
        """Calculate vested amount for a category at given month."""
        tge_unlock = int(total * tge_pct)
        remaining = total - tge_unlock
        
        if month == 0:
            return tge_unlock
        
        if month <= cliff:
            return tge_unlock
        
        if vesting == 0:
            return total
        
        vesting_end = cliff + vesting
        if month >= vesting_end:
            return total
        
        # Linear vesting during vesting period
        months_vested = month - cliff
        vested_amount = tge_unlock + (remaining * months_vested // vesting)
        return min(vested_amount, total)
    
    # === SEED ROUND: 20M, 0% TGE, 12 cliff, 24 vesting ===
    seed_vested = get_vested_amount(20_000_000, 0.0, 12, 24, simulation_month)
    if seed_vested > 0:
        # ~10-15 seed investors with power-law distribution
        seed_investors = 12
        for i in range(seed_investors):
            # Top 3 investors hold ~60% of seed round
            if i == 0:
                share = seed_vested * 0.25
            elif i == 1:
                share = seed_vested * 0.20
            elif i == 2:
                share = seed_vested * 0.15
            else:
                # Remaining 9 investors share 40%
                share = (seed_vested * 0.40) / (seed_investors - 3) * (0.7 + random.random() * 0.6)
            holder_balances.append(share)
    
    # === PRIVATE ROUND: 30M, 10% TGE, 6 cliff, 18 vesting ===
    private_vested = get_vested_amount(30_000_000, 0.10, 6, 18, simulation_month)
    if private_vested > 0:
        # ~15-25 private investors (VCs, strategic)
        private_investors = 20
        for i in range(private_investors):
            # Top 5 VCs hold ~65% of private round
            if i < 5:
                share = private_vested * 0.13 * (1 - i * 0.15)  # Decreasing share
            else:
                # Remaining 15 investors share 35%
                share = (private_vested * 0.35) / (private_investors - 5) * (0.6 + random.random() * 0.8)
            holder_balances.append(share)
    
    # === PUBLIC SALE: 50M, 50% TGE, 0 cliff, 3 vesting ===
    public_vested = get_vested_amount(50_000_000, 0.50, 0, 3, simulation_month)
    if public_vested > 0:
        # Public sale has many more holders - ~500-2000 at TGE, grows with users
        # Some whales, many small holders
        public_holders = max(500, min(active_users // 2, 5000))
        
        # Top 10% hold ~50% (whales who got in early)
        whale_count = max(10, public_holders // 10)
        whale_pool = public_vested * 0.50
        for i in range(whale_count):
            # Power-law among whales
            share = whale_pool * (0.4 ** (i / 3)) / whale_count * 3
            holder_balances.append(max(share, 100))
        
        # Remaining 90% hold 50%
        retail_count = public_holders - whale_count
        retail_pool = public_vested * 0.50
        avg_retail = retail_pool / max(1, retail_count)
        for i in range(retail_count):
            variance = 0.1 + random.random() * 2.5  # High variance in retail
            holder_balances.append(max(avg_retail * variance, 50))
    
    # === TEAM: 100M, 0% TGE, 12 cliff, 36 vesting ===
    team_vested = get_vested_amount(100_000_000, 0.0, 12, 36, simulation_month)
    if team_vested > 0:
        # ~30 team members with different allocation levels
        team_members = 30
        # Founders (2-3) hold ~40%, exec team (5-7) hold ~30%, rest hold 30%
        for i in range(team_members):
            if i < 3:  # Founders
                share = team_vested * 0.40 / 3 * (1 - i * 0.1)
            elif i < 10:  # Executive team
                share = team_vested * 0.30 / 7 * (0.8 + random.random() * 0.4)
            else:  # Rest of team
                share = team_vested * 0.30 / (team_members - 10) * (0.5 + random.random())
            holder_balances.append(share)
    
    # === ADVISORS: 50M, 0% TGE, 6 cliff, 18 vesting ===
    advisors_vested = get_vested_amount(50_000_000, 0.0, 6, 18, simulation_month)
    if advisors_vested > 0:
        # ~12 advisors
        advisor_count = 12
        for i in range(advisor_count):
            # Top 3 advisors hold ~50%
            if i < 3:
                share = advisors_vested * 0.50 / 3 * (1 - i * 0.15)
            else:
                share = advisors_vested * 0.50 / (advisor_count - 3) * (0.7 + random.random() * 0.6)
            holder_balances.append(share)
    
    # === FOUNDATION: 20M, 25% TGE, 3 cliff, 24 vesting ===
    foundation_vested = get_vested_amount(20_000_000, 0.25, 3, 24, simulation_month)
    if foundation_vested > 0:
        # 2 foundation wallets (operational + reserve)
        holder_balances.append(foundation_vested * 0.6)
        holder_balances.append(foundation_vested * 0.4)
    
    # === MARKETING: 80M, 25% TGE, 3 cliff, 18 vesting ===
    marketing_vested = get_vested_amount(80_000_000, 0.25, 3, 18, simulation_month)
    if marketing_vested > 0:
        # 3 marketing wallets (campaigns, partnerships, reserves)
        holder_balances.append(marketing_vested * 0.50)
        holder_balances.append(marketing_vested * 0.30)
        holder_balances.append(marketing_vested * 0.20)
    
    # === REWARDS DISTRIBUTED TO USERS ===
    # Users earn tokens through rewards, staking, etc.
    # This is the main driver of decentralization over time
    if active_users > 0 and monthly_rewards_vcoin > 0:
        # Cumulative rewards distributed by this month
        # Rewards: 5.83M/month for 60 months
        months_of_rewards = min(simulation_month, 60)
        total_rewards_distributed = months_of_rewards * 5_833_333
        
        # Not all rewards go to user wallets - some to staking, burns, etc.
        # Assume ~60% ends up in user wallets (rest is burned, fees, etc.)
        user_reward_pool = total_rewards_distributed * 0.60
        
        if user_reward_pool > 0:
            # Distribute among active users with power-law
            # Top 10% (power users) hold 50% of rewards earned
            # Next 30% (regular users) hold 35%  
            # Bottom 60% (casual users) hold 15%
            
            power_users = max(1, int(active_users * 0.10))
            regular_users = max(1, int(active_users * 0.30))
            casual_users = max(1, active_users - power_users - regular_users)
            
            # Power users (top 10%)
            power_pool = user_reward_pool * 0.50
            avg_power = power_pool / power_users
            for i in range(power_users):
                variance = 0.3 + random.random() * 1.4
                holder_balances.append(avg_power * variance)
            
            # Regular users (30%)
            regular_pool = user_reward_pool * 0.35
            avg_regular = regular_pool / regular_users
            for i in range(regular_users):
                variance = 0.4 + random.random() * 1.2
                holder_balances.append(avg_regular * variance)
            
            # Casual users (60%)
            casual_pool = user_reward_pool * 0.15
            avg_casual = casual_pool / casual_users
            for i in range(casual_users):
                variance = 0.2 + random.random() * 1.6
                holder_balances.append(max(avg_casual * variance, 10))
    
    # === EXCLUDED FROM GINI (Protocol-controlled, not tradeable) ===
    # - Treasury (200M): DAO-governed, not individual holdings
    # - Liquidity (100M): Locked in DEX pools, protocol-owned
    # These are NOT added to holder_balances as they don't represent individual wealth
    
    # Remove any zero or negative balances
    holder_balances = [b for b in holder_balances if b > 0]
    
    return holder_balances


def calculate_runway(
    treasury_balance_usd: float,
    monthly_expenses_usd: float,
    monthly_revenue_usd: float,
    burn_runway_months: int = 36
) -> Dict[str, any]:
    """
    Calculate treasury runway.
    
    Args:
        treasury_balance_usd: Current treasury balance
        monthly_expenses_usd: Monthly operating expenses
        monthly_revenue_usd: Monthly revenue
        burn_runway_months: Target runway (default 36 months)
    
    Returns:
        Dict with runway metrics
    """
    net_burn = monthly_expenses_usd - monthly_revenue_usd
    
    if net_burn <= 0:
        # Revenue covers expenses
        return {
            'runway_months': float('inf'),
            'runway_years': float('inf'),
            'is_sustainable': True,
            'interpretation': 'Self-sustaining',
            'net_burn_monthly': round(net_burn, 2),
            'monthly_revenue': round(monthly_revenue_usd, 2),
            'monthly_expenses': round(monthly_expenses_usd, 2),
            'treasury_balance': round(treasury_balance_usd, 2),
            'runway_health': 100,
        }
    
    runway_months = treasury_balance_usd / net_burn if net_burn > 0 else 0
    runway_years = runway_months / 12
    
    # Determine health
    if runway_months >= burn_runway_months:
        interpretation = 'Healthy runway'
        runway_health = 100
    elif runway_months >= 24:
        interpretation = 'Moderate runway'
        runway_health = 80
    elif runway_months >= 12:
        interpretation = 'Caution - 1 year runway'
        runway_health = 50
    elif runway_months >= 6:
        interpretation = 'Critical - 6 month runway'
        runway_health = 25
    else:
        interpretation = 'Emergency - runway critical'
        runway_health = 10
    
    return {
        'runway_months': round(runway_months, 1),
        'runway_years': round(runway_years, 2),
        'is_sustainable': runway_months >= burn_runway_months,
        'interpretation': interpretation,
        'net_burn_monthly': round(net_burn, 2),
        'monthly_revenue': round(monthly_revenue_usd, 2),
        'monthly_expenses': round(monthly_expenses_usd, 2),
        'treasury_balance': round(treasury_balance_usd, 2),
        'runway_health': runway_health,
        'months_to_sustainability': round((monthly_expenses_usd - monthly_revenue_usd) / (monthly_revenue_usd * 0.1), 1) if monthly_revenue_usd > 0 else float('inf'),
    }


def calculate_all_metrics(
    circulating_supply: float,
    transaction_volume: float,
    staked_supply: float,
    token_price: float,
    protocol_revenue: float,
    burn_rate: float,
    buyback_rate: float,
    utility_score: float,
    governance_participation: float,
    liquidity_ratio: float,
    treasury_balance: float,
    monthly_expenses: float
) -> Dict[str, any]:
    """
    Calculate all token metrics in one call.
    
    Returns comprehensive tokenomics health report.
    """
    velocity = calculate_token_velocity(
        transaction_volume,
        circulating_supply
    )
    
    staking_ratio = staked_supply / circulating_supply if circulating_supply > 0 else 0
    
    real_yield = calculate_real_yield(
        protocol_revenue,
        staked_supply,
        token_price
    )
    
    value_accrual = calculate_value_accrual_score(
        burn_rate,
        buyback_rate,
        staking_ratio,
        utility_score,
        governance_participation,
        liquidity_ratio
    )
    
    runway = calculate_runway(
        treasury_balance,
        monthly_expenses,
        protocol_revenue
    )
    
    # Calculate overall health score
    health_components = [
        velocity['health_score'],
        100 if real_yield['is_sustainable'] else 50,
        value_accrual['total_score'],
        runway['runway_health'],
    ]
    overall_health = sum(health_components) / len(health_components)
    
    return {
        'velocity': velocity,
        'real_yield': real_yield,
        'value_accrual': value_accrual,
        'runway': runway,
        'overall_health': round(overall_health, 1),
        'summary': {
            'velocity_score': velocity['health_score'],
            'yield_sustainable': real_yield['is_sustainable'],
            'value_accrual_grade': value_accrual['grade'],
            'runway_months': runway['runway_months'],
            'overall_health': round(overall_health, 1),
        },
    }

