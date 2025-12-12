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
        'staking_participation': 0.10,  # 10% stake tokens (WhitePaper)
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
        'staking_participation': 0.10,  # 10% stake tokens (WhitePaper)
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
        'staking_participation': 0.10,  # 10% stake tokens (WhitePaper)
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


class FiveAStarConfig(BaseModel):
    """
    Configuration for a single 5A star pillar.
    
    Each star (Identity, Accuracy, Agility, Activity, Approved) can be configured
    with its own weight, tier thresholds, and behavior factors.
    """
    weight: float = Field(
        default=0.20, ge=0.0, le=1.0,
        description="Weight of this star in compound calculations (0.0-1.0)"
    )
    tier_thresholds: list = Field(
        default=[30, 60, 90],
        description="Thresholds for Bronze(<30)/Silver(<60)/Gold(<90)/Diamond(90+)"
    )
    avg_percentage: float = Field(
        default=50.0, ge=0.0, le=100.0,
        description="Average percentage for this star across user population"
    )
    std_deviation: float = Field(
        default=20.0, ge=0.0, le=50.0,
        description="Standard deviation for star distribution"
    )
    min_percentage: float = Field(
        default=0.0, ge=0.0, le=100.0,
        description="Minimum percentage a user can have for this star (0% = can earn nothing)"
    )
    max_percentage: float = Field(
        default=100.0, ge=0.0, le=100.0,
        description="Maximum percentage a user can have for this star"
    )


