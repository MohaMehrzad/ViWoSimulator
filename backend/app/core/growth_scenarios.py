"""
Growth Scenarios Module - User Growth Projections for VCoin

Implements three realistic growth scenarios (Conservative, Base, Bullish) with:
- Waitlist conversion modeling
- FOMO event triggers (TGE, partnerships, viral moments)
- Market condition multipliers (Bear, Neutral, Bull)
- Token price projections
- Monthly growth rate calculations

Based on research data for March 2026 - March 2027 token launch window:
- Bitcoin halving cycle position (18 months post-halving)
- Global crypto user growth projections (850M-1B users)
- Solana ecosystem expansion
- SocialFi market trends

Data Sources:
- Similar token launches (FriendTech, Lens, Farcaster)
- Crypto social app retention benchmarks
- Market cycle analysis
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math

# === CONSTANTS ===

# Monthly churn dampening factor
# Converts cumulative retention rates to monthly churn estimates.
# Retention rates (e.g., month6_retention = 0.06) represent cumulative retention from Day 0,
# not month-over-month retention. This factor approximates monthly churn from cumulative rates.
# Value of 0.3 means ~30% of the implied cumulative churn actually occurs in each month.
MONTHLY_CHURN_DAMPENING_FACTOR = 0.3


class GrowthScenario(str, Enum):
    """Growth scenario selection"""
    CONSERVATIVE = "conservative"
    BASE = "base"
    BULLISH = "bullish"


class MarketCondition(str, Enum):
    """Macro market condition"""
    BEAR = "bear"
    NEUTRAL = "neutral"
    BULL = "bull"


class FomoEventType(str, Enum):
    """Types of FOMO-inducing events"""
    TGE_LAUNCH = "tge_launch"           # Token Generation Event
    PARTNERSHIP = "partnership"          # Major partnership announcement
    VIRAL_MOMENT = "viral_moment"        # Viral content/trend
    EXCHANGE_LISTING = "exchange_listing" # CEX/DEX listing
    INFLUENCER = "influencer"            # Major influencer adoption
    HOLIDAY = "holiday"                  # Holiday season boost
    FEATURE_LAUNCH = "feature_launch"    # Major feature release
    MILESTONE = "milestone"              # User/volume milestone


@dataclass
class FomoEvent:
    """A FOMO-inducing event that affects user growth"""
    month: int
    event_type: FomoEventType
    impact_multiplier: float  # Multiplier on base growth (e.g., 2.0 = 2x growth)
    description: str
    duration_days: int = 14  # How long the effect lasts
    
    def to_dict(self) -> dict:
        return {
            "month": self.month,
            "event_type": self.event_type.value,
            "impact_multiplier": self.impact_multiplier,
            "description": self.description,
            "duration_days": self.duration_days,
        }


@dataclass
class GrowthScenarioConfig:
    """
    Configuration for a growth scenario.
    
    All rates are based on research for crypto/social app launches.
    """
    name: str
    description: str
    
    # Waitlist conversion (Month 0 -> Month 1)
    waitlist_conversion_rate: float  # 40-70% typical for crypto launches
    
    # Month 1 FOMO multiplier (TGE excitement)
    month1_fomo_multiplier: float  # 2.5x - 12x based on hype level
    
    # Monthly organic growth rates by phase (as decimal)
    # Phase 1: Months 1-3 (Launch hype)
    # Phase 2: Months 4-6 (Stabilization)
    # Phase 3: Months 7-9 (Growth or decline)
    # Phase 4: Months 10-12 (Maturity)
    monthly_growth_rates: List[float]  # 12 months of growth rates
    
    # Retention modifiers
    month1_retention: float  # D30 retention
    month3_retention: float
    month6_retention: float
    month12_retention: float
    
    # Viral coefficient (users acquired per existing user)
    viral_coefficient: float  # 0.3 - 0.8 typical
    
    # Token price projections
    token_price_start: float  # Launch price in USD
    token_price_month6_multiplier: float  # 6-month price multiplier
    token_price_end_multiplier: float  # 12-month price multiplier
    
    # Expected FOMO events
    fomo_events: List[FomoEvent] = field(default_factory=list)
    
    # Summary projections (for display)
    expected_month1_users: int = 0
    expected_month12_mau: int = 0
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "waitlist_conversion_rate": self.waitlist_conversion_rate,
            "month1_fomo_multiplier": self.month1_fomo_multiplier,
            "monthly_growth_rates": self.monthly_growth_rates,
            "month1_retention": self.month1_retention,
            "month3_retention": self.month3_retention,
            "month6_retention": self.month6_retention,
            "month12_retention": self.month12_retention,
            "viral_coefficient": self.viral_coefficient,
            "token_price_start": self.token_price_start,
            "token_price_month6_multiplier": self.token_price_month6_multiplier,
            "token_price_end_multiplier": self.token_price_end_multiplier,
            "fomo_events": [e.to_dict() for e in self.fomo_events],
            "expected_month1_users": self.expected_month1_users,
            "expected_month12_mau": self.expected_month12_mau,
        }


# ============================================================================
# FOMO EVENT SCHEDULES
# ============================================================================

CONSERVATIVE_FOMO_EVENTS = [
    FomoEvent(
        month=1,
        event_type=FomoEventType.TGE_LAUNCH,
        impact_multiplier=2.5,
        description="Token Generation Event - modest launch with targeted marketing",
    ),
    FomoEvent(
        month=4,
        event_type=FomoEventType.FEATURE_LAUNCH,
        impact_multiplier=1.3,
        description="V2 feature release - improved UX and new monetization",
    ),
    FomoEvent(
        month=8,
        event_type=FomoEventType.PARTNERSHIP,
        impact_multiplier=1.4,
        description="Partnership with niche content platform",
    ),
    FomoEvent(
        month=11,
        event_type=FomoEventType.HOLIDAY,
        impact_multiplier=1.2,
        description="Holiday season marketing push",
    ),
]

BASE_FOMO_EVENTS = [
    FomoEvent(
        month=1,
        event_type=FomoEventType.TGE_LAUNCH,
        impact_multiplier=5.0,
        description="Token Generation Event - strong launch with crypto community buzz",
    ),
    FomoEvent(
        month=2,
        event_type=FomoEventType.INFLUENCER,
        impact_multiplier=1.8,
        description="Mid-tier crypto influencer endorsements",
    ),
    FomoEvent(
        month=4,
        event_type=FomoEventType.EXCHANGE_LISTING,
        impact_multiplier=2.0,
        description="Tier-2 CEX listing (MEXC, Gate.io level)",
    ),
    FomoEvent(
        month=6,
        event_type=FomoEventType.MILESTONE,
        impact_multiplier=1.5,
        description="10K active users milestone celebration",
    ),
    FomoEvent(
        month=8,
        event_type=FomoEventType.PARTNERSHIP,
        impact_multiplier=1.6,
        description="Strategic partnership with Web3 project",
    ),
    FomoEvent(
        month=11,
        event_type=FomoEventType.HOLIDAY,
        impact_multiplier=1.4,
        description="Holiday campaign with bonus rewards",
    ),
    FomoEvent(
        month=12,
        event_type=FomoEventType.FEATURE_LAUNCH,
        impact_multiplier=1.3,
        description="Major platform upgrade announcement",
    ),
]

BULLISH_FOMO_EVENTS = [
    FomoEvent(
        month=1,
        event_type=FomoEventType.TGE_LAUNCH,
        impact_multiplier=12.0,
        description="Viral Token Generation Event - massive crypto Twitter buzz",
    ),
    FomoEvent(
        month=1,
        event_type=FomoEventType.INFLUENCER,
        impact_multiplier=3.0,
        description="Top-tier crypto influencer adoption (500K+ followers)",
    ),
    FomoEvent(
        month=2,
        event_type=FomoEventType.VIRAL_MOMENT,
        impact_multiplier=2.5,
        description="Viral content moment drives organic growth",
    ),
    FomoEvent(
        month=3,
        event_type=FomoEventType.EXCHANGE_LISTING,
        impact_multiplier=3.0,
        description="Tier-1 CEX listing (Binance/Coinbase level)",
    ),
    FomoEvent(
        month=5,
        event_type=FomoEventType.MILESTONE,
        impact_multiplier=2.0,
        description="50K active users milestone - viral celebration",
    ),
    FomoEvent(
        month=6,
        event_type=FomoEventType.PARTNERSHIP,
        impact_multiplier=2.5,
        description="Major Web2 social platform partnership",
    ),
    FomoEvent(
        month=8,
        event_type=FomoEventType.FEATURE_LAUNCH,
        impact_multiplier=1.8,
        description="Revolutionary feature launch (AI integration)",
    ),
    FomoEvent(
        month=10,
        event_type=FomoEventType.MILESTONE,
        impact_multiplier=1.6,
        description="100K users milestone announcement",
    ),
    FomoEvent(
        month=11,
        event_type=FomoEventType.HOLIDAY,
        impact_multiplier=1.5,
        description="Holiday season viral campaign",
    ),
    FomoEvent(
        month=12,
        event_type=FomoEventType.EXCHANGE_LISTING,
        impact_multiplier=2.0,
        description="Additional major exchange listings",
    ),
]


# ============================================================================
# SCENARIO CONFIGURATIONS
# ============================================================================

CONSERVATIVE_SCENARIO = GrowthScenarioConfig(
    name="Conservative",
    description="Cautious growth with focus on retention over acquisition. "
                "Assumes modest marketing budget, organic-first approach, "
                "and potential market headwinds.",
    
    # Waitlist: 40% convert (lower confidence in token)
    waitlist_conversion_rate=0.40,
    
    # Month 1: 2.5x FOMO (modest excitement)
    month1_fomo_multiplier=2.5,
    
    # Monthly growth rates (can go negative for churn)
    # Conservative assumes slow growth with potential decline
    monthly_growth_rates=[
        0.25,   # Month 1: +25% (launch momentum)
        0.10,   # Month 2: +10% (initial curiosity)
        0.00,   # Month 3: 0% (stabilization)
        -0.05,  # Month 4: -5% (reality check)
        -0.03,  # Month 5: -3% (summer lull)
        0.02,   # Month 6: +2% (feature release)
        0.03,   # Month 7: +3% (slight recovery)
        0.05,   # Month 8: +5% (partnership bump)
        0.02,   # Month 9: +2% (steady)
        0.01,   # Month 10: +1% (plateau)
        0.04,   # Month 11: +4% (holiday prep)
        0.03,   # Month 12: +3% (holiday boost)
    ],
    
    # Conservative retention (slightly below crypto average)
    month1_retention=0.18,
    month3_retention=0.08,
    month6_retention=0.04,
    month12_retention=0.02,
    
    # Low viral coefficient
    viral_coefficient=0.3,
    
    # Token price: Flat to slight decline, then recovery
    token_price_start=0.03,
    token_price_month6_multiplier=0.66,  # -34% by month 6
    token_price_end_multiplier=1.0,      # Back to launch price
    
    fomo_events=CONSERVATIVE_FOMO_EVENTS,
    
    # Expected outcomes (1000 waitlist baseline)
    expected_month1_users=3300,   # 1000 * 0.40 * 2.5 + organic
    expected_month12_mau=3000,    # Slight decline from peak
)

BASE_SCENARIO = GrowthScenarioConfig(
    name="Base",
    description="Balanced growth scenario based on comparable SocialFi launches. "
                "Assumes solid execution, reasonable marketing spend, "
                "and neutral-to-positive market conditions.",
    
    # Waitlist: 50% convert
    waitlist_conversion_rate=0.50,
    
    # Month 1: 5x FOMO (solid crypto community response)
    month1_fomo_multiplier=5.0,
    
    # Monthly growth rates (sustainable growth curve)
    monthly_growth_rates=[
        0.40,   # Month 1: +40% (strong launch)
        0.25,   # Month 2: +25% (influencer boost)
        0.15,   # Month 3: +15% (organic growth)
        0.20,   # Month 4: +20% (exchange listing)
        0.10,   # Month 5: +10% (steady)
        0.12,   # Month 6: +12% (milestone celebration)
        0.08,   # Month 7: +8% (summer stable)
        0.10,   # Month 8: +10% (partnership)
        0.06,   # Month 9: +6% (steady growth)
        0.05,   # Month 10: +5% (maturing)
        0.08,   # Month 11: +8% (holiday campaign)
        0.07,   # Month 12: +7% (year-end momentum)
    ],
    
    # Average SocialFi retention
    month1_retention=0.22,
    month3_retention=0.10,
    month6_retention=0.06,
    month12_retention=0.035,
    
    # Moderate viral coefficient
    viral_coefficient=0.5,
    
    # Token price: Growth to 3-4x
    token_price_start=0.03,
    token_price_month6_multiplier=2.0,   # 2x by month 6
    token_price_end_multiplier=3.5,      # 3.5x by month 12
    
    fomo_events=BASE_FOMO_EVENTS,
    
    # Expected outcomes (1000 waitlist baseline)
    expected_month1_users=5800,   # 1000 * 0.50 * 5.0 + organic + viral
    expected_month12_mau=14500,   # Strong growth
)

BULLISH_SCENARIO = GrowthScenarioConfig(
    name="Bullish",
    description="Aggressive growth scenario assuming viral adoption, "
                "strong market conditions (bull market), major partnerships, "
                "and successful influencer campaigns.",
    
    # Waitlist: 60% convert (high FOMO)
    waitlist_conversion_rate=0.60,
    
    # Month 1: 12x FOMO (viral launch)
    month1_fomo_multiplier=12.0,
    
    # Monthly growth rates (exponential early, sustained later)
    monthly_growth_rates=[
        0.80,   # Month 1: +80% (viral launch)
        0.50,   # Month 2: +50% (viral moment continues)
        0.35,   # Month 3: +35% (major exchange listing)
        0.25,   # Month 4: +25% (sustained momentum)
        0.30,   # Month 5: +30% (milestone celebration)
        0.25,   # Month 6: +25% (major partnership)
        0.15,   # Month 7: +15% (summer growth)
        0.18,   # Month 8: +18% (feature launch)
        0.12,   # Month 9: +12% (steady)
        0.15,   # Month 10: +15% (100K milestone)
        0.12,   # Month 11: +12% (holiday viral)
        0.18,   # Month 12: +18% (exchange listings)
    ],
    
    # Best-case retention (product-market fit)
    month1_retention=0.28,
    month3_retention=0.15,
    month6_retention=0.10,
    month12_retention=0.06,
    
    # High viral coefficient
    viral_coefficient=0.8,
    
    # Token price: Growth to 7-10x
    token_price_start=0.03,
    token_price_month6_multiplier=4.0,   # 4x by month 6
    token_price_end_multiplier=7.0,      # 7x by month 12
    
    fomo_events=BULLISH_FOMO_EVENTS,
    
    # Expected outcomes (1000 waitlist baseline)
    expected_month1_users=12800,   # 1000 * 0.60 * 12.0 + viral
    expected_month12_mau=62500,    # Massive growth
)


# Scenario lookup dictionary
GROWTH_SCENARIOS: Dict[GrowthScenario, GrowthScenarioConfig] = {
    GrowthScenario.CONSERVATIVE: CONSERVATIVE_SCENARIO,
    GrowthScenario.BASE: BASE_SCENARIO,
    GrowthScenario.BULLISH: BULLISH_SCENARIO,
}


# ============================================================================
# MARKET CONDITION MULTIPLIERS
# ============================================================================

@dataclass
class MarketConditionConfig:
    """Market condition impact on growth and price"""
    name: str
    description: str
    growth_multiplier: float      # Affects user acquisition
    retention_multiplier: float   # Affects retention rates
    price_multiplier: float       # Affects token price trajectory
    fomo_multiplier: float        # Affects FOMO event impact
    cac_multiplier: float         # Affects customer acquisition cost


MARKET_CONDITIONS: Dict[MarketCondition, MarketConditionConfig] = {
    MarketCondition.BEAR: MarketConditionConfig(
        name="Bear Market",
        description="Crypto winter conditions - reduced interest, "
                    "lower liquidity, higher CAC, risk-off sentiment.",
        growth_multiplier=0.6,      # 40% less growth
        retention_multiplier=0.8,   # 20% worse retention
        price_multiplier=0.5,       # 50% price reduction
        fomo_multiplier=0.7,        # FOMO events less impactful
        cac_multiplier=1.5,         # 50% higher CAC
    ),
    MarketCondition.NEUTRAL: MarketConditionConfig(
        name="Neutral Market",
        description="Sideways market - stable conditions, "
                    "balanced interest, normal acquisition costs.",
        growth_multiplier=1.0,
        retention_multiplier=1.0,
        price_multiplier=1.0,
        fomo_multiplier=1.0,
        cac_multiplier=1.0,
    ),
    MarketCondition.BULL: MarketConditionConfig(
        name="Bull Market",
        description="Crypto bull run - high interest, increased liquidity, "
                    "lower CAC, risk-on sentiment, FOMO amplified.",
        growth_multiplier=1.5,      # 50% more growth
        retention_multiplier=1.1,   # 10% better retention
        price_multiplier=2.0,       # 2x price amplification
        fomo_multiplier=1.5,        # FOMO events more impactful
        cac_multiplier=0.7,         # 30% lower CAC
    ),
}


# ============================================================================
# 5-YEAR MARKET CYCLE ANALYSIS (2026-2030)
# ============================================================================

@dataclass
class MarketCycleYearConfig:
    """Year-specific market cycle configuration"""
    year: int
    phase: str                    # Market cycle phase
    growth_multiplier: float      # Affects user acquisition
    retention_multiplier: float   # Affects retention rates
    price_multiplier: float       # Affects token price trajectory
    description: str


# Bitcoin Halving April 2024 - Market cycle analysis for 2026-2030
# Based on historical halving cycles and 2024-2025 market conditions
MARKET_CYCLE_2026_2030: Dict[int, MarketCycleYearConfig] = {
    2026: MarketCycleYearConfig(
        year=2026,
        phase="Peak Bull / Altcoin Season",
        growth_multiplier=1.6,
        retention_multiplier=1.15,
        price_multiplier=2.5,
        description="Peak of bull cycle expected. Maximum FOMO, highest valuations. "
                    "Social tokens and SocialFi projects see maximum interest. "
                    "Token launch timing optimal (March 2026 TGE)."
    ),
    2027: MarketCycleYearConfig(
        year=2027,
        phase="Late Bull / Distribution",
        growth_multiplier=1.2,
        retention_multiplier=1.0,
        price_multiplier=1.8,
        description="Distribution phase begins. Smart money taking profits. "
                    "New user acquisition slows but platform maturity increases. "
                    "Focus on retention and utility over speculation."
    ),
    2028: MarketCycleYearConfig(
        year=2028,
        phase="Bear / Accumulation",
        growth_multiplier=0.7,
        retention_multiplier=0.85,
        price_multiplier=0.5,
        description="Next halving approaches (expected April 2028). Bear market conditions. "
                    "CAC increases, retention becomes critical. "
                    "Building phase - focus on product and community."
    ),
    2029: MarketCycleYearConfig(
        year=2029,
        phase="Recovery / New Cycle Begins",
        growth_multiplier=1.1,
        retention_multiplier=1.0,
        price_multiplier=1.0,
        description="Post-halving recovery begins. Market sentiment improving. "
                    "Platform is mature with established user base. "
                    "Positioned for next growth cycle."
    ),
    2030: MarketCycleYearConfig(
        year=2030,
        phase="Early Bull / Mature Platform",
        growth_multiplier=1.4,
        retention_multiplier=1.1,
        price_multiplier=1.5,
        description="New bull cycle in progress. Platform has 4+ years of operation. "
                    "Established brand, lower CAC, high retention. "
                    "Expansion into new markets and features."
    ),
}


def get_cycle_multipliers(year: int, base_month: int = 0) -> Dict[str, float]:
    """
    Get market cycle multipliers for a specific year.
    
    Args:
        year: Calendar year (2026-2030)
        base_month: Month within the year (0-11) for fine-grained adjustments
    
    Returns:
        Dictionary with growth, retention, and price multipliers
    """
    if year not in MARKET_CYCLE_2026_2030:
        # Default to neutral for years outside range
        return {
            "growth_multiplier": 1.0,
            "retention_multiplier": 1.0,
            "price_multiplier": 1.0,
            "phase": "Unknown",
        }
    
    config = MARKET_CYCLE_2026_2030[year]
    
    # Optional: Add monthly variance within the year
    # e.g., Q4 tends to be stronger (holiday season)
    monthly_adjustment = 1.0
    if base_month >= 9:  # Oct-Dec
        monthly_adjustment = 1.1  # 10% boost
    elif base_month >= 6:  # Jul-Sep
        monthly_adjustment = 0.95  # Summer lull
    
    return {
        "growth_multiplier": config.growth_multiplier * monthly_adjustment,
        "retention_multiplier": config.retention_multiplier,
        "price_multiplier": config.price_multiplier,
        "phase": config.phase,
        "description": config.description,
    }


def get_5_year_projection_multipliers(start_year: int = 2026, start_month: int = 3) -> List[Dict]:
    """
    Get month-by-month multipliers for a 60-month (5-year) projection.
    
    Args:
        start_year: Starting year (default 2026)
        start_month: Starting month 1-12 (default March = 3)
    
    Returns:
        List of 60 monthly multiplier dictionaries
    """
    projections = []
    current_year = start_year
    current_month = start_month
    
    for month_index in range(60):
        multipliers = get_cycle_multipliers(current_year, current_month - 1)
        multipliers["month"] = month_index + 1
        multipliers["calendar_year"] = current_year
        multipliers["calendar_month"] = current_month
        projections.append(multipliers)
        
        # Advance month
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1
    
    return projections


# ============================================================================
# GROWTH CALCULATION FUNCTIONS
# ============================================================================

def calculate_waitlist_conversion(
    waitlist_users: int,
    scenario: GrowthScenarioConfig,
    market_condition: MarketCondition,
) -> int:
    """
    Calculate initial users from waitlist conversion at TGE.
    
    Args:
        waitlist_users: Number of users on waitlist
        scenario: Selected growth scenario
        market_condition: Current market condition
    
    Returns:
        Number of converted users
    """
    market_config = MARKET_CONDITIONS[market_condition]
    
    # Base conversion from waitlist
    base_conversion = waitlist_users * scenario.waitlist_conversion_rate
    
    # Apply market condition modifier
    adjusted_conversion = base_conversion * market_config.growth_multiplier
    
    # Apply Month 1 FOMO multiplier
    fomo_adjusted = adjusted_conversion * (1 + (scenario.month1_fomo_multiplier - 1) * 0.3)
    
    return int(fomo_adjusted)


def get_fomo_event_for_month(
    month: int,
    scenario: GrowthScenarioConfig,
) -> Optional[FomoEvent]:
    """Get FOMO event for a specific month, if any."""
    for event in scenario.fomo_events:
        if event.month == month:
            return event
    return None


def calculate_monthly_growth(
    month: int,
    current_users: int,
    scenario: GrowthScenarioConfig,
    market_condition: MarketCondition,
    token_price: float,
) -> Tuple[int, int, float]:
    """
    Calculate user growth for a specific month.
    
    Args:
        month: Month number (1-60, extended from original 1-12)
        current_users: Current active user count
        scenario: Selected growth scenario
        market_condition: Current market condition
        token_price: Current token price
    
    Returns:
        Tuple of (new_users, churned_users, growth_rate)
    
    MED-08 Fix: Extended to support months 13-60 by extrapolating from year 1 data.
    For months > 12, uses year-specific market cycle multipliers if available,
    otherwise extrapolates with a decay factor toward steady-state growth.
    """
    if month < 1:
        return 0, 0, 0.0
    
    market_config = MARKET_CONDITIONS[market_condition]
    
    # MED-08 Fix: Extend beyond 12 months
    if month > 12:
        # For months 13-60, extrapolate from last year's data with decay
        # Get the equivalent month in year 1 (cyclic pattern)
        equivalent_month = ((month - 1) % 12) + 1
        base_growth_rate = scenario.monthly_growth_rates[equivalent_month - 1]
        
        # Apply decay factor: growth stabilizes over time
        # Year 2: 80% of year 1 rate, Year 3: 65%, Year 4: 55%, Year 5: 50%
        years_elapsed = (month - 1) // 12
        decay_factors = [1.0, 0.80, 0.65, 0.55, 0.50]
        decay_factor = decay_factors[min(years_elapsed, len(decay_factors) - 1)]
        
        # Apply market cycle multiplier if available
        year = 2026 + years_elapsed
        if year in MARKET_CYCLE_2026_2030:
            cycle_config = MARKET_CYCLE_2026_2030[year]
            base_growth_rate = base_growth_rate * decay_factor * cycle_config.growth_multiplier
        else:
            base_growth_rate = base_growth_rate * decay_factor
    else:
        # Original behavior for months 1-12
        base_growth_rate = scenario.monthly_growth_rates[month - 1]
    
    # Apply market condition modifier
    adjusted_growth_rate = base_growth_rate * market_config.growth_multiplier
    
    # Check for FOMO event this month
    fomo_event = get_fomo_event_for_month(month, scenario)
    if fomo_event:
        # FOMO events boost growth
        fomo_boost = (fomo_event.impact_multiplier - 1) * market_config.fomo_multiplier
        adjusted_growth_rate += fomo_boost * 0.3  # Dampen to be realistic
    
    # Viral growth component
    viral_new_users = int(current_users * scenario.viral_coefficient * 0.1)
    
    # Calculate organic growth
    organic_growth = int(current_users * adjusted_growth_rate)
    
    # Total new users
    new_users = max(0, organic_growth + viral_new_users)
    
    # Calculate churn based on retention
    # Use appropriate retention rate based on month
    if month <= 1:
        retention_rate = scenario.month1_retention
    elif month <= 3:
        retention_rate = scenario.month3_retention
    elif month <= 6:
        retention_rate = scenario.month6_retention
    else:
        retention_rate = scenario.month12_retention
    
    # Apply market condition to retention
    adjusted_retention = retention_rate * market_config.retention_multiplier
    
    # Apply monthly churn dampening factor to convert cumulative retention to monthly churn
    # See MONTHLY_CHURN_DAMPENING_FACTOR constant for detailed explanation
    churn_rate = 1 - adjusted_retention
    churned_users = int(current_users * churn_rate * MONTHLY_CHURN_DAMPENING_FACTOR)
    
    return new_users, churned_users, adjusted_growth_rate


def calculate_token_price(
    month: int,
    scenario: GrowthScenarioConfig,
    market_condition: MarketCondition,
    base_price: float,
) -> float:
    """
    Calculate token price for a specific month.
    
    Uses logarithmic interpolation between key price points.
    
    Args:
        month: Month number (1-12)
        scenario: Selected growth scenario
        market_condition: Current market condition
        base_price: Starting token price
    
    Returns:
        Projected token price
    """
    market_config = MARKET_CONDITIONS[market_condition]
    
    # Get scenario price multipliers
    start_mult = 1.0
    mid_mult = scenario.token_price_month6_multiplier
    end_mult = scenario.token_price_end_multiplier
    
    # Apply market condition
    mid_mult *= market_config.price_multiplier
    end_mult *= market_config.price_multiplier
    
    # Interpolate based on month
    if month <= 0:
        multiplier = start_mult
    elif month <= 6:
        # Linear interpolation for first 6 months
        t = month / 6.0
        multiplier = start_mult + (mid_mult - start_mult) * t
    else:
        # Linear interpolation for months 7-12
        t = (month - 6) / 6.0
        multiplier = mid_mult + (end_mult - mid_mult) * t
    
    return base_price * multiplier


def get_scenario_summary(
    scenario: GrowthScenario,
    market_condition: MarketCondition,
    starting_waitlist: int = 1000,
    token_price: float = 0.03,
) -> Dict:
    """
    Get a summary projection for a scenario.
    
    Returns key metrics for the 12-month projection.
    """
    config = GROWTH_SCENARIOS[scenario]
    market_config = MARKET_CONDITIONS[market_condition]
    
    # Calculate Month 1 users
    month1_users = calculate_waitlist_conversion(
        starting_waitlist, config, market_condition
    )
    
    # Simulate 12 months
    monthly_mau = [month1_users]
    current_users = month1_users
    
    for month in range(2, 13):
        new_users, churned, _ = calculate_monthly_growth(
            month, current_users, config, market_condition, token_price
        )
        current_users = max(0, current_users + new_users - churned)
        monthly_mau.append(current_users)
    
    # Calculate price curve
    price_curve = [
        calculate_token_price(m, config, market_condition, token_price)
        for m in range(1, 13)
    ]
    
    return {
        "scenario": scenario.value,
        "market_condition": market_condition.value,
        "starting_waitlist": starting_waitlist,
        "month1_users": month1_users,
        "month6_mau": monthly_mau[5] if len(monthly_mau) > 5 else 0,
        "month12_mau": monthly_mau[-1],
        "peak_mau": max(monthly_mau),
        "growth_percentage": ((monthly_mau[-1] / month1_users) - 1) * 100 if month1_users > 0 else 0,
        "monthly_mau": monthly_mau,
        "token_price_start": token_price,
        "token_price_month6": price_curve[5] if len(price_curve) > 5 else token_price,
        "token_price_end": price_curve[-1],
        "price_curve": price_curve,
        "fomo_events": [e.to_dict() for e in config.fomo_events],
    }


def get_all_scenario_comparison(
    market_condition: MarketCondition,
    starting_waitlist: int = 1000,
    token_price: float = 0.03,
) -> Dict[str, Dict]:
    """
    Get comparison of all three scenarios under the same market condition.
    """
    return {
        scenario.value: get_scenario_summary(
            scenario, market_condition, starting_waitlist, token_price
        )
        for scenario in GrowthScenario
    }


# =============================================================================
# 5A POLICY INTEGRATION (Dynamic 5A - December 2025)
# =============================================================================
# These functions integrate the 5A gamification system with growth scenarios,
# affecting retention, growth rates, and overall platform dynamics.

# Segment retention multipliers (how segment affects base retention)
FIVE_A_SEGMENT_RETENTION_MULTIPLIERS = {
    'inactive': 0.3,      # 70% higher churn than baseline
    'lurkers': 0.7,       # 30% higher churn
    'casual': 1.0,        # Baseline retention
    'active': 1.3,        # 30% better retention
    'power_users': 1.8,   # 80% better retention
}


def calculate_five_a_retention_boost(
    segment_distribution: Dict[str, float],
) -> float:
    """
    Calculate retention multiplier based on 5A segment distribution.
    
    Args:
        segment_distribution: Dict with segment percentages
            e.g., {'inactive': 0.20, 'lurkers': 0.40, 'casual': 0.25, 'active': 0.12, 'power_users': 0.03}
    
    Returns:
        Retention multiplier (0.3 to 1.8), applied to base retention rate.
        Higher values = better retention.
    """
    if not segment_distribution:
        return 1.0
    
    total_weight = sum(segment_distribution.values())
    if total_weight == 0:
        return 1.0
    
    weighted_sum = 0.0
    for segment, percent in segment_distribution.items():
        multiplier = FIVE_A_SEGMENT_RETENTION_MULTIPLIERS.get(segment, 1.0)
        weighted_sum += percent * multiplier
    
    return weighted_sum / total_weight


def calculate_five_a_growth_boost(
    avg_multiplier: float,
    active_percent: float,
) -> float:
    """
    Calculate growth rate boost based on 5A metrics.
    
    Higher 5A scores indicate more engaged users who are more likely to:
    - Refer friends (viral growth)
    - Create content that attracts new users
    - Provide positive reviews and word-of-mouth
    
    Args:
        avg_multiplier: Average 5A multiplier across users (0.0 to 2.0)
            - 0.6 = typical realistic distribution
            - 1.0 = neutral (50% stars)
            - 1.5+ = highly engaged platform
        active_percent: Percentage of users in active + power_users segments (0.0 to 1.0)
            - 0.15 = baseline (12% active + 3% power)
            - 0.30 = highly engaged platform
    
    Returns:
        Growth rate multiplier (0.8 to 1.3)
        - 0.8 = low engagement, viral growth suffers
        - 1.0 = neutral
        - 1.3 = high engagement, amplified viral growth
    """
    # Factor 1: Average multiplier impact
    # Below 0.5x avg = penalty, above 1.0x = bonus
    base_boost = (avg_multiplier - 0.5) * 0.4  # Range: -0.2 to +0.6
    
    # Factor 2: Active user percentage impact
    # Baseline is 15% (12% active + 3% power), higher = more viral
    engagement_boost = (active_percent - 0.15) * 0.5  # Range: -0.075 to +0.075
    
    # Combine and clamp
    total_boost = 1.0 + base_boost + engagement_boost
    return max(0.8, min(1.3, total_boost))


def calculate_monthly_growth_with_five_a(
    month: int,
    current_users: int,
    scenario: GrowthScenarioConfig,
    market_condition: MarketCondition,
    token_price: float,
    segment_distribution: Optional[Dict[str, float]] = None,
    avg_five_a_multiplier: float = 1.0,
) -> Tuple[int, int, float, Dict[str, float]]:
    """
    Calculate monthly growth with 5A policy integration.
    
    This extends calculate_monthly_growth to incorporate:
    - 5A-weighted retention (high 5A = better retention)
    - 5A growth boost (engaged users = viral growth)
    
    Args:
        month: Month number (1-60)
        current_users: Current active user count
        scenario: Selected growth scenario
        market_condition: Current market condition
        token_price: Current token price
        segment_distribution: 5A segment percentages
        avg_five_a_multiplier: Average 5A multiplier across users
    
    Returns:
        Tuple of (new_users, churned_users, growth_rate, five_a_impacts)
        five_a_impacts contains:
        - retention_boost: Applied retention multiplier
        - growth_boost: Applied growth multiplier
    """
    if month < 1:
        return 0, 0, 0.0, {'retention_boost': 1.0, 'growth_boost': 1.0}
    
    market_config = MARKET_CONDITIONS[market_condition]
    
    # Calculate base growth rate (same logic as calculate_monthly_growth)
    if month > 12:
        equivalent_month = ((month - 1) % 12) + 1
        base_growth_rate = scenario.monthly_growth_rates[equivalent_month - 1]
        years_elapsed = (month - 1) // 12
        decay_factors = [1.0, 0.80, 0.65, 0.55, 0.50]
        decay_factor = decay_factors[min(years_elapsed, len(decay_factors) - 1)]
        year = 2026 + years_elapsed
        if year in MARKET_CYCLE_2026_2030:
            cycle_config = MARKET_CYCLE_2026_2030[year]
            base_growth_rate = base_growth_rate * decay_factor * cycle_config.growth_multiplier
        else:
            base_growth_rate = base_growth_rate * decay_factor
    else:
        base_growth_rate = scenario.monthly_growth_rates[month - 1]
    
    # Apply market condition
    adjusted_growth_rate = base_growth_rate * market_config.growth_multiplier
    
    # Calculate 5A growth boost
    active_percent = 0.15  # Default baseline
    if segment_distribution:
        active_percent = (
            segment_distribution.get('active', 0.12) +
            segment_distribution.get('power_users', 0.03)
        )
    
    five_a_growth_boost = calculate_five_a_growth_boost(avg_five_a_multiplier, active_percent)
    adjusted_growth_rate *= five_a_growth_boost
    
    # Apply FOMO event boost
    fomo_event = get_fomo_event_for_month(month, scenario)
    if fomo_event:
        fomo_boost = (fomo_event.impact_multiplier - 1) * market_config.fomo_multiplier
        adjusted_growth_rate += fomo_boost * 0.3
    
    # Calculate viral + organic growth
    viral_new_users = int(current_users * scenario.viral_coefficient * 0.1 * five_a_growth_boost)
    organic_growth = int(current_users * adjusted_growth_rate)
    new_users = max(0, organic_growth + viral_new_users)
    
    # Calculate retention with 5A boost
    if month <= 1:
        retention_rate = scenario.month1_retention
    elif month <= 3:
        retention_rate = scenario.month3_retention
    elif month <= 6:
        retention_rate = scenario.month6_retention
    else:
        retention_rate = scenario.month12_retention
    
    # Apply market condition
    adjusted_retention = retention_rate * market_config.retention_multiplier
    
    # Apply 5A retention boost
    five_a_retention_boost = 1.0
    if segment_distribution:
        five_a_retention_boost = calculate_five_a_retention_boost(segment_distribution)
    
    adjusted_retention *= five_a_retention_boost
    adjusted_retention = min(adjusted_retention, 0.95)  # Cap at 95% retention
    
    # Calculate churn
    churn_rate = 1 - adjusted_retention
    churned_users = int(current_users * churn_rate * MONTHLY_CHURN_DAMPENING_FACTOR)
    
    five_a_impacts = {
        'retention_boost': round(five_a_retention_boost, 3),
        'growth_boost': round(five_a_growth_boost, 3),
        'adjusted_retention_rate': round(adjusted_retention, 4),
        'adjusted_growth_rate': round(adjusted_growth_rate, 4),
    }
    
    return new_users, churned_users, adjusted_growth_rate, five_a_impacts


# =============================================================================
# MULTI-YEAR MARKETING BUDGET HELPERS (Dec 2025)
# =============================================================================

def get_marketing_budget_multiplier_for_year(year: int) -> float:
    """
    Get the cumulative marketing budget multiplier for a given year.
    
    Based on the default multipliers:
    - Year 1: 1.0x (base)
    - Year 2: 2.0x (2x of Year 1)
    - Year 3: 6.0x (3x of Year 2 = 6x of Year 1)
    - Year 4: 12.0x (2x of Year 3 = 12x of Year 1)
    - Year 5: 24.0x (2x of Year 4 = 24x of Year 1)
    
    Args:
        year: Year number (1-5)
    
    Returns:
        Cumulative multiplier relative to Year 1
    """
    if year <= 1:
        return 1.0
    
    # Default multipliers (can be overridden via params)
    multipliers = {
        1: 1.0,
        2: 2.0,   # 2x of Year 1
        3: 6.0,   # 3x of Year 2
        4: 12.0,  # 2x of Year 3
        5: 24.0,  # 2x of Year 4
    }
    
    return multipliers.get(year, multipliers[5])


def calculate_marketing_driven_growth_boost(
    month: int,
    base_users: int,
    year1_marketing_budget: float,
    effective_cac: float = 40.0,
) -> Dict[str, float]:
    """
    Calculate additional user growth from marketing budget beyond Year 1.
    
    This function estimates how many additional users can be acquired
    from the increased marketing budget in years 2-5.
    
    Args:
        month: Month number (1-60)
        base_users: Current user base
        year1_marketing_budget: Year 1 annual marketing budget
        effective_cac: Effective customer acquisition cost (blended)
    
    Returns:
        Dictionary with:
        - year: Current year (1-5)
        - annual_budget: Marketing budget for this year
        - monthly_budget: Marketing budget for this month
        - potential_users: Users that could be acquired this month
        - growth_multiplier: Multiplier compared to Year 1
    """
    year = ((month - 1) // 12) + 1
    month_in_year = ((month - 1) % 12) + 1
    
    # Get cumulative multiplier for this year
    cumulative_multiplier = get_marketing_budget_multiplier_for_year(year)
    annual_budget = year1_marketing_budget * cumulative_multiplier
    
    # Distribution within year (front-loaded: 50% in first 3 months)
    distribution = {
        1: 0.2333, 2: 0.1667, 3: 0.1000,
        4: 0.0667, 5: 0.0667, 6: 0.0667,
        7: 0.0556, 8: 0.0556, 9: 0.0556,
        10: 0.0444, 11: 0.0444, 12: 0.0444,
    }
    
    monthly_budget = annual_budget * distribution.get(month_in_year, 0)
    
    # Calculate potential users from marketing (using effective CAC)
    potential_users = int(monthly_budget / effective_cac) if effective_cac > 0 else 0
    
    return {
        'year': year,
        'annual_budget': annual_budget,
        'monthly_budget': monthly_budget,
        'potential_users': potential_users,
        'growth_multiplier': cumulative_multiplier,
    }


# =============================================================================
# USER GROWTH PRICE IMPACT (Dec 2025)
# =============================================================================
# Based on research:
# - Blockchain gaming: ~2.4x elasticity (12% DAU growth = 29% value increase)
# - Friend.tech: Strong correlation but 98% drop when users declined
# - Metcalfe's Law: Overstated for crypto (10-1000x higher than Facebook)
# - a16z framework: Recommends dampened network effects with multiple metrics

def calculate_user_growth_price_multiplier(
    current_users: int,
    baseline_users: int,
    elasticity: float = 0.35,
    max_multiplier: float = 3.0,
) -> Dict[str, float]:
    """
    Calculate token price multiplier based on user growth with logarithmic dampening.
    
    This implements a research-backed model for how user growth affects token price:
    - Uses dampened Metcalfe's Law (n^1.2 instead of n^2)
    - Applies logarithmic dampening at scale to prevent unrealistic projections
    - Caps maximum multiplier to ensure conservative estimates
    
    Research basis:
    - Blockchain gaming tokens: 12% DAU increase → 29% market cap increase (~2.4x elasticity)
    - But pure correlation leads to overestimation; we use 0.35 elasticity as default
    - Logarithmic dampening ensures diminishing returns at scale
    
    Args:
        current_users: Current active user count
        baseline_users: Baseline user count (typically Year 1 starting users)
        elasticity: How much user growth translates to price (0.35 = 35%)
        max_multiplier: Maximum price multiplier cap (default 3.0x)
    
    Returns:
        Dictionary with:
        - multiplier: The price multiplier to apply
        - user_growth_ratio: How much users have grown
        - dampening_factor: Scale-based dampening applied
        - raw_impact: Impact before dampening
    """
    if baseline_users <= 0 or current_users <= 0:
        return {
            'multiplier': 1.0,
            'user_growth_ratio': 1.0,
            'dampening_factor': 1.0,
            'raw_impact': 0.0,
        }
    
    # Calculate user growth ratio
    user_growth_ratio = current_users / baseline_users
    
    # If users haven't grown (or shrunk), no positive price impact
    if user_growth_ratio <= 1.0:
        # Could apply negative impact for user decline, but keep neutral for now
        return {
            'multiplier': 1.0,
            'user_growth_ratio': user_growth_ratio,
            'dampening_factor': 1.0,
            'raw_impact': 0.0,
        }
    
    # Calculate logarithmic dampening factor based on user scale
    # At 1K users: dampening = 1.0 (full impact)
    # At 10K users: dampening = 0.75
    # At 100K users: dampening = 0.50
    # At 1M users: dampening = 0.25
    # Formula: dampening = 1 / (1 + 0.25 * log10(users / 1000))
    log_users = math.log10(max(current_users, 1000))
    dampening_factor = 1.0 / (1.0 + 0.25 * (log_users - 3))  # log10(1000) = 3
    dampening_factor = max(0.1, min(1.0, dampening_factor))  # Clamp between 0.1 and 1.0
    
    # Calculate raw impact from user growth
    # Using (growth_ratio - 1) so that 2x users = 1.0 raw growth factor
    raw_growth_factor = user_growth_ratio - 1.0
    
    # Apply elasticity (how much growth translates to price)
    raw_impact = raw_growth_factor * elasticity
    
    # Apply dampening based on scale
    dampened_impact = raw_impact * dampening_factor
    
    # Calculate final multiplier (1.0 = no change)
    multiplier = 1.0 + dampened_impact
    
    # Cap at maximum multiplier
    multiplier = min(multiplier, max_multiplier)
    
    return {
        'multiplier': round(multiplier, 4),
        'user_growth_ratio': round(user_growth_ratio, 4),
        'dampening_factor': round(dampening_factor, 4),
        'raw_impact': round(raw_impact, 4),
    }


def get_user_growth_price_impact_for_year(
    year: int,
    year_end_users: int,
    year1_baseline_users: int,
    elasticity: float = 0.35,
    max_multiplier: float = 3.0,
) -> Dict[str, float]:
    """
    Get the user-growth-driven price multiplier for a specific year.
    
    This is a convenience function that wraps calculate_user_growth_price_multiplier
    for year-based calculations in the 5-year projections.
    
    Args:
        year: Year number (1-5)
        year_end_users: Users at end of the year
        year1_baseline_users: Baseline users from Year 1 (for comparison)
        elasticity: Price elasticity (default 0.35)
        max_multiplier: Maximum price multiplier cap
    
    Returns:
        Same as calculate_user_growth_price_multiplier
    """
    if year <= 1:
        # Year 1 is the baseline, no growth impact
        return {
            'multiplier': 1.0,
            'user_growth_ratio': 1.0,
            'dampening_factor': 1.0,
            'raw_impact': 0.0,
        }
    
    return calculate_user_growth_price_multiplier(
        current_users=year_end_users,
        baseline_users=year1_baseline_users,
        elasticity=elasticity,
        max_multiplier=max_multiplier,
    )