"""
Identity Module calculations.

Updated for Issues #3, #9, #11:
- Issue #3: Uses maturity-adjusted conversion rates
- Issue #9: Linear cost scaling
- Issue #11: Realistic profile sales assumptions
"""

from app.config import config
from app.models import SimulationParameters, ModuleResult


def calculate_identity(params: SimulationParameters, users: int) -> ModuleResult:
    """
    Calculate Identity module revenue, costs, and profit.
    
    Logic:
    - verificationRate = % of users who UPGRADE to paid tiers
    - Basic tier is FREE and doesn't count toward revenue
    - Of those who upgrade, distribute: 75% Verified, 20% Premium, 5% Enterprise
    
    Issue #3: Conversion rate now uses realistic values (0.5-5%)
    Issue #11: Profile sales now use realistic assumptions
    """
    dist = config.USER_DISTRIBUTION['IDENTITY_TIERS']
    
    # Issue #3: Get effective conversion rate (may be adjusted for maturity)
    if hasattr(params, 'get_effective_conversion_rate'):
        conversion_rate = params.get_effective_conversion_rate()
    else:
        conversion_rate = params.verification_rate
    
    # verificationRate determines what % of users upgrade to paid tiers
    upgraded_users = round(users * conversion_rate)
    
    # Distribution of PAYING users only (Basic is free)
    verified_users = round(upgraded_users * dist['VERIFIED'])   # 75% of upgraded
    premium_users = round(upgraded_users * dist['PREMIUM'])     # 20% of upgraded
    enterprise_users = round(upgraded_users * dist['ENTERPRISE']) # 5% of upgraded
    
    # Basic users are the rest (FREE - no revenue from them)
    basic_users = max(0, users - upgraded_users)
    
    # Revenue from tier upgrades (monthly recurring)
    tier_revenue = (
        verified_users * params.verified_price +
        premium_users * params.premium_price +
        enterprise_users * params.enterprise_price
    )
    
    # Revenue from profile transfers
    # Issue #11: More conservative - only 2% of upgraded users transfer
    transfer_rate = config.ACTIVITY_RATES.get('PROFILE_TRANSFERS', 0.02)
    monthly_transfers = round(upgraded_users * transfer_rate)
    transfer_revenue = monthly_transfers * params.transfer_fee
    
    # Revenue from profile sales
    # Issue #11: Use configurable average price and realistic monthly sales
    avg_profile_price = getattr(params, 'avg_profile_price', config.MARKETPLACE.AVG_PROFILE_PRICE_USD)
    sale_revenue = params.monthly_sales * avg_profile_price * params.sale_commission
    
    # Total revenue (all in USD)
    revenue = tier_revenue + transfer_revenue + sale_revenue
    
    # Issue #9: Linear cost scaling
    costs = config.get_linear_cost('IDENTITY', users)
    
    # Profit
    profit = revenue - costs
    margin = (profit / revenue * 100) if revenue > 0 else 0
    
    return ModuleResult(
        revenue=round(revenue, 2),
        costs=round(costs, 2),
        profit=round(profit, 2),
        margin=round(margin, 1),
        breakdown={
            'basic_users': basic_users,
            'verified_users': verified_users,
            'premium_users': premium_users,
            'enterprise_users': enterprise_users,
            'upgraded_users': upgraded_users,
            'conversion_rate': round(conversion_rate * 100, 2),
            'tier_revenue': round(tier_revenue, 2),
            'transfer_revenue': round(transfer_revenue, 2),
            'sale_revenue': round(sale_revenue, 2),
            'monthly_transfers': monthly_transfers,
            'monthly_sales': params.monthly_sales,
            'avg_profile_price': avg_profile_price,
        }
    )
