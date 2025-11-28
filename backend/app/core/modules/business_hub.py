"""
Business Hub Module - Freelancer/Startup Ecosystem Revenue Calculations.

=== BUSINESS HUB (Mid-2027) ===

A comprehensive business ecosystem for freelancers, startups,
and established businesses with job matching, funding, and project management.

Revenue Streams:
1. Freelancer Platform
   - Job posting fees (VCoin)
   - Commission on earnings (12%)
   - Escrow fees (2%)

2. Startup Launchpad
   - Registration fees (VCoin)
   - Accelerator program fees (VCoin)
   - Token launch services

3. Funding Portal
   - Platform fee on funding (4%)
   - Investor network fees (VCoin/year)

4. Project Management SaaS
   - Professional tier subscriptions
   - Business tier subscriptions
   - Enterprise tier subscriptions

5. Learning Academy
   - Course sales (platform share 30%)
   - Monthly subscriptions

Launch Timeline: Month 21 (Mid-2027)
"""

from typing import Dict
from app.models import SimulationParameters, BusinessHubParameters


def calculate_business_hub(
    params: SimulationParameters,
    current_month: int,
    users: int,
    token_price: float
) -> Dict:
    """
    Calculate Business Hub revenue.
    
    Args:
        params: Simulation parameters
        current_month: Current month in simulation
        users: Total active users
        token_price: Current token price
    
    Returns:
        Dict with Business Hub revenue metrics
    """
    # Check if Business Hub is enabled
    bh_params = params.business_hub
    if not bh_params or not bh_params.enable_business_hub:
        return {
            'enabled': False,
            'revenue': 0,
            'costs': 0,
            'profit': 0,
            'launch_month': bh_params.business_hub_launch_month if bh_params else 21,
            'months_until_launch': (bh_params.business_hub_launch_month if bh_params else 21) - current_month,
        }
    
    # Check if launched
    if current_month < bh_params.business_hub_launch_month:
        return {
            'enabled': True,
            'launched': False,
            'revenue': 0,
            'costs': 0,
            'profit': 0,
            'launch_month': bh_params.business_hub_launch_month,
            'months_until_launch': bh_params.business_hub_launch_month - current_month,
        }
    
    # Growth curve
    months_active = current_month - bh_params.business_hub_launch_month + 1
    growth_factor = min(1.0, months_active / 12)
    
    # === FREELANCER PLATFORM ===
    
    active_freelancers = int(bh_params.freelancer_active_count * growth_factor)
    monthly_freelance_volume = bh_params.freelancer_monthly_transactions_usd * growth_factor
    
    # Job postings (estimate 0.5 jobs per freelancer per month)
    job_postings = int(active_freelancers * 0.5)
    job_posting_revenue_vcoin = job_postings * bh_params.freelancer_job_posting_fee
    job_posting_revenue_usd = job_posting_revenue_vcoin * token_price
    
    # Commission on transactions
    freelancer_commission = monthly_freelance_volume * bh_params.freelancer_commission_rate
    
    # Escrow fees
    freelancer_escrow_revenue = monthly_freelance_volume * bh_params.freelancer_escrow_fee
    
    freelancer_total = job_posting_revenue_usd + freelancer_commission + freelancer_escrow_revenue
    
    # === STARTUP LAUNCHPAD ===
    
    monthly_startups = int(bh_params.startup_monthly_registrations * growth_factor)
    startup_registration_vcoin = monthly_startups * bh_params.startup_registration_fee
    startup_registration_usd = startup_registration_vcoin * token_price
    
    accelerator_participants = int(bh_params.accelerator_participants * growth_factor)
    accelerator_revenue_vcoin = accelerator_participants * bh_params.accelerator_fee
    accelerator_revenue_usd = accelerator_revenue_vcoin * token_price
    
    startup_total = startup_registration_usd + accelerator_revenue_usd
    
    # === FUNDING PORTAL ===
    
    monthly_funding_volume = bh_params.funding_portal_monthly_volume * growth_factor
    funding_platform_fee = monthly_funding_volume * bh_params.funding_platform_fee
    
    investor_network_members = int(bh_params.investor_network_members * growth_factor)
    investor_fee_monthly = bh_params.investor_network_fee / 12  # Convert annual to monthly
    investor_network_revenue_vcoin = investor_network_members * investor_fee_monthly
    investor_network_revenue_usd = investor_network_revenue_vcoin * token_price
    
    funding_total = funding_platform_fee + investor_network_revenue_usd
    
    # === PROJECT MANAGEMENT SAAS ===
    
    pm_pro_users = int(bh_params.pm_professional_users * growth_factor)
    pm_biz_users = int(bh_params.pm_business_users * growth_factor)
    pm_enterprise_users = int(bh_params.pm_enterprise_users * growth_factor)
    
    pm_pro_revenue_vcoin = pm_pro_users * bh_params.pm_professional_fee
    pm_biz_revenue_vcoin = pm_biz_users * bh_params.pm_business_fee
    pm_enterprise_revenue_vcoin = pm_enterprise_users * bh_params.pm_enterprise_fee
    
    pm_total_vcoin = pm_pro_revenue_vcoin + pm_biz_revenue_vcoin + pm_enterprise_revenue_vcoin
    pm_total_usd = pm_total_vcoin * token_price
    
    # === LEARNING ACADEMY ===
    
    course_sales = int(bh_params.academy_monthly_course_sales * growth_factor)
    total_course_revenue = course_sales * bh_params.academy_avg_course_price
    academy_course_share_vcoin = total_course_revenue * bh_params.academy_platform_share
    academy_course_share_usd = academy_course_share_vcoin * token_price
    
    subscription_users = int(bh_params.academy_subscription_users * growth_factor)
    subscription_revenue_vcoin = subscription_users * bh_params.academy_subscription_fee
    subscription_revenue_usd = subscription_revenue_vcoin * token_price
    
    academy_total = academy_course_share_usd + subscription_revenue_usd
    
    # === COSTS ===
    
    # Customer support
    total_users = active_freelancers + monthly_startups + pm_pro_users + pm_biz_users + pm_enterprise_users
    support_cost = (total_users / 100) * 200  # $200 per 100 users
    
    # Infrastructure
    infrastructure_cost = 4000 * growth_factor
    
    # Payment processing (on funded amounts)
    payment_processing_cost = monthly_funding_volume * 0.02  # 2% to processors
    
    # Marketing
    marketing_cost = 2000 * growth_factor
    
    total_costs = support_cost + infrastructure_cost + payment_processing_cost + marketing_cost
    
    # === TOTALS ===
    
    total_revenue = (
        freelancer_total +
        startup_total +
        funding_total +
        pm_total_usd +
        academy_total
    )
    
    profit = total_revenue - total_costs
    margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Total VCoin collected
    total_vcoin_revenue = (
        job_posting_revenue_vcoin +
        startup_registration_vcoin +
        accelerator_revenue_vcoin +
        investor_network_revenue_vcoin +
        pm_total_vcoin +
        academy_course_share_vcoin +
        subscription_revenue_vcoin
    )
    
    return {
        'enabled': True,
        'launched': True,
        'months_active': months_active,
        'growth_factor': round(growth_factor, 2),
        
        # Revenue
        'revenue': round(total_revenue, 2),
        'freelancer_revenue': round(freelancer_total, 2),
        'startup_revenue': round(startup_total, 2),
        'funding_revenue': round(funding_total, 2),
        'pm_saas_revenue': round(pm_total_usd, 2),
        'academy_revenue': round(academy_total, 2),
        
        # Freelancer metrics
        'active_freelancers': active_freelancers,
        'job_postings': job_postings,
        'monthly_freelance_volume': round(monthly_freelance_volume, 2),
        'freelancer_commission': round(freelancer_commission, 2),
        
        # Startup metrics
        'monthly_startups': monthly_startups,
        'accelerator_participants': accelerator_participants,
        
        # Funding metrics
        'monthly_funding_volume': round(monthly_funding_volume, 2),
        'investor_network_members': investor_network_members,
        
        # PM SaaS metrics
        'pm_professional_users': pm_pro_users,
        'pm_business_users': pm_biz_users,
        'pm_enterprise_users': pm_enterprise_users,
        'pm_total_users': pm_pro_users + pm_biz_users + pm_enterprise_users,
        
        # Academy metrics
        'course_sales': course_sales,
        'subscription_users': subscription_users,
        
        # VCoin revenue
        'total_vcoin_revenue': round(total_vcoin_revenue, 2),
        
        # Costs
        'costs': round(total_costs, 2),
        'support_cost': round(support_cost, 2),
        'infrastructure_cost': round(infrastructure_cost, 2),
        'payment_processing_cost': round(payment_processing_cost, 2),
        'marketing_cost': round(marketing_cost, 2),
        
        # Profit
        'profit': round(profit, 2),
        'margin': round(margin, 1),
        
        # Configuration
        'launch_month': bh_params.business_hub_launch_month,
        'freelancer_commission_rate': bh_params.freelancer_commission_rate * 100,
        'funding_platform_fee_rate': bh_params.funding_platform_fee * 100,
        'academy_platform_share': bh_params.academy_platform_share * 100,
    }

