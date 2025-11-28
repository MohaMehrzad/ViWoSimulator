"""
Content Module calculations.

=== REDESIGNED: Break-Even Anti-Bot Model (November 2025) ===

Philosophy:
- This module should BREAK EVEN (no profit, no loss)
- Primary purpose: DETER BOTS, not generate revenue
- Real creators should NOT feel penalized
- Platform revenue comes from 5% Reward Fee (calculated in rewards.py)

Anti-Bot Mechanisms:
1. Progressive posting fees (first 5 posts free daily, then small fees)
2. Verified/Staked users get FREE unlimited posting
3. Engagement-based fee refund (posts with real engagement get refunded)
4. Daily/Monthly limits enforced
5. VCoin stake required for premium features

Creator-Friendly Features:
- NO platform creator fee (creators keep 100% of tips/sales)
- Verified creators post for free
- Stakers post for free
- Engagement rewards offset any fees

Bot Deterrence Formula:
- Non-verified users: First 5 posts/day FREE, then 0.1 VCoin per post
- Excessive posting (>15/day): Blocked, not charged
- Stake 100+ VCoin: Unlimited free posting
- Verified account: Unlimited free posting

Result: Revenue ≈ Costs (break-even)
"""

from app.config import config
from app.models import SimulationParameters, ModuleResult


