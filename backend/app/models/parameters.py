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
    include_compliance_costs: bool = Field(
        default=False,
        description="Include compliance costs in simulation (enable for realistic projections)"
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
        default=0.05, ge=0, le=0.10,  # Updated: 3% -> 5% for better recapture
        description="Burn rate (0-10%, sustainable deflation)"
    )
    buyback_percent: float = Field(
        default=0.03, ge=0, le=0.10,  # Updated: 2% -> 3% for better recapture
        description="Buyback percentage (0-10%)"
    )
    # Issue #3 - Realistic conversion rates
    verification_rate: float = Field(
        default=0.02, ge=0.005, le=0.05,  # Updated: 1.5% -> 2% (better product)
        description="Paid tier conversion rate (realistic 0.5-5%)"
    )
    # Issue #8 - Realistic posting rates
    posts_per_user: float = Field(
        default=0.6, ge=0.1, le=5.0,  # Was 3, now 0.6 (10% create × 6 posts)
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
        default=100000, ge=10000, le=10000000,
        description="Initial liquidity pool in USD (minimum $100K recommended)"
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
    
    # === CREATOR ECONOMY PARAMETERS (NEW - Nov 2025) ===
    platform_creator_fee: float = Field(
        default=0.05, ge=0.0, le=0.20,
        description="Platform fee on creator earnings (5% default)"
    )
    boost_post_fee_vcoin: float = Field(
        default=5, ge=0,
        description="VCoin fee to boost a post"
    )
    premium_dm_fee_vcoin: float = Field(
        default=2, ge=0,
        description="VCoin fee to DM non-followers"
    )
    premium_reaction_fee_vcoin: float = Field(
        default=1, ge=0,
        description="VCoin fee for premium reactions"
    )
    
    # === MODULE TOGGLES ===
    enable_advertising: bool = Field(default=False, description="Enable advertising module")
    enable_messaging: bool = Field(default=False, description="Enable messaging module")
    enable_community: bool = Field(default=False, description="Enable community module")
    enable_exchange: bool = Field(default=True, description="Enable exchange/wallet module")
    enable_nft: bool = Field(default=False, description="Enable NFT features")  # Issue #12
    
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
    # Note: Small fees on media help recapture tokens and generate revenue
    text_post_fee_vcoin: float = Field(default=0, ge=0, description="Text post fee in VCoin (keep free)")
    image_post_fee_vcoin: float = Field(default=0.5, ge=0, description="Image post fee in VCoin")
    video_post_fee_vcoin: float = Field(default=1, ge=0, description="Video post fee in VCoin")
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
    
    # === COMMUNITY MODULE PRICING (USD) ===
    small_community_fee: float = Field(default=0, ge=0, description="Small community monthly fee")
    medium_community_fee: float = Field(default=3, ge=0, description="Medium community monthly fee")
    large_community_fee: float = Field(default=10, ge=0, description="Large community monthly fee")
    enterprise_community_fee: float = Field(default=35, ge=0, description="Enterprise community monthly fee")
    event_hosting_fee: float = Field(default=2, ge=0, description="Event hosting fee")
    community_verification_fee: float = Field(default=8, ge=0, description="Community verification fee")
    community_analytics_fee: float = Field(default=5, ge=0, description="Community analytics fee")
    
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
    
    # === MESSAGING MODULE PRICING (USD) ===
    encrypted_dm_fee: float = Field(default=0, ge=0, description="Encrypted DM fee per message")
    group_chat_fee: float = Field(default=0.25, ge=0, description="Group chat creation fee")
    file_transfer_fee: float = Field(default=0.02, ge=0, description="File transfer fee")
    voice_call_fee: float = Field(default=0.01, ge=0, description="Voice/video call fee per minute")
    message_storage_fee: float = Field(default=0.50, ge=0, description="Message storage monthly fee")
    messaging_premium_fee: float = Field(default=2, ge=0, description="Messaging premium features fee")
    
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
        """Ensure individual deflation rates are sustainable"""
        if v > 0.10:
            raise ValueError("Individual burn/buyback rate cannot exceed 10%")
        return v
    
    @model_validator(mode='after')
    def validate_combined_deflation(self) -> 'SimulationParameters':
        """
        Issue #5 fix: Ensure combined burn + buyback is sustainable.
        Total deflation > 15% is unsustainable for any real token economy.
        """
        total_deflation = self.burn_rate + self.buyback_percent
        if total_deflation > 0.15:
            raise ValueError(
                f"Combined burn ({self.burn_rate*100}%) + buyback ({self.buyback_percent*100}%) "
                f"= {total_deflation*100}% exceeds sustainable maximum of 15%"
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