class FiveAPolicyParameters(BaseModel):
    """
    5A Policy gamification configuration.
    
    The 5A Policy evaluates users on 5 pillars:
    1. Identity (Authenticity/Authority) - KYC level, profile completeness, verification status
    2. Accuracy (Honesty) - Content quality, factual accuracy, report accuracy
    3. Agility - Response time, engagement speed, adaptability
    4. Activity - Daily actions, posting frequency, platform engagement
    5. Approved (Liability) - Reputation score, community standing, trust level
    
    LINEAR FORMULA (December 2025):
    - multiplier = (average_stars / 100) * 2.0
    - 0% average = 0x multiplier (earn nothing)
    - 50% average = 1x multiplier (neutral baseline)
    - 100% average = 2x multiplier (earn double)
    
    REALISTIC DISTRIBUTION (Based on 90-9-1 Rule):
    - Lurkers (60%): Low activity, minimal engagement
    - Casual (25%): Weekly activity, some engagement
    - Active (12%): Daily activity, regular posting
    - Power Users (3%): High creators, verified, engaged
    """
    enable_five_a: bool = Field(
        default=True,
        description="Enable 5A Policy gamification system"
    )
    
    # Use segment-based distribution for realistic simulation
    use_segments: bool = Field(
        default=True,
        description="Use 4-segment user model (Lurkers/Casual/Active/Power) instead of uniform distribution"
    )
    
    # Segment percentages (must sum to 100%)
    segment_lurkers_percent: float = Field(
        default=0.60, ge=0.0, le=1.0,
        description="Percentage of users who are lurkers (view only, minimal interaction)"
    )
    segment_casual_percent: float = Field(
        default=0.25, ge=0.0, le=1.0,
        description="Percentage of users who are casual (weekly activity)"
    )
    segment_active_percent: float = Field(
        default=0.12, ge=0.0, le=1.0,
        description="Percentage of users who are active (daily activity)"
    )
    segment_power_percent: float = Field(
        default=0.03, ge=0.0, le=1.0,
        description="Percentage of users who are power users (top creators)"
    )
    
    # Per-star configuration - REALISTIC DEFAULTS based on research
    # These represent population-weighted averages across all segments
    identity_star: FiveAStarConfig = Field(
        default_factory=lambda: FiveAStarConfig(
            weight=0.25, avg_percentage=38.0, std_deviation=25.0
        ),
        description="Identity (Authority) - Most users don't complete KYC fully"
    )
    accuracy_star: FiveAStarConfig = Field(
        default_factory=lambda: FiveAStarConfig(
            weight=0.20, avg_percentage=52.0, std_deviation=20.0
        ),
        description="Accuracy (Honesty) - Content quality varies widely"
    )
    agility_star: FiveAStarConfig = Field(
        default_factory=lambda: FiveAStarConfig(
            weight=0.15, avg_percentage=35.0, std_deviation=22.0
        ),
        description="Agility - Response time skewed by lurkers"
    )
    activity_star: FiveAStarConfig = Field(
        default_factory=lambda: FiveAStarConfig(
            weight=0.25, avg_percentage=28.0, std_deviation=28.0
        ),
        description="Activity - 60% lurkers drag down average significantly"
    )
    approved_star: FiveAStarConfig = Field(
        default_factory=lambda: FiveAStarConfig(
            weight=0.15, avg_percentage=58.0, std_deviation=18.0
        ),
        description="Approved (Liability) - Most users maintain basic standing"
    )
    
    # Linear multiplier settings (0x to 2x scale)
    compound_base: float = Field(
        default=1.0, ge=0.1, le=2.0,
        description="(Legacy) Base multiplier - ignored in linear formula"
    )
    compound_exponent: float = Field(
        default=1.5, ge=0.5, le=3.0,
        description="(Legacy) Exponent - ignored in linear formula"
    )
    min_multiplier: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Minimum multiplier at 0% stars (0x = earn nothing)"
    )
    max_multiplier: float = Field(
        default=2.0, ge=1.0, le=10.0,
        description="Maximum multiplier at 100% stars (2x = earn double)"
    )
    
    # Module impact settings
    reward_impact_weight: float = Field(
        default=1.0, ge=0.0, le=2.0,
        description="How strongly 5A affects reward distribution (0=none, 1=full, 2=double)"
    )
    staking_apy_bonus_max: float = Field(
        default=0.50, ge=0.0, le=1.0,
        description="Maximum staking APY bonus for top performers (0.50 = +50%)"
    )
    governance_power_bonus_max: float = Field(
        default=0.50, ge=0.0, le=1.0,
        description="Maximum governance power bonus for top performers"
    )
    fee_discount_max: float = Field(
        default=0.50, ge=0.0, le=0.90,
        description="Maximum fee discount for high 5A users (0.50 = 50% off)"
    )
    content_visibility_bonus_max: float = Field(
        default=0.50, ge=0.0, le=2.0,
        description="Maximum content visibility boost for high 5A creators"
    )
    
    # Evolution settings (for monthly progression)
    monthly_improvement_rate: float = Field(
        default=0.02, ge=0.0, le=0.10,
        description="Average monthly improvement in star ratings for active users"
    )
    inactivity_decay_rate: float = Field(
        default=0.05, ge=0.0, le=0.20,
        description="Monthly decay rate for inactive users' star ratings"
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


class OrganicGrowthParameters(BaseModel):
    """
    Organic user growth configuration (December 2025).
    
    Models natural user acquisition through:
    - Word-of-mouth (K-factor: 0.15-0.25 for social/crypto apps)
    - App store discovery (0.5-1% monthly organic downloads)
    - Network effects (logarithmic scaling with user base)
    - Social sharing and content virality
    - Referral participation (8-15% of users refer others)
    
    Based on industry research:
    - Monthly organic growth: 2-5% (conservative), 5-10% (base), 10-15% (bullish)
    - Finance apps: 27% YoY growth, crypto apps: 45% session surge
    - Network effects: Dampened Metcalfe's Law (n^1.2 vs n^2)
    - Viral coefficient: 0.15-0.25 typical for consumer apps
    
    Sources:
    - App Annie/data.ai Mobile Trends 2024-2025
    - Y Combinator startup metrics
    - Blockchain gaming elasticity research (~2.4x)
    """
    enable_organic_growth: bool = Field(
        default=False,
        description="Enable organic user growth module (OFF by default)"
    )
    
    # Base growth rate
    base_monthly_growth_rate: float = Field(
        default=0.08, ge=0.0, le=0.25,
        description="Base monthly organic growth rate (8% = realistic for social/crypto, 5% conservative, 15% bullish)"
    )
    
    # Word-of-mouth / viral coefficient
    word_of_mouth_coefficient: float = Field(
        default=0.35, ge=0.0, le=1.0,
        description="K-factor: users acquired per referrer per month (0.35 = social platforms, WhatsApp had 0.6+)"
    )
    
    # App store organic discovery
    app_store_discovery_rate: float = Field(
        default=0.015, ge=0.0, le=0.05,
        description="Monthly organic app store discovery rate (1.5% = realistic with good ASO, scales with reviews)"
    )
    
    # Network effects
    network_effect_strength: float = Field(
        default=0.60, ge=0.0, le=1.0,
        description="Network effect strength (0.60 = strong social platform, 0.35 = dampened, 1.0 = full Metcalfe's)"
    )
    
    # User participation rates
    referral_participation_rate: float = Field(
        default=0.18, ge=0.0, le=0.40,
        description="Percentage of users who refer others (18% = social/crypto apps, scales to 25% at larger user bases)"
    )
    
    social_sharing_rate: float = Field(
        default=0.12, ge=0.0, le=0.30,
        description="Percentage of users who share on social media (12% = realistic, increases with engagement)"
    )
    
    # Content virality
    content_virality_factor: float = Field(
        default=0.25, ge=0.0, le=1.0,
        description="Content-driven viral growth factor (25% = social platform, content is growth engine)"
    )
    
    # Growth phase modifiers
    early_stage_boost: float = Field(
        default=1.5, ge=1.0, le=3.0,
        description="Organic growth boost for early stage (months 1-6), 1.5x = 50% boost from launch excitement"
    )
    
    maturity_dampening: float = Field(
        default=0.85, ge=0.5, le=1.2,
        description="Growth factor at maturity (0.85 = slight reduction, social platforms stay strong due to network effects)"
    )
    
    # Seasonal adjustments
    apply_seasonality: bool = Field(
        default=True,
        description="Apply seasonal adjustments (Q4 boost, summer dip)"
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
    
    # === 5A POLICY GAMIFICATION (Dec 2025) ===
    five_a: Optional[FiveAPolicyParameters] = Field(
        default_factory=FiveAPolicyParameters,
        description="5A Policy gamification parameters (Identity, Accuracy, Agility, Activity, Approved)"
    )
    
    # === ORGANIC USER GROWTH (Dec 2025) ===
    organic_growth: Optional[OrganicGrowthParameters] = Field(
        default_factory=OrganicGrowthParameters,
        description="Organic user growth parameters (word-of-mouth, app store, network effects)"
    )
    
    # === GROWTH SCENARIO SETTINGS (NEW - Nov 2025) ===
    growth_scenario: GrowthScenarioType = Field(
        default=GrowthScenarioType.BASE,
        description="Growth scenario for user projections (conservative, base, bullish)"
    )
    market_condition: MarketConditionType = Field(
        default=MarketConditionType.NEUTRAL,
        description="Macro market condition affecting growth (bear, neutral, bull)"
    )
    starting_waitlist_users: int = Field(
        default=2000, ge=100, le=100000,
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
        description="Total annual marketing budget in USD (distributed over 12 months if use_distributed_marketing_budget=True)"
    )
    use_distributed_marketing_budget: bool = Field(
        default=True,
        description="Distribute marketing budget over 12 months (50% in first 3 months) instead of all at once"
    )
    marketing_budget_distribution_months: Optional[list] = Field(
        default=None,
        description="Custom monthly budget distribution (12 values). If None, uses default distribution: 50% in first 3 months"
    )
    # === MULTI-YEAR MARKETING BUDGET (Dec 2025) ===
    # Marketing budget multipliers for years 2-5 (each year doubles the previous by default)
    marketing_budget_year2_multiplier: float = Field(
        default=2.0, ge=0.0, le=10.0,
        description="Year 2 marketing budget as multiplier of Year 1 (2.0 = 2x Year 1)"
    )
    marketing_budget_year3_multiplier: float = Field(
        default=2.0, ge=0.0, le=10.0,
        description="Year 3 marketing budget as multiplier of Year 2 (2.0 = 2x Year 2 = 4x Y1)"
    )
    marketing_budget_year4_multiplier: float = Field(
        default=2.0, ge=0.0, le=10.0,
        description="Year 4 marketing budget as multiplier of Year 3 (2.0 = 2x Year 3 = 8x Y1)"
    )
    marketing_budget_year5_multiplier: float = Field(
        default=2.0, ge=0.0, le=10.0,
        description="Year 5 marketing budget as multiplier of Year 4 (2.0 = 2x Year 4 = 16x Y1)"
    )
    # === USER GROWTH PRICE IMPACT (Dec 2025) ===
    # Based on research: blockchain gaming shows ~2.4x elasticity, but with dampening
    # Friend.tech showed strong correlation but pure Metcalfe's Law is overstated
    enable_user_growth_price_impact: bool = Field(
        default=True,
        description="Enable token price adjustment based on user growth (network effects)"
    )
    user_growth_price_elasticity: float = Field(
        default=0.35, ge=0.0, le=1.0,
        description="How much user growth affects token price (0.35 = 35% of growth translates to price appreciation)"
    )
    user_growth_price_max_multiplier: float = Field(
        default=3.0, ge=1.0, le=10.0,
        description="Maximum price multiplier from user growth alone (cap to prevent unrealistic projections)"
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
        default=3000, ge=1000, le=50000,
        description="CAC for HQ creators (100K+ followers)"
    )
    mid_level_creator_cac: float = Field(
        default=500, ge=200, le=10000,
        description="CAC for mid-level creators (10K+ followers)"
    )
    high_quality_creators_needed: int = Field(
        default=5, ge=0, le=50,
        description="Number of HQ creators to acquire"
    )
    mid_level_creators_needed: int = Field(
        default=15, ge=0, le=200,  # Reduced from 30
        description="Number of mid-level creators"
    )
    
    # === ECONOMIC PARAMETERS ===
    # Issue #5 - Sustainable token economics (Updated Nov 2025)
    burn_rate: float = Field(
        default=0.10, ge=0, le=0.25,  # 10% burn rate for recapture
        description="Burn rate (0-25%, % of collected fees burned)"
    )
    buyback_percent: float = Field(
        default=0.10, ge=0, le=0.25,  # 10% buyback for recapture
        description="% of USD revenue used to buyback VCoin from market (0-25%)"
    )
    # Issue #3 - Realistic conversion rates
    verification_rate: float = Field(
        default=0.02, ge=0.005, le=0.05,  # Updated: 1.5% -> 2% (better product)
        description="Paid tier conversion rate (realistic 0.5-5%)"
    )
    # Issue #8 - Realistic posting rates
    posts_per_user: float = Field(
        default=9.7, ge=0.1, le=30.0,  # Posts per user per month
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
    # MED-001 Fix: Renamed from ad_cpm_multiplier to ad_fill_rate for clarity
    # The parameter name was confusing - it's not a CPM multiplier, it's the fill rate
    ad_fill_rate: float = Field(
        default=0.20, ge=0.05, le=1.0,  # Updated: 20% fill rate (viable launch)
        description="Ad fill rate - percentage of ad inventory that gets filled (platform maturity dependent)"
    )
    # Backward compatibility alias (deprecated)
    @property
    def ad_cpm_multiplier(self) -> float:
        """Deprecated: Use ad_fill_rate instead. This alias exists for backward compatibility."""
        return self.ad_fill_rate
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
        default=100_000_000, ge=10000, le=100_000_000,
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
    # MED-03: Configurable liquidity pool distribution
    liquidity_pool_usdc_percent: float = Field(
        default=0.40, ge=0.0, le=1.0,
        description="Percentage of liquidity in VCoin/USDC pool (40% default)"
    )
    liquidity_pool_sol_percent: float = Field(
        default=0.35, ge=0.0, le=1.0,
        description="Percentage of liquidity in VCoin/SOL pool (35% default)"
    )
    liquidity_pool_usdt_percent: float = Field(
        default=0.25, ge=0.0, le=1.0,
        description="Percentage of liquidity in VCoin/USDT pool (25% default)"
    )
    # MED-004 Fix: Make CLMM concentration factor configurable
    # Previously hardcoded to 4.0/3.0/2.0 based on liquidity level
    # Real CLMM efficiency depends on price range: Narrow=10-20x, Wide=2-3x, Full=1x
    clmm_concentration_factor: float = Field(
        default=4.0, ge=1.0, le=20.0,
        description="CLMM capital efficiency multiplier (1x=full range, 4x=typical, 10-20x=narrow range)"
    )
    
    # === STAKING PARAMETERS (NEW - Nov 2025) ===
    staking_apy: float = Field(
        default=0.07, ge=0.0, le=0.30,
        description="Annual staking APY (7% default - budget constrained)"
    )
    staking_participation_rate: float = Field(
        default=0.10, ge=0.0, le=0.50,
        description="% of users who stake tokens (10% default, affects Value Accrual)"
    )
    avg_stake_amount: float = Field(
        default=20000, ge=100, le=100000,
        description="Average stake amount per staker in VCoin"
    )
    staker_fee_discount: float = Field(
        default=0.10, ge=0.0, le=0.50,
        description="Fee discount for stakers (10% default)"
    )
    min_stake_amount: float = Field(
        default=1000, ge=0,
        description="Minimum stake amount in VCoin"
    )
    stake_lock_days: int = Field(
        default=180, ge=0, le=365,
        description="Minimum stake lock period in days (6 months)"
    )
    staking_protocol_fee: float = Field(
        default=0.05, ge=0.0, le=0.20,
        description="Protocol fee on staking rewards (5% default)"
    )
    
    # === GAME THEORY PARAMETERS (Issue #5, #6 Fix - Dec 2025) ===
    # Used in game theory analysis for staking equilibrium calculations
    lock_period_months: int = Field(
        default=3, ge=1, le=24,
        description="Lock period for staking in months (affects game theory analysis)"
    )
    early_unstake_penalty: float = Field(
        default=0.10, ge=0.0, le=0.50,
        description="Penalty for early unstaking as percentage (10% default)"
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
        default=3.0, ge=0.01, le=10.0,
        description="Target USD value for boost post fee"
    )
    boost_post_min_usd: float = Field(
        default=1.0, ge=0.01, le=5.0,
        description="Minimum boost post fee in USD"
    )
    boost_post_max_usd: float = Field(
        default=5.0, ge=0.05, le=10.0,
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
    enable_advertising: bool = Field(default=True, description="Enable advertising module")
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
    # NOTE: content_sale_commission was removed - Content module is break-even by design (creators keep 100%)
    
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
    # MED-04: Configurable average swap size
    exchange_avg_swap_size: float = Field(
        default=30.0, ge=1.0, le=1000.0,
        description="Average swap size in USD for swap count calculations"
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
            return self.ad_fill_rate
        
        adjustments = self.get_maturity_adjustments()
        return adjustments.get('ad_fill_rate', self.ad_fill_rate)
    
    def get_effective_cpm(self) -> tuple:
        """Get CPM rates adjusted for platform maturity"""
        if not self.auto_adjust_for_maturity:
            return (self.banner_cpm, self.video_cpm)
        
        adjustments = self.get_maturity_adjustments()
        return (
            adjustments.get('banner_cpm', self.banner_cpm),
            adjustments.get('video_cpm', self.video_cpm)
        )
    
    # Issue #7 Fix: Add maturity-adjusted profile marketplace getters
    def get_effective_monthly_sales(self) -> int:
        """Get monthly profile sales adjusted for platform maturity"""
        if not self.auto_adjust_for_maturity:
            return self.monthly_sales
        
        adjustments = self.get_maturity_adjustments()
        return adjustments.get('profile_sales_monthly', self.monthly_sales)
    
    def get_effective_avg_profile_price(self) -> float:
        """Get average profile price adjusted for platform maturity"""
        if not self.auto_adjust_for_maturity:
            return self.avg_profile_price
        
        adjustments = self.get_maturity_adjustments()
        return adjustments.get('avg_profile_price', self.avg_profile_price)
    
    def get_effective_nft_percentage(self) -> float:
        """Get NFT minting percentage adjusted for platform maturity"""
        if not self.auto_adjust_for_maturity:
            return self.nft_mint_percentage
        
        adjustments = self.get_maturity_adjustments()
        return adjustments.get('nft_percentage', self.nft_mint_percentage)
    
    def get_effective_creator_percentage(self) -> float:
        """Get creator percentage adjusted for platform maturity"""
        creator_pct = getattr(self, 'creator_percentage', 0.10)
        if not self.auto_adjust_for_maturity:
            return creator_pct
        
        adjustments = self.get_maturity_adjustments()
        return adjustments.get('creator_percentage', creator_pct)
    
    def get_effective_staking_participation(self) -> float:
        """
        Get staking participation rate adjusted for platform maturity.
        
        HIGH-04 Fix: Staking participation varies by platform maturity:
        - Launch: 8% (early adopters only)
        - Growing: 12% (building community)
        - Established: 20% (mature ecosystem)
        
        Returns:
            Effective staking participation rate (0.0-1.0)
        """
        if not self.auto_adjust_for_maturity:
            return self.staking_participation_rate
        
        adjustments = self.get_maturity_adjustments()
        return adjustments.get('staking_participation', self.staking_participation_rate)
    
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
    
    def get_marketing_budget_for_year(self, year: int) -> float:
        """
        Get marketing budget for a specific year (1-5).
        
        Budget scales based on multipliers (each year doubles the previous by default):
        - Year 1: Base marketing_budget
        - Year 2: Year 1 * marketing_budget_year2_multiplier (default 2x)
        - Year 3: Year 2 * marketing_budget_year3_multiplier (default 2x = 4x of Y1)
        - Year 4: Year 3 * marketing_budget_year4_multiplier (default 2x = 8x of Y1)
        - Year 5: Year 4 * marketing_budget_year5_multiplier (default 2x = 16x of Y1)
        
        Args:
            year: Year number (1-5)
        
        Returns:
            Annual marketing budget for the specified year in USD
        """
        if year <= 0:
            return 0.0
        if year == 1:
            return self.marketing_budget
        
        # Calculate cumulative multiplier
        year1_budget = self.marketing_budget
        year2_budget = year1_budget * self.marketing_budget_year2_multiplier
        
        if year == 2:
            return year2_budget
        
        year3_budget = year2_budget * self.marketing_budget_year3_multiplier
        if year == 3:
            return year3_budget
        
        year4_budget = year3_budget * self.marketing_budget_year4_multiplier
        if year == 4:
            return year4_budget
        
        year5_budget = year4_budget * self.marketing_budget_year5_multiplier
        if year >= 5:
            return year5_budget
        
        return 0.0
    
    def get_marketing_budget_for_month(self, month: int) -> float:
        """
        Get marketing budget for a specific month (1-60).
        
        Distributes the yearly budget across 12 months using the same
        distribution pattern as Year 1 (50% in first 3 months of each year).
        
        Args:
            month: Month number (1-60)
        
        Returns:
            Monthly marketing budget in USD
        """
        if month <= 0 or month > 60:
            return 0.0
        
        # Determine which year this month belongs to
        year = ((month - 1) // 12) + 1
        month_in_year = ((month - 1) % 12) + 1
        
        # Get annual budget for this year
        annual_budget = self.get_marketing_budget_for_year(year)
        
        if not self.use_distributed_marketing_budget:
            # Evenly distributed
            return annual_budget / 12
        
        # Use distribution pattern (50% in first 3 months)
        distribution = {
            1: 0.2333, 2: 0.1667, 3: 0.1000,
            4: 0.0667, 5: 0.0667, 6: 0.0667,
            7: 0.0556, 8: 0.0556, 9: 0.0556,
            10: 0.0444, 11: 0.0444, 12: 0.0444,
        }
        
        return annual_budget * distribution.get(month_in_year, 0)

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
