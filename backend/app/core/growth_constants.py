"""
Growth scenario constants for 5-year projections.

Ported from frontend constants.ts to ensure backend calculations
match UI exactly.
"""

from typing import Dict, List, Any, TypedDict


class GrowthScenarioConfig(TypedDict):
    """Growth scenario configuration"""
    name: str
    description: str
    waitlist_conversion_rate: float
    month1_fomo_multiplier: float
    monthly_growth_rates: List[float]
    month1_retention: float
    month3_retention: float
    month6_retention: float
    month12_retention: float
    viral_coefficient: float
    token_price_start: float
    token_price_month6_multiplier: float
    token_price_end_multiplier: float
    expected_month1_users: int
    expected_month12_mau: int


class MarketConditionConfig(TypedDict):
    """Market condition multipliers"""
    name: str
    description: str
    growth_multiplier: float
    retention_multiplier: float
    price_multiplier: float
    fomo_multiplier: float
    cac_multiplier: float


class MarketCycleYearConfig(TypedDict):
    """Market cycle data for a specific year"""
    year: int
    phase: str
    growth_multiplier: float
    retention_multiplier: float
    price_multiplier: float
    description: str


# === GROWTH SCENARIOS ===
GROWTH_SCENARIOS: Dict[str, GrowthScenarioConfig] = {
    "conservative": {
        "name": "Conservative",
        "description": "Cautious growth with focus on retention over acquisition. Assumes modest marketing budget, organic-first approach, and potential market headwinds.",
        "waitlist_conversion_rate": 0.40,
        "month1_fomo_multiplier": 2.5,
        "monthly_growth_rates": [0.25, 0.10, 0.00, -0.05, -0.03, 0.02, 0.03, 0.05, 0.02, 0.01, 0.04, 0.03],
        "month1_retention": 0.18,
        "month3_retention": 0.08,
        "month6_retention": 0.04,
        "month12_retention": 0.02,
        "viral_coefficient": 0.3,
        "token_price_start": 0.03,
        "token_price_month6_multiplier": 0.66,
        "token_price_end_multiplier": 1.0,
        "expected_month1_users": 3300,
        "expected_month12_mau": 3000,
    },
    "base": {
        "name": "Base",
        "description": "Balanced growth scenario based on comparable SocialFi launches. Assumes solid execution, reasonable marketing spend, and neutral-to-positive market conditions.",
        "waitlist_conversion_rate": 0.50,
        "month1_fomo_multiplier": 5.0,
        "monthly_growth_rates": [0.40, 0.25, 0.15, 0.20, 0.10, 0.12, 0.08, 0.10, 0.06, 0.05, 0.08, 0.07],
        "month1_retention": 0.22,
        "month3_retention": 0.10,
        "month6_retention": 0.06,
        "month12_retention": 0.035,
        "viral_coefficient": 0.5,
        "token_price_start": 0.03,
        "token_price_month6_multiplier": 2.0,
        "token_price_end_multiplier": 3.5,
        "expected_month1_users": 5800,
        "expected_month12_mau": 14500,
    },
    "bullish": {
        "name": "Bullish",
        "description": "Aggressive growth scenario assuming viral adoption, strong market conditions (bull market), major partnerships, and successful influencer campaigns.",
        "waitlist_conversion_rate": 0.60,
        "month1_fomo_multiplier": 12.0,
        "monthly_growth_rates": [0.80, 0.50, 0.35, 0.25, 0.30, 0.25, 0.15, 0.18, 0.12, 0.15, 0.12, 0.18],
        "month1_retention": 0.28,
        "month3_retention": 0.15,
        "month6_retention": 0.10,
        "month12_retention": 0.06,
        "viral_coefficient": 0.8,
        "token_price_start": 0.03,
        "token_price_month6_multiplier": 4.0,
        "token_price_end_multiplier": 7.0,
        "expected_month1_users": 12800,
        "expected_month12_mau": 62500,
    },
}


# === MARKET CONDITIONS ===
MARKET_CONDITIONS: Dict[str, MarketConditionConfig] = {
    "bear": {
        "name": "Bear Market",
        "description": "Crypto winter conditions - reduced interest, lower liquidity, higher CAC, risk-off sentiment.",
        "growth_multiplier": 0.6,
        "retention_multiplier": 0.8,
        "price_multiplier": 0.5,
        "fomo_multiplier": 0.7,
        "cac_multiplier": 1.5,
    },
    "neutral": {
        "name": "Neutral Market",
        "description": "Sideways market - stable conditions, balanced interest, normal acquisition costs.",
        "growth_multiplier": 1.0,
        "retention_multiplier": 1.0,
        "price_multiplier": 1.0,
        "fomo_multiplier": 1.0,
        "cac_multiplier": 1.0,
    },
    "bull": {
        "name": "Bull Market",
        "description": "Crypto bull run - high interest, increased liquidity, lower CAC, risk-on sentiment, FOMO amplified.",
        "growth_multiplier": 1.5,
        "retention_multiplier": 1.1,
        "price_multiplier": 2.0,
        "fomo_multiplier": 1.5,
        "cac_multiplier": 0.7,
    },
}


