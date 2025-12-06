"""
Recapture calculations - token burn, buyback, staking, treasury.

=== UPDATED: Revenue-Based Buybacks (November 2025) ===

CRITICAL FIX: Buybacks now use USD REVENUE to purchase tokens from market.

TOKEN FLOW MODEL:
1. Users EARN VCoin through rewards (monthly emission)
2. Platform takes 5% fee BEFORE distribution (primary revenue)
3. Users SPEND a portion of earned VCoin in the platform (velocity)
4. Platform RECAPTURES spent VCoin through:
   - BURN: % of collected VCoin is destroyed (deflationary)
   - TREASURY: % of collected VCoin goes to DAO treasury
   - STAKING: Tokens locked by users for rewards
5. BUYBACKS: % of USD REVENUE is used to BUY VCoin from market
   - This creates actual buy pressure
   - Bought tokens can be burned or added to treasury

Key distinction:
- Burns reduce supply from transaction fees (VCoin flow)
- Buybacks create buy pressure using protocol profits (USD flow)
"""

from typing import Optional
from app.config import config
from app.models import (
    SimulationParameters, 
    ModuleResult, 
    RewardsResult, 
    RecaptureResult
)


def apply_safety_caps(
    requested_amount: float, 
    cap_type: str, 
    monthly_emission: float,
    total_revenue_usd: float = 0,
    token_price: float = 0.03,
    circulating_supply: float = None
) -> float:
    """
    Apply absolute safety caps to prevent impossible recapture amounts.
    
    Args:
        requested_amount: Requested recapture amount in VCoin
        cap_type: Type of recapture ('burn', 'buyback', 'staking', 'treasury', 'other')
        monthly_emission: Monthly token emission for emission-based caps
        total_revenue_usd: Total platform revenue in USD (for revenue-based buyback caps)
        token_price: Current token price (for revenue-based buyback caps)
        circulating_supply: Current circulating supply (dynamic based on simulation month)
    
    Returns:
        Capped amount in VCoin
    """
    caps = config.ABSOLUTE_CAPS
    # Use provided circulating_supply or fall back to TGE value for backward compatibility
    if circulating_supply is None:
        circulating_supply = config.SUPPLY.TGE_CIRCULATING
    
    # Cap 1: Never exceed emission for token-flow based recapture
    # (burns, treasury, staking come from token circulation)
    if cap_type != 'buyback':
        capped = min(requested_amount, monthly_emission * caps.MAX_RECAPTURE_RATE)
    else:
        # Buybacks are revenue-based, not emission-based
        # Cap at 100% of revenue converted to tokens (can't spend more than earned)
        max_buyback_usd = total_revenue_usd  # Max: spend all revenue on buybacks
        max_buyback_vcoin = max_buyback_usd / token_price if token_price > 0 else 0
        capped = min(requested_amount, max_buyback_vcoin)
    
    # Cap 2: Apply type-specific limits based on circulating supply
    circulating_limits = {
        'burn': circulating_supply * caps.MONTHLY_BURN_LIMIT,
        'buyback': circulating_supply * caps.MONTHLY_BUYBACK_LIMIT,
        'staking': circulating_supply * caps.MONTHLY_STAKING_LIMIT,
        'treasury': circulating_supply * 0.10,
        'other': circulating_supply * 0.03,
    }
    
    if cap_type in circulating_limits:
        capped = min(capped, circulating_limits[cap_type])
    
    return max(0, capped)


