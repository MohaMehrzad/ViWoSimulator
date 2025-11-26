"""
Content Module calculations.

Updated for Issues #8, #9, #12 and Nov 2025 Creator Economy:
- Issue #8: Realistic posts per user (only 10% are creators)
- Issue #9: Linear cost scaling
- Issue #12: Reduced NFT mint percentage to 0.1%
- NEW: Boost post fees (5 VCoin per boost)
- NEW: Premium DM fees (2 VCoin to DM non-followers)
- NEW: Premium reaction fees (1 VCoin)
- NEW: Platform creator fee (5% on creator earnings)
"""

from app.config import config
from app.models import SimulationParameters, ModuleResult


def calculate_content(params: SimulationParameters, users: int) -> ModuleResult:
    """
    Calculate Content module revenue, costs, and profit.
    
    Issue #8 fix: Only 10% of users are creators, not everyone posts
    Issue #12 fix: NFT mints reduced to 0.1% of posts
    Nov 2025: Added creator economy features
    """
    # Issue #8: Calculate posts based on creator percentage
    creator_percentage = getattr(
        params, 'creator_percentage', 
        config.ACTIVITY_RATES.get('CREATOR_PERCENTAGE', 0.10)
    )
    posts_per_creator = getattr(
        params, 'posts_per_creator',
        config.ACTIVITY_RATES.get('POSTS_PER_CREATOR', 6)
    )
    
    # Number of active creators
    creators = int(users * creator_percentage)
    
    # Total posts calculated from:
    # 1. Creator-based: creators × posts_per_creator
    # 2. User-based: all users × posts_per_user (e.g., 0.6 = 10% creators × 6 posts)
    # Use whichever calculation gives more posts (allows slider to have effect)
    creator_based_posts = int(creators * posts_per_creator)
    user_based_posts = int(users * params.posts_per_user)
    
    # Use the larger of the two calculations
    # This allows both the creator percentage AND posts_per_user slider to have effect
    total_posts = max(creator_based_posts, user_based_posts)
    
    # Post type distribution
    # Issue #12: NFT reduced from 2% to 0.1%
    dist = config.USER_DISTRIBUTION['CONTENT_TYPES']
    text_posts = round(total_posts * dist['TEXT'])      # 65%
    image_posts = round(total_posts * dist['IMAGE'])    # 30%
    video_posts = round(total_posts * dist['VIDEO'])    # 4.9%
    
    # Issue #12: NFT mints now use configurable percentage
    # Updated: Ensure minimum 1 NFT mint when enabled (even with few posts)
    nft_percentage = getattr(params, 'nft_mint_percentage', dist['NFT'])
    if params.enable_nft:
        # Calculate based on percentage, but ensure at least 1 mint if enabled
        nft_mints = max(1, round(total_posts * nft_percentage))
        # Also add baseline NFT activity: ~1% of creators mint NFTs monthly
        nft_mints = max(nft_mints, max(1, int(creators * 0.01)))
    else:
        nft_mints = 0
    
    # Post fee revenue (convert VCoin fees to USD)
    text_fee_usd = params.text_post_fee_vcoin * params.token_price
    image_fee_usd = params.image_post_fee_vcoin * params.token_price
    video_fee_usd = params.video_post_fee_vcoin * params.token_price
    nft_fee_usd = params.nft_mint_fee_vcoin * params.token_price
    
    post_fees_revenue = (
        text_posts * text_fee_usd +
        image_posts * image_fee_usd +
        video_posts * video_fee_usd +
        nft_mints * nft_fee_usd
    )
    
    # Track VCoin fees separately for recapture
    post_fees_vcoin = (
        text_posts * params.text_post_fee_vcoin +
        image_posts * params.image_post_fee_vcoin +
        video_posts * params.video_post_fee_vcoin +
        nft_mints * params.nft_mint_fee_vcoin
    )
    
    # === NEW: Boost Post Revenue (Nov 2025) ===
    # 5% of posts get boosted at 5 VCoin each
    boost_post_fee = getattr(params, 'boost_post_fee_vcoin', 5)
    boost_rate = config.ACTIVITY_RATES.get('BOOSTED_POSTS', 0.05)
    boosted_posts = int(total_posts * boost_rate)
    boost_fees_vcoin = boosted_posts * boost_post_fee
    boost_fees_usd = boost_fees_vcoin * params.token_price
    
    # === NEW: Premium DM Revenue (Nov 2025) ===
    # 10% of users send premium DMs to non-followers (avg 3/month)
    premium_dm_fee = getattr(params, 'premium_dm_fee_vcoin', 2)
    premium_dm_users = int(users * 0.10)
    premium_dms_per_user = 3
    total_premium_dms = premium_dm_users * premium_dms_per_user
    premium_dm_vcoin = total_premium_dms * premium_dm_fee
    premium_dm_usd = premium_dm_vcoin * params.token_price
    
    # === NEW: Premium Reaction Revenue (Nov 2025) ===
    # 5% of users use premium reactions (avg 5/month)
    premium_reaction_fee = getattr(params, 'premium_reaction_fee_vcoin', 1)
    premium_reaction_users = int(users * 0.05)
    reactions_per_user = 5
    total_premium_reactions = premium_reaction_users * reactions_per_user
    premium_reaction_vcoin = total_premium_reactions * premium_reaction_fee
    premium_reaction_usd = premium_reaction_vcoin * params.token_price
    
    # Premium content revenue (scaled down for realistic expectations)
    # Issue #8: Scale with actual creator count
    premium_volume_adjusted = params.premium_content_volume_vcoin * (creators / max(users, 1))
    premium_revenue = premium_volume_adjusted * params.token_price
    
    # Content sale commission (NFT sales revenue)
    content_sale_volume_usd = params.content_sale_volume_vcoin * params.token_price
    nft_sales_revenue = content_sale_volume_usd * params.content_sale_commission if params.enable_nft else 0
    
    # === NEW: Creator Economy Platform Fee (Nov 2025) ===
    # Platform takes 5% of creator earnings (tips, subscriptions, etc.)
    platform_creator_fee = getattr(params, 'platform_creator_fee', 0.05)
    # Estimate creator earnings: premium content + tips (10% of users tip avg $2)
    tipping_users = int(users * 0.10)
    avg_tip_usd = 2.0
    total_tips_usd = tipping_users * avg_tip_usd
    creator_earnings_usd = premium_revenue + total_tips_usd + nft_sales_revenue
    platform_fee_from_creators = creator_earnings_usd * platform_creator_fee
    
    # Total creator economy VCoin (for recapture)
    creator_economy_vcoin = boost_fees_vcoin + premium_dm_vcoin + premium_reaction_vcoin
    
    # Total revenue
    revenue = (
        post_fees_revenue + 
        premium_revenue + 
        nft_sales_revenue +
        boost_fees_usd +
        premium_dm_usd +
        premium_reaction_usd +
        platform_fee_from_creators
    )
    
    # Issue #9: Linear cost scaling with post-based component
    costs = config.get_linear_cost('CONTENT', users, total_posts)
    
    # Profit
    profit = revenue - costs
    margin = (profit / revenue * 100) if revenue > 0 else 0
    
    return ModuleResult(
        revenue=round(revenue, 2),
        costs=round(costs, 2),
        profit=round(profit, 2),
        margin=round(margin, 1),
        breakdown={
            'creators': creators,
            'creator_percentage': round(creator_percentage * 100, 1),
            'text_posts': text_posts,
            'image_posts': image_posts,
            'video_posts': video_posts,
            'nft_mints': nft_mints,
            'nft_enabled': params.enable_nft,
            'post_fees': round(post_fees_revenue, 2),
            'post_fees_vcoin': round(post_fees_vcoin, 2),
            'premium_revenue': round(premium_revenue, 2),
            'sale_commission': round(nft_sales_revenue, 2),
            'monthly_posts': total_posts,
            'premium_volume_vcoin': round(premium_volume_adjusted, 2),
            'content_sale_volume_vcoin': params.content_sale_volume_vcoin,
            'premium_volume_usd': round(premium_revenue, 2),
            'content_sale_volume_usd': round(content_sale_volume_usd, 2),
            # NEW: Creator Economy metrics
            'boosted_posts': boosted_posts,
            'boost_fees_vcoin': round(boost_fees_vcoin, 2),
            'boost_fees_usd': round(boost_fees_usd, 2),
            'premium_dms': total_premium_dms,
            'premium_dm_vcoin': round(premium_dm_vcoin, 2),
            'premium_dm_usd': round(premium_dm_usd, 2),
            'premium_reactions': total_premium_reactions,
            'premium_reaction_vcoin': round(premium_reaction_vcoin, 2),
            'premium_reaction_usd': round(premium_reaction_usd, 2),
            'creator_economy_vcoin': round(creator_economy_vcoin, 2),
            'creator_earnings_usd': round(creator_earnings_usd, 2),
            'platform_creator_fee': round(platform_fee_from_creators, 2),
            'platform_creator_fee_rate': round(platform_creator_fee * 100, 1),
        }
    )
