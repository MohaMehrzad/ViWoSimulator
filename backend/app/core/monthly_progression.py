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

This transforms the static snapshot simulation into a realistic
multi-month projection that accounts for churn, growth curves,
and market dynamics.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Tuple
from enum import Enum
import math

from app.models import SimulationParameters, PlatformMaturity, GrowthScenarioType, MarketConditionType
from app.models.results import FomoEventResult, GrowthProjectionResult
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
)
from app.config import config


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
    community_revenue: float
    advertising_revenue: float
    messaging_revenue: float
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
    fomo_events_triggered: List[FomoEvent] = field(default_factory=list)
    token_price_final: float = 0.03


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
    months: int = 24
) -> float:
    """
    Estimate Lifetime Value based on ARPU and retention curve.
    
    LTV = Sum of (Monthly Revenue × Retention Rate) over lifetime
    """
    ltv = 0
    for month in range(1, months + 1):
        retention = retention_curve.get_retention_at_month(month)
        ltv += arpu_monthly * retention
    return ltv


def run_monthly_progression_simulation(
    params: SimulationParameters,
    duration_months: int = 24,
    include_seasonality: bool = True,
    market_saturation_factor: float = 0.0,
    target_market_size: int = 1_000_000,  # Total addressable market
    progress_callback: Optional[Callable[[int, int], None]] = None,
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
    
    Returns:
        MonthlyProgressionResult with full time-series data
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
    
    for month in range(1, duration_months + 1):
        # Apply seasonality to marketing effectiveness
        seasonality = calculate_seasonality_multiplier(month, include_seasonality)
        
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
        active_users = tracker.get_active_users_at_month(month)
        
        # Calculate churned users
        prev_active = monthly_data[-1].active_users if monthly_data else 0
        users_churned = max(0, prev_active + total_acquired_this_month - active_users)
        
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
            community_revenue=round(sim_result.community.revenue, 2),
            advertising_revenue=round(sim_result.advertising.revenue, 2),
            messaging_revenue=round(sim_result.messaging.revenue, 2),
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
    def calculate_cagr(start: float, end: float, periods: int) -> float:
        if start <= 0 or end <= 0 or periods <= 0:
            return 0
        return ((end / start) ** (1 / periods) - 1) * 100
    
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
    """
    from app.core.deterministic import calculate_customer_acquisition
    
    # Limit to 12 months for growth scenarios (that's what we have data for)
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
    
    for month in range(1, duration_months + 1):
        # Calculate token price for this month
        token_price = calculate_token_price(
            month, scenario_config, market_condition, base_token_price
        )
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
            community_revenue=round(sim_result.community.revenue, 2),
            advertising_revenue=round(sim_result.advertising.revenue, 2),
            messaging_revenue=round(sim_result.messaging.revenue, 2),
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
    def calculate_cagr(start: float, end: float, periods: int) -> float:
        if start <= 0 or end <= 0 or periods <= 0:
            return 0
        return ((end / start) ** (1 / periods) - 1) * 100
    
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
        fomo_events_triggered=fomo_events_triggered,
        token_price_final=round(token_price_curve[-1] if token_price_curve else base_token_price, 4),
    )