def calculate_token_velocity(
    params: SimulationParameters,
    users: int,
    monthly_emission: float
) -> dict:
    """
    Calculate token velocity - how much of the emitted tokens flow through the economy.
    
    Token velocity depends on:
    1. Platform utility (what can users spend on)
    2. User behavior (spending vs holding)
    3. Incentive design (staking rewards, fee discounts)
    
    Industry benchmarks for token velocity:
    - High utility tokens: 20-40% monthly spend rate
    - Medium utility: 10-20% monthly spend rate
    - Low utility/speculative: 5-10% monthly spend rate
    
    Nov 2025: Adjusted for break-even content model
    - Content fees are minimal (anti-bot only)
    - Velocity comes from premium features (user choice)
    """
    # Base spending rate - what % of earned tokens do users spend monthly
    base_spend_rate = 0.20  # 20% of earned tokens spent monthly
    
    # Adjust based on platform features enabled
    utility_multiplier = 1.0
    
    if params.enable_exchange:
        utility_multiplier += 0.2  # Exchange adds significant utility
    if params.enable_advertising:
        utility_multiplier += 0.1  # Advertisers spend tokens
    
    # Content posting (minimal in break-even model)
    # Only add utility if users opt into premium features
    if getattr(params, 'enable_nft', False):
        utility_multiplier += 0.1  # NFT adds utility
    
    # Premium content (user choice)
    if params.premium_content_volume_vcoin > 0:
        utility_multiplier += 0.1
    
    # Premium features (boost, DMs, reactions) - user choice
    boost_fee = getattr(params, 'boost_post_fee_vcoin', 5)
    premium_dm_fee = getattr(params, 'premium_dm_fee_vcoin', 2)
    premium_reaction_fee = getattr(params, 'premium_reaction_fee_vcoin', 1)
    
    if boost_fee > 0:
        utility_multiplier += 0.1
    if premium_dm_fee > 0:
        utility_multiplier += 0.05
    if premium_reaction_fee > 0:
        utility_multiplier += 0.05
    
    # Calculate effective velocity
    effective_spend_rate = min(0.60, base_spend_rate * utility_multiplier)
    
    # Tokens spent = emission * spend rate
    tokens_spent = monthly_emission * effective_spend_rate
    
    # Staking rate - tokens locked (now uses user-configured participation rate)
    staking_apy = getattr(params, 'staking_apy', 0.10)
    staking_participation = getattr(params, 'staking_participation_rate', 0.15)
    
    # Base stake rate from participation (15% participation = 15% of tokens locked)
    base_stake_rate = staking_participation
    
    # APY modifier: Higher APY encourages more staking
    if staking_apy >= 0.15:
        base_stake_rate *= 1.2  # 20% more staking at 15%+ APY
    elif staking_apy >= 0.10:
        base_stake_rate *= 1.1  # 10% more staking at 10%+ APY
    
    # Exchange staker discounts encourage staking
    if params.enable_exchange:
        base_stake_rate *= 1.1  # 10% more staking when exchange is active
    
    # Cap at reasonable maximum
    base_stake_rate = min(0.40, base_stake_rate)  # Max 40% of emission staked
    
    tokens_staked = monthly_emission * base_stake_rate
    
    return {
        'spend_rate': effective_spend_rate,
        'tokens_spent': tokens_spent,
        'stake_rate': base_stake_rate,
        'tokens_staked': tokens_staked,
        'utility_multiplier': utility_multiplier,
    }