def calculate_content(params: SimulationParameters, users: int) -> ModuleResult:
    """
    Calculate Content module with BREAK-EVEN anti-bot model.
    
    Design Goals:
    1. Revenue ≈ Costs (break-even, not profit center)
    2. Deter bots effectively with progressive fees
    3. Verified/Staked users post FREE
    4. NO platform creator fee (creators keep 100%)
    5. Real engagement refunds any fees paid
    
    The platform makes money from 5% Reward Fee, NOT from content fees.
    """
    # === USER SEGMENTATION ===
    
    # Creator percentage (10-18% of users create content)
    creator_percentage = getattr(
        params, 'creator_percentage', 
        config.ACTIVITY_RATES.get('CREATOR_PERCENTAGE', 0.10)
    )
    posts_per_creator = getattr(
        params, 'posts_per_creator',
        config.ACTIVITY_RATES.get('POSTS_PER_CREATOR', 6)
    )
    
    creators = int(users * creator_percentage)
    
    # Calculate total posts
    creator_based_posts = int(creators * posts_per_creator)
    user_based_posts = int(users * params.posts_per_user)
    total_posts = max(creator_based_posts, user_based_posts)
    
    # === USER TIERS (Anti-Bot Segmentation) ===
    
    # Get staking participation rate from maturity settings
    maturity_adjustments = params.get_maturity_adjustments() if hasattr(params, 'get_maturity_adjustments') else {}
    staking_participation = maturity_adjustments.get('staking_participation', 0.08)
    
    # Verified users (from identity module conversion rate)
    verified_rate = params.get_effective_conversion_rate() if hasattr(params, 'get_effective_conversion_rate') else params.verification_rate
    
    # User segments among creators:
    # 1. Verified creators - post FREE (already paid for verification)
    # 2. Staked creators - post FREE (stake as commitment)
    # 3. Regular creators - first 5 posts/day free, then minimal fee
    # 4. Suspected bots - blocked at limit, no extra fees
    
    verified_creators = int(creators * verified_rate)
    staked_creators = int(creators * staking_participation)
    # Some creators are both verified AND staked, avoid double counting
    free_posting_creators = min(creators, int(verified_creators + staked_creators * 0.7))
    paying_creators = max(0, creators - free_posting_creators)
    
    # === POST DISTRIBUTION ===
    
    dist = config.USER_DISTRIBUTION['CONTENT_TYPES']
    text_posts = round(total_posts * dist['TEXT'])      # 65%
    image_posts = round(total_posts * dist['IMAGE'])    # 30%
    video_posts = round(total_posts * dist['VIDEO'])    # 4.9%
    
    # NFT mints (if enabled)
    nft_percentage = getattr(params, 'nft_mint_percentage', dist.get('NFT', 0.005))
    if getattr(params, 'enable_nft', False):
        nft_mints = max(1, round(total_posts * nft_percentage))
        nft_mints = max(nft_mints, max(1, int(creators * 0.01)))
    else:
        nft_mints = 0
    
    # === ANTI-BOT FEE CALCULATION (Break-Even Design) ===
    
    # Free daily allowance: 5 posts per creator per day = 150 posts/month
    free_posts_per_creator_monthly = 5 * 30  # 150 free posts
    
    # Posts from FREE creators (verified/staked) - no fees
    posts_from_free_creators = int(free_posting_creators * posts_per_creator)
    
    # Posts from paying creators
    posts_from_paying_creators = max(0, total_posts - posts_from_free_creators)
    
    # Of paying creators' posts, first 150/month are free
    free_allowance_posts = min(posts_from_paying_creators, paying_creators * free_posts_per_creator_monthly)
    
    # Posts that incur the anti-bot fee (excess posts from non-verified)
    excess_posts = max(0, posts_from_paying_creators - free_allowance_posts)
    
    # Anti-bot fee: Very small (0.1 VCoin) - just enough to deter spam
    # This is NOT a revenue source, just a deterrent
    anti_bot_fee_vcoin = 0.1
    anti_bot_fees_vcoin = excess_posts * anti_bot_fee_vcoin
    anti_bot_fees_usd = anti_bot_fees_vcoin * params.token_price
    
    # === ENGAGEMENT-BASED REFUND ===
    # Real posts get engagement and earn rewards that offset any fees
    # Estimate: 80% of excess posts are from real users who get engagement
    # They effectively get refunded through rewards
    engagement_refund_rate = 0.80
    effective_anti_bot_revenue = anti_bot_fees_usd * (1 - engagement_refund_rate)
    
    # === NFT MINTING (Covers Processing Cost Only) ===
    # NFT fee covers Solana transaction + storage costs, no profit margin
    # Solana NFT costs: ~0.01 SOL ($0.50) for mint + metadata
    nft_processing_cost_usd = 0.50
    nft_mint_fee_vcoin = nft_processing_cost_usd / params.token_price if params.token_price > 0 else 15
    nft_fees_vcoin = nft_mints * nft_mint_fee_vcoin
    nft_fees_usd = nft_mints * nft_processing_cost_usd  # Break-even
    
    # === OPTIONAL PREMIUM FEATURES (User Choice, Not Required) ===
    
    # Boost posts - OPTIONAL, users choose to pay for visibility
    boost_post_fee = getattr(params, 'boost_post_fee_vcoin', 5)
    boost_rate = config.ACTIVITY_RATES.get('BOOSTED_POSTS', 0.05)
    boosted_posts = int(total_posts * boost_rate)
    boost_fees_vcoin = boosted_posts * boost_post_fee
    boost_fees_usd = boost_fees_vcoin * params.token_price
    
    # Premium DMs - OPTIONAL, pay to message non-followers
    premium_dm_fee = getattr(params, 'premium_dm_fee_vcoin', 2)
    premium_dm_users = int(users * 0.10)
    premium_dms_per_user = 3
    total_premium_dms = premium_dm_users * premium_dms_per_user
    premium_dm_vcoin = total_premium_dms * premium_dm_fee
    premium_dm_usd = premium_dm_vcoin * params.token_price
    
    # Premium reactions - OPTIONAL, special animated reactions
    premium_reaction_fee = getattr(params, 'premium_reaction_fee_vcoin', 1)
    premium_reaction_users = int(users * 0.05)
    reactions_per_user = 5
    total_premium_reactions = premium_reaction_users * reactions_per_user
    premium_reaction_vcoin = total_premium_reactions * premium_reaction_fee
    premium_reaction_usd = premium_reaction_vcoin * params.token_price
    
    # === CREATOR EARNINGS (Platform takes 0% - Creators keep 100%) ===
    # Platform does NOT take a cut of creator earnings
    # Revenue comes from 5% Reward Fee instead
    
    premium_volume_adjusted = params.premium_content_volume_vcoin * (creators / max(users, 1))
    premium_content_volume_usd = premium_volume_adjusted * params.token_price
    
    content_sale_volume_usd = params.content_sale_volume_vcoin * params.token_price
    
    # Tips flow 100% to creators (no platform fee)
    tipping_users = int(users * 0.10)
    avg_tip_usd = 2.0
    total_tips_usd = tipping_users * avg_tip_usd
    
    # Creator total earnings (they keep 100% minus platform fee if enabled)
    creator_earnings_usd = premium_content_volume_usd + total_tips_usd + content_sale_volume_usd
    
    # Issue #5 Fix: Use platform_creator_fee parameter instead of hardcoded 0
    # Default is 0 (creators keep 100%), but can be configured to charge platform fee
    platform_creator_fee_rate = getattr(params, 'platform_creator_fee', 0.0)
    platform_fee_from_creators = creator_earnings_usd * platform_creator_fee_rate
    
    # === TOTAL REVENUE (Designed to Equal Costs) ===
    
    # Revenue sources (minimal, just covers costs):
    # 1. Anti-bot fees (after refunds) - minimal
    # 2. NFT processing fees - break-even with Solana costs
    # 3. Optional premium features - user choice
    # 4. Platform creator fee (if enabled) - Issue #5 fix
    
    # Core posting revenue (break-even anti-bot)
    core_posting_revenue = effective_anti_bot_revenue + nft_fees_usd
    
    # Optional premium revenue (users opt-in)
    optional_premium_revenue = boost_fees_usd + premium_dm_usd + premium_reaction_usd
    
    # Total revenue (includes platform creator fee if enabled)
    total_revenue = core_posting_revenue + optional_premium_revenue + platform_fee_from_creators
    
    # === COSTS ===
    
    # Infrastructure costs (linear scaling)
    infrastructure_costs = config.get_linear_cost('CONTENT', users, total_posts)
    
    # Solana transaction costs for NFTs
    solana_nft_costs = nft_mints * 0.50  # Same as NFT fee (break-even)
    
    # Total costs
    total_costs = infrastructure_costs + solana_nft_costs
    
    # === BREAK-EVEN ADJUSTMENT ===
    # If revenue > costs, reduce effective revenue (refund more)
    # If revenue < costs, it's acceptable (anti-bot is a service)
    
    profit = total_revenue - total_costs
    
    # For simulation display, show actual numbers
    # In practice, excess profit would be redistributed to creators
    margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Track VCoin for recapture calculations
    total_vcoin_collected = (
        anti_bot_fees_vcoin + 
        nft_fees_vcoin + 
        boost_fees_vcoin + 
        premium_dm_vcoin + 
        premium_reaction_vcoin
    )
    
    # VCoin that gets refunded (engagement rewards)
    vcoin_refunded = anti_bot_fees_vcoin * engagement_refund_rate
    net_vcoin_collected = total_vcoin_collected - vcoin_refunded
    
    return ModuleResult(
        revenue=round(total_revenue, 2),
        costs=round(total_costs, 2),
        profit=round(profit, 2),
        margin=round(margin, 1),
        breakdown={
            # User segments
            'creators': creators,
            'creator_percentage': round(creator_percentage * 100, 1),
            'verified_creators': verified_creators,
            'staked_creators': staked_creators,
            'free_posting_creators': free_posting_creators,
            'paying_creators': paying_creators,
            
            # Post counts
            'monthly_posts': total_posts,
            'text_posts': text_posts,
            'image_posts': image_posts,
            'video_posts': video_posts,
            'nft_mints': nft_mints,
            'nft_enabled': getattr(params, 'enable_nft', False),
            
            # Anti-bot metrics
            'posts_from_free_creators': posts_from_free_creators,
            'posts_from_paying_creators': posts_from_paying_creators,
            'free_allowance_posts': int(free_allowance_posts),
            'excess_posts_with_fee': excess_posts,
            'anti_bot_fee_vcoin': anti_bot_fee_vcoin,
            'anti_bot_fees_collected_vcoin': round(anti_bot_fees_vcoin, 2),
            'anti_bot_fees_collected_usd': round(anti_bot_fees_usd, 2),
            'engagement_refund_rate': round(engagement_refund_rate * 100, 1),
            'effective_anti_bot_revenue': round(effective_anti_bot_revenue, 2),
            
            # NFT metrics (break-even)
            'nft_processing_cost_usd': nft_processing_cost_usd,
            'nft_fees_vcoin': round(nft_fees_vcoin, 2),
            'nft_fees_usd': round(nft_fees_usd, 2),
            
            # Optional premium features
            'boosted_posts': boosted_posts,
            'boost_fees_vcoin': round(boost_fees_vcoin, 2),
            'boost_fees_usd': round(boost_fees_usd, 2),
            'premium_dms': total_premium_dms,
            'premium_dm_vcoin': round(premium_dm_vcoin, 2),
            'premium_dm_usd': round(premium_dm_usd, 2),
            'premium_reactions': total_premium_reactions,
            'premium_reaction_vcoin': round(premium_reaction_vcoin, 2),
            'premium_reaction_usd': round(premium_reaction_usd, 2),
            
            # Creator earnings (minus platform fee if enabled)
            'creator_earnings_usd': round(creator_earnings_usd, 2),
            'total_tips_usd': round(total_tips_usd, 2),
            'premium_content_volume_usd': round(premium_content_volume_usd, 2),
            'content_sale_volume_usd': round(content_sale_volume_usd, 2),
            # Issue #5 Fix: Show actual platform_creator_fee values
            'platform_creator_fee': round(platform_fee_from_creators, 2),
            'platform_creator_fee_rate': round(platform_creator_fee_rate, 4),
            
            # VCoin tracking for recapture
            'total_vcoin_collected': round(total_vcoin_collected, 2),
            'vcoin_refunded': round(vcoin_refunded, 2),
            'net_vcoin_collected': round(net_vcoin_collected, 2),
            
            # Revenue breakdown
            'core_posting_revenue': round(core_posting_revenue, 2),
            'optional_premium_revenue': round(optional_premium_revenue, 2),
            
            # Break-even indicator
            'is_break_even': abs(profit) < total_costs * 0.1 if total_costs > 0 else True,
            
            # Legacy fields for compatibility
            'post_fees': round(effective_anti_bot_revenue, 2),
            'post_fees_vcoin': round(anti_bot_fees_vcoin, 2),
            'premium_revenue': round(optional_premium_revenue, 2),
            'sale_commission': 0.0,  # No commission - creators keep 100%
            'premium_volume_vcoin': round(premium_volume_adjusted, 2),
            'content_sale_volume_vcoin': params.content_sale_volume_vcoin,
            'creator_economy_vcoin': round(boost_fees_vcoin + premium_dm_vcoin + premium_reaction_vcoin, 2),
        }
    )