# === 5-YEAR MARKET CYCLE ANALYSIS (2026-2030) ===
# Bitcoin Halving April 2024 - Market cycle analysis for 2026-2030
MARKET_CYCLE_2026_2030: Dict[int, MarketCycleYearConfig] = {
    2026: {
        "year": 2026,
        "phase": "Peak Bull / Altcoin Season",
        "growth_multiplier": 1.6,
        "retention_multiplier": 1.15,
        "price_multiplier": 2.5,
        "description": "Peak of bull cycle expected. Maximum FOMO, highest valuations. Social tokens and SocialFi projects see maximum interest. Token launch timing optimal (March 2026 TGE).",
    },
    2027: {
        "year": 2027,
        "phase": "Late Bull / Distribution",
        "growth_multiplier": 1.2,
        "retention_multiplier": 1.0,
        "price_multiplier": 1.8,
        "description": "Distribution phase begins. Smart money taking profits. New user acquisition slows but platform maturity increases. Focus on retention and utility over speculation.",
    },
    2028: {
        "year": 2028,
        "phase": "Bear / Accumulation",
        "growth_multiplier": 0.7,
        "retention_multiplier": 0.85,
        "price_multiplier": 0.5,
        "description": "Next halving approaches (expected April 2028). Bear market conditions. CAC increases, retention becomes critical. Building phase - focus on product and community.",
    },
    2029: {
        "year": 2029,
        "phase": "Recovery / New Cycle Begins",
        "growth_multiplier": 1.1,
        "retention_multiplier": 1.0,
        "price_multiplier": 1.0,
        "description": "Post-halving recovery begins. Market sentiment improving. Platform is mature with established user base. Positioned for next growth cycle.",
    },
    2030: {
        "year": 2030,
        "phase": "Early Bull / Mature Platform",
        "growth_multiplier": 1.4,
        "retention_multiplier": 1.1,
        "price_multiplier": 1.5,
        "description": "New bull cycle in progress. Platform has 4+ years of operation. Established brand, lower CAC, high retention. Expansion into new markets and features.",
    },
}


# === FUTURE MODULE DEFAULT PARAMETERS ===
FUTURE_MODULE_DEFAULTS = {
    "vchain": {
        "enable_vchain": False,
        "vchain_launch_month": 24,
        "vchain_tx_fee_percent": 0.002,
        "vchain_bridge_fee_percent": 0.001,
        "vchain_gas_markup_percent": 0.08,
        "vchain_monthly_tx_volume_usd": 25_000_000,
        "vchain_monthly_bridge_volume_usd": 50_000_000,
        "vchain_validator_apy": 0.10,
        "vchain_min_validator_stake": 100000,
        "vchain_validator_count": 100,
        "vchain_enterprise_clients": 10,
        "vchain_avg_enterprise_revenue": 5000,
    },
    "marketplace": {
        "enable_marketplace": False,
        "marketplace_launch_month": 18,
        "marketplace_physical_commission": 0.08,  # 8%
        "marketplace_digital_commission": 0.15,   # 15%
        "marketplace_nft_commission": 0.025,      # 2.5%
        "marketplace_service_commission": 0.08,   # 8%
        "marketplace_crypto_payment_fee": 0.01,   # 1%
        "marketplace_escrow_fee": 0.01,           # 1%
        "marketplace_monthly_gmv_usd": 5_000_000,
        "marketplace_gmv_physical_percent": 0.40,
        "marketplace_gmv_digital_percent": 0.35,
        "marketplace_gmv_nft_percent": 0.10,
        "marketplace_gmv_services_percent": 0.15,
        "marketplace_active_sellers": 500,
        "marketplace_verified_seller_rate": 0.30,
        "marketplace_store_subscription_rate": 0.20,
        "marketplace_store_subscription_fee": 1000,  # VCoin
        "marketplace_featured_listing_fee": 100,     # VCoin
        "marketplace_monthly_ad_clicks": 100000,
        "marketplace_ad_cpc": 0.50,
        "marketplace_max_commission_usd": 500,
    },
    "business_hub": {
        "enable_business_hub": False,
        "business_hub_launch_month": 21,
        "business_hub_freelancer_fee_percent": 0.12,      # 12%
        "business_hub_startup_listing_fee": 500,          # VCoin
        "business_hub_funding_fee_percent": 0.05,         # 5%
        "business_hub_pm_tools_subscription_fee": 500,    # VCoin/month
        "business_hub_freelancer_adoption_rate": 0.02,    # 2% of users
        "business_hub_avg_project_value": 500,            # USD
        "business_hub_avg_projects_per_month": 1.0,       # Per freelancer
        "business_hub_pm_subscription_rate": 0.05,        # 5% of users
        "business_hub_startup_listings_monthly": 10,
        "business_hub_avg_funding_raised": 50000,         # USD
    },
    "cross_platform": {
        "enable_cross_platform": False,
        "cross_platform_launch_month": 15,
        "cross_platform_subscription_fee": 333,           # VCoin (~$10/month at $0.03)
        "cross_platform_rental_commission": 0.15,         # 15%
        "cross_platform_subscription_rate": 0.03,         # 3% of users
        "cross_platform_rental_rate": 0.01,               # 1% of users rent
        "cross_platform_avg_rental_revenue": 1667,        # VCoin (~$50/month at $0.03)
    },
}