def calculate_recapture(
    params: SimulationParameters,
    identity: ModuleResult,
    content: ModuleResult,
    advertising: ModuleResult,
    exchange: ModuleResult,
    rewards: RewardsResult,
    users: int,
    total_revenue_usd: float = 0,
    circulating_supply: float = None,
    five_a_engagement_boost: float = 0.0,
) -> RecaptureResult:
    """
    Calculate total token recapture based on token velocity model.
    
    === UPDATED: Revenue-Based Buybacks (Nov 2025) ===
    
    Key changes:
    - BURN: Applied to collected VCoin fees (token flow)
    - BUYBACK: Uses % of USD revenue to buy tokens from market
    
    5A Integration (Dec 2025):
    - High 5A engagement increases token velocity (more in-platform spending)
    - five_a_engagement_boost affects the recapture rate positively
    
    Args:
        total_revenue_usd: Total platform revenue in USD for buyback calculation
        circulating_supply: Current circulating supply (dynamic based on simulation month)
        five_a_engagement_boost: Average 5A engagement boost (0.0-0.5)
    """
    # Use provided circulating_supply or fall back to TGE value for backward compatibility
    if circulating_supply is None:
        circulating_supply = config.SUPPLY.TGE_CIRCULATING
    monthly_emission = rewards.monthly_reward_pool
    
    # Calculate token velocity
    velocity = calculate_token_velocity(params, users, monthly_emission)
    
    # 5A Integration: High engagement increases in-platform spending
    # This boosts the effective velocity by up to 20%
    five_a_velocity_multiplier = 1.0 + (five_a_engagement_boost * 0.4)  # Up to +20% velocity
    
    # === DIRECT VCOIN TRANSACTIONS ===
    # These are explicit VCoin spends that contribute to recapture
    
    direct_vcoin_spent = 0.0
    
    # === CONTENT MODULE (Break-Even Model) ===
    # Use NET VCoin collected (after engagement refunds)
    # This is what actually contributes to recapture
    net_vcoin_from_content = content.breakdown.get('net_vcoin_collected', 0)
    
    # If old format, calculate from components
    if net_vcoin_from_content == 0:
        # Legacy: use total VCoin collected
        post_fees_vcoin = content.breakdown.get('post_fees_vcoin', 0)
        creator_economy_vcoin = content.breakdown.get('creator_economy_vcoin', 0)
        direct_vcoin_spent += post_fees_vcoin + creator_economy_vcoin
    else:
        # New break-even model: use net collected after refunds
        direct_vcoin_spent += net_vcoin_from_content
    
    # Premium content volume (user choice, not affected by break-even)
    direct_vcoin_spent += params.premium_content_volume_vcoin
    
    # Issue #2 fix: Removed dead code checking for 'platform_creator_fee_rate'
    # Content module uses break-even anti-bot model where creators keep 100%
    # (sale_commission is explicitly set to 0.0 in content.py)
    
    # === IDENTITY MODULE ===
    identity_vcoin = identity.breakdown.get('vcoin_spent', 0)
    if identity_vcoin == 0:
        # Calculate from tier subscriptions
        tier_revenue = identity.breakdown.get('tier_revenue', 0)
        if params.token_price > 0:
            identity_vcoin = tier_revenue / params.token_price
    direct_vcoin_spent += identity_vcoin
    
    # === EXCHANGE MODULE ===
    if params.enable_exchange:
        exchange_vcoin = exchange.breakdown.get('swap_fees_vcoin', 0)
        if exchange_vcoin == 0:
            # Estimate from swap fee revenue
            swap_fee_revenue = exchange.breakdown.get('swap_fee_revenue', 0)
            if params.token_price > 0:
                exchange_vcoin = swap_fee_revenue / params.token_price
        direct_vcoin_spent += exchange_vcoin
    
    # === TOTAL TOKENS FLOWING THROUGH ECONOMY ===
    # NEW-CALC-001 FIX: Cap individual sources BEFORE summing to avoid discontinuity
    # Previously, capping AFTER summing created sudden jumps when inputs were high
    # Now each source is limited to 40% of emission, ensuring smooth behavior
    
    velocity_cap = monthly_emission * 0.40
    direct_cap = monthly_emission * 0.40
    
    # Apply 5A velocity multiplier to in-platform spending
    boosted_velocity_tokens = velocity['tokens_spent'] * five_a_velocity_multiplier
    capped_velocity_tokens = min(boosted_velocity_tokens, velocity_cap)
    capped_direct_tokens = min(direct_vcoin_spent, direct_cap)
    
    total_tokens_flowing = capped_velocity_tokens + capped_direct_tokens
    
    # Final sanity cap at 80% of emission (sum of two 40% caps)
    total_tokens_flowing = min(total_tokens_flowing, monthly_emission * 0.80)
    
    # === CALCULATE RECAPTURE COMPONENTS ===
    
    # BURN: Applied to collected VCoin fees (token flow)
    # This destroys tokens from platform transaction fees
    raw_burn = total_tokens_flowing * params.burn_rate
    
    # BUYBACK: Uses USD REVENUE to buy tokens from market
    # This creates actual buy pressure and is a proper tokenomics mechanism
    # buyback_percent is % of revenue used for buybacks
    buyback_usd_spent = total_revenue_usd * params.buyback_percent
    raw_buyback = buyback_usd_spent / params.token_price if params.token_price > 0 else 0
    
    # Treasury: Receives portion of collected tokens AND revenue
    # Default is 20% (from config or params)
    treasury_revenue_share = getattr(params, 'treasury_revenue_share', config.TREASURY_REVENUE_SHARE)
    remaining_after_burn = total_tokens_flowing - raw_burn  # Buyback no longer from token flow
    
    # Treasury accumulates from transaction velocity
    # Use full fee distribution config (BURN: 20%, TREASURY: 50%, REWARDS: 30%)
    # Treasury share is its portion of the non-burned tokens
    fee_dist = config.FEE_DISTRIBUTION
    non_burn_total = fee_dist.TREASURY + fee_dist.REWARDS
    treasury_fee_share = fee_dist.TREASURY / non_burn_total if non_burn_total > 0 else 0.5
    # Note: BURN portion is already handled separately via raw_burn calculation
    
    # Combine with revenue share for total treasury contribution
    effective_treasury_rate = (treasury_fee_share + treasury_revenue_share) * 0.5
    raw_treasury = remaining_after_burn * effective_treasury_rate
    
    # Staking: Tokens locked from circulation
    raw_staking = velocity['tokens_staked']
    
    # Add explicit staking from modules
    premium_users = identity.breakdown.get('premium_users', 0)
    raw_staking += premium_users * 10  # Premium users stake for benefits
    
    if params.enable_exchange:
        exchange_users = exchange.breakdown.get('active_exchange_users', 0)
        raw_staking += exchange_users * 5  # Exchange users stake for discounts
    
    # Verified/staked creators (from new content model)
    staked_creators = content.breakdown.get('staked_creators', 0)
    verified_creators = content.breakdown.get('verified_creators', 0)
    raw_staking += staked_creators * 50  # Staked creators lock tokens
    
    # === APPLY SAFETY CAPS ===
    burn_vcoin = apply_safety_caps(raw_burn, 'burn', monthly_emission, circulating_supply=circulating_supply)
    # Buyback uses revenue-based cap instead of emission-based cap
    buyback_vcoin = apply_safety_caps(
        raw_buyback, 'buyback', monthly_emission,
        total_revenue_usd=total_revenue_usd,
        token_price=params.token_price,
        circulating_supply=circulating_supply
    )
    treasury_vcoin = apply_safety_caps(raw_treasury, 'treasury', monthly_emission, circulating_supply=circulating_supply)
    staking_vcoin = apply_safety_caps(raw_staking, 'staking', monthly_emission, circulating_supply=circulating_supply)
    
    # Total recaptured
    total_recaptured = burn_vcoin + buyback_vcoin + treasury_vcoin + staking_vcoin
    
    # Final cap at 80% of emission
    max_recapture = monthly_emission * config.ABSOLUTE_CAPS.MAX_RECAPTURE_RATE
    if total_recaptured > max_recapture:
        scale = max_recapture / total_recaptured
        burn_vcoin *= scale
        buyback_vcoin *= scale
        treasury_vcoin *= scale
        staking_vcoin *= scale
        total_recaptured = max_recapture
    
    # Issue #6: Recapture rate with division-by-zero guard
    # If monthly_emission is 0 (edge case with 0% reward allocation), return 0 to avoid NaN
    recapture_rate = (total_recaptured / monthly_emission * 100) if monthly_emission > 0 else 0
    
    # USD values for reporting
    total_fees_usd = total_tokens_flowing * params.token_price
    
    # CRIT-002 Fix: Calculate effective burn rate as % of monthly emission
    # This shows the ACTUAL deflationary impact, not just the configured rate
    # Users expect to see "5% burn" meaning 5% of emission, but the configured
    # burn_rate is applied to token velocity (50% of emission), so effective is ~2.5%
    effective_burn_rate = (burn_vcoin / monthly_emission * 100) if monthly_emission > 0 else 0
    
    return RecaptureResult(
        total_recaptured=round(total_recaptured, 2),
        recapture_rate=round(min(recapture_rate, 80), 1),
        burns=round(burn_vcoin, 2),
        treasury=round(treasury_vcoin, 2),
        staking=round(staking_vcoin, 2),
        buybacks=round(buyback_vcoin, 2),
        buyback_usd_spent=round(buyback_usd_spent, 2),  # NEW: USD spent on buybacks
        total_revenue_source_vcoin=round(total_tokens_flowing + staking_vcoin, 2),
        total_transaction_fees_usd=round(total_fees_usd, 2),
        total_royalties_usd=round(direct_vcoin_spent * params.token_price * 0.1, 2),
        # CRIT-002 Fix: Show effective burn rate vs configured rate
        effective_burn_rate=round(effective_burn_rate, 2),
        configured_burn_rate=round(params.burn_rate * 100, 2),
    )
