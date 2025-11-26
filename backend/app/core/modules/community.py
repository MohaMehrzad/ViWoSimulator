"""
Community Module calculations.

Updated for Issue #9: Linear cost scaling
"""

from app.config import config
from app.models import SimulationParameters, ModuleResult


def calculate_community(params: SimulationParameters, users: int) -> ModuleResult:
    """
    Calculate Community module revenue, costs, and profit.
    
    Issue #9: Now uses linear cost scaling for realistic cost projections.
    """
    if not params.enable_community:
        return ModuleResult(
            revenue=0,
            costs=0,
            profit=0,
            margin=0,
            breakdown={
                'total_communities': 0,
                'small_communities': 0,
                'medium_communities': 0,
                'large_communities': 0,
                'enterprise_communities': 0,
                'monthly_events': 0,
                'verified_communities': 0,
                'analytics_subscribers': 0,
                'subscription_revenue': 0,
                'event_revenue': 0,
                'verification_revenue': 0,
                'analytics_revenue': 0,
            }
        )
    
    dist = config.USER_DISTRIBUTION['COMMUNITY_SIZES']
    
    # Calculate number of communities based on users per community
    users_per_community = config.ACTIVITY_RATES.get('USERS_PER_COMMUNITY', 15)
    total_communities = max(1, users // users_per_community)
    
    # Community size distribution
    small_communities = round(total_communities * dist['SMALL'])      # 50%
    medium_communities = round(total_communities * dist['MEDIUM'])    # 30%
    large_communities = round(total_communities * dist['LARGE'])      # 15%
    enterprise_communities = round(total_communities * dist['ENTERPRISE'])  # 5%
    
    # Subscription revenue (monthly fees by tier)
    subscription_revenue = (
        small_communities * params.small_community_fee +
        medium_communities * params.medium_community_fee +
        large_communities * params.large_community_fee +
        enterprise_communities * params.enterprise_community_fee
    )
    
    # Event hosting revenue (15% of communities host events, reduced from 20%)
    event_rate = config.ACTIVITY_RATES.get('COMMUNITY_EVENTS', 0.15)
    monthly_events = round(total_communities * event_rate)
    event_revenue = monthly_events * params.event_hosting_fee
    
    # Verification revenue (5% are verified, reduced from 10%)
    verification_rate = config.ACTIVITY_RATES.get('VERIFIED_COMMUNITIES', 0.05)
    verified_communities = round(total_communities * verification_rate)
    verification_revenue = verified_communities * params.community_verification_fee
    
    # Analytics revenue (10% eligible, reduced from 15%)
    analytics_rate = config.ACTIVITY_RATES.get('COMMUNITY_ANALYTICS_ELIGIBLE', 0.10)
    analytics_subscribers = round(total_communities * analytics_rate)
    analytics_revenue = analytics_subscribers * params.community_analytics_fee
    
    # Total revenue
    revenue = subscription_revenue + event_revenue + verification_revenue + analytics_revenue
    
    # Issue #9: Linear cost scaling
    costs = config.get_linear_cost('COMMUNITY', users)
    
    # Profit
    profit = revenue - costs
    margin = (profit / revenue * 100) if revenue > 0 else 0
    
    return ModuleResult(
        revenue=round(revenue, 2),
        costs=round(costs, 2),
        profit=round(profit, 2),
        margin=round(margin, 1),
        breakdown={
            'total_communities': total_communities,
            'small_communities': small_communities,
            'medium_communities': medium_communities,
            'large_communities': large_communities,
            'enterprise_communities': enterprise_communities,
            'monthly_events': monthly_events,
            'verified_communities': verified_communities,
            'analytics_subscribers': analytics_subscribers,
            'subscription_revenue': round(subscription_revenue, 2),
            'event_revenue': round(event_revenue, 2),
            'verification_revenue': round(verification_revenue, 2),
            'analytics_revenue': round(analytics_revenue, 2),
        }
    )
