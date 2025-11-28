"""
Cross-Platform Module - Content Sharing and Account Renting Revenue.

=== CROSS-PLATFORM (Start of 2027) ===

A revolutionary feature allowing users to share, syndicate, or rent
access to social media accounts across platforms.

Revenue Streams:
1. Content Sharing Subscriptions
   - Creator tier (VCoin/month)
   - Professional tier (VCoin/month)
   - Agency tier (VCoin/month)

2. Account Renting
   - Commission on rentals (15%)
   - Escrow fees (2%)

3. Insurance
   - Premium on protected rentals (3%)

4. Verification
   - Account verification fees (VCoin)
   - Premium verified badge (VCoin/year)

5. Analytics & API
   - Advanced analytics subscription (VCoin/month)
   - API access subscription (VCoin/month)

6. Content Licensing
   - Commission on license deals (20%)

Launch Timeline: Month 15 (Start of 2027)
"""

from typing import Dict
from app.models import SimulationParameters, CrossPlatformParameters


def calculate_cross_platform(
    params: SimulationParameters,
    current_month: int,
    users: int,
    token_price: float
) -> Dict:
    """
    Calculate Cross-Platform revenue.
    
    Args:
        params: Simulation parameters
        current_month: Current month in simulation
        users: Total active users
        token_price: Current token price
    
    Returns:
        Dict with Cross-Platform revenue metrics
    """
    # Check if Cross-Platform is enabled
    cp_params = params.cross_platform
    if not cp_params or not cp_params.enable_cross_platform:
        return {
            'enabled': False,
            'revenue': 0,
            'costs': 0,
            'profit': 0,
            'launch_month': cp_params.cross_platform_launch_month if cp_params else 15,
            'months_until_launch': (cp_params.cross_platform_launch_month if cp_params else 15) - current_month,
        }
    
    # Check if launched
    if current_month < cp_params.cross_platform_launch_month:
        return {
            'enabled': True,
            'launched': False,
            'revenue': 0,
            'costs': 0,
            'profit': 0,
            'launch_month': cp_params.cross_platform_launch_month,
            'months_until_launch': cp_params.cross_platform_launch_month - current_month,
        }
    
    # Growth curve
    months_active = current_month - cp_params.cross_platform_launch_month + 1
    growth_factor = min(1.0, months_active / 12)
    
    # === CONTENT SHARING SUBSCRIPTIONS ===
    
    creator_subs = int(cp_params.cross_platform_creator_subscribers * growth_factor)
    pro_subs = int(cp_params.cross_platform_professional_subscribers * growth_factor)
    agency_subs = int(cp_params.cross_platform_agency_subscribers * growth_factor)
    
    creator_revenue_vcoin = creator_subs * cp_params.cross_platform_creator_tier_fee
    pro_revenue_vcoin = pro_subs * cp_params.cross_platform_professional_tier_fee
    agency_revenue_vcoin = agency_subs * cp_params.cross_platform_agency_tier_fee
    
    subscription_revenue_vcoin = creator_revenue_vcoin + pro_revenue_vcoin + agency_revenue_vcoin
    subscription_revenue_usd = subscription_revenue_vcoin * token_price
    
    # === ACCOUNT RENTING ===
    
    monthly_rental_volume = cp_params.cross_platform_monthly_rental_volume * growth_factor
    
    rental_commission = monthly_rental_volume * cp_params.cross_platform_rental_commission
    rental_escrow = monthly_rental_volume * cp_params.cross_platform_escrow_fee
    
    active_renters = int(cp_params.cross_platform_active_renters * growth_factor)
    active_owners = int(cp_params.cross_platform_active_owners * growth_factor)
    
    rental_total = rental_commission + rental_escrow
    
    # === INSURANCE ===
    
    insured_transactions = monthly_rental_volume * cp_params.cross_platform_insurance_take_rate
    insurance_revenue = insured_transactions * cp_params.cross_platform_insurance_rate
    
    # === VERIFICATION ===
    
    monthly_verifications = int(cp_params.cross_platform_monthly_verifications * growth_factor)
    verification_revenue_vcoin = monthly_verifications * cp_params.cross_platform_verification_fee
    verification_revenue_usd = verification_revenue_vcoin * token_price
    
    # Premium verified (monthly portion of annual fee)
    premium_verified = int(cp_params.cross_platform_premium_verified_users * growth_factor)
    premium_verified_monthly_vcoin = (cp_params.cross_platform_premium_verified_fee / 12) * premium_verified
    premium_verified_monthly_usd = premium_verified_monthly_vcoin * token_price
    
    verification_total = verification_revenue_usd + premium_verified_monthly_usd
    
    # === ANALYTICS & API ===
    
    analytics_users = int(cp_params.cross_platform_advanced_analytics_users * growth_factor)
    api_users = int(cp_params.cross_platform_api_users * growth_factor)
    
    analytics_revenue_vcoin = analytics_users * cp_params.cross_platform_analytics_fee
    api_revenue_vcoin = api_users * cp_params.cross_platform_api_fee
    
    analytics_total_vcoin = analytics_revenue_vcoin + api_revenue_vcoin
    analytics_total_usd = analytics_total_vcoin * token_price
    
    # === CONTENT LICENSING ===
    
    monthly_license_volume = cp_params.cross_platform_monthly_license_volume * growth_factor
    license_revenue = monthly_license_volume * cp_params.cross_platform_license_commission
    
    # === COSTS ===
    
    # Insurance claims (estimate 5% claim rate)
    insurance_claims = insured_transactions * 0.05
    
    # Dispute resolution
    disputes_per_month = int((active_renters + active_owners) * 0.02)  # 2% dispute rate
    dispute_cost = disputes_per_month * 50  # $50 per dispute
    
    # API infrastructure
    api_infrastructure = api_users * 10  # $10 per API user per month
    
    # Customer support
    total_users = creator_subs + pro_subs + agency_subs + active_renters + analytics_users
    support_cost = (total_users / 100) * 150  # $150 per 100 users
    
    # Platform infrastructure
    infrastructure_cost = 3000 * growth_factor
    
    total_costs = insurance_claims + dispute_cost + api_infrastructure + support_cost + infrastructure_cost
    
    # === TOTALS ===
    
    total_revenue = (
        subscription_revenue_usd +
        rental_total +
        insurance_revenue +
        verification_total +
        analytics_total_usd +
        license_revenue
    )
    
    profit = total_revenue - total_costs
    margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Total VCoin collected
    total_vcoin_revenue = (
        subscription_revenue_vcoin +
        verification_revenue_vcoin +
        premium_verified_monthly_vcoin +
        analytics_total_vcoin
    )
    
    return {
        'enabled': True,
        'launched': True,
        'months_active': months_active,
        'growth_factor': round(growth_factor, 2),
        
        # Revenue
        'revenue': round(total_revenue, 2),
        'subscription_revenue': round(subscription_revenue_usd, 2),
        'rental_revenue': round(rental_total, 2),
        'insurance_revenue': round(insurance_revenue, 2),
        'verification_revenue': round(verification_total, 2),
        'analytics_revenue': round(analytics_total_usd, 2),
        'license_revenue': round(license_revenue, 2),
        
        # Subscription metrics
        'creator_subscribers': creator_subs,
        'professional_subscribers': pro_subs,
        'agency_subscribers': agency_subs,
        'total_subscribers': creator_subs + pro_subs + agency_subs,
        
        # Rental metrics
        'monthly_rental_volume': round(monthly_rental_volume, 2),
        'rental_commission': round(rental_commission, 2),
        'rental_escrow_revenue': round(rental_escrow, 2),
        'active_renters': active_renters,
        'active_owners': active_owners,
        
        # Insurance metrics
        'insured_volume': round(insured_transactions, 2),
        'insurance_take_rate': round(cp_params.cross_platform_insurance_take_rate * 100, 1),
        
        # Verification metrics
        'monthly_verifications': monthly_verifications,
        'premium_verified_users': premium_verified,
        
        # Analytics metrics
        'analytics_users': analytics_users,
        'api_users': api_users,
        
        # Licensing metrics
        'monthly_license_volume': round(monthly_license_volume, 2),
        
        # VCoin revenue
        'total_vcoin_revenue': round(total_vcoin_revenue, 2),
        'subscription_vcoin': round(subscription_revenue_vcoin, 2),
        'verification_vcoin': round(verification_revenue_vcoin, 2),
        'analytics_vcoin': round(analytics_total_vcoin, 2),
        
        # Costs
        'costs': round(total_costs, 2),
        'insurance_claims': round(insurance_claims, 2),
        'dispute_cost': round(dispute_cost, 2),
        'api_infrastructure_cost': round(api_infrastructure, 2),
        'support_cost': round(support_cost, 2),
        'infrastructure_cost': round(infrastructure_cost, 2),
        
        # Profit
        'profit': round(profit, 2),
        'margin': round(margin, 1),
        
        # Configuration
        'launch_month': cp_params.cross_platform_launch_month,
        'rental_commission_rate': cp_params.cross_platform_rental_commission * 100,
        'insurance_rate': cp_params.cross_platform_insurance_rate * 100,
        'license_commission_rate': cp_params.cross_platform_license_commission * 100,
    }

