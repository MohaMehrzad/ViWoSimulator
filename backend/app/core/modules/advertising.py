"""
Advertising Module calculations.

Updated for Issues #7, #9:
- Issue #7: CPM rates adjusted for platform maturity
- Issue #9: Linear cost scaling
- Dec 2025: Added 5A Policy integration for creator ad revenue share
"""

from typing import Optional
from app.config import config
from app.models import SimulationParameters, ModuleResult


def calculate_advertising(
    params: SimulationParameters,
    users: int,
    five_a_creator_boost: float = 0.0,
) -> ModuleResult:
    """
    Calculate Advertising module revenue, costs, and profit.
    
    Issue #7: CPM rates now depend on platform maturity
    - Launch: $0.25 banner, $1.00 video, 10% fill
    - Growing: $2.00 banner, $6.00 video, 30% fill  
    - Established: $8.00 banner, $25.00 video, 70% fill
    
    5A Integration (Dec 2025):
    - High 5A creators get better ad revenue share
    - five_a_creator_boost is average boost across population (0.0-0.5)
    - This increases effective CPM for high-performing creators
    """
    if not params.enable_advertising:
        return ModuleResult(
            revenue=0,
            costs=0,
            profit=0,
            margin=0,
            breakdown={
                'banner_impressions': 0,
                'video_impressions': 0,
                'promoted_posts': 0,
                'campaigns': 0,
                'analytics_subscribers': 0,
                'banner_revenue': 0,
                'video_revenue': 0,
                'promoted_revenue': 0,
                'campaign_revenue': 0,
                'analytics_revenue': 0,
                'effective_fill_rate': 0,
                'effective_banner_cpm': 0,
                'effective_video_cpm': 0,
            }
        )
    
    dist = config.USER_DISTRIBUTION['AD_FORMATS']
    
    # Issue #7: Get effective CPM rates (maturity-adjusted)
    if hasattr(params, 'get_effective_cpm'):
        effective_banner_cpm, effective_video_cpm = params.get_effective_cpm()
    else:
        effective_banner_cpm = params.banner_cpm
        effective_video_cpm = params.video_cpm
    
    # Issue #7: Get effective fill rate
    if hasattr(params, 'get_effective_ad_fill_rate'):
        effective_fill_rate = params.get_effective_ad_fill_rate()
    else:
        effective_fill_rate = params.ad_fill_rate  # Fixed: was ad_cpm_multiplier
    
    # Ad impressions: Users see 30 ads per month on average (reduced from 50)
    ads_per_user = config.ACTIVITY_RATES.get('ADS_PER_USER', 30)
    total_impressions = users * ads_per_user
    
    # Ad type distribution: 70% banner, 30% video
    banner_impressions = round(total_impressions * dist['BANNER'])
    video_impressions = round(total_impressions * dist['VIDEO'])
    
    # Revenue from CPM ads (per 1000 impressions)
    # Apply fill rate to reflect realistic ad inventory sold
    banner_revenue = (banner_impressions / 1000) * effective_banner_cpm * effective_fill_rate
    video_revenue = (video_impressions / 1000) * effective_video_cpm * effective_fill_rate
    
    # Minimum floor revenue for enabled advertising (covers base operations)
    # Even with few users, an ad network generates some baseline revenue
    if users > 0:
        min_ad_revenue = max(10.0, users * 0.05)  # $0.05 per user minimum, floor $10
        banner_revenue = max(banner_revenue, min_ad_revenue * 0.7)
        video_revenue = max(video_revenue, min_ad_revenue * 0.3)
    
    # Revenue from promoted posts (3% of posts, reduced from 5%)
    # Use creator count for post calculation
    creator_percentage = config.ACTIVITY_RATES.get('CREATOR_PERCENTAGE', 0.10)
    posts_per_creator = config.ACTIVITY_RATES.get('POSTS_PER_CREATOR', 6)
    total_posts = int(users * creator_percentage * posts_per_creator)
    
    promoted_rate = config.ACTIVITY_RATES.get('PROMOTED_POSTS', 0.03)
    promoted_posts = round(total_posts * promoted_rate)
    promoted_revenue = promoted_posts * params.promoted_post_fee
    
    # Revenue from advertisers (0.5% of users are potential advertisers)
    advertiser_rate = config.ACTIVITY_RATES.get('ADVERTISERS', 0.005)
    advertisers = max(1, round(users * advertiser_rate))
    
    # Revenue from campaign management (20% of advertisers run managed campaigns)
    monthly_campaigns = max(1, round(advertisers * 0.20))
    campaign_revenue = monthly_campaigns * params.campaign_management_fee
    
    # Analytics dashboard subscriptions (10% of advertisers)
    analytics_rate = config.ACTIVITY_RATES.get('AD_ANALYTICS_SUBSCRIBERS', 0.10)
    analytics_subscribers = round(advertisers * analytics_rate)
    analytics_revenue = analytics_subscribers * params.ad_analytics_fee
    
    # Total base revenue
    base_revenue = banner_revenue + video_revenue + promoted_revenue + campaign_revenue + analytics_revenue
    
    # 5A Integration: High 5A creators get better ad revenue share
    # This manifests as slightly higher effective CPM for quality content
    # The boost reflects better advertiser confidence in quality creators
    five_a_revenue_boost = base_revenue * five_a_creator_boost * 0.1  # Up to +5% revenue boost
    revenue = base_revenue + five_a_revenue_boost
    
    # Issue #9: Linear cost scaling
    costs = config.get_linear_cost('ADVERTISING', users)
    
    # Profit
    profit = revenue - costs
    margin = (profit / revenue * 100) if revenue > 0 else 0
    
    return ModuleResult(
        revenue=round(revenue, 2),
        costs=round(costs, 2),
        profit=round(profit, 2),
        margin=round(margin, 1),
        breakdown={
            'banner_impressions': banner_impressions,
            'video_impressions': video_impressions,
            'promoted_posts': promoted_posts,
            'campaigns': monthly_campaigns,
            'advertisers': advertisers,
            'analytics_subscribers': analytics_subscribers,
            'banner_revenue': round(banner_revenue, 2),
            'video_revenue': round(video_revenue, 2),
            'promoted_revenue': round(promoted_revenue, 2),
            'campaign_revenue': round(campaign_revenue, 2),
            'analytics_revenue': round(analytics_revenue, 2),
            'effective_fill_rate': round(effective_fill_rate * 100, 1),
            'effective_banner_cpm': round(effective_banner_cpm, 2),
            'effective_video_cpm': round(effective_video_cpm, 2),
            'total_posts_for_promotion': total_posts,
            # 5A Integration
            'five_a_creator_boost': round(five_a_creator_boost * 100, 2),
            'five_a_revenue_boost': round(five_a_revenue_boost, 2),
            'base_revenue': round(base_revenue, 2),
        }
    )
