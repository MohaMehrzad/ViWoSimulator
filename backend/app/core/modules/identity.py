"""
Identity Module calculations.

Updated for Issues #3, #9, #11:
- Issue #3: Uses maturity-adjusted conversion rates
- Issue #9: Linear cost scaling
- Issue #11: Realistic profile sales assumptions
- Dec 2025: Added 5A Policy integration for fee discounts
"""

from typing import Optional
from app.config import config
from app.models import SimulationParameters, ModuleResult


def calculate_identity(
    params: SimulationParameters,
    users: int,
    five_a_fee_discount: float = 0.0,
) -> ModuleResult:
    """
    Calculate Identity module revenue, costs, and profit.
    
    Logic:
    - verificationRate = % of users who UPGRADE to paid tiers
    - Basic tier is FREE and doesn't count toward revenue
    - Of those who upgrade, distribute: 75% Verified, 20% Premium, 5% Enterprise
    
    Issue #3: Conversion rate now uses realistic values (0.5-5%)
    Issue #11: Profile sales now use realistic assumptions
    
    5A Integration (Dec 2025):
    - High 5A users receive fee discounts on tier subscriptions
    - five_a_fee_discount is average discount across population (0.0-0.5)
    """
    # Check if module is enabled
    if not getattr(params, 'enable_identity', True):
        return ModuleResult(
            revenue=0,
            costs=0,
            profit=0,
            margin=0,
            breakdown={
                'enabled': False,
                'basic_users': 0,
                'verified_users': 0,
                'premium_users': 0,
                'enterprise_users': 0,
                'upgraded_users': 0,
                'conversion_rate': 0,
                'tier_revenue': 0,
                'transfer_revenue': 0,
                'sale_revenue': 0,
                'monthly_transfers': 0,
                'monthly_sales': 0,
                'avg_profile_price': 0,
            }
        )
    
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
    # 5A Integration: Apply fee discount for high performers
    tier_discount_factor = 1.0 - five_a_fee_discount
    tier_revenue = (
        verified_users * params.verified_price +
        premium_users * params.premium_price +
        enterprise_users * params.enterprise_price
    ) * tier_discount_factor
    
    # Revenue from profile transfers
    # Issue #11: More conservative - only 2% of upgraded users transfer
    transfer_rate = config.ACTIVITY_RATES.get('PROFILE_TRANSFERS', 0.02)
    monthly_transfers = round(upgraded_users * transfer_rate)
    transfer_revenue = monthly_transfers * params.transfer_fee
    
    # Revenue from profile sales
    # Issue #11: Use configurable average price and realistic monthly sales
    # Issue #7 Fix: Use maturity-adjusted values when auto_adjust enabled
    if hasattr(params, 'get_effective_avg_profile_price'):
        avg_profile_price = params.get_effective_avg_profile_price()
    else:
        avg_profile_price = getattr(params, 'avg_profile_price', config.MARKETPLACE.AVG_PROFILE_PRICE_USD)
    
    if hasattr(params, 'get_effective_monthly_sales'):
        monthly_sales = params.get_effective_monthly_sales()
    else:
        monthly_sales = params.monthly_sales
    
    sale_revenue = monthly_sales * avg_profile_price * params.sale_commission
    
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
            'monthly_sales': monthly_sales,  # Issue #7 Fix: Use maturity-adjusted value
            'avg_profile_price': avg_profile_price,
            # 5A Integration
            'five_a_fee_discount': round(five_a_fee_discount * 100, 2),
            'five_a_discount_applied': round(tier_revenue * five_a_fee_discount / tier_discount_factor, 2) if tier_discount_factor > 0 else 0,
        }
    )
