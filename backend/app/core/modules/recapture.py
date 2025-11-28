"""
Recapture calculations - token burn, buyback, staking, treasury.

=== UPDATED: Break-Even Content Module Integration (November 2025) ===

MAJOR CHANGES:
- Content module now operates at BREAK-EVEN (no profit, bot deterrent only)
- Platform revenue comes from 5% REWARD FEE (see rewards.py)
- VCoin collected from content is largely refunded to engaged users
- Only NET VCoin collected contributes to recapture
- Treasury receives configurable % of platform revenue (default 20%)

TOKEN FLOW MODEL:
1. Users EARN VCoin through rewards (monthly emission)
2. Platform takes 5% fee BEFORE distribution (primary revenue)
3. Users SPEND a portion of earned VCoin in the platform (velocity)
4. The platform RECAPTURES a portion of spent VCoin (burn/buyback/stake)
5. Treasury receives 20% of platform revenue for governance

Content Module VCoin Flow (Break-Even):
- Collected from anti-bot fees → Refunded to engaged users (80%)
- Only 20% of anti-bot fees contribute to recapture
- Premium features (boost, DMs, reactions) fully contribute

Key insight: Recapture is based on TOKEN VELOCITY - how much of the emitted 
tokens flow back through the economy via platform features.
"""

from app.config import config
from app.models import (
    SimulationParameters, 
    ModuleResult, 
    RewardsResult, 
    RecaptureResult
)


def apply_safety_caps(requested_amount: float, cap_type: str, monthly_emission: float) -> float:
    """
    Apply absolute safety caps to prevent impossible recapture amounts.
    """
    caps = config.ABSOLUTE_CAPS
    circulating_supply = config.SUPPLY.TGE_CIRCULATING
    
    # Cap 1: Never exceed emission
    capped = min(requested_amount, monthly_emission * caps.MAX_RECAPTURE_RATE)
    
    # Cap 2: Apply type-specific limits
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
    if params.enable_community:
        utility_multiplier += 0.1  # Community features
    if params.enable_messaging:
        utility_multiplier += 0.1  # Messaging premium features
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
    
    # Staking rate - tokens locked
    staking_apy = getattr(params, 'staking_apy', 0.10)
    base_stake_rate = 0.05  # 5% of emission locked in staking
    
    if params.enable_exchange:
        base_stake_rate += 0.05  # Exchange fee discounts for staking
    
    if staking_apy >= 0.10:
        base_stake_rate += 0.05  # Higher APY encourages staking
    
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
    community: ModuleResult,
    advertising: ModuleResult,
    messaging: ModuleResult,
    exchange: ModuleResult,
    rewards: RewardsResult,
    users: int
) -> RecaptureResult:
    """
    Calculate total token recapture based on token velocity model.
    
    === UPDATED FOR BREAK-EVEN CONTENT MODEL ===
    
    Content module now:
    - Collects minimal anti-bot fees
    - Refunds 80% of fees to engaged users
    - Only NET VCoin collected contributes to recapture
    
    Platform revenue comes from 5% Reward Fee (see rewards.py),
    NOT from content module fees.
    """
    monthly_emission = rewards.monthly_reward_pool
    
    # Calculate token velocity
    velocity = calculate_token_velocity(params, users, monthly_emission)
    
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
    
    # Content sales (NFT) - platform takes commission only if enabled
    # In break-even model, creators keep 100%, so no commission
    platform_creator_fee_rate = content.breakdown.get('platform_creator_fee_rate', 0)
    if platform_creator_fee_rate > 0:
        direct_vcoin_spent += params.content_sale_volume_vcoin * params.content_sale_commission
    
    # === IDENTITY MODULE ===
    identity_vcoin = identity.breakdown.get('vcoin_spent', 0)
    if identity_vcoin == 0:
        # Calculate from tier subscriptions
        tier_revenue = identity.breakdown.get('tier_revenue', 0)
        if params.token_price > 0:
            identity_vcoin = tier_revenue / params.token_price
    direct_vcoin_spent += identity_vcoin
    
    # === MESSAGING MODULE ===
    messaging_vcoin = messaging.breakdown.get('vcoin_spent', 0)
    if messaging_vcoin == 0:
        # Estimate from revenue
        messaging_revenue = messaging.revenue
        if params.token_price > 0:
            messaging_vcoin = messaging_revenue / params.token_price * 0.3  # 30% in VCoin
    direct_vcoin_spent += messaging_vcoin
    
    # === COMMUNITY MODULE ===
    community_vcoin = community.breakdown.get('vcoin_spent', 0)
    if community_vcoin == 0:
        # Estimate from subscriptions
        subscription_revenue = community.breakdown.get('subscription_revenue', 0)
        if params.token_price > 0:
            community_vcoin = subscription_revenue / params.token_price * 0.5  # 50% in VCoin
    direct_vcoin_spent += community_vcoin
    
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
    # Velocity-based spending + direct VCoin transactions
    total_tokens_flowing = velocity['tokens_spent'] + direct_vcoin_spent
    
    # Cap at 80% of emission (can't spend more than earned)
    total_tokens_flowing = min(total_tokens_flowing, monthly_emission * 0.80)
    
    # === CALCULATE RECAPTURE COMPONENTS ===
    
    # Burn: Applied to tokens spent
    raw_burn = total_tokens_flowing * params.burn_rate
    
    # Buyback: Applied to tokens spent  
    raw_buyback = total_tokens_flowing * params.buyback_percent
    
    # Treasury: Receives configurable percentage of platform revenue
    # Default is 20% (from config or params)
    treasury_revenue_share = getattr(params, 'treasury_revenue_share', config.TREASURY_REVENUE_SHARE)
    remaining_after_burn = total_tokens_flowing - raw_burn - raw_buyback
    
    # Treasury accumulates from transaction velocity
    # Base treasury share from fee distribution config
    treasury_fee_share = config.FEE_DISTRIBUTION.TREASURY / (
        config.FEE_DISTRIBUTION.TREASURY + config.FEE_DISTRIBUTION.REWARDS
    )
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
    burn_vcoin = apply_safety_caps(raw_burn, 'burn', monthly_emission)
    buyback_vcoin = apply_safety_caps(raw_buyback, 'buyback', monthly_emission)
    treasury_vcoin = apply_safety_caps(raw_treasury, 'treasury', monthly_emission)
    staking_vcoin = apply_safety_caps(raw_staking, 'staking', monthly_emission)
    
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
    
    return RecaptureResult(
        total_recaptured=round(total_recaptured, 2),
        recapture_rate=round(min(recapture_rate, 80), 1),
        burns=round(burn_vcoin, 2),
        treasury=round(treasury_vcoin, 2),
        staking=round(staking_vcoin, 2),
        buybacks=round(buyback_vcoin, 2),
        total_revenue_source_vcoin=round(total_tokens_flowing + staking_vcoin, 2),
        total_transaction_fees_usd=round(total_fees_usd, 2),
        total_royalties_usd=round(direct_vcoin_spent * params.token_price * 0.1, 2),
    )
