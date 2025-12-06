"""
Monthly Progression Simulation Engine - Issue #16 Fix

Implements time-series simulation with:
- Cohort-based user retention tracking
- Monthly iteration with cumulative metrics
- Seasonality adjustments (Q4 boost, summer dip)
- CAC inflation as market saturates
- Market saturation modeling (Issue #14)
- Growth scenario projections (Nov 2025)
- FOMO event triggers and token price projections
- Token allocation vesting schedule (Nov 2025)
- Circulating supply tracking over 60 months

This transforms the static snapshot simulation into a realistic
multi-month projection that accounts for churn, growth curves,
and market dynamics.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Tuple
from enum import Enum
import math

from app.models import SimulationParameters, PlatformMaturity, GrowthScenarioType, MarketConditionType
from app.models.results import (
    FomoEventResult, 
    GrowthProjectionResult, 
    CirculatingSupplyResult,
    TokenCategoryUnlock,
    VestingScheduleResult,
    TreasuryResult,
)
from app.core.retention import (
    CohortTracker,
    VCOIN_RETENTION,
    SOCIAL_APP_RETENTION,
    CRYPTO_APP_RETENTION,
    RetentionCurve,
    RetentionModel,
    RETENTION_CURVES,
)
from app.core.deterministic import run_deterministic_simulation
from app.core.growth_scenarios import (
    GrowthScenario,
    MarketCondition,
    FomoEvent,
    GROWTH_SCENARIOS,
    MARKET_CONDITIONS,
    calculate_waitlist_conversion,
    calculate_monthly_growth,
    calculate_token_price,
    get_fomo_event_for_month,
    get_cycle_multipliers,
    MARKET_CYCLE_2025_2030,
    # 5A Integration (Dec 2025)
    calculate_five_a_retention_boost,
    calculate_five_a_growth_boost,
    calculate_monthly_growth_with_five_a,
)
from app.core.modules import (
    calculate_governance,
    calculate_vchain,
    calculate_marketplace,
    calculate_business_hub,
    calculate_cross_platform,
)
from app.core.modules.five_a_policy import (
    evolve_user_segments,
    calculate_platform_maturity,
    USER_SEGMENTS,
    SEGMENT_ORDER,
)
from app.core.modules.liquidity import calculate_five_a_price_impact
from app.config import config


def calculate_future_modules_revenue(
    params: SimulationParameters,
    current_month: int,
    users: int,
    token_price: float
) -> Dict[str, Dict]:
    """
    Calculate revenue from future modules if enabled.
    
    Args:
        params: Simulation parameters
        current_month: Current month in simulation
        users: Total active users
        token_price: Current token price
    
    Returns:
        Dict with revenue from each enabled future module
    """
    results = {
        'vchain': {'enabled': False, 'revenue': 0, 'profit': 0},
        'marketplace': {'enabled': False, 'revenue': 0, 'profit': 0},
        'business_hub': {'enabled': False, 'revenue': 0, 'profit': 0},
        'cross_platform': {'enabled': False, 'revenue': 0, 'profit': 0},
        'total_revenue': 0,
        'total_profit': 0,
    }
    
    # VChain
    if params.vchain and params.vchain.enable_vchain:
        vchain_result = calculate_vchain(params, current_month, users, token_price)
        results['vchain'] = vchain_result
        results['total_revenue'] += vchain_result.get('revenue', 0)
        results['total_profit'] += vchain_result.get('profit', 0)
    
    # Marketplace
    if params.marketplace and params.marketplace.enable_marketplace:
        marketplace_result = calculate_marketplace(params, current_month, users, token_price)
        results['marketplace'] = marketplace_result
        results['total_revenue'] += marketplace_result.get('revenue', 0)
        results['total_profit'] += marketplace_result.get('profit', 0)
    
    # Business Hub
    if params.business_hub and params.business_hub.enable_business_hub:
        bh_result = calculate_business_hub(params, current_month, users, token_price)
        results['business_hub'] = bh_result
        results['total_revenue'] += bh_result.get('revenue', 0)
        results['total_profit'] += bh_result.get('profit', 0)
    
    # Cross-Platform
    if params.cross_platform and params.cross_platform.enable_cross_platform:
        cp_result = calculate_cross_platform(params, current_month, users, token_price)
        results['cross_platform'] = cp_result
        results['total_revenue'] += cp_result.get('revenue', 0)
        results['total_profit'] += cp_result.get('profit', 0)
    
    return results


def apply_market_cycle_multipliers(
    base_growth_rate: float,
    base_retention: float,
    base_price_multiplier: float,
    year: int,
    month_in_year: int
) -> Dict[str, float]:
    """
    Apply market cycle multipliers based on year.
    
    Args:
        base_growth_rate: Base growth rate
        base_retention: Base retention rate
        base_price_multiplier: Base price multiplier
        year: Calendar year (2025-2030)
        month_in_year: Month within the year (1-12)
    
    Returns:
        Dict with adjusted rates
    """
    multipliers = get_cycle_multipliers(year, month_in_year - 1)
    
    return {
        'growth_rate': base_growth_rate * multipliers['growth_multiplier'],
        'retention_rate': base_retention * multipliers['retention_multiplier'],
        'price_multiplier': base_price_multiplier * multipliers['price_multiplier'],
        'phase': multipliers.get('phase', 'Unknown'),
    }


# Seasonality multipliers by month (1-12)
# Based on typical social media app patterns
SEASONALITY_MULTIPLIERS = {
    1: 1.15,   # January: New Year resolutions
    2: 0.95,   # February: Post-holiday dip
    3: 1.00,   # March: Stable
    4: 1.00,   # April: Stable
    5: 0.95,   # May: Pre-summer slowdown
    6: 0.85,   # June: Summer dip
    7: 0.80,   # July: Peak summer dip
    8: 0.85,   # August: Late summer
    9: 1.05,   # September: Back to school
    10: 1.10,  # October: Pre-holiday
    11: 1.20,  # November: Holiday shopping
    12: 1.25,  # December: Peak holiday season
}


# === TOKEN ALLOCATION VESTING SCHEDULE (November 2025) ===

def calculate_vesting_unlock(month: int) -> Dict[str, int]:
    """
    Calculate token unlocks for each category at a given month.
    
    Based on official VCoin tokenomics:
    - Seed: 2% (20M), 0% TGE, 12 month cliff, 24 month vesting
    - Private: 3% (30M), 10% TGE, 6 month cliff, 18 month vesting  
    - Public: 5% (50M), 50% TGE, 0 cliff, 3 month vesting
    - Team: 10% (100M), 0% TGE, 12 month cliff, 36 month vesting
    - Advisors: 5% (50M), 0% TGE, 6 month cliff, 18 month vesting
    - Treasury: 20% (200M), Programmatic release
    - Rewards: 35% (350M), 5,833,333/month for 60 months
    - Liquidity: 10% (100M), 100% TGE
    - Foundation: 2% (20M), 25% TGE, 3 month cliff, 24 month vesting
    - Marketing: 8% (80M), 25% TGE, 3 month cliff, 18 month vesting
    
    Args:
        month: Month number (0 = TGE, 1 = first month after TGE, etc.)
    
    Returns:
        Dict with unlock amounts per category
    """
    unlocks = {
        'seed': 0,
        'private': 0,
        'public': 0,
        'team': 0,
        'advisors': 0,
        'treasury': 0,
        'rewards': 0,
        'liquidity': 0,
        'foundation': 0,
        'marketing': 0,
    }
    
    # TGE (month 0)
    # CRIT-01 Fix: Rewards should NOT emit at TGE - only months 1-60
    # TGE is the token generation event; rewards emission starts month 1
    if month == 0:
        unlocks['private'] = 3_000_000      # 10% of 30M
        unlocks['public'] = 25_000_000      # 50% of 50M
        unlocks['liquidity'] = 100_000_000  # 100% of 100M
        unlocks['foundation'] = 5_000_000   # 25% of 20M
        unlocks['marketing'] = 20_000_000   # 25% of 80M
        # unlocks['rewards'] removed - rewards start month 1, not TGE
        return unlocks
    
    # Seed: 20M total, 0% TGE, cliff 12, vesting 24 months
    # After cliff (M12), vest 20M / 24 = 833,333/month for 24 months (M13-M36)
    if 13 <= month <= 36:
        unlocks['seed'] = 833_333
    
    # Private: 30M total, 10% TGE (3M), cliff 6, vesting 18 months
    # After cliff (M6), vest (30M - 3M) / 18 = 1,500,000/month for 18 months (M7-M24)
    if 7 <= month <= 24:
        unlocks['private'] = 1_500_000
    
    # Public: 50M total, 50% TGE (25M), no cliff, vesting 3 months
    # Vest (50M - 25M) / 3 = 8,333,333/month for 3 months (M1-M3)
    if 1 <= month <= 3:
        unlocks['public'] = 8_333_333
    
    # Team: 100M total, 0% TGE, 12 month cliff, 36 month vesting period
    # After cliff ends at M12, vest 100M over 36 months (M13-M48)
    # Monthly unlock: 100M / 36 = 2,777,778 VCoin
    if 13 <= month <= 48:
        unlocks['team'] = 2_777_778
    
    # Advisors: 50M total, 0% TGE, cliff 6, vesting 18 months
    # After cliff (M6), vest 50M / 18 = 2,777,778/month for 18 months (M7-M24)
    if 7 <= month <= 24:
        unlocks['advisors'] = 2_777_778
    
    # Treasury: 200M (20% of supply) - Programmatic/Governance-Controlled Release
    # 
    # IMPORTANT: Treasury unlocks are NOT included in the vesting schedule because:
    # 1. Treasury releases are governance-controlled (DAO votes required)
    # 2. Release timing and amounts depend on protocol needs (grants, partnerships, etc.)
    # 3. This provides flexibility for the protocol to respond to market conditions
    # 
    # Treasury funds may be used for:
    # - Community grants and ecosystem development
    # - Strategic partnerships and integrations
    # - Protocol development and maintenance
    # - Emergency reserves and liquidity support
    # 
    # To model treasury releases, use the governance module or add custom logic.
    unlocks['treasury'] = 0
    
    # Rewards: 350M / 60 months = 5,833,333/month
    if 1 <= month <= 60:
        unlocks['rewards'] = 5_833_333
    
    # Issue #8 Fix: Corrected vesting calculation comments
    # Foundation: 20M total, 25% TGE (5M), cliff 3 months, vesting over 24 months
    # After cliff (M3), vest (20M - 5M) / 24 = 625,000/month for 24 months (M4-M27)
    if 4 <= month <= 27:
        unlocks['foundation'] = 625_000
    
    # Marketing: 80M total, 25% TGE (20M), cliff 3 months, vesting over 18 months
    # After cliff (M3), vest (80M - 20M) / 18 = 3,333,333/month for 18 months (M4-M21)
    if 4 <= month <= 21:
        unlocks['marketing'] = 3_333_333
    
    return unlocks


def calculate_circulating_supply_at_month(month: int) -> CirculatingSupplyResult:
    """
    Calculate cumulative circulating supply at a given month.
    
    Args:
        month: Month number (0 = TGE)
    
    Returns:
        CirculatingSupplyResult with detailed breakdown
    """
    # Calculate cumulative unlocks from TGE to this month
    cumulative = {
        'seed': 0,
        'private': 0,
        'public': 0,
        'team': 0,
        'advisors': 0,
        'treasury': 0,
        'rewards': 0,
        'liquidity': 0,
        'foundation': 0,
        'marketing': 0,
    }
    
    # Sum all unlocks from month 0 to current month
    for m in range(month + 1):
        unlocks = calculate_vesting_unlock(m)
        for key in cumulative:
            cumulative[key] += unlocks.get(key, 0)
    
    # Get this month's unlocks
    current_unlocks = calculate_vesting_unlock(month)
    total_new_unlocks = sum(current_unlocks.values())
    
    # Calculate total circulating
    total_circulating = sum(cumulative.values())
    total_supply = 1_000_000_000
    circulating_percent = (total_circulating / total_supply) * 100
    
    # Build category breakdown
    category_breakdown = {}
    allocations = {
        'seed': 20_000_000,
        'private': 30_000_000,
        'public': 50_000_000,
        'team': 100_000_000,
        'advisors': 50_000_000,
        'treasury': 200_000_000,
        'rewards': 350_000_000,
        'liquidity': 100_000_000,
        'foundation': 20_000_000,
        'marketing': 80_000_000,
    }
    
    for key, total in allocations.items():
        category_breakdown[key] = TokenCategoryUnlock(
            category=key,
            tokens_unlocked=current_unlocks.get(key, 0),
            cumulative_unlocked=cumulative.get(key, 0),
            total_allocation=total,
            percent_unlocked=(cumulative.get(key, 0) / total * 100) if total > 0 else 0,
        )
    
    return CirculatingSupplyResult(
        month=month,
        seed_unlock=current_unlocks.get('seed', 0),
        private_unlock=current_unlocks.get('private', 0),
        public_unlock=current_unlocks.get('public', 0),
        team_unlock=current_unlocks.get('team', 0),
        advisors_unlock=current_unlocks.get('advisors', 0),
        treasury_unlock=current_unlocks.get('treasury', 0),
        rewards_unlock=current_unlocks.get('rewards', 0),
        liquidity_unlock=current_unlocks.get('liquidity', 0),
        foundation_unlock=current_unlocks.get('foundation', 0),
        marketing_unlock=current_unlocks.get('marketing', 0),
        total_new_unlocks=total_new_unlocks,
        cumulative_circulating=total_circulating,
        circulating_percent=round(circulating_percent, 2),
        category_breakdown=category_breakdown,
    )


def generate_full_vesting_schedule(duration_months: int = 60) -> VestingScheduleResult:
    """
    Generate the complete vesting schedule for all 60 months.
    
    Returns:
        VestingScheduleResult with monthly supply data
    """
    monthly_supply = []
    
    # TGE (month 0)
    tge_supply = calculate_circulating_supply_at_month(0)
    monthly_supply.append(tge_supply)
    
    # Track milestones
    month_25 = 0
    month_50 = 0
    month_75 = 0
    
    for month in range(1, duration_months + 1):
        supply = calculate_circulating_supply_at_month(month)
        monthly_supply.append(supply)
        
        # Track milestone months
        if month_25 == 0 and supply.circulating_percent >= 25:
            month_25 = month
        if month_50 == 0 and supply.circulating_percent >= 50:
            month_50 = month
        if month_75 == 0 and supply.circulating_percent >= 75:
            month_75 = month
    
    final_supply = monthly_supply[-1] if monthly_supply else calculate_circulating_supply_at_month(0)
    
    # MED-01 Fix: Use dynamic TGE value from monthly_supply instead of hardcoded value
    tge_supply = monthly_supply[0] if monthly_supply else calculate_circulating_supply_at_month(0)
    
    return VestingScheduleResult(
        duration_months=duration_months,
        monthly_supply=monthly_supply,
        tge_circulating=tge_supply.cumulative_circulating,  # MED-01: Was hardcoded 158_833_333
        final_circulating=final_supply.cumulative_circulating,
        max_circulating=1_000_000_000,
        month_25_percent_circulating=month_25,
        month_50_percent_circulating=month_50,
        month_75_percent_circulating=month_75,
        month_full_circulating=60,
        seed_completion_month=36,
        private_completion_month=24,  # CRIT-02 Fix: was 18, but vests M7-M24
        public_completion_month=3,
        team_completion_month=48,
        advisors_completion_month=24,  # CRIT-03 Fix: was 18, but vests M7-M24
        foundation_completion_month=27,
        marketing_completion_month=21,
        rewards_completion_month=60,
    )


@dataclass
class MonthlyMetrics:
    """Metrics for a single month in the projection"""
    month: int
    
    # User metrics
    users_acquired: int
    users_churned: int
    active_users: int
    total_acquired_lifetime: int
    retention_rate: float
    
    # Financial metrics
    revenue: float
    costs: float
    profit: float
    margin: float
    
    # Module breakdown
    identity_revenue: float
    content_revenue: float
    advertising_revenue: float
    exchange_revenue: float
    platform_fee_revenue: float
    
    # Token metrics
    tokens_distributed: float
    tokens_recaptured: float
    recapture_rate: float
    net_emission: float
    
    # Acquisition metrics
    cac_effective: float
    ltv_estimate: float
    marketing_spend: float
    
    # Derived metrics
    arpu: float  # Average Revenue Per User
    arr: float   # Annualized Recurring Revenue
    
    # Cohort breakdown (optional)
    cohort_breakdown: Dict[int, int] = field(default_factory=dict)
    
    # Growth scenario fields (NEW - Nov 2025)
    fomo_event: Optional[FomoEvent] = None
    token_price: float = 0.03
    scenario_multiplier: float = 1.0
    growth_rate: float = 0.0
    
    # Dynamic allocation fields (NEW - Nov 2025)
    dynamic_allocation_percent: float = 0.0  # Current allocation percentage
    dynamic_growth_factor: float = 0.0  # User growth factor (0-1)
    per_user_monthly_vcoin: float = 0.0  # VCoin per user per month
    per_user_monthly_usd: float = 0.0  # USD equivalent per user per month
    allocation_capped: bool = False  # Whether per-user cap was applied
    
    # Token allocation / vesting fields (NEW - Nov 2025)
    circulating_supply: int = 0  # Total circulating supply at this month
    circulating_percent: float = 0.0  # Percentage of total supply
    new_unlocks: int = 0  # New tokens unlocked this month
    
    # Treasury tracking (NEW - Nov 2025)
    treasury_revenue_usd: float = 0.0  # Revenue going to treasury this month
    treasury_accumulated_usd: float = 0.0  # Cumulative treasury balance
    
    # 5A Policy fields (NEW - Dec 2025)
    five_a_enabled: bool = False
    five_a_avg_multiplier: float = 1.0  # Average compound multiplier
    five_a_reward_redistribution: float = 0.0  # Percentage redistributed
    five_a_fee_discount_total: float = 0.0  # Total fee discounts in USD
    five_a_staking_apy_boost: float = 0.0  # Average staking APY boost
    five_a_governance_boost: float = 0.0  # Average governance power boost
    five_a_avg_identity_pct: float = 50.0  # Average identity star percentage
    five_a_avg_activity_pct: float = 50.0  # Average activity star percentage
    
    # 5A Dynamic Evolution fields (NEW - Dec 2025)
    five_a_segment_inactive: int = 0  # Users in inactive segment
    five_a_segment_lurkers: int = 0   # Users in lurkers segment
    five_a_segment_casual: int = 0    # Users in casual segment
    five_a_segment_active: int = 0    # Users in active segment
    five_a_segment_power: int = 0     # Users in power_users segment
    five_a_retention_boost: float = 1.0  # Retention multiplier from 5A
    five_a_growth_boost: float = 1.0     # Growth multiplier from 5A
    five_a_price_impact: float = 0.0     # Price impact percentage
    five_a_churned_users: int = 0        # Users churned due to 5A evolution
    five_a_improved_users: int = 0       # Users who improved segments
    five_a_decayed_users: int = 0        # Users who decayed segments


@dataclass
class MonthlyProgressionResult:
    """Complete result of monthly progression simulation"""
    duration_months: int
    monthly_data: List[MonthlyMetrics]
    
    # Summary statistics
    total_users_acquired: int
    peak_active_users: int
    final_active_users: int
    average_retention_rate: float
    
    total_revenue: float
    total_costs: float
    total_profit: float
    average_margin: float
    
    # Growth metrics
    cagr_users: float  # Compound Annual Growth Rate for users
    cagr_revenue: float  # CAGR for revenue
    
    # Token summary
    total_tokens_distributed: float
    total_tokens_recaptured: float
    overall_recapture_rate: float
    
    # Payback period
    months_to_profitability: Optional[int]
    cumulative_profit_curve: List[float]
    
    # Retention analysis
    retention_curve: Dict[int, float]  # Month -> retention rate
    
    # Growth scenario data (NEW - Nov 2025)
    growth_projection: Optional[GrowthProjectionResult] = None
    scenario_used: Optional[str] = None
    market_condition_used: Optional[str] = None
    # Issue #2 Fix: Changed from List[FomoEvent] to List[FomoEventResult] for proper API serialization
    fomo_events_triggered: List[FomoEventResult] = field(default_factory=list)
    token_price_final: float = 0.03
    
    # Token allocation / vesting (NEW - Nov 2025)
    vesting_schedule: Optional[VestingScheduleResult] = None
    final_circulating_supply: int = 0
    final_circulating_percent: float = 0.0
    
    # Treasury tracking (NEW - Nov 2025)
    treasury_result: Optional[TreasuryResult] = None
    total_treasury_accumulated_usd: float = 0.0
    total_treasury_accumulated_vcoin: float = 0.0


def calculate_seasonality_multiplier(month_number: int, apply_seasonality: bool) -> float:
    """Get seasonality multiplier for a given month (1-12)"""
    if not apply_seasonality:
        return 1.0
    
    # Convert to 1-12 range
    month_in_year = ((month_number - 1) % 12) + 1
    return SEASONALITY_MULTIPLIERS.get(month_in_year, 1.0)


def calculate_saturated_cac(
    base_cac: float,
    market_penetration: float,
    saturation_factor: float = 0.5
) -> float:
    """
    Issue #14: CAC increases as market saturates.
    
    Args:
        base_cac: Starting CAC
        market_penetration: Current market penetration (0-1)
        saturation_factor: How aggressively CAC increases (0-1)
    
    Returns:
        Adjusted CAC
    """
    # CAC increases exponentially with market penetration
    # At 50% penetration with factor 0.5, CAC increases by ~64%
    saturation_multiplier = 1 + (market_penetration ** 2) * 3 * saturation_factor
    return base_cac * saturation_multiplier


def estimate_ltv(
    arpu_monthly: float,
    retention_curve: RetentionCurve,
    months: int = 24,
    arpu_growth_rate: float = 0.0
) -> float:
    """
    Estimate Lifetime Value based on ARPU, retention curve, and ARPU growth.
    
    LTV = Sum of (Monthly Revenue × Retention Rate) over lifetime
    
    Args:
        arpu_monthly: Starting Average Revenue Per User per month
        retention_curve: Retention curve defining user drop-off
        months: Number of months to project (default 24)
        arpu_growth_rate: Monthly ARPU growth rate (default 0.0, e.g., 0.02 = 2%)
            Typically ARPU grows as users become more engaged and adopt premium features.
    
    Returns:
        Estimated Lifetime Value in same currency as arpu_monthly
    """
    ltv = 0
    current_arpu = arpu_monthly
    for month in range(1, months + 1):
        retention = retention_curve.get_retention_at_month(month)
        ltv += current_arpu * retention
        # Apply ARPU growth for next month
        current_arpu *= (1 + arpu_growth_rate)
    return ltv


def run_monthly_progression_simulation(
    params: SimulationParameters,
    duration_months: int = 24,
    include_seasonality: bool = True,
    market_saturation_factor: float = 0.0,
    target_market_size: int = 1_000_000,  # Total addressable market
    progress_callback: Optional[Callable[[int, int], None]] = None,
    start_year: int = 2025,  # HIGH-03: Starting year for market cycle
    start_month: int = 3,    # HIGH-03: Starting month (default March)
    apply_market_cycle: bool = True,  # HIGH-03: Apply 5-year market cycle
) -> MonthlyProgressionResult:
    """
    Run monthly progression simulation with retention, seasonality, and market dynamics.
    
    Args:
        params: Base simulation parameters
        duration_months: How many months to project (6-60)
        include_seasonality: Apply seasonal adjustments
        market_saturation_factor: How saturated the market is (0-1)
        target_market_size: Total addressable market for saturation calc
        progress_callback: Optional callback for progress updates
        start_year: Calendar year when simulation starts (default 2025)
        start_month: Calendar month when simulation starts (default March = 3)
        apply_market_cycle: Whether to apply 5-year market cycle adjustments
    
    Returns:
        MonthlyProgressionResult with full time-series data
    
    HIGH-03 Fix: Added market cycle integration for simulations > 12 months.
    Uses MARKET_CYCLE_2025_2030 for growth, retention, and price multipliers.
    """
    # Select retention curve based on parameters
    retention_curve = VCOIN_RETENTION
    if hasattr(params, 'retention') and params.retention:
        model_type = params.retention.model_type
        if model_type.value in [m.value for m in RetentionModel]:
            retention_curve = RETENTION_CURVES.get(
                RetentionModel(model_type.value), 
                VCOIN_RETENTION
            )
    
    # Initialize cohort tracker
    tracker = CohortTracker(retention_curve)
    
    # Track monthly results
    monthly_data: List[MonthlyMetrics] = []
    
    # Running totals
    total_revenue = 0
    total_costs = 0
    total_tokens_distributed = 0
    total_tokens_recaptured = 0
    cumulative_profit = 0
    cumulative_profit_curve = []
    
    # Track profitability
    months_to_profitability = None
    
    # Base monthly marketing budget
    base_monthly_marketing = params.marketing_budget / 12
    
    # 5A Segment Evolution (Dec 2025)
    # Initialize segment counts based on USER_SEGMENTS defaults
    five_a_enabled = params.five_a is not None and params.five_a.enable_five_a
    segment_counts = {
        'inactive': 0,
        'lurkers': 0,
        'casual': 0,
        'active': 0,
        'power_users': 0,
    }
    cumulative_churned_5a = 0
    cumulative_improved = 0
    cumulative_decayed = 0
    
    # HIGH-03: Track current calendar year/month for market cycle
    current_calendar_year = start_year
    current_calendar_month = start_month
    
    for month in range(1, duration_months + 1):
        # Apply seasonality to marketing effectiveness
        seasonality = calculate_seasonality_multiplier(month, include_seasonality)
        
        # HIGH-03: Apply 5-year market cycle multipliers for simulations > 12 months
        cycle_growth_mult = 1.0
        cycle_retention_mult = 1.0
        cycle_price_mult = 1.0
        cycle_phase = "Year 1"
        
        if apply_market_cycle and duration_months > 12:
            cycle_data = apply_market_cycle_multipliers(
                base_growth_rate=1.0,
                base_retention=1.0,
                base_price_multiplier=1.0,
                year=current_calendar_year,
                month_in_year=current_calendar_month
            )
            cycle_growth_mult = cycle_data['growth_rate']
            cycle_retention_mult = cycle_data['retention_rate']
            cycle_price_mult = cycle_data['price_multiplier']
            cycle_phase = cycle_data.get('phase', 'Unknown')
        
        # Advance calendar month/year for next iteration
        current_calendar_month += 1
        if current_calendar_month > 12:
            current_calendar_month = 1
            current_calendar_year += 1
        
        # Calculate market penetration
        total_acquired_so_far = tracker.get_total_acquired()
        market_penetration = min(1.0, total_acquired_so_far / target_market_size)
        
        # Calculate effective CAC with saturation
        base_cac = (
            params.cac_north_america_consumer * params.north_america_budget_percent +
            params.cac_global_low_income_consumer * params.global_low_income_budget_percent
        )
        effective_cac = calculate_saturated_cac(
            base_cac, 
            market_penetration, 
            market_saturation_factor
        )
        
        # HIGH-03: Apply market cycle growth multiplier to user acquisition
        effective_cac = effective_cac / cycle_growth_mult if cycle_growth_mult > 0 else effective_cac
        
        # Calculate users acquired this month
        monthly_marketing = base_monthly_marketing * seasonality
        
        # Creator acquisition (fixed monthly targets)
        monthly_creator_cost = (
            (params.high_quality_creators_needed / 12) * params.high_quality_creator_cac +
            (params.mid_level_creators_needed / 12) * params.mid_level_creator_cac
        )
        
        consumer_budget = max(0, monthly_marketing - monthly_creator_cost)
        consumers_acquired = int(consumer_budget / effective_cac) if effective_cac > 0 else 0
        creators_acquired = int(
            (params.high_quality_creators_needed + params.mid_level_creators_needed) / 12
        )
        
        total_acquired_this_month = consumers_acquired + creators_acquired
        
        # Add cohort to tracker
        tracker.add_cohort(month, total_acquired_this_month)
        
        # Calculate active users with retention
        base_active_users = tracker.get_active_users_at_month(month)
        
        # HIGH-03: Apply market cycle retention multiplier
        # Bull markets have better retention (people stay engaged with crypto)
        # Bear markets have worse retention (people lose interest)
        if apply_market_cycle and duration_months > 12 and cycle_retention_mult != 1.0:
            # Adjust active users based on cycle retention
            retention_adjustment = (cycle_retention_mult - 1.0) * 0.3  # Dampen the effect
            active_users = int(base_active_users * (1 + retention_adjustment))
        else:
            active_users = base_active_users
        
        # Calculate churned users
        prev_active = monthly_data[-1].active_users if monthly_data else 0
        users_churned = max(0, prev_active + total_acquired_this_month - active_users)
        
        # === 5A SEGMENT EVOLUTION (Dec 2025) ===
        # Evolve user segments monthly and calculate 5A impacts
        five_a_retention_boost_val = 1.0
        five_a_growth_boost_val = 1.0
        five_a_price_impact_val = 0.0
        five_a_churned_from_evolution = 0
        five_a_improved = 0
        five_a_decayed = 0
        
        if five_a_enabled and active_users > 0:
            # Calculate platform maturity (increases improvement rates)
            platform_maturity = calculate_platform_maturity(month, duration_months)
            
            # Evolve existing segments and add new users
            evolution_result = evolve_user_segments(
                current_counts=segment_counts,
                month=month,
                platform_maturity=platform_maturity,
                new_users=total_acquired_this_month,
            )
            
            # Update segment counts
            segment_counts = evolution_result['counts']
            five_a_churned_from_evolution = evolution_result['churned']
            five_a_improved = evolution_result['improved']
            five_a_decayed = evolution_result['decayed']
            
            # Track cumulative evolution stats
            cumulative_churned_5a += five_a_churned_from_evolution
            cumulative_improved += five_a_improved
            cumulative_decayed += five_a_decayed
            
            # Calculate segment distribution as percentages
            total_in_segments = sum(segment_counts.values())
            if total_in_segments > 0:
                segment_distribution = {
                    seg: count / total_in_segments 
                    for seg, count in segment_counts.items()
                }
            else:
                # Default distribution for empty segments
                segment_distribution = {
                    'inactive': 0.20, 'lurkers': 0.40, 'casual': 0.25,
                    'active': 0.12, 'power_users': 0.03
                }
            
            # Calculate 5A retention boost
            five_a_retention_boost_val = calculate_five_a_retention_boost(segment_distribution)
            
            # Calculate 5A growth boost
            active_percent = (
                segment_distribution.get('active', 0.12) +
                segment_distribution.get('power_users', 0.03)
            )
            avg_5a_mult = 0.6  # Will be updated after sim runs
            five_a_growth_boost_val = calculate_five_a_growth_boost(avg_5a_mult, active_percent)
            
            # Calculate 5A price impact
            # Get burns from previous month (or estimate for first month)
            prev_burns = total_tokens_recaptured * 0.1  # Estimate ~10% of recapture is burns
            circulating = params.initial_liquidity_vcoin * 2 if hasattr(params, 'initial_liquidity_vcoin') else 100_000_000
            price_impact_result = calculate_five_a_price_impact(
                avg_multiplier=avg_5a_mult,
                active_percent=active_percent,
                monthly_burns=prev_burns,
                circulating_supply=circulating,
                segment_distribution=segment_distribution,
            )
            five_a_price_impact_val = (price_impact_result.get('total_multiplier', 1.0) - 1.0) * 100  # As percentage
        else:
            # Initialize segment counts for first month if not using 5A
            if month == 1 and active_users > 0:
                segment_counts = {
                    'inactive': int(active_users * 0.20),
                    'lurkers': int(active_users * 0.40),
                    'casual': int(active_users * 0.25),
                    'active': int(active_users * 0.12),
                    'power_users': int(active_users * 0.03),
                }
            segment_distribution = {
                'inactive': 0.20, 'lurkers': 0.40, 'casual': 0.25,
                'active': 0.12, 'power_users': 0.03
            }
        
        # Run deterministic simulation for this month's active users
        # Create a modified params with current active users
        month_params = params.model_copy()
        month_params.starting_users = active_users
        # Disable retention in deterministic sim - cohort tracker already handles retention
        month_params.apply_retention = False
        # Disable growth scenarios in deterministic sim - we handle them separately
        month_params.use_growth_scenarios = False
        
        # Run simulation
        sim_result = run_deterministic_simulation(month_params)
        
        # Calculate ARPU
        month_revenue = sim_result.totals.revenue
        arpu = month_revenue / active_users if active_users > 0 else 0
        
        # Calculate LTV estimate
        ltv = estimate_ltv(arpu, retention_curve)
        
        # Token metrics
        tokens_distributed = sim_result.rewards.monthly_emission
        tokens_recaptured = sim_result.recapture.total_recaptured
        recapture_rate = sim_result.recapture.recapture_rate
        
        # Add compliance costs if enabled
        compliance_cost = 0
        if params.include_compliance_costs and hasattr(params, 'compliance'):
            compliance_cost = params.compliance.monthly_total
        
        month_costs = sim_result.totals.costs + compliance_cost
        month_profit = month_revenue - month_costs
        month_margin = (month_profit / month_revenue * 100) if month_revenue > 0 else 0
        
        # Update running totals
        total_revenue += month_revenue
        total_costs += month_costs
        cumulative_profit += month_profit
        cumulative_profit_curve.append(cumulative_profit)
        total_tokens_distributed += tokens_distributed
        total_tokens_recaptured += tokens_recaptured
        
        # Track profitability milestone
        if months_to_profitability is None and cumulative_profit > 0:
            months_to_profitability = month
        
        # Get cohort breakdown
        cohort_breakdown = tracker.get_cohort_breakdown(month)
        
        # Get retention stats
        retention_stats = tracker.get_retention_stats(month)
        
        # Extract 5A metrics if available
        five_a = sim_result.five_a
        five_a_enabled = five_a.enabled if five_a else False
        
        # Create monthly metrics
        metrics = MonthlyMetrics(
            month=month,
            users_acquired=total_acquired_this_month,
            users_churned=users_churned,
            active_users=active_users,
            total_acquired_lifetime=tracker.get_total_acquired(),
            retention_rate=round(retention_stats['overall_retention_rate'] * 100, 2),
            revenue=round(month_revenue, 2),
            costs=round(month_costs, 2),
            profit=round(month_profit, 2),
            margin=round(month_margin, 1),
            identity_revenue=round(sim_result.identity.revenue, 2),
            content_revenue=round(sim_result.content.revenue, 2),
            advertising_revenue=round(sim_result.advertising.revenue, 2),
            exchange_revenue=round(sim_result.exchange.revenue, 2),
            platform_fee_revenue=round(sim_result.platform_fees.reward_fee_usd, 2),
            tokens_distributed=round(tokens_distributed, 2),
            tokens_recaptured=round(tokens_recaptured, 2),
            recapture_rate=round(recapture_rate, 1),
            net_emission=round(tokens_distributed - tokens_recaptured, 2),
            cac_effective=round(effective_cac, 2),
            ltv_estimate=round(ltv, 2),
            marketing_spend=round(monthly_marketing, 2),
            arpu=round(arpu, 2),
            arr=round(month_revenue * 12, 2),
            cohort_breakdown=cohort_breakdown,
            # Dynamic allocation fields
            dynamic_allocation_percent=round(sim_result.rewards.dynamic_allocation_percent * 100, 2),
            dynamic_growth_factor=round(sim_result.rewards.growth_factor, 4),
            per_user_monthly_vcoin=round(sim_result.rewards.per_user_monthly_vcoin, 2),
            per_user_monthly_usd=round(sim_result.rewards.per_user_monthly_usd, 4),
            allocation_capped=sim_result.rewards.allocation_capped,
            # 5A Policy fields (Dec 2025)
            five_a_enabled=five_a.enabled if five_a else False,
            five_a_avg_multiplier=round(five_a.avg_compound_multiplier, 3) if five_a else 1.0,
            five_a_reward_redistribution=round(five_a.reward_redistribution_percent, 2) if five_a else 0.0,
            five_a_fee_discount_total=round(five_a.fee_discount_total_usd, 2) if five_a else 0.0,
            five_a_staking_apy_boost=round(five_a.staking_apy_boost_avg, 2) if five_a else 0.0,
            five_a_governance_boost=round(five_a.governance_power_boost_avg, 2) if five_a else 0.0,
            five_a_avg_identity_pct=round(five_a.population_avg_identity, 1) if five_a else 50.0,
            five_a_avg_activity_pct=round(five_a.population_avg_activity, 1) if five_a else 50.0,
            # 5A Dynamic Evolution fields (Dec 2025)
            five_a_segment_inactive=segment_counts.get('inactive', 0),
            five_a_segment_lurkers=segment_counts.get('lurkers', 0),
            five_a_segment_casual=segment_counts.get('casual', 0),
            five_a_segment_active=segment_counts.get('active', 0),
            five_a_segment_power=segment_counts.get('power_users', 0),
            five_a_retention_boost=round(five_a_retention_boost_val, 3),
            five_a_growth_boost=round(five_a_growth_boost_val, 3),
            five_a_price_impact=round(five_a_price_impact_val, 2),
            five_a_churned_users=five_a_churned_from_evolution,
            five_a_improved_users=five_a_improved,
            five_a_decayed_users=five_a_decayed,
        )
        
        monthly_data.append(metrics)
        
        # Progress callback
        if progress_callback:
            progress_callback(month, duration_months)
    
    # Calculate summary statistics
    active_users_list = [m.active_users for m in monthly_data]
    peak_active_users = max(active_users_list) if active_users_list else 0
    final_active_users = monthly_data[-1].active_users if monthly_data else 0
    
    avg_retention = sum(m.retention_rate for m in monthly_data) / len(monthly_data) if monthly_data else 0
    avg_margin = sum(m.margin for m in monthly_data) / len(monthly_data) if monthly_data else 0
    
    # Calculate CAGR
    # HIGH-004 Fix: CAGR is only meaningful for periods >= 12 months
    # For shorter periods, the annualization creates misleading results
    # (e.g., 2x growth in 6 months = 300% CAGR, which is technically correct but misleading)
    def calculate_cagr(start: float, end: float, periods_in_years: float) -> float:
        if start <= 0 or end <= 0 or periods_in_years <= 0:
            return 0
        # HIGH-004 Fix: Return 0 for periods < 1 year to avoid misleading CAGR
        # CAGR is Compound ANNUAL Growth Rate - sub-year periods are extrapolated
        if periods_in_years < 1.0:
            # For sub-year periods, return simple growth rate instead of CAGR
            # This is more intuitive: "grew 50% in 6 months" vs "300% CAGR"
            return 0  # Return 0 to indicate CAGR not applicable
        return ((end / start) ** (1 / periods_in_years) - 1) * 100
    
    cagr_users = calculate_cagr(
        monthly_data[0].active_users if monthly_data else 1,
        final_active_users,
        duration_months / 12
    ) if monthly_data else 0
    
    first_revenue = monthly_data[0].revenue if monthly_data else 1
    last_revenue = monthly_data[-1].revenue if monthly_data else 1
    cagr_revenue = calculate_cagr(
        first_revenue if first_revenue > 0 else 1,
        last_revenue if last_revenue > 0 else 1,
        duration_months / 12
    )
    
    # Build retention curve summary
    retention_summary = {}
    for month in [1, 3, 6, 12, 24, 36]:
        if month <= duration_months:
            retention_summary[month] = round(
                retention_curve.get_retention_at_month(month) * 100, 
                1
            )
    
    # Overall recapture rate
    overall_recapture = (
        total_tokens_recaptured / total_tokens_distributed * 100
        if total_tokens_distributed > 0 else 0
    )
    
    # Generate vesting schedule if tracking is enabled
    track_vesting = getattr(params, 'track_vesting_schedule', True)
    vesting_schedule = None
    final_circulating = 0
    final_circulating_pct = 0.0
    
    if track_vesting:
        vesting_schedule = generate_full_vesting_schedule(min(duration_months, 60))
        if vesting_schedule.monthly_supply:
            final_idx = min(duration_months, len(vesting_schedule.monthly_supply) - 1)
            final_supply = vesting_schedule.monthly_supply[final_idx]
            final_circulating = final_supply.cumulative_circulating
            final_circulating_pct = final_supply.circulating_percent
            
            # Update monthly_data with circulating supply info
            for i, metrics in enumerate(monthly_data):
                if i < len(vesting_schedule.monthly_supply):
                    supply = vesting_schedule.monthly_supply[i]
                    metrics.circulating_supply = supply.cumulative_circulating
                    metrics.circulating_percent = supply.circulating_percent
                    metrics.new_unlocks = supply.total_new_unlocks
    
    # Calculate treasury accumulation
    treasury_revenue_share = getattr(params, 'treasury_revenue_share', 0.20)
    total_treasury_usd = 0.0
    cumulative_treasury = 0.0
    
    for metrics in monthly_data:
        treasury_contribution = metrics.revenue * treasury_revenue_share
        cumulative_treasury += treasury_contribution
        metrics.treasury_revenue_usd = round(treasury_contribution, 2)
        metrics.treasury_accumulated_usd = round(cumulative_treasury, 2)
    
    total_treasury_usd = cumulative_treasury
    total_treasury_vcoin = total_treasury_usd / params.token_price if params.token_price > 0 else 0
    
    treasury_result = TreasuryResult(
        revenue_contribution_usd=round(total_treasury_usd, 2),
        revenue_contribution_vcoin=round(total_treasury_vcoin, 2),
        total_accumulated_usd=round(total_treasury_usd, 2),
        total_accumulated_vcoin=round(total_treasury_vcoin, 2),
        revenue_share_rate=treasury_revenue_share,
    )
    
    return MonthlyProgressionResult(
        duration_months=duration_months,
        monthly_data=monthly_data,
        total_users_acquired=tracker.get_total_acquired(),
        peak_active_users=peak_active_users,
        final_active_users=final_active_users,
        average_retention_rate=round(avg_retention, 1),
        total_revenue=round(total_revenue, 2),
        total_costs=round(total_costs, 2),
        total_profit=round(total_revenue - total_costs, 2),
        average_margin=round(avg_margin, 1),
        cagr_users=round(cagr_users, 1),
        cagr_revenue=round(cagr_revenue, 1),
        total_tokens_distributed=round(total_tokens_distributed, 2),
        total_tokens_recaptured=round(total_tokens_recaptured, 2),
        overall_recapture_rate=round(overall_recapture, 1),
        months_to_profitability=months_to_profitability,
        cumulative_profit_curve=[round(p, 2) for p in cumulative_profit_curve],
        retention_curve=retention_summary,
        # Vesting schedule (NEW - Nov 2025)
        vesting_schedule=vesting_schedule,
        final_circulating_supply=final_circulating,
        final_circulating_percent=final_circulating_pct,
        # Treasury (NEW - Nov 2025)
        treasury_result=treasury_result,
        total_treasury_accumulated_usd=round(total_treasury_usd, 2),
        total_treasury_accumulated_vcoin=round(total_treasury_vcoin, 2),
    )


def run_growth_scenario_simulation(
    params: SimulationParameters,
    duration_months: int = 12,
    include_seasonality: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> MonthlyProgressionResult:
    """
    Run monthly progression simulation using growth scenario projections.
    
    Uses the marketing-calculated users as the base, then applies:
    - Growth scenario multipliers (Conservative 0.8x, Base 1.0x, Bullish 1.5x)
    - FOMO events (partnerships, listings, viral moments)
    - Market condition multipliers
    - Token price projections
    
    Args:
        params: Simulation parameters with growth_scenario and market_condition
        duration_months: How many months to project (max 12 for scenarios)
        include_seasonality: Apply seasonal adjustments
        progress_callback: Optional callback for progress updates
    
    Returns:
        MonthlyProgressionResult with growth scenario data
    
    Note:
        Growth scenarios are limited to 12 months as scenario data (FOMO events,
        growth rates, retention benchmarks) is only defined for the first year.
        For longer projections, use run_monthly_progression_simulation() instead.
    """
    import logging
    from app.core.deterministic import calculate_customer_acquisition
    
    # Limit to 12 months for growth scenarios (that's what we have data for)
    if duration_months > 12:
        logging.warning(
            f"Growth scenario simulation requested for {duration_months} months, "
            f"but scenario data is only available for 12 months. "
            f"Limiting to 12 months. Use run_monthly_progression_simulation() for longer projections."
        )
    duration_months = min(duration_months, 12)
    
    # Map parameter enum to core enum
    scenario_map = {
        GrowthScenarioType.CONSERVATIVE: GrowthScenario.CONSERVATIVE,
        GrowthScenarioType.BASE: GrowthScenario.BASE,
        GrowthScenarioType.BULLISH: GrowthScenario.BULLISH,
    }
    market_map = {
        MarketConditionType.BEAR: MarketCondition.BEAR,
        MarketConditionType.NEUTRAL: MarketCondition.NEUTRAL,
        MarketConditionType.BULL: MarketCondition.BULL,
    }
    
    scenario = scenario_map.get(params.growth_scenario, GrowthScenario.BASE)
    market_condition = market_map.get(params.market_condition, MarketCondition.BULL)
    scenario_config = GROWTH_SCENARIOS[scenario]
    market_config = MARKET_CONDITIONS[market_condition]
    
    # Get base token price
    base_token_price = params.token_price
    
    # Calculate base users from marketing budget (same as regular simulation)
    customer_acquisition = calculate_customer_acquisition(params)
    base_users_from_marketing = customer_acquisition.total_users
    
    # Use override if provided, otherwise use marketing-calculated users
    if params.starting_waitlist_users and params.starting_waitlist_users > 0:
        base_users = params.starting_waitlist_users
    else:
        base_users = base_users_from_marketing
    
    # Apply scenario FOMO multiplier and market condition to get Month 1 users
    # This represents the TGE launch excitement
    scenario_multiplier = scenario_config.month1_fomo_multiplier * market_config.fomo_multiplier
    month1_users = max(1, int(base_users * scenario_multiplier * 0.3))  # 30% dampening for realism
    
    # Store the base users for reference
    waitlist_users = base_users
    
    # Track monthly results
    monthly_data: List[MonthlyMetrics] = []
    monthly_mau: List[int] = []
    monthly_acquired: List[int] = []
    monthly_churned_list: List[int] = []
    monthly_growth_rates: List[float] = []
    token_price_curve: List[float] = []
    fomo_events_triggered: List[FomoEvent] = []
    
    # Running totals
    total_revenue = 0.0
    total_costs = 0.0
    total_tokens_distributed = 0.0
    total_tokens_recaptured = 0.0
    cumulative_profit = 0.0
    cumulative_profit_curve: List[float] = []
    months_to_profitability: Optional[int] = None
    total_users_acquired = 0
    
    current_users = month1_users
    
    # Initialize segment tracking for growth scenario simulation
    segment_counts_gs = {
        'inactive': 0, 'lurkers': 0, 'casual': 0,
        'active': 0, 'power_users': 0
    }
    
    for month in range(1, duration_months + 1):
        # Calculate base token price for this month
        token_price = calculate_token_price(
            month, scenario_config, market_condition, base_token_price
        )
        
        # Apply 5A price impact if enabled
        five_a_enabled = params.five_a is not None and params.five_a.enable_five_a if hasattr(params, 'five_a') and params.five_a else False
        if five_a_enabled and current_users > 0:
            # Calculate platform maturity
            platform_maturity = calculate_platform_maturity(month, duration_months)
            
            # Evolve segments for growth scenario
            evolution_result = evolve_user_segments(
                current_counts=segment_counts_gs,
                month=month,
                platform_maturity=platform_maturity,
                new_users=monthly_acquired[-1] if monthly_acquired else 0,
            )
            segment_counts_gs = evolution_result['counts']
            
            # Calculate segment distribution
            total_in_segs = sum(segment_counts_gs.values())
            if total_in_segs > 0:
                seg_dist = {seg: c / total_in_segs for seg, c in segment_counts_gs.items()}
            else:
                seg_dist = {'inactive': 0.20, 'lurkers': 0.40, 'casual': 0.25, 'active': 0.12, 'power_users': 0.03}
            
            # Calculate active percent and price impact
            active_pct = seg_dist.get('active', 0.12) + seg_dist.get('power_users', 0.03)
            burns_estimate = total_tokens_recaptured * 0.1 if total_tokens_recaptured > 0 else 0
            circulating_estimate = 100_000_000  # Approximate circulating supply
            
            price_impact = calculate_five_a_price_impact(
                avg_multiplier=0.6 + (platform_maturity * 0.4),  # Improves with maturity
                active_percent=active_pct,
                monthly_burns=burns_estimate,
                circulating_supply=circulating_estimate,
                segment_distribution=seg_dist,
            )
            token_price *= price_impact.get('total_multiplier', 1.0)
        
        token_price_curve.append(token_price)
        
        # Calculate growth for this month
        new_users, churned, growth_rate = calculate_monthly_growth(
            month, current_users, scenario_config, market_condition, token_price
        )
        
        # Check for FOMO event this month
        fomo_event = None
        if params.enable_fomo_events:
            fomo_event = get_fomo_event_for_month(month, scenario_config)
            if fomo_event:
                fomo_events_triggered.append(fomo_event)
        
        # Month 1 special handling
        if month == 1:
            users_acquired = month1_users
            users_churned = 0
            active_users = month1_users
        else:
            users_acquired = new_users
            users_churned = churned
            active_users = max(0, current_users + new_users - churned)
        
        total_users_acquired += users_acquired
        current_users = active_users
        
        # Track monthly lists
        monthly_mau.append(active_users)
        monthly_acquired.append(users_acquired)
        monthly_churned_list.append(users_churned)
        monthly_growth_rates.append(growth_rate)
        
        # Apply seasonality to marketing effectiveness
        seasonality = calculate_seasonality_multiplier(month, include_seasonality)
        
        # Run deterministic simulation for this month's active users
        month_params = params.model_copy()
        month_params.starting_users = active_users
        month_params.token_price = token_price
        # Disable retention in deterministic sim - we already handle retention in monthly progression
        month_params.apply_retention = False
        # Disable growth scenarios in deterministic sim - we already handle them in monthly progression
        month_params.use_growth_scenarios = False
        
        # Run simulation
        sim_result = run_deterministic_simulation(month_params)
        
        # Calculate ARPU
        month_revenue = sim_result.totals.revenue
        arpu = month_revenue / active_users if active_users > 0 else 0
        
        # Token metrics
        tokens_distributed = sim_result.rewards.monthly_emission
        tokens_recaptured = sim_result.recapture.total_recaptured
        recapture_rate = sim_result.recapture.recapture_rate
        
        # Add compliance costs if enabled
        compliance_cost = 0
        if params.include_compliance_costs and hasattr(params, 'compliance'):
            compliance_cost = params.compliance.monthly_total
        
        month_costs = sim_result.totals.costs + compliance_cost
        month_profit = month_revenue - month_costs
        month_margin = (month_profit / month_revenue * 100) if month_revenue > 0 else 0
        
        # Update running totals
        total_revenue += month_revenue
        total_costs += month_costs
        cumulative_profit += month_profit
        cumulative_profit_curve.append(cumulative_profit)
        total_tokens_distributed += tokens_distributed
        total_tokens_recaptured += tokens_recaptured
        
        # Track profitability milestone
        if months_to_profitability is None and cumulative_profit > 0:
            months_to_profitability = month
        
        # Extract 5A metrics if available
        five_a = sim_result.five_a
        five_a_enabled = five_a.enabled if five_a else False
        
        # Create monthly metrics with growth scenario data
        metrics = MonthlyMetrics(
            month=month,
            users_acquired=users_acquired,
            users_churned=users_churned,
            active_users=active_users,
            total_acquired_lifetime=total_users_acquired,
            retention_rate=round(
                (active_users / total_users_acquired * 100) if total_users_acquired > 0 else 0, 
                2
            ),
            revenue=round(month_revenue, 2),
            costs=round(month_costs, 2),
            profit=round(month_profit, 2),
            margin=round(month_margin, 1),
            identity_revenue=round(sim_result.identity.revenue, 2),
            content_revenue=round(sim_result.content.revenue, 2),
            advertising_revenue=round(sim_result.advertising.revenue, 2),
            exchange_revenue=round(sim_result.exchange.revenue, 2),
            platform_fee_revenue=round(sim_result.platform_fees.reward_fee_usd, 2),
            tokens_distributed=round(tokens_distributed, 2),
            tokens_recaptured=round(tokens_recaptured, 2),
            recapture_rate=round(recapture_rate, 1),
            net_emission=round(tokens_distributed - tokens_recaptured, 2),
            cac_effective=0.0,  # N/A for growth scenarios
            ltv_estimate=round(arpu * 6, 2),  # Simplified LTV estimate
            marketing_spend=round(params.marketing_budget / 12 * seasonality, 2),
            arpu=round(arpu, 2),
            arr=round(month_revenue * 12, 2),
            cohort_breakdown={},
            # Growth scenario specific fields
            fomo_event=fomo_event,
            token_price=round(token_price, 4),
            scenario_multiplier=round(market_config.growth_multiplier, 2),
            growth_rate=round(growth_rate * 100, 2),
            # Dynamic allocation fields
            dynamic_allocation_percent=round(sim_result.rewards.dynamic_allocation_percent * 100, 2),
            dynamic_growth_factor=round(sim_result.rewards.growth_factor, 4),
            per_user_monthly_vcoin=round(sim_result.rewards.per_user_monthly_vcoin, 2),
            per_user_monthly_usd=round(sim_result.rewards.per_user_monthly_usd, 4),
            allocation_capped=sim_result.rewards.allocation_capped,
            # 5A Policy fields (Dec 2025)
            five_a_enabled=five_a_enabled,
            five_a_avg_multiplier=round(five_a.avg_compound_multiplier, 3) if five_a_enabled else 1.0,
            five_a_reward_redistribution=round(five_a.reward_redistribution_percent, 2) if five_a_enabled else 0.0,
            five_a_fee_discount_total=round(five_a.fee_discount_total_usd, 2) if five_a_enabled else 0.0,
            five_a_staking_apy_boost=round(five_a.staking_apy_boost_avg, 2) if five_a_enabled else 0.0,
            five_a_governance_boost=round(five_a.governance_power_boost_avg, 2) if five_a_enabled else 0.0,
            five_a_avg_identity_pct=round(five_a.population_avg_identity, 1) if five_a_enabled else 50.0,
            five_a_avg_activity_pct=round(five_a.population_avg_activity, 1) if five_a_enabled else 50.0,
        )
        
        monthly_data.append(metrics)
        
        # Progress callback
        if progress_callback:
            progress_callback(month, duration_months)
    
    # Calculate summary statistics
    peak_active_users = max(monthly_mau) if monthly_mau else 0
    final_active_users = monthly_mau[-1] if monthly_mau else 0
    
    avg_retention = sum(m.retention_rate for m in monthly_data) / len(monthly_data) if monthly_data else 0
    avg_margin = sum(m.margin for m in monthly_data) / len(monthly_data) if monthly_data else 0
    
    # Calculate CAGR
    # HIGH-004 Fix: CAGR is only meaningful for periods >= 12 months
    def calculate_cagr(start: float, end: float, periods_in_years: float) -> float:
        if start <= 0 or end <= 0 or periods_in_years <= 0:
            return 0
        # HIGH-004 Fix: Return 0 for periods < 1 year to avoid misleading CAGR
        if periods_in_years < 1.0:
            return 0  # CAGR not applicable for sub-year periods
        return ((end / start) ** (1 / periods_in_years) - 1) * 100
    
    cagr_users = calculate_cagr(
        monthly_mau[0] if monthly_mau else 1,
        final_active_users,
        duration_months / 12
    )
    
    first_revenue = monthly_data[0].revenue if monthly_data else 1
    last_revenue = monthly_data[-1].revenue if monthly_data else 1
    cagr_revenue = calculate_cagr(
        first_revenue if first_revenue > 0 else 1,
        last_revenue if last_revenue > 0 else 1,
        duration_months / 12
    )
    
    # Overall recapture rate
    overall_recapture = (
        total_tokens_recaptured / total_tokens_distributed * 100
        if total_tokens_distributed > 0 else 0
    )
    
    # Create growth projection result
    growth_projection = GrowthProjectionResult(
        scenario=scenario.value,
        market_condition=market_condition.value,
        starting_waitlist=waitlist_users,
        monthly_mau=monthly_mau,
        monthly_acquired=monthly_acquired,
        monthly_churned=monthly_churned_list,
        monthly_growth_rates=[round(r * 100, 2) for r in monthly_growth_rates],
        token_price_curve=[round(p, 4) for p in token_price_curve],
        token_price_start=base_token_price,
        token_price_month6=token_price_curve[5] if len(token_price_curve) > 5 else base_token_price,
        token_price_end=token_price_curve[-1] if token_price_curve else base_token_price,
        fomo_events=[
            FomoEventResult(
                month=e.month,
                event_type=e.event_type.value,
                impact_multiplier=e.impact_multiplier,
                description=e.description,
                duration_days=e.duration_days,
            )
            for e in fomo_events_triggered
        ],
        total_users_acquired=total_users_acquired,
        month1_users=month1_users,
        month6_mau=monthly_mau[5] if len(monthly_mau) > 5 else 0,
        final_mau=final_active_users,
        peak_mau=peak_active_users,
        growth_percentage=round(
            ((final_active_users / month1_users) - 1) * 100 if month1_users > 0 else 0,
            1
        ),
        waitlist_conversion_rate=scenario_config.waitlist_conversion_rate,
        month1_fomo_multiplier=scenario_config.month1_fomo_multiplier,
        viral_coefficient=scenario_config.viral_coefficient,
    )
    
    # Create retention curve summary (simplified for growth scenarios)
    retention_summary = {
        1: round(scenario_config.month1_retention * 100, 1),
        3: round(scenario_config.month3_retention * 100, 1),
        6: round(scenario_config.month6_retention * 100, 1),
        12: round(scenario_config.month12_retention * 100, 1),
    }
    
    # Generate vesting schedule if tracking is enabled
    track_vesting = getattr(params, 'track_vesting_schedule', True)
    vesting_schedule = None
    final_circulating = 0
    final_circulating_pct = 0.0
    
    if track_vesting:
        vesting_schedule = generate_full_vesting_schedule(min(duration_months, 60))
        if vesting_schedule.monthly_supply:
            final_idx = min(duration_months, len(vesting_schedule.monthly_supply) - 1)
            final_supply = vesting_schedule.monthly_supply[final_idx]
            final_circulating = final_supply.cumulative_circulating
            final_circulating_pct = final_supply.circulating_percent
            
            # Update monthly_data with circulating supply info
            for i, metrics in enumerate(monthly_data):
                if i < len(vesting_schedule.monthly_supply):
                    supply = vesting_schedule.monthly_supply[i]
                    metrics.circulating_supply = supply.cumulative_circulating
                    metrics.circulating_percent = supply.circulating_percent
                    metrics.new_unlocks = supply.total_new_unlocks
    
    # Calculate treasury accumulation
    treasury_revenue_share = getattr(params, 'treasury_revenue_share', 0.20)
    total_treasury_usd = 0.0
    cumulative_treasury = 0.0
    
    for metrics in monthly_data:
        treasury_contribution = metrics.revenue * treasury_revenue_share
        cumulative_treasury += treasury_contribution
        metrics.treasury_revenue_usd = round(treasury_contribution, 2)
        metrics.treasury_accumulated_usd = round(cumulative_treasury, 2)
    
    total_treasury_usd = cumulative_treasury
    # Use final token price for treasury VCoin calculation
    final_token_price = token_price_curve[-1] if token_price_curve else base_token_price
    total_treasury_vcoin = total_treasury_usd / final_token_price if final_token_price > 0 else 0
    
    treasury_result = TreasuryResult(
        revenue_contribution_usd=round(total_treasury_usd, 2),
        revenue_contribution_vcoin=round(total_treasury_vcoin, 2),
        total_accumulated_usd=round(total_treasury_usd, 2),
        total_accumulated_vcoin=round(total_treasury_vcoin, 2),
        revenue_share_rate=treasury_revenue_share,
    )
    
    return MonthlyProgressionResult(
        duration_months=duration_months,
        monthly_data=monthly_data,
        total_users_acquired=total_users_acquired,
        peak_active_users=peak_active_users,
        final_active_users=final_active_users,
        average_retention_rate=round(avg_retention, 1),
        total_revenue=round(total_revenue, 2),
        total_costs=round(total_costs, 2),
        total_profit=round(total_revenue - total_costs, 2),
        average_margin=round(avg_margin, 1),
        cagr_users=round(cagr_users, 1),
        cagr_revenue=round(cagr_revenue, 1),
        total_tokens_distributed=round(total_tokens_distributed, 2),
        total_tokens_recaptured=round(total_tokens_recaptured, 2),
        overall_recapture_rate=round(overall_recapture, 1),
        months_to_profitability=months_to_profitability,
        cumulative_profit_curve=[round(p, 2) for p in cumulative_profit_curve],
        retention_curve=retention_summary,
        # Growth scenario specific data
        growth_projection=growth_projection,
        scenario_used=scenario.value,
        market_condition_used=market_condition.value,
        # Issue #2 Fix: Convert FomoEvent to FomoEventResult for proper serialization
        fomo_events_triggered=[
            FomoEventResult(
                month=e.month,
                event_type=e.event_type.value,
                impact_multiplier=e.impact_multiplier,
                description=e.description,
                duration_days=e.duration_days,
            )
            for e in fomo_events_triggered
        ],
        token_price_final=round(token_price_curve[-1] if token_price_curve else base_token_price, 4),
        # Vesting schedule (NEW - Nov 2025)
        vesting_schedule=vesting_schedule,
        final_circulating_supply=final_circulating,
        final_circulating_percent=final_circulating_pct,
        # Treasury (NEW - Nov 2025)
        treasury_result=treasury_result,
        total_treasury_accumulated_usd=round(total_treasury_usd, 2),
        total_treasury_accumulated_vcoin=round(total_treasury_vcoin, 2),
    )

