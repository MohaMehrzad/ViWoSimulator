"""
Pydantic models for simulation parameters.

Updated with 2024-2025 industry benchmarks and platform maturity model.
Addresses Issues #2, #3, #4, #5, #8, #11, #12, #13 from the audit.

Nov 2025: Added growth scenario parameters for user growth projections.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from enum import Enum


class GrowthScenarioType(str, Enum):
    """Growth scenario selection for user projections"""
    CONSERVATIVE = "conservative"
    BASE = "base"
    BULLISH = "bullish"


class MarketConditionType(str, Enum):
    """Macro market condition affecting growth"""
    BEAR = "bear"
    NEUTRAL = "neutral"
    BULL = "bull"


class PlatformMaturity(str, Enum):
    """
    Platform maturity tier that affects realistic parameter ranges.
    
    Different maturity levels have different expected metrics for:
    - Customer Acquisition Costs (CAC)
    - Conversion rates (paid subscriptions)
    - Ad CPM rates and fill rates
    - User engagement metrics
    
    Based on industry benchmarks from App Annie, AppsFlyer, and public
    company filings (Meta, Snap, Pinterest 10-K reports).
    """
    LAUNCH = "launch"           # 0-6 months: Low CPM, low conversion, high CAC
    GROWING = "growing"         # 6-18 months: Improving metrics
    ESTABLISHED = "established" # 18+ months: Industry-standard rates


class RetentionModelType(str, Enum):
    """Retention curve model selection"""
    SOCIAL_APP = "social_app"
    CRYPTO_APP = "crypto_app"
    GAMING = "gaming"
    UTILITY = "utility"
    CUSTOM = "custom"


# Maturity-based default adjustments
# These multiply/adjust base parameters based on platform maturity
# Updated Nov 2025: Made "launch" settings viable for profitability
MATURITY_ADJUSTMENTS = {
    PlatformMaturity.LAUNCH: {
        # Launch platform - lower metrics but still viable
        'cac_multiplier': 1.3,          # 30% higher CAC for new brand
        'conversion_rate': 0.015,       # 1.5% paid conversion
        'ad_fill_rate': 0.20,           # 20% ad fill rate (was 10%)
        'banner_cpm': 0.50,             # $0.50 banner CPM (was $0.25)
        'video_cpm': 2.00,              # $2.00 video CPM (was $1.00)
        'profile_sales_monthly': 1,     # Some early sales
        'avg_profile_price': 20,        # Low prices
        'nft_percentage': 0.001,        # 0.1% NFT mints
        'creator_percentage': 0.12,     # 12% are creators
        'staking_participation': 0.08,  # 8% stake tokens
    },
    PlatformMaturity.GROWING: {
        'cac_multiplier': 1.15,         # 15% higher CAC
        'conversion_rate': 0.025,       # 2.5% paid conversion
        'ad_fill_rate': 0.40,           # 40% ad fill rate
        'banner_cpm': 3.00,             # $3.00 banner CPM
        'video_cpm': 10.00,             # $10.00 video CPM
        'profile_sales_monthly': 8,     # Active trading
        'avg_profile_price': 60,        # Growing prices
        'nft_percentage': 0.005,        # 0.5% NFT mints
        'creator_percentage': 0.15,     # 15% are creators
        'staking_participation': 0.12,  # 12% stake tokens
    },
    PlatformMaturity.ESTABLISHED: {
        'cac_multiplier': 1.0,          # Base CAC
        'conversion_rate': 0.04,        # 4% paid conversion
        'ad_fill_rate': 0.70,           # 70% ad fill rate
        'banner_cpm': 8.00,             # $8.00 banner CPM
        'video_cpm': 25.00,             # $25.00 video CPM
        'profile_sales_monthly': 20,    # Active marketplace
        'avg_profile_price': 100,       # Established prices
        'nft_percentage': 0.01,         # 1% NFT mints
        'creator_percentage': 0.18,     # 18% are creators
        'staking_participation': 0.20,  # 20% stake tokens
    },
}


class ComplianceCosts(BaseModel):
    """
    Regulatory and compliance costs - Issue #13 fix.
    
    These are often overlooked but critical for crypto platforms:
    - KYC/AML: Required for exchanges, fiat on/off ramps
    - Legal: Ongoing securities compliance, terms of service
    - Insurance: Crypto custody, liability insurance
    - Audits: Smart contract audits, financial audits
    
    Costs scaled for early-stage platforms. Enterprise costs are 5-10x higher.
    """
    kyc_aml_monthly: float = Field(
        default=500, ge=0, 
        description="KYC/AML provider monthly cost (starter tier)"
    )
    legal_monthly: float = Field(
        default=1000, ge=0,
        description="Ongoing legal counsel monthly (fractional/retainer)"
    )
    insurance_monthly: float = Field(
        default=500, ge=0,
        description="Crypto/liability insurance monthly (basic coverage)"
    )
    audit_quarterly: float = Field(
        default=2500, ge=0,
        description="Quarterly security/financial audits"
    )
    gdpr_privacy_monthly: float = Field(
        default=250, ge=0,
        description="GDPR/privacy compliance monthly"
    )
    
    @property
    def monthly_total(self) -> float:
        """Total monthly compliance cost (amortized)"""
        return (
            self.kyc_aml_monthly +
            self.legal_monthly +
            self.insurance_monthly +
            (self.audit_quarterly / 3) +  # Amortize quarterly to monthly
            self.gdpr_privacy_monthly
        )
    
    @classmethod
    def minimal(cls) -> 'ComplianceCosts':
        """Minimal compliance for very early stage / MVP"""
        return cls(
            kyc_aml_monthly=0,
            legal_monthly=500,
            insurance_monthly=0,
            audit_quarterly=0,
            gdpr_privacy_monthly=100,
        )


class RegionalComplianceCosts(BaseModel):
    """
    Regional compliance costs by jurisdiction.
    
    Based on 2024-2025 regulatory landscape:
    - US: SEC frameworks, state-by-state requirements
    - EU: MiCA regulation (effective 2024-2025)
    - UK: FCA registration and marketing rules
    - APAC: Singapore MAS, Hong Kong SFC, Japan JFSA
    """
    # United States
    us_annual: float = Field(
        default=100000, ge=0,
        description="US compliance annual cost (SEC, state licensing)"
    )
    us_geo_blocking_states: list = Field(
        default=["NY", "HI"],
        description="States geo-blocked until licensed"
    )
    
    # European Union (MiCA)
    eu_mica_annual: float = Field(
        default=100000, ge=0,
        description="EU MiCA compliance annual cost"
    )
    eu_casp_license_cost: float = Field(
        default=50000, ge=0,
        description="CASP license application cost (one-time)"
    )
    
    # United Kingdom
    uk_fca_annual: float = Field(
        default=50000, ge=0,
        description="UK FCA registration annual cost"
    )
    
    # Asia Pacific
    apac_annual: float = Field(
        default=100000, ge=0,
        description="APAC regional annual cost (Singapore, HK, Japan)"
    )
    
    # Ongoing costs
    kyc_provider_monthly: float = Field(
        default=2000, ge=0,
        description="KYC provider monthly cost (Jumio, Onfido tier)"
    )
    chainalysis_monthly: float = Field(
        default=3000, ge=0,
        description="Transaction monitoring (Chainalysis/Elliptic)"
    )
    legal_retainer_monthly: float = Field(
        default=5000, ge=0,
        description="Ongoing legal counsel retainer"
    )
    
    @property
    def year1_total(self) -> float:
        """Year 1 total compliance cost (partial year for new regions)"""
        return (
            self.us_annual * 0.5 +  # Partial year
            self.eu_mica_annual * 0.5 +
            self.uk_fca_annual * 0.5 +
            self.apac_annual * 0.25 +  # Later expansion
            (self.kyc_provider_monthly + self.chainalysis_monthly + 
             self.legal_retainer_monthly) * 12
        )
    
    @property
    def year2_total(self) -> float:
        """Year 2+ full compliance cost"""
        return (
            self.us_annual +
            self.eu_mica_annual +
            self.uk_fca_annual +
            self.apac_annual +
            (self.kyc_provider_monthly + self.chainalysis_monthly + 
             self.legal_retainer_monthly) * 12
        )
    
    @property
    def monthly_ongoing(self) -> float:
        """Monthly ongoing costs (providers + retainer)"""
        return (
            self.kyc_provider_monthly +
            self.chainalysis_monthly +
            self.legal_retainer_monthly
        )


# =============================================================================
# FUTURE MODULES (2026-2028) - All disabled by default
# =============================================================================

class VChainParameters(BaseModel):
    """
    VChain cross-chain network parameters.
    
    Launch Timeline: 2027-2028
    A proprietary cross-chain network enabling seamless interaction
    between all major blockchain networks through a unified interface.
    """
    # Module toggle (DISABLED BY DEFAULT)
    enable_vchain: bool = Field(
        default=False,
        description="Enable VChain cross-chain network module"
    )
    
    # Launch timing
    vchain_launch_month: int = Field(
        default=24,  # Month 24 = 2 years after TGE
        ge=12, le=60,
        description="Month when VChain launches (1-60)"
    )
    
    # Transaction fees
    vchain_tx_fee_percent: float = Field(
        default=0.002,  # 0.2%
        ge=0.0005, le=0.01,
        description="Cross-chain transaction fee (0.05%-1%)"
    )
    vchain_min_tx_fee_usd: float = Field(
        default=0.10,
        ge=0,
        description="Minimum transaction fee in USD"
    )
    vchain_max_tx_fee_usd: float = Field(
        default=50.0,
        ge=0,
        description="Maximum transaction fee in USD"
    )
    
    # Bridge fees
    vchain_bridge_fee_percent: float = Field(
        default=0.001,  # 0.1%
        ge=0.0001, le=0.005,
        description="Bridge fee percentage"
    )
    
    # Gas abstraction
    vchain_gas_markup_percent: float = Field(
        default=0.08,  # 8% markup
        ge=0.0, le=0.20,
        description="Markup on gas abstraction"
    )
    
    # Volume projections (VALIDATED: Reduced to realistic Year 1 levels)
    vchain_monthly_tx_volume_usd: float = Field(
        default=25_000_000,  # $25M monthly - realistic Year 1
        ge=0,
        description="Projected monthly cross-chain volume"
    )
    vchain_monthly_bridge_volume_usd: float = Field(
        default=50_000_000,  # $50M monthly - realistic Year 1
        ge=0,
        description="Projected monthly bridge volume"
    )
    
    # Validator economics
    vchain_validator_apy: float = Field(
        default=0.10,  # 10%
        ge=0.0, le=0.30,
        description="Validator staking APY"
    )
    vchain_min_validator_stake: float = Field(
        default=100000,
        ge=0,
        description="Minimum VCoin stake to run validator"
    )
    vchain_validator_count: int = Field(
        default=100,
        ge=10, le=1000,
        description="Target number of validators"
    )
    
    # Enterprise API
    vchain_enterprise_clients: int = Field(
        default=10,
        ge=0, le=1000,
        description="Number of enterprise API clients"
    )
    vchain_avg_enterprise_revenue: float = Field(
        default=5000,  # $5K/month average
        ge=0,
        description="Average enterprise client monthly revenue"
    )


class MarketplaceParameters(BaseModel):
    """
    Marketplace physical/digital goods parameters.
    
    Launch Timeline: 2026-2027
    A full-featured marketplace for physical products, digital goods,
    NFTs, and services with cryptocurrency payments.
    """
    # Module toggle (DISABLED BY DEFAULT)
    enable_marketplace: bool = Field(
        default=False,
        description="Enable Marketplace module"
    )
    
    # Launch timing
    marketplace_launch_month: int = Field(
        default=18,  # Month 18 = 1.5 years after TGE
        ge=6, le=60,
        description="Month when Marketplace launches (1-60)"
    )
    
    # Commission rates (VALIDATED against industry benchmarks Nov 2025)
    # Amazon: 8-15%, eBay: 10-15%, App Store: 30%, Steam: 30%
    marketplace_physical_commission: float = Field(
        default=0.08,  # 8% (industry: 8-15%)
        ge=0.05, le=0.15,
        description="Commission on physical goods sales"
    )
    marketplace_digital_commission: float = Field(
        default=0.15,  # 15% (industry: 15-30%)
        ge=0.08, le=0.25,
        description="Commission on digital goods sales"
    )
    marketplace_nft_commission: float = Field(
        default=0.025,  # 2.5%
        ge=0.01, le=0.10,
        description="Commission on NFT sales"
    )
    marketplace_service_commission: float = Field(
        default=0.08,  # 8%
        ge=0.03, le=0.15,
        description="Commission on service transactions"
    )
    marketplace_max_commission_usd: float = Field(
        default=500,
        ge=0,
        description="Maximum commission per transaction"
    )
    
    # Payment processing
    marketplace_crypto_payment_fee: float = Field(
        default=0.01,  # 1%
        ge=0, le=0.05,
        description="Crypto payment processing fee"
    )
    marketplace_escrow_fee: float = Field(
        default=0.01,  # 1%
        ge=0, le=0.05,
        description="Escrow service fee"
    )
    
    # Volume projections
    marketplace_monthly_gmv_usd: float = Field(
        default=5_000_000,  # $5M GMV monthly
        ge=0,
        description="Projected monthly Gross Merchandise Value"
    )
    marketplace_gmv_physical_percent: float = Field(
        default=0.40,
        ge=0, le=1.0,
        description="Physical goods GMV percentage"
    )
    marketplace_gmv_digital_percent: float = Field(
        default=0.35,
        ge=0, le=1.0,
        description="Digital goods GMV percentage"
    )
    marketplace_gmv_nft_percent: float = Field(
        default=0.10,
        ge=0, le=1.0,
        description="NFT GMV percentage"
    )
    marketplace_gmv_services_percent: float = Field(
        default=0.15,
        ge=0, le=1.0,
        description="Services GMV percentage"
    )
    
    # Seller metrics
    marketplace_active_sellers: int = Field(
        default=1000,
        ge=0,
        description="Number of active sellers"
    )
    marketplace_verified_seller_rate: float = Field(
        default=0.15,  # 15%
        ge=0, le=1.0,
        description="Percentage of verified sellers"
    )
    marketplace_store_subscription_rate: float = Field(
        default=0.10,  # 10%
        ge=0, le=1.0,
        description="Percentage of sellers with store subscriptions"
    )
    
    # Listing fees (in VCoin)
    marketplace_featured_listing_fee: float = Field(
        default=10,
        ge=0,
        description="Featured listing fee in VCoin"
    )
    marketplace_store_subscription_fee: float = Field(
        default=100,
        ge=0,
        description="Monthly store subscription fee in VCoin"
    )
    
    # Advertising
    marketplace_ad_cpc: float = Field(
        default=0.25,  # $0.25 CPC
        ge=0,
        description="Cost per click for sponsored listings"
    )
    marketplace_monthly_ad_clicks: int = Field(
        default=50000,
        ge=0,
        description="Monthly sponsored listing clicks"
    )


class BusinessHubParameters(BaseModel):
    """
    Business Hub freelancer/startup ecosystem parameters.
    
    Launch Timeline: Mid-2027
    A comprehensive business ecosystem for freelancers, startups,
    and established businesses with job matching, funding, and project management.
    """
    # Module toggle (DISABLED BY DEFAULT)
    enable_business_hub: bool = Field(
        default=False,
        description="Enable Business Hub module"
    )
    
    # Launch timing
    business_hub_launch_month: int = Field(
        default=21,  # Month 21 = Mid-2027
        ge=12, le=60,
        description="Month when Business Hub launches (1-60)"
    )
    
    # Freelancer platform
    freelancer_job_posting_fee: float = Field(
        default=20,  # VCoin
        ge=0,
        description="Job posting fee in VCoin"
    )
    # VALIDATED: Upwork 10-20%, Fiverr 20%, Toptal 30-50%
    freelancer_commission_rate: float = Field(
        default=0.12,  # 12% (industry: 10-20%)
        ge=0.08, le=0.20,
        description="Freelancer earnings commission"
    )
    freelancer_escrow_fee: float = Field(
        default=0.02,  # 2%
        ge=0, le=0.05,
        description="Escrow service fee"
    )
    freelancer_monthly_transactions_usd: float = Field(
        default=500_000,  # $500K/month
        ge=0,
        description="Monthly freelance transaction volume"
    )
    freelancer_active_count: int = Field(
        default=5000,
        ge=0,
        description="Active freelancers on platform"
    )
    
    # Startup launchpad
    startup_monthly_registrations: int = Field(
        default=50,
        ge=0,
        description="New startup registrations per month"
    )
    startup_registration_fee: float = Field(
        default=500,  # VCoin
        ge=0,
        description="Startup registration fee in VCoin"
    )
    accelerator_participants: int = Field(
        default=10,
        ge=0,
        description="Monthly accelerator participants"
    )
    accelerator_fee: float = Field(
        default=10000,  # VCoin
        ge=0,
        description="Accelerator program fee in VCoin"
    )
    
    # Funding portal
    funding_portal_monthly_volume: float = Field(
        default=2_000_000,  # $2M raised monthly
        ge=0,
        description="Monthly funding facilitated"
    )
    funding_platform_fee: float = Field(
        default=0.04,  # 4% average
        ge=0.02, le=0.10,
        description="Average funding platform fee"
    )
    investor_network_members: int = Field(
        default=200,
        ge=0,
        description="Investor network members"
    )
    investor_network_fee: float = Field(
        default=5000,  # VCoin/year
        ge=0,
        description="Annual investor network fee in VCoin"
    )
    
    # Project management SaaS
    pm_free_users: int = Field(
        default=10000,
        ge=0,
        description="Free tier project management users"
    )
    pm_professional_users: int = Field(
        default=1000,
        ge=0,
        description="Professional tier users"
    )
    pm_professional_fee: float = Field(
        default=100,  # VCoin/month
        ge=0,
        description="Professional tier monthly fee in VCoin"
    )
    pm_business_users: int = Field(
        default=200,
        ge=0,
        description="Business tier users"
    )
    pm_business_fee: float = Field(
        default=500,  # VCoin/month
        ge=0,
        description="Business tier monthly fee in VCoin"
    )
    pm_enterprise_users: int = Field(
        default=20,
        ge=0,
        description="Enterprise tier users"
    )
    pm_enterprise_fee: float = Field(
        default=2000,  # VCoin/month
        ge=0,
        description="Enterprise tier monthly fee in VCoin"
    )
    
    # Learning academy
    academy_monthly_course_sales: int = Field(
        default=500,
        ge=0,
        description="Monthly course sales"
    )
    academy_avg_course_price: float = Field(
        default=150,  # VCoin
        ge=0,
        description="Average course price in VCoin"
    )
    academy_platform_share: float = Field(
        default=0.30,  # 30% platform, 70% instructor
        ge=0.10, le=0.50,
        description="Platform share of course sales"
    )
    academy_subscription_users: int = Field(
        default=300,
        ge=0,
        description="Monthly subscription users"
    )
    academy_subscription_fee: float = Field(
        default=200,  # VCoin/month
        ge=0,
        description="Monthly academy subscription fee in VCoin"
    )


class CrossPlatformParameters(BaseModel):
    """
    Cross-platform content sharing and account renting parameters.
    
    Launch Timeline: Start of 2027
    A revolutionary feature allowing users to share, syndicate, or rent
    access to social media accounts across platforms.
    """
    # Module toggle (DISABLED BY DEFAULT)
    enable_cross_platform: bool = Field(
        default=False,
        description="Enable Cross-Platform content sharing module"
    )
    
    # Launch timing
    cross_platform_launch_month: int = Field(
        default=15,  # Month 15 = Start of 2027
        ge=6, le=60,
        description="Month when Cross-Platform launches (1-60)"
    )
    
    # Content sharing subscriptions
    cross_platform_creator_tier_fee: float = Field(
        default=100,  # VCoin/month
        ge=0,
        description="Creator tier monthly fee in VCoin"
    )
    cross_platform_professional_tier_fee: float = Field(
        default=300,  # VCoin/month
        ge=0,
        description="Professional tier monthly fee in VCoin"
    )
    cross_platform_agency_tier_fee: float = Field(
        default=1000,  # VCoin/month
        ge=0,
        description="Agency tier monthly fee in VCoin"
    )
    cross_platform_creator_subscribers: int = Field(
        default=2000,
        ge=0,
        description="Creator tier subscribers"
    )
    cross_platform_professional_subscribers: int = Field(
        default=500,
        ge=0,
        description="Professional tier subscribers"
    )
    cross_platform_agency_subscribers: int = Field(
        default=50,
        ge=0,
        description="Agency tier subscribers"
    )
    
    # Account renting
    cross_platform_monthly_rental_volume: float = Field(
        default=500_000,  # $500K monthly rental volume
        ge=0,
        description="Monthly account rental transaction volume"
    )
    # VALIDATED: Similar to influencer/creator platforms 15-20%
    cross_platform_rental_commission: float = Field(
        default=0.15,  # 15% (industry: 15-20%)
        ge=0.10, le=0.25,
        description="Average rental commission rate"
    )
    cross_platform_escrow_fee: float = Field(
        default=0.02,  # 2%
        ge=0, le=0.05,
        description="Escrow fee on rentals"
    )
    cross_platform_active_renters: int = Field(
        default=5000,
        ge=0,
        description="Active account renters"
    )
    cross_platform_active_owners: int = Field(
        default=1000,
        ge=0,
        description="Active account owners renting out"
    )
    
    # Insurance
    cross_platform_insurance_take_rate: float = Field(
        default=0.50,  # 50% of transactions buy insurance
        ge=0, le=1.0,
        description="Percentage of rentals with insurance"
    )
    cross_platform_insurance_rate: float = Field(
        default=0.03,  # 3% average premium
        ge=0, le=0.10,
        description="Average insurance premium rate"
    )
    
    # Verification
    cross_platform_monthly_verifications: int = Field(
        default=200,
        ge=0,
        description="Monthly account verifications"
    )
    cross_platform_verification_fee: float = Field(
        default=50,  # VCoin
        ge=0,
        description="Account verification fee in VCoin"
    )
    cross_platform_premium_verified_users: int = Field(
        default=100,
        ge=0,
        description="Premium verified badge holders"
    )
    cross_platform_premium_verified_fee: float = Field(
        default=500,  # VCoin/year
        ge=0,
        description="Premium verified annual fee in VCoin"
    )
    
    # Analytics
    cross_platform_advanced_analytics_users: int = Field(
        default=300,
        ge=0,
        description="Advanced analytics subscribers"
    )
    cross_platform_analytics_fee: float = Field(
        default=50,  # VCoin/month
        ge=0,
        description="Advanced analytics monthly fee in VCoin"
    )
    cross_platform_api_users: int = Field(
        default=50,
        ge=0,
        description="API access subscribers"
    )
    cross_platform_api_fee: float = Field(
        default=500,  # VCoin/month
        ge=0,
        description="API access monthly fee in VCoin"
    )
    
    # Content licensing
    cross_platform_monthly_license_volume: float = Field(
        default=100_000,  # $100K monthly license volume
        ge=0,
        description="Monthly content licensing volume"
    )
    cross_platform_license_commission: float = Field(
        default=0.20,  # 20%
        ge=0.10, le=0.30,
        description="Content licensing commission"
    )


class ReferralParameters(BaseModel):
    """
    Referral program configuration (2025 Standards).
    
    Tiered rewards system for user acquisition:
    - Starter: 1-10 referrals, 50 VCoin/ref, max 500/mo
    - Builder: 11-50 referrals, 75 VCoin/ref, max 3000/mo
    - Ambassador: 51-200 referrals, 100 VCoin/ref, max 10000/mo
    - Partner: 200+ referrals, negotiated rates
    """
    enable_referral: bool = Field(
        default=True,
        description="Enable referral program in simulation"
    )
    qualification_rate: float = Field(
        default=0.70, ge=0.50, le=0.95,
        description="Percentage of referrals that meet qualification criteria"
    )
    active_referrer_rate: float = Field(
        default=0.15, ge=0.05, le=0.40,
        description="Percentage of users who actively refer others"
    )
    sybil_rejection_rate: float = Field(
        default=0.05, ge=0.01, le=0.20,
        description="Percentage of referrals flagged as sybil attacks"
    )
    starter_bonus_vcoin: float = Field(
        default=50.0, ge=10, le=200,
        description="Bonus per referral for Starter tier"
    )
    builder_bonus_vcoin: float = Field(
        default=75.0, ge=25, le=300,
        description="Bonus per referral for Builder tier"
    )
    ambassador_bonus_vcoin: float = Field(
        default=100.0, ge=50, le=500,
        description="Bonus per referral for Ambassador tier"
    )
    qualification_days: int = Field(
        default=7, ge=3, le=30,
        description="Days referee must be active to qualify"
    )
    min_posts_required: int = Field(
        default=5, ge=1, le=20,
        description="Minimum posts referee must make to qualify"
    )


class PointsParameters(BaseModel):
    """
    Pre-launch points system configuration (2025 Standards).
    
    Points earned before TGE convert to tokens:
    - Pool: 10,000,000 VCoin (1% of supply)
    - Formula: user_tokens = (user_points / total_points) × pool
    """
    enable_points: bool = Field(
        default=True,
        description="Enable pre-launch points system"
    )
    points_pool_tokens: int = Field(
        default=10_000_000, ge=1_000_000, le=50_000_000,
        description="Token pool for points conversion (1% of supply default)"
    )
    participation_rate: float = Field(
        default=0.80, ge=0.50, le=1.0,
        description="Percentage of waitlist that earns points"
    )
    sybil_rejection_rate: float = Field(
        default=0.05, ge=0.01, le=0.20,
        description="Percentage of suspicious accounts rejected"
    )
    waitlist_signup_points: int = Field(
        default=100, ge=50, le=500,
        description="Points for waitlist signup"
    )
    social_follow_points: int = Field(
        default=25, ge=10, le=100,
        description="Points per social platform follow"
    )
    daily_checkin_points: int = Field(
        default=5, ge=1, le=20,
        description="Points for daily check-in"
    )
    invite_join_points: int = Field(
        default=50, ge=20, le=200,
        description="Points when invited friend joins waitlist"
    )
    invite_verify_points: int = Field(
        default=100, ge=50, le=500,
        description="Points when invited friend verifies email"
    )
    beta_testing_points: int = Field(
        default=500, ge=100, le=2000,
        description="Points for beta testing participation"
    )


class GaslessParameters(BaseModel):
    """
    Gasless onboarding configuration (2025 Standards).
    
    Sponsored transactions for seamless UX:
    - New users: First 10 transactions free
    - Verified: 50/month
    - Premium: Unlimited
    """
    enable_gasless: bool = Field(
        default=True,
        description="Enable gasless transaction sponsorship"
    )
    new_user_free_transactions: int = Field(
        default=10, ge=5, le=50,
        description="Free transactions for new users (one-time)"
    )
    verified_user_monthly_transactions: int = Field(
        default=50, ge=20, le=200,
        description="Monthly sponsored transactions for verified users"
    )
    premium_unlimited: bool = Field(
        default=True,
        description="Unlimited sponsored transactions for premium users"
    )
    monthly_sponsorship_budget_usd: float = Field(
        default=5000.0, ge=500, le=100000,
        description="Monthly budget for transaction sponsorship"
    )
    base_transaction_cost_usd: float = Field(
        default=0.00025, ge=0.0001, le=0.01,
        description="Base Solana transaction cost in USD"
    )
    priority_fee_usd: float = Field(
        default=0.0001, ge=0.0, le=0.001,
        description="Optional priority fee in USD"
    )
    account_creation_cost_usd: float = Field(
        default=0.10, ge=0.05, le=0.50,
        description="One-time account rent cost for new users"
    )
    new_user_rate: float = Field(
        default=0.30, ge=0.10, le=0.60,
        description="Percentage of users who are new each month"
    )


class RetentionParameters(BaseModel):
    """
    User retention configuration - Issue #1 fix.
    
    Based on 2024-2025 industry benchmarks:
    - App Annie / data.ai retention reports
    - AppsFlyer State of App Marketing 2024
    - Adjust Mobile App Trends 2024
    """
    model_type: RetentionModelType = Field(
        default=RetentionModelType.SOCIAL_APP,
        description="Which retention curve model to use"
    )
    platform_age_months: int = Field(
        default=6, ge=1, le=120,
        description="Platform age in months (affects cumulative retention)"
    )
    # Custom retention rates (used when model_type = CUSTOM)
    month_1_retention: float = Field(
        default=0.22, ge=0.05, le=0.60,
        description="Month 1 retention rate (Day 30)"
    )
    month_3_retention: float = Field(
        default=0.10, ge=0.02, le=0.40,
        description="Month 3 retention rate"
    )
    month_6_retention: float = Field(
        default=0.06, ge=0.01, le=0.25,
        description="Month 6 retention rate"
    )
    month_12_retention: float = Field(
        default=0.03, ge=0.005, le=0.15,
        description="Month 12 (Year 1) retention rate"
    )


class SimulationParameters(BaseModel):
    """
    Input parameters for the token economy simulation.
    
    All defaults updated to 2024-2025 industry benchmarks.
    """
    
    # === PLATFORM MATURITY (NEW) ===
    platform_maturity: PlatformMaturity = Field(
        default=PlatformMaturity.LAUNCH,
        description="Platform maturity tier (affects realistic ranges)"
    )
    auto_adjust_for_maturity: bool = Field(
        default=True,
        description="Auto-adjust parameters based on maturity tier"
    )
    
    # === RETENTION MODEL (NEW - Issue #1) ===
    retention: RetentionParameters = Field(
        default_factory=RetentionParameters,
        description="User retention configuration"
    )
    apply_retention: bool = Field(
        default=True,
        description="Apply retention model to user calculations"
    )
    
    # === COMPLIANCE COSTS (NEW - Issue #13) ===
    compliance: ComplianceCosts = Field(
        default_factory=ComplianceCosts,
        description="Regulatory and compliance costs"
    )
    regional_compliance: Optional[RegionalComplianceCosts] = Field(
        default=None,
        description="Regional compliance costs by jurisdiction"
    )
    include_compliance_costs: bool = Field(
        default=False,
        description="Include compliance costs in simulation (enable for realistic projections)"
    )
    
    # === FUTURE MODULES (2026-2028) - All disabled by default ===
    vchain: Optional[VChainParameters] = Field(
        default=None,
        description="VChain cross-chain network parameters"
    )
    marketplace: Optional[MarketplaceParameters] = Field(
        default=None,
        description="Marketplace physical/digital goods parameters"
    )
    business_hub: Optional[BusinessHubParameters] = Field(
        default=None,
        description="Business Hub freelancer/startup parameters"
    )
    cross_platform: Optional[CrossPlatformParameters] = Field(
        default=None,
        description="Cross-platform content sharing parameters"
    )
    
    # === PRE-LAUNCH MODULES (NEW - Nov 2025) ===
    referral: Optional[ReferralParameters] = Field(
        default_factory=ReferralParameters,
        description="Referral program parameters"
    )
    points: Optional[PointsParameters] = Field(
        default_factory=PointsParameters,
        description="Pre-launch points system parameters"
    )
    gasless: Optional[GaslessParameters] = Field(
        default_factory=GaslessParameters,
        description="Gasless onboarding parameters"
    )
    
    # === GROWTH SCENARIO SETTINGS (NEW - Nov 2025) ===
    growth_scenario: GrowthScenarioType = Field(
        default=GrowthScenarioType.BASE,
        description="Growth scenario for user projections (conservative, base, bullish)"
    )
    market_condition: MarketConditionType = Field(
        default=MarketConditionType.BULL,
        description="Macro market condition affecting growth (bear, neutral, bull)"
    )
    starting_waitlist_users: int = Field(
        default=1000, ge=100, le=100000,
        description="Number of users on waitlist at token launch"
    )
    enable_fomo_events: bool = Field(
        default=True,
        description="Enable FOMO event triggers (TGE, partnerships, viral moments)"
    )
    use_growth_scenarios: bool = Field(
        default=True,
        description="Use growth scenario projections instead of CAC-based calculations"
    )
    
    # === TOKEN ALLOCATION / VESTING (NEW - Nov 2025) ===
    track_vesting_schedule: bool = Field(
        default=True,
        description="Track full 60-month vesting schedule in monthly progression"
    )
    treasury_revenue_share: float = Field(
        default=0.20, ge=0.0, le=0.50,
        description="Percentage of platform revenue going to Treasury/DAO (20% default)"
    )
    
    # === CORE PARAMETERS ===
    token_price: float = Field(
        default=0.03, ge=0.001, le=1.0, 
        description="VCoin token price in USD"
    )
    marketing_budget: float = Field(
        default=150000, ge=0, 
        description="Monthly marketing budget in USD"
    )
    starting_users: int = Field(
        default=0, ge=0, 
        description="Starting user count (0 = calculate from budget)"
    )
    
    # === USER ACQUISITION (Issue #2 - Realistic CAC) ===
    north_america_budget_percent: float = Field(
        default=0.35, ge=0, le=1, 
        description="% of consumer budget for NA"
    )
    global_low_income_budget_percent: float = Field(
        default=0.65, ge=0, le=1, 
        description="% of consumer budget for global"
    )
    # Updated CAC values based on 2024-2025 data
    # These are ACTIVE USER CAC, not install CAC
    cac_north_america_consumer: float = Field(
        default=75, ge=25, le=200,  # Was $50, now $75
        description="CAC for NA active consumer (not just install)"
    )
    cac_global_low_income_consumer: float = Field(
        default=25, ge=10, le=80,  # Was $12, now $25
        description="CAC for global active consumer (not just install)"
    )
    high_quality_creator_cac: float = Field(
        default=8000, ge=1000, le=50000,  # Was $3000, now $8000
        description="CAC for HQ creators (100K+ followers)"
    )
    mid_level_creator_cac: float = Field(
        default=1500, ge=200, le=10000,  # Was $250, now $1500
        description="CAC for mid-level creators (10K+ followers)"
    )
    high_quality_creators_needed: int = Field(
        default=3, ge=0, le=50,  # Reduced from 5
        description="Number of HQ creators to acquire"
    )
    mid_level_creators_needed: int = Field(
        default=15, ge=0, le=200,  # Reduced from 30
        description="Number of mid-level creators"
    )
    
    # === ECONOMIC PARAMETERS ===
    # Issue #5 - Sustainable token economics (Updated Nov 2025)
    burn_rate: float = Field(
        default=0.05, ge=0, le=0.25,  # Updated: max 25% for aggressive deflation
        description="Burn rate (0-25%, % of collected fees burned)"
    )
    buyback_percent: float = Field(
        default=0.03, ge=0, le=0.25,  # Updated: max 25% for aggressive buybacks
        description="% of USD revenue used to buyback VCoin from market (0-25%)"
    )
    # Issue #3 - Realistic conversion rates
    verification_rate: float = Field(
        default=0.02, ge=0.005, le=0.05,  # Updated: 1.5% -> 2% (better product)
        description="Paid tier conversion rate (realistic 0.5-5%)"
    )
    # Issue #8 - Realistic posting rates
    posts_per_user: float = Field(
        default=0.6, ge=0.1, le=30.0,  # Allow up to 30 posts/month (1 post/day average)
        description="Average posts per user per month (all users)"
    )
    creator_percentage: float = Field(
        default=0.15, ge=0.03, le=0.25,  # Updated: 10% -> 15% (creator-focused)
        description="Percentage of users who create content"
    )
    posts_per_creator: float = Field(
        default=6.0, ge=1.0, le=30.0,  # NEW: Active creators post 6/month
        description="Posts per active creator per month"
    )
    ad_cpm_multiplier: float = Field(
        default=0.20, ge=0.05, le=1.0,  # Updated: 20% fill rate (viable launch)
        description="Ad fill rate (platform maturity dependent)"
    )
    reward_allocation_percent: float = Field(
        default=0.08, ge=0.05, le=0.90, 
        description="% of daily emission allocated for rewards (5-90%)"
    )
    
    # === DYNAMIC REWARD ALLOCATION (NEW - Nov 2025) ===
    enable_dynamic_allocation: bool = Field(
        default=True,
        description="Enable dynamic reward allocation based on user growth"
    )
    initial_users_for_allocation: int = Field(
        default=1000, ge=100, le=100000,
        description="Starting user count for allocation scaling (growth_factor = 0)"
    )
    target_users_for_max_allocation: int = Field(
        default=1_000_000, ge=10000, le=100_000_000,
        description="User count at which maximum allocation (90%) is reached"
    )
    max_per_user_monthly_usd: float = Field(
        default=50.0, ge=1.0, le=500.0,
        description="Maximum per-user monthly reward in USD equivalent (inflation guard)"
    )
    min_per_user_monthly_usd: float = Field(
        default=0.10, ge=0.01, le=10.0,
        description="Minimum per-user monthly reward in USD equivalent"
    )
    
    # === LIQUIDITY PARAMETERS (NEW - Nov 2025) ===
    initial_liquidity_usd: float = Field(
        default=500000, ge=10000, le=10000000,
        description="Initial liquidity pool in USD ($500K recommended for 70%+ health)"
    )
    protocol_owned_liquidity: float = Field(
        default=0.70, ge=0.0, le=1.0,
        description="Protocol-owned liquidity percentage (70% recommended)"
    )
    liquidity_lock_months: int = Field(
        default=24, ge=6, le=60,
        description="Liquidity lock duration in months"
    )
    target_liquidity_ratio: float = Field(
        default=0.15, ge=0.05, le=0.50,
        description="Target liquidity/market cap ratio (15%+ for health)"
    )
    
    # === STAKING PARAMETERS (NEW - Nov 2025) ===
    staking_apy: float = Field(
        default=0.10, ge=0.0, le=0.30,
        description="Annual staking APY (10% default)"
    )
    staking_participation_rate: float = Field(
        default=0.15, ge=0.0, le=0.50,
        description="% of users who stake tokens (15% default, affects Value Accrual)"
    )
    avg_stake_amount: float = Field(
        default=2000, ge=100, le=100000,
        description="Average stake amount per staker in VCoin"
    )
    staker_fee_discount: float = Field(
        default=0.30, ge=0.0, le=0.50,
        description="Fee discount for stakers (30% default)"
    )
    min_stake_amount: float = Field(
        default=100, ge=0,
        description="Minimum stake amount in VCoin"
    )
    stake_lock_days: int = Field(
        default=30, ge=0, le=365,
        description="Minimum stake lock period in days"
    )
    staking_protocol_fee: float = Field(
        default=0.05, ge=0.0, le=0.20,
        description="Protocol fee on staking rewards (5% default)"
    )
    
    # === GOVERNANCE PARAMETERS (NEW - Nov 2025) ===
    governance_proposal_fee: float = Field(
        default=100, ge=0,
        description="Fee to create a governance proposal (VCoin)"
    )
    governance_badge_price: float = Field(
        default=50, ge=0,
        description="Governance badge NFT price (VCoin)"
    )
    governance_premium_fee: float = Field(
        default=100, ge=0,
        description="Premium governance features monthly fee (VCoin)"
    )
    governance_min_vevcoin_to_vote: float = Field(
        default=1.0, ge=0,
        description="Minimum veVCoin to vote"
    )
    governance_min_vevcoin_to_propose: float = Field(
        default=1000.0, ge=0,
        description="Minimum veVCoin to create proposals"
    )
    governance_voting_period_days: int = Field(
        default=7, ge=1, le=30,
        description="Voting period duration in days"
    )
    
    # Governance participation settings (affects Value Accrual)
    governance_participation_rate: float = Field(
        default=0.10, ge=0.0, le=0.50,
        description="% of stakers who actively vote (10% default, affects Value Accrual)"
    )
    governance_delegation_rate: float = Field(
        default=0.20, ge=0.0, le=0.80,
        description="% of non-voters who delegate their votes (20% default)"
    )
    governance_avg_lock_weeks: int = Field(
        default=26, ge=4, le=208,
        description="Average veVCoin lock duration in weeks (26 = 6 months)"
    )
    governance_proposals_per_month: int = Field(
        default=5, ge=0, le=30,
        description="Expected number of governance proposals per month"
    )
    
    # === CREATOR ECONOMY PARAMETERS (NEW - Nov 2025) ===
    # Dynamic Boost Post Fee - scales based on users and token price
    boost_post_target_usd: float = Field(
        default=0.15, ge=0.01, le=5.0,
        description="Target USD value for boost post fee"
    )
    boost_post_min_usd: float = Field(
        default=0.05, ge=0.01, le=1.0,
        description="Minimum boost post fee in USD"
    )
    boost_post_max_usd: float = Field(
        default=0.50, ge=0.05, le=10.0,
        description="Maximum boost post fee in USD"
    )
    boost_post_scale_users: int = Field(
        default=100000, ge=1000, le=10000000,
        description="User count at which boost fee reaches minimum"
    )
    # Other premium features
    premium_dm_fee_vcoin: float = Field(
        default=2, ge=0,
        description="VCoin fee to DM non-followers"
    )
    premium_reaction_fee_vcoin: float = Field(
        default=1, ge=0,
        description="VCoin fee for premium reactions"
    )
    
    # === MODULE TOGGLES ===
    # Core modules (enabled by default)
    enable_identity: bool = Field(default=True, description="Enable Identity verification module")
    enable_content: bool = Field(default=True, description="Enable Content creation module")
    enable_rewards: bool = Field(default=True, description="Enable Rewards distribution module")
    enable_staking: bool = Field(default=True, description="Enable Staking module")
    enable_liquidity: bool = Field(default=True, description="Enable Liquidity tracking module")
    enable_governance: bool = Field(default=True, description="Enable Governance module")
    # Optional modules
    enable_advertising: bool = Field(default=False, description="Enable advertising module")
    enable_exchange: bool = Field(default=True, description="Enable exchange/wallet module")
    enable_nft: bool = Field(default=True, description="Enable NFT features (enabled by default)")
    
    # === IDENTITY MODULE PRICING (USD) ===
    basic_price: float = Field(default=0, ge=0, description="Basic tier monthly price")
    verified_price: float = Field(default=4, ge=0, description="Verified tier monthly price")
    premium_price: float = Field(default=12, ge=0, description="Premium tier monthly price")
    enterprise_price: float = Field(default=59, ge=0, description="Enterprise tier monthly price")
    transfer_fee: float = Field(default=2, ge=0, description="Profile transfer fee")
    sale_commission: float = Field(default=0.10, ge=0, le=0.5, description="Profile sale commission rate")
    # Issue #11 - Realistic profile sales
    monthly_sales: int = Field(
        default=1, ge=0, le=100,  # Was 8, now 1 for launch
        description="Estimated monthly profile sales"
    )
    avg_profile_price: float = Field(
        default=25, ge=5, le=500,  # Was $100, now $25 for launch
        description="Average profile sale price"
    )
    
    # === CONTENT MODULE PRICING (VCoin) ===
    # Issue #12 - NFT reality (Updated Nov 2025)
    nft_mint_fee_vcoin: float = Field(
        default=50, ge=0,  # Updated: 25 -> 50 for better recapture
        description="NFT minting fee in VCoin"
    )
    nft_mint_percentage: float = Field(
        default=0.005, ge=0, le=0.10,  # Updated: 0.5% for visible revenue
        description="% of posts that are NFT mints (balanced for simulation visibility)"
    )
    premium_content_volume_vcoin: float = Field(default=1000, ge=0, description="Monthly premium content volume")
    content_sale_volume_vcoin: float = Field(default=500, ge=0, description="Monthly content sale volume")
    content_sale_commission: float = Field(default=0.10, ge=0, le=0.5, description="Content sale commission")
    
    # === ADVERTISING MODULE PRICING (USD) - Updated Nov 2025 ===
    banner_cpm: float = Field(
        default=0.50, ge=0.05, le=20,  # Updated: $0.50 (viable launch)
        description="Banner ad CPM (maturity dependent)"
    )
    video_cpm: float = Field(
        default=2.00, ge=0.10, le=50,  # Updated: $2.00 (viable launch)
        description="Video ad CPM (maturity dependent)"
    )
    promoted_post_fee: float = Field(default=1.00, ge=0, description="Promoted post fee")
    campaign_management_fee: float = Field(default=20, ge=0, description="Campaign management fee")
    ad_analytics_fee: float = Field(default=15, ge=0, description="Ad analytics subscription fee")
    
    # === EXCHANGE/WALLET MODULE - Issue #4 (Updated Nov 2025) ===
    exchange_swap_fee_percent: float = Field(
        default=0.005, ge=0, le=0.05,  # 0.5% swap fee (industry standard)
        description="Swap/exchange fee (0.5% default)"
    )
    exchange_withdrawal_fee: float = Field(
        default=1.50, ge=0, 
        description="Flat withdrawal fee in USD"
    )
    exchange_user_adoption_rate: float = Field(
        default=0.10, ge=0.01, le=0.30,  # Updated: 5% -> 10% for token platform
        description="% of users who use exchange features"
    )
    exchange_avg_monthly_volume: float = Field(
        default=150, ge=0, le=2000,  # Updated: $100 -> $150 for token platform
        description="Avg monthly trading volume per active user (USD)"
    )
    exchange_withdrawals_per_user: float = Field(
        default=0.5, ge=0, le=5,  # Was 0.4, now 0.5
        description="Avg monthly withdrawals per active user"
    )
    
    # === REWARD DISTRIBUTION ===
    text_post_points: float = Field(default=3, ge=0, description="Points for text posts")
    image_post_points: float = Field(default=6, ge=0, description="Points for image posts")
    audio_post_points: float = Field(default=10, ge=0, description="Points for audio posts")
    short_video_points: float = Field(default=15, ge=0, description="Points for short videos")
    post_videos_points: float = Field(default=25, ge=0, description="Points for long videos")
    music_points: float = Field(default=20, ge=0, description="Points for music")
    podcast_points: float = Field(default=30, ge=0, description="Points for podcasts")
    audio_book_points: float = Field(default=45, ge=0, description="Points for audio books")
    like_points: float = Field(default=0.2, ge=0, description="Points for likes")
    comment_points: float = Field(default=2, ge=0, description="Points for comments")
    share_points: float = Field(default=3, ge=0, description="Points for shares")
    follow_points: float = Field(default=0.5, ge=0, description="Points for follows")
    max_posts_per_day: int = Field(default=15, ge=1, description="Max posts per day (anti-bot)")
    max_likes_per_day: int = Field(default=50, ge=1, description="Max likes per day (anti-bot)")
    max_comments_per_day: int = Field(default=30, ge=1, description="Max comments per day (anti-bot)")
    high_quality_multiplier: float = Field(default=1.5, ge=1, description="Quality multiplier for HQ content")
    verified_multiplier: float = Field(default=1.15, ge=1, description="Multiplier for verified users")
    premium_multiplier: float = Field(default=1.3, ge=1, description="Multiplier for premium users")
    day_7_decay: int = Field(default=40, ge=0, le=100, description="Content decay at day 7 (%)")
    day_30_decay: int = Field(default=8, ge=0, le=100, description="Content decay at day 30 (%)")
    max_daily_reward_usd: float = Field(default=15, ge=1, description="Max daily reward per user in USD")

    # === VALIDATION ===
    @field_validator('burn_rate', 'buyback_percent')
    @classmethod
    def validate_deflation_rates(cls, v: float) -> float:
        """Ensure individual deflation rates are within limits"""
        if v > 0.25:
            raise ValueError("Individual burn/buyback rate cannot exceed 25%")
        return v
    
    @model_validator(mode='after')
    def validate_combined_deflation(self) -> 'SimulationParameters':
        """
        Issue #5 fix: Ensure combined burn + buyback is sustainable.
        Total deflation > 50% is extremely aggressive but allowed for simulation.
        """
        total_deflation = self.burn_rate + self.buyback_percent
        if total_deflation > 0.50:
            raise ValueError(
                f"Combined burn ({self.burn_rate*100}%) + buyback ({self.buyback_percent*100}%) "
                f"= {total_deflation*100}% exceeds maximum of 50%"
            )
        return self
    
    def get_maturity_adjustments(self) -> dict:
        """Get parameter adjustments for current maturity tier"""
        return MATURITY_ADJUSTMENTS.get(self.platform_maturity, {})
    
    def get_effective_conversion_rate(self) -> float:
        """Get conversion rate adjusted for platform maturity"""
        if not self.auto_adjust_for_maturity:
            return self.verification_rate
        
        adjustments = self.get_maturity_adjustments()
        return adjustments.get('conversion_rate', self.verification_rate)
    
    def get_effective_ad_fill_rate(self) -> float:
        """Get ad fill rate adjusted for platform maturity"""
        if not self.auto_adjust_for_maturity:
            return self.ad_cpm_multiplier
        
        adjustments = self.get_maturity_adjustments()
        return adjustments.get('ad_fill_rate', self.ad_cpm_multiplier)
    
    def get_effective_cpm(self) -> tuple:
        """Get CPM rates adjusted for platform maturity"""
        if not self.auto_adjust_for_maturity:
            return (self.banner_cpm, self.video_cpm)
        
        adjustments = self.get_maturity_adjustments()
        return (
            adjustments.get('banner_cpm', self.banner_cpm),
            adjustments.get('video_cpm', self.video_cpm)
        )
    
    def get_future_modules_enabled(self) -> list:
        """Return list of enabled future modules"""
        enabled = []
        if self.vchain and self.vchain.enable_vchain:
            enabled.append('vchain')
        if self.marketplace and self.marketplace.enable_marketplace:
            enabled.append('marketplace')
        if self.business_hub and self.business_hub.enable_business_hub:
            enabled.append('business_hub')
        if self.cross_platform and self.cross_platform.enable_cross_platform:
            enabled.append('cross_platform')
        return enabled
    
    def get_total_compliance_monthly(self) -> float:
        """Get total monthly compliance cost including regional"""
        total = 0.0
        if self.include_compliance_costs:
            total += self.compliance.monthly_total
            if self.regional_compliance:
                total += self.regional_compliance.monthly_ongoing
        return total

    class Config:
        populate_by_name = True


class MonteCarloOptions(BaseModel):
    """Options for Monte Carlo simulation"""
    parameters: SimulationParameters
    iterations: int = Field(default=1000, ge=100, le=10000, description="Number of iterations")


class AgentBasedOptions(BaseModel):
    """Options for Agent-Based simulation"""
    parameters: SimulationParameters
    agent_count: int = Field(default=1000, ge=100, le=10000, description="Number of agents")
    duration_months: int = Field(default=12, ge=1, le=60, description="Simulation duration in months")


class MonthlyProgressionOptions(BaseModel):
    """Options for Monthly Progression simulation (NEW - Issue #16)"""
    parameters: SimulationParameters
    duration_months: int = Field(default=24, ge=6, le=60, description="Projection duration in months")
    include_seasonality: bool = Field(default=True, description="Apply seasonal adjustments")
    market_saturation_factor: float = Field(
        default=0.0, ge=0, le=1.0,
        description="Market saturation (0=virgin market, 1=saturated)"
    )
    # Growth scenario overrides (use parameters.growth_scenario if not specified)
    use_growth_scenarios: bool = Field(
        default=True,
        description="Use growth scenario projections instead of CAC-based calculations"
    )
