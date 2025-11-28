"""
Marketplace Module - Physical/Digital Goods Revenue Calculations.

=== MARKETPLACE (2026-2027) ===

A full-featured marketplace for physical products, digital goods,
NFTs, and services with cryptocurrency payments.

Revenue Streams:
1. Commission on Physical Goods (8%)
2. Commission on Digital Goods (15%)
3. Commission on NFT Sales (2.5%)
4. Commission on Services (8%)
5. Payment Processing Fee (1%)
6. Escrow Service Fee (1%)
7. Featured Listings (VCoin)
8. Store Subscriptions (VCoin)
9. Sponsored Listing Ads (CPC)

Launch Timeline: Month 18 (1.5 years after TGE)
"""

from typing import Dict
from app.models import SimulationParameters, MarketplaceParameters


def calculate_marketplace(
    params: SimulationParameters,
    current_month: int,
    users: int,
    token_price: float
) -> Dict:
    """
    Calculate Marketplace revenue.
    
    Args:
        params: Simulation parameters
        current_month: Current month in simulation
        users: Total active users
        token_price: Current token price
    
    Returns:
        Dict with Marketplace revenue metrics
    """
    # Check if Marketplace is enabled
    mp_params = params.marketplace
    if not mp_params or not mp_params.enable_marketplace:
        return {
            'enabled': False,
            'revenue': 0,
            'costs': 0,
            'profit': 0,
            'launch_month': mp_params.marketplace_launch_month if mp_params else 18,
            'months_until_launch': (mp_params.marketplace_launch_month if mp_params else 18) - current_month,
        }
    
    # Check if launched
    if current_month < mp_params.marketplace_launch_month:
        return {
            'enabled': True,
            'launched': False,
            'revenue': 0,
            'costs': 0,
            'profit': 0,
            'launch_month': mp_params.marketplace_launch_month,
            'months_until_launch': mp_params.marketplace_launch_month - current_month,
        }
    
    # Growth curve
    months_active = current_month - mp_params.marketplace_launch_month + 1
    growth_factor = min(1.0, months_active / 12)
    
    # === GMV CALCULATIONS ===
    
    monthly_gmv = mp_params.marketplace_monthly_gmv_usd * growth_factor
    
    # GMV by category
    physical_gmv = monthly_gmv * mp_params.marketplace_gmv_physical_percent
    digital_gmv = monthly_gmv * mp_params.marketplace_gmv_digital_percent
    nft_gmv = monthly_gmv * mp_params.marketplace_gmv_nft_percent
    services_gmv = monthly_gmv * mp_params.marketplace_gmv_services_percent
    
    # === COMMISSION REVENUE ===
    
    physical_commission = physical_gmv * mp_params.marketplace_physical_commission
    digital_commission = digital_gmv * mp_params.marketplace_digital_commission
    nft_commission = nft_gmv * mp_params.marketplace_nft_commission
    services_commission = services_gmv * mp_params.marketplace_service_commission
    
    # Apply max commission cap
    total_commission = (
        min(physical_commission, mp_params.marketplace_max_commission_usd * (physical_gmv / 1000)) +
        min(digital_commission, mp_params.marketplace_max_commission_usd * (digital_gmv / 1000)) +
        nft_commission +
        services_commission
    )
    
    # === PAYMENT PROCESSING ===
    
    crypto_payment_revenue = monthly_gmv * mp_params.marketplace_crypto_payment_fee
    escrow_revenue = monthly_gmv * 0.7 * mp_params.marketplace_escrow_fee  # 70% use escrow
    
    # === SELLER SERVICES ===
    
    active_sellers = int(mp_params.marketplace_active_sellers * growth_factor)
    
    # Featured listings
    featured_listings_monthly = int(active_sellers * 0.20)  # 20% feature listings
    featured_revenue_vcoin = featured_listings_monthly * mp_params.marketplace_featured_listing_fee
    featured_revenue_usd = featured_revenue_vcoin * token_price
    
    # Store subscriptions
    store_subscribers = int(active_sellers * mp_params.marketplace_store_subscription_rate)
    store_revenue_vcoin = store_subscribers * mp_params.marketplace_store_subscription_fee
    store_revenue_usd = store_revenue_vcoin * token_price
    
    # === ADVERTISING ===
    
    monthly_ad_clicks = int(mp_params.marketplace_monthly_ad_clicks * growth_factor)
    ad_revenue = monthly_ad_clicks * mp_params.marketplace_ad_cpc
    
    # === COSTS ===
    
    # Payment processing costs (3rd party)
    payment_processing_cost = monthly_gmv * 0.005  # 0.5% to payment processors
    
    # Fraud prevention
    fraud_cost = monthly_gmv * 0.002  # 0.2% fraud prevention
    
    # Customer support (per 1000 transactions)
    transactions = monthly_gmv / 100  # avg $100 order
    support_cost = (transactions / 1000) * 500  # $500 per 1000 orders
    
    # Infrastructure
    infrastructure_cost = 3000 * growth_factor
    
    total_costs = (
        payment_processing_cost +
        fraud_cost +
        support_cost +
        infrastructure_cost
    )
    
    # === TOTALS ===
    
    total_revenue = (
        total_commission +
        crypto_payment_revenue +
        escrow_revenue +
        featured_revenue_usd +
        store_revenue_usd +
        ad_revenue
    )
    
    profit = total_revenue - total_costs
    margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        'enabled': True,
        'launched': True,
        'months_active': months_active,
        'growth_factor': round(growth_factor, 2),
        
        # Revenue
        'revenue': round(total_revenue, 2),
        'commission_revenue': round(total_commission, 2),
        'physical_commission': round(physical_commission, 2),
        'digital_commission': round(digital_commission, 2),
        'nft_commission': round(nft_commission, 2),
        'services_commission': round(services_commission, 2),
        'payment_processing_revenue': round(crypto_payment_revenue, 2),
        'escrow_revenue': round(escrow_revenue, 2),
        'featured_revenue_usd': round(featured_revenue_usd, 2),
        'store_subscription_revenue_usd': round(store_revenue_usd, 2),
        'ad_revenue': round(ad_revenue, 2),
        
        # GMV metrics
        'monthly_gmv': round(monthly_gmv, 2),
        'physical_gmv': round(physical_gmv, 2),
        'digital_gmv': round(digital_gmv, 2),
        'nft_gmv': round(nft_gmv, 2),
        'services_gmv': round(services_gmv, 2),
        
        # Sellers
        'active_sellers': active_sellers,
        'verified_sellers': int(active_sellers * mp_params.marketplace_verified_seller_rate),
        'store_subscribers': store_subscribers,
        'featured_listings_monthly': featured_listings_monthly,
        
        # Advertising
        'monthly_ad_clicks': monthly_ad_clicks,
        
        # VCoin revenue
        'featured_revenue_vcoin': round(featured_revenue_vcoin, 2),
        'store_revenue_vcoin': round(store_revenue_vcoin, 2),
        
        # Costs
        'costs': round(total_costs, 2),
        'payment_processing_cost': round(payment_processing_cost, 2),
        'fraud_cost': round(fraud_cost, 2),
        'support_cost': round(support_cost, 2),
        'infrastructure_cost': round(infrastructure_cost, 2),
        
        # Profit
        'profit': round(profit, 2),
        'margin': round(margin, 1),
        
        # Take rate (effective commission)
        'effective_take_rate': round((total_commission / monthly_gmv * 100) if monthly_gmv > 0 else 0, 2),
        
        # Configuration
        'launch_month': mp_params.marketplace_launch_month,
        'physical_commission_rate': mp_params.marketplace_physical_commission * 100,
        'digital_commission_rate': mp_params.marketplace_digital_commission * 100,
        'nft_commission_rate': mp_params.marketplace_nft_commission * 100,
        'service_commission_rate': mp_params.marketplace_service_commission * 100,
    }

