"""
Deterministic simulation engine.

Updated to address Issues #1, #6, #9, #10, #13, #15:
- Issue #1: Apply retention model to user calculations
- Issue #6: Fixed recapture to use actual VCoin flows
- Issue #9: Use linear cost scaling
- Issue #10: Include exchange in recapture
- Issue #13: Include compliance costs
- Issue #15: Documented fee flow to prevent double-counting

Nov 2025 Updates:
- Added Liquidity module with health score (target 70%+)
- Added Staking module with APY calculations
- Integrated creator economy features

Dec 2025 Updates:
- Added 5-year projection calculations (backend matching frontend UI)

MONEY FLOW DOCUMENTATION (Issue #15):
1. Module Revenue (USD) -> Totals revenue
2. Module Costs (USD) -> Totals costs
3. Platform Fee (5% of rewards) -> Added to revenue (NOT double-counted)
4. Compliance Costs -> Added to total costs
5. Recapture (VCoin only) -> Tracked separately, NOT revenue
"""

from pydantic import BaseModel  # LOW-05: For filter_model_fields utility
from app.models import (
    SimulationParameters,
    SimulationResult,
    CustomerAcquisitionMetrics,
    TotalsResult,
    PlatformFeesResult,
    LiquidityResult,
    StakingResult,
    GovernanceResult,
    VChainResult,
    MarketplaceResult,
    BusinessHubResult,
    CrossPlatformResult,
    TokenMetricsResult,
    StartingUsersSummary,
)
from app.models.results import (
    TokenVelocityResult, 
    RealYieldResult, 
    ValueAccrualResult,
    GiniResult,
    RunwayResult,
    InflationResult,
    WhaleAnalysisResult,
    TopHoldersGroup,
    OrganicGrowthResult,
    WhaleInfo,
    DumpScenarioResult,
    AttackAnalysisResult,
    AttackScenarioDetail,
    SecurityFeatures,
    LiquidityFarmingResult,
    FarmingAPY,
    FarmingRiskMetrics,
    FarmingSimulation,
    FarmingSimulationMonth,
    ILScenario,
    GameTheoryResult,
    StrategyMetrics,
    StakingEquilibrium,
    StakingAnalysis,
    GovernanceParticipation,
    VoterApathy,
    CoordinationGameAnalysis,
    ReferralResult,
    PointsResult,
    GaslessResult,
    PreLaunchResult,
    FiveAResult,
)
from app.core.modules.identity import calculate_identity
from app.core.modules.content import calculate_content
from app.core.modules.advertising import calculate_advertising
from app.core.modules.exchange import calculate_exchange
from app.core.modules.rewards import calculate_rewards
# MED-07 Fix: Import PLATFORM_FEE_RATE from centralized config (not from rewards.py)
from app.core.modules.recapture import calculate_recapture
from app.core.modules.liquidity import calculate_liquidity
from app.core.modules.staking import calculate_staking
from app.core.modules.governance import calculate_governance
from app.core.modules.vchain import calculate_vchain
from app.core.modules.marketplace import calculate_marketplace
from app.core.modules.business_hub import calculate_business_hub
from app.core.modules.cross_platform import calculate_cross_platform
# Pre-Launch Modules (Nov 2025)
from app.core.modules.referral import calculate_referral
from app.core.modules.points import calculate_points
from app.core.modules.gasless import calculate_gasless
# 5A Policy Gamification (Dec 2025)
from app.core.modules.five_a_policy import calculate_five_a
# Organic User Growth (Dec 2025)
from app.core.modules.organic_growth import calculate_organic_growth
# 5-Year Projections (Dec 2025)
from app.core.five_year_projections import calculate_5_year_projections
from app.core.metrics import (
    calculate_token_velocity,
    calculate_real_yield,
    calculate_value_accrual_score,
    calculate_utility_score,
    calculate_gini_coefficient,
    calculate_runway,
)
from app.core.whale_analysis import calculate_whale_concentration
from app.core.attack_scenarios import calculate_attack_scenarios
from app.core.liquidity_farming import calculate_full_farming_analysis
from app.core.game_theory import calculate_full_game_theory_analysis
from app.core.sensitivity import run_all_stress_tests, run_monte_carlo_sensitivity
from app.core.retention import (
    apply_retention_to_snapshot, 
    VCOIN_RETENTION,
    WAITLIST_USER_RETENTION,
    RetentionModel,
    RetentionCurve,
    RETENTION_CURVES,
    CohortTracker,
)
from app.config import config

# MED-07 Fix: Use centralized PLATFORM_FEE_RATE from config
PLATFORM_FEE_RATE = config.PLATFORM_FEE_RATE

# LOW-04 Fix: APY boost calculation constants (extracted from inline magic numbers)
# These control how staking APY affects the effective staking ratio for value accrual scoring
APY_BOOST_BASE_RATE = 0.10        # Base APY threshold (10%) - APY at this level = 1.0x boost
APY_BOOST_MULTIPLIER = 5.0        # How much each 1% APY above base increases boost (e.g., 20% APY = 1.5x)
APY_BOOST_MIN = 0.5               # Minimum boost (for APY well below base rate)
APY_BOOST_MAX = 2.0               # Maximum boost (caps at 2x regardless of APY)
STAKING_RATIO_CAP = 0.60          # Maximum staking ratio for value accrual (60%)


# LOW-05 Fix: Utility function to filter dict keys to match Pydantic model fields
from typing import Type, Dict, Any, TypeVar, Tuple
T = TypeVar('T', bound=BaseModel)

def filter_model_fields(data: Dict[str, Any], model_class: Type[T]) -> T:
    """
    Create a Pydantic model instance by filtering dict keys to only those in the model.
    
    LOW-05 Fix: Extracted from repeated dict comprehension pattern to reduce code duplication.
    
    Args:
        data: Dictionary containing potentially extra keys
        model_class: Pydantic model class to instantiate
    
    Returns:
        Instance of model_class with only valid fields from data
    
    Example:
        result = filter_model_fields(raw_data, GovernanceResult)
    """
    filtered = {k: v for k, v in data.items() if k in model_class.model_fields}
    return model_class(**filtered)


def calculate_distributed_acquisition_with_retention(
    params: SimulationParameters,
    platform_age_months: int,
    retention_curve: RetentionCurve,
    is_waitlist: bool = False
) -> Tuple[int, int]:
    """
    Calculate total acquired and active users from distributed budget with cohort retention.
    
    Simulates month-by-month acquisition and applies cohort-based retention.
    
    Args:
        params: Simulation parameters
        platform_age_months: Current platform age in months
        retention_curve: Retention curve to apply
        is_waitlist: If True, only returns waitlist users (acquired at month 0)
    
    Returns:
        Tuple of (total_acquired, total_active)
    """
    if is_waitlist:
        # Waitlist users are acquired at month 0 (before platform launch)
        waitlist_count = getattr(params, 'starting_waitlist_users', 0)
        if waitlist_count == 0:
            return 0, 0
        
        # Apply retention based on platform age
        active, _ = apply_retention_to_snapshot(
            waitlist_count,
            platform_age_months,
            retention_curve
        )
        return waitlist_count, max(active, int(waitlist_count * 0.20))
    
    # For CAC users, simulate month-by-month acquisition
    if not getattr(params, 'use_distributed_marketing_budget', False):
        # Legacy: All budget spent at once
        return 0, 0  # Handled by old logic
    
    # Use cohort tracker for realistic simulation
    tracker = CohortTracker(retention_curve)
    
    # Get monthly budgets and acquire users each month
    total_acquired = 0
    
    for month in range(1, min(platform_age_months + 1, 13)):
        # Get budget for this month
        if getattr(params, 'marketing_budget_distribution_months', None):
            if month <= len(params.marketing_budget_distribution_months):
                monthly_budget = params.marketing_budget_distribution_months[month - 1]
            else:
                monthly_budget = 0
        else:
            # Default distribution
            total_budget = params.marketing_budget
            distribution = {
                1: 0.2333, 2: 0.1667, 3: 0.1000,
                4: 0.0667, 5: 0.0667, 6: 0.0667,
                7: 0.0556, 8: 0.0556, 9: 0.0556,
                10: 0.0444, 11: 0.0444, 12: 0.0444,
            }
            monthly_budget = total_budget * distribution.get(month, 0)
        
        # Calculate users acquired this month (excluding creators - they're handled separately)
        # Subtract creator costs from monthly budget
        monthly_creator_cost = (
            (params.high_quality_creators_needed / 12) * params.high_quality_creator_cac +
            (params.mid_level_creators_needed / 12) * params.mid_level_creator_cac
        )
        consumer_budget = max(0, monthly_budget - monthly_creator_cost)
        
        # Calculate CAC (blended)
        na_percent = params.north_america_budget_percent / (params.north_america_budget_percent + params.global_low_income_budget_percent)
        global_percent = 1 - na_percent
        blended_cac = (
            params.cac_north_america_consumer * na_percent +
            params.cac_global_low_income_consumer * global_percent
        )
        
        users_acquired = int(consumer_budget / blended_cac) if blended_cac > 0 else 0
        
        # Add to tracker
        tracker.add_cohort(month, users_acquired)
        total_acquired += users_acquired
    
    # Calculate active users at platform_age_months
    active_users = tracker.get_active_users_at_month(platform_age_months)
    
    return total_acquired, active_users


def get_marketing_budget_for_snapshot(params: SimulationParameters, platform_age_months: int = 6) -> float:
    """
    Calculate cumulative marketing budget spent up to platform_age_months.
    
    Dec 2025: Supports distributed marketing budget.
    
    Args:
        params: Simulation parameters
        platform_age_months: Platform age in months (determines how much budget was spent)
    
    Returns:
        Total budget spent up to this month
    """
    if not getattr(params, 'use_distributed_marketing_budget', False):
        # Legacy behavior: assume budget is annual, use proportional amount
        return params.marketing_budget * (platform_age_months / 12)
    
    # Use distributed budget
    if getattr(params, 'marketing_budget_distribution_months', None):
        # Custom distribution provided
        monthly_budgets = params.marketing_budget_distribution_months[:platform_age_months]
        return sum(monthly_budgets)
    else:
        # Default distribution (50% in first 3 months)
        total_budget = params.marketing_budget
        distribution = {
            1: 0.2333, 2: 0.1667, 3: 0.1000,
            4: 0.0667, 5: 0.0667, 6: 0.0667,
            7: 0.0556, 8: 0.0556, 9: 0.0556,
            10: 0.0444, 11: 0.0444, 12: 0.0444,
        }
        cumulative = 0
        for month in range(1, min(platform_age_months + 1, 13)):
            cumulative += total_budget * distribution.get(month, 0)
        return cumulative


def calculate_customer_acquisition(params: SimulationParameters, platform_age_months: int = 6) -> Tuple[CustomerAcquisitionMetrics, int, int]:
    """
    Calculate customer acquisition breakdown from marketing budget.
    Uses segmented acquisition model: creators + consumers across regions.
    
    Issue #2 fix: Uses updated realistic CAC values.
    Issue #6 fix: Scales down creators when budget is insufficient.
    Dec 2025 fix: Supports distributed marketing budget based on platform age.
    Dec 2025 v2: Returns active user count when distributed budget is enabled.
    
    Args:
        params: Simulation parameters
        platform_age_months: Platform age in months (determines cumulative budget spent)
    
    Returns:
        Tuple of (CustomerAcquisitionMetrics, total_acquired_cac_users, active_cac_users_after_retention)
    """
    # Get cumulative budget spent up to this month
    total_budget = get_marketing_budget_for_snapshot(params, platform_age_months)
    
    # Creator costs (using updated realistic CAC from Issue #2)
    high_creator_cost_requested = params.high_quality_creators_needed * params.high_quality_creator_cac
    mid_creator_cost_requested = params.mid_level_creators_needed * params.mid_level_creator_cac
    total_creator_cost_requested = high_creator_cost_requested + mid_creator_cost_requested
    
    # Issue #6 fix: Scale down creators proportionally when budget is insufficient
    if total_creator_cost_requested > total_budget and total_creator_cost_requested > 0:
        scale_factor = total_budget / total_creator_cost_requested
        high_creators_actual = int(params.high_quality_creators_needed * scale_factor)
        mid_creators_actual = int(params.mid_level_creators_needed * scale_factor)
        total_creator_cost = (high_creators_actual * params.high_quality_creator_cac +
                              mid_creators_actual * params.mid_level_creator_cac)
        consumer_budget = 0
        budget_shortfall = True
        budget_shortfall_amount = total_creator_cost_requested - total_budget
    else:
        high_creators_actual = params.high_quality_creators_needed
        mid_creators_actual = params.mid_level_creators_needed
        total_creator_cost = total_creator_cost_requested
        consumer_budget = max(0, total_budget - total_creator_cost)
        budget_shortfall = False
        budget_shortfall_amount = 0.0
    
    # Normalize regional percentages
    total_percent = params.north_america_budget_percent + params.global_low_income_budget_percent
    if total_percent <= 0:
        na_percent = 0.5
        global_percent = 0.5
    else:
        na_percent = params.north_america_budget_percent / total_percent
        global_percent = params.global_low_income_budget_percent / total_percent
    
    # Regional budgets
    na_budget = consumer_budget * na_percent
    global_budget = consumer_budget * global_percent
    
    # Calculate users from budget and CAC (using realistic CAC values)
    na_users = int(na_budget / params.cac_north_america_consumer) if params.cac_north_america_consumer > 0 else 0
    global_users = int(global_budget / params.cac_global_low_income_consumer) if params.cac_global_low_income_consumer > 0 else 0
    
    # Total users includes actual creators (not requested)
    total_creators = high_creators_actual + mid_creators_actual
    total_users_acquired = total_creators + na_users + global_users
    
    # Blended CAC - uses actual spend and acquired users
    blended_cac = total_budget / total_users_acquired if total_users_acquired > 0 else 0
    
    # Dec 2025: Calculate total users that would be acquired over FULL YEAR (12 months)
    # This is what gets displayed in "Calculated Users" UI
    total_users_acquired_full_year = total_users_acquired
    
    if getattr(params, 'use_distributed_marketing_budget', False):
        # Calculate total acquisitions over 12 months (not just platform_age)
        total_acquired_12m, _ = calculate_distributed_acquisition_with_retention(
            params, 12, VCOIN_RETENTION, is_waitlist=False  # 12 months, retention not needed for count
        )
        # Add creators over 12 months
        total_users_acquired_full_year = total_creators + total_acquired_12m
    
    # Now calculate ACTIVE users at platform_age_months for actual simulation
    total_users_active = total_users_acquired  # Default to acquired
    
    if getattr(params, 'use_distributed_marketing_budget', False) and params.apply_retention:
        # Get retention curve
        retention_curve = VCOIN_RETENTION
        if hasattr(params, 'retention') and hasattr(params.retention, 'model_type'):
            model_type = params.retention.model_type
            if model_type.value in [m.value for m in RetentionModel]:
                retention_curve = RETENTION_CURVES.get(
                    RetentionModel(model_type.value),
                    VCOIN_RETENTION
                )
        
        # Calculate active users with cohort-based retention at platform_age
        _, total_users_active = calculate_distributed_acquisition_with_retention(
            params, platform_age_months, retention_curve, is_waitlist=False
        )
        
        # Add creators (they don't churn as much - use simple retention)
        if total_creators > 0:
            creators_active, _ = apply_retention_to_snapshot(
                total_creators, platform_age_months, retention_curve
            )
            creators_active = max(creators_active, int(total_creators * 0.30))  # Min 30% retention for creators
            total_users_active += creators_active
    
    # Calculate blended CAC for full year acquisitions
    blended_cac_full_year = params.marketing_budget / total_users_acquired_full_year if total_users_acquired_full_year > 0 else 0
    
    return (
        CustomerAcquisitionMetrics(
            total_creator_cost=round(total_creator_cost, 2),
            consumer_acquisition_budget=round(consumer_budget, 2),
            north_america_budget=round(na_budget, 2),
            global_low_income_budget=round(global_budget, 2),
            north_america_users=na_users,
            global_low_income_users=global_users,
            # Dec 2025: Show total acquired over FULL YEAR (12 months) for UI display
            # This shows cumulative user acquisition, not active after churn
            total_users=total_users_acquired_full_year,
            blended_cac=round(blended_cac_full_year, 2),
            # Issue #6: New fields for budget constraint handling
            high_quality_creators_actual=high_creators_actual,
            mid_level_creators_actual=mid_creators_actual,
            budget_shortfall=budget_shortfall,
            budget_shortfall_amount=round(budget_shortfall_amount, 2),
        ),
        total_users_acquired_full_year,  # Total acquired over 12 months (for UI display)
        total_users_active,              # Total active at platform_age (for simulation calculations)
    )


def run_deterministic_simulation(
    params: SimulationParameters,
    simulation_month: int = 1
) -> SimulationResult:
    """
    Run a complete deterministic simulation.
    Same inputs always produce same outputs.
    
    Args:
        params: Simulation parameters
        simulation_month: Current month in simulation (1-60). Default is 1.
            HIGH-006 Fix: Added to allow future modules to launch in snapshot mode.
            Future modules (VChain, Marketplace, etc.) only activate when
            simulation_month >= their launch_month. Default of 1 means
            future modules won't show revenue in basic snapshot simulations.
            Set to higher values to simulate future states.
    
    Key updates for 2025:
    - Issue #1: Applies retention model if enabled
    - Issue #9: Uses linear cost scaling
    - Issue #10: Includes exchange in recapture
    - Issue #13: Includes compliance costs
    - Nov 2025: Applies growth scenario multipliers when enabled
    - HIGH-006: Added simulation_month for future module testing
    """
    # Get platform age for budget and retention calculations
    platform_age = getattr(params.retention, 'platform_age_months', 6) if hasattr(params, 'retention') else 6
    
    # Step 1: Calculate customer acquisition to get user count
    # Dec 2025: Pass platform_age_months to support distributed marketing budget
    # Dec 2025 v2: Function now returns tuple (metrics, acquired, active)
    customer_acquisition_base, total_acquired_from_cac, total_active_from_cac = calculate_customer_acquisition(params, platform_age)
    acquired_users = total_active_from_cac  # Use active users (after cohort retention) not total acquired
    
    # Use provided starting_users if specified, otherwise use calculated
    if params.starting_users > 0:
        acquired_users = params.starting_users
    
    # Nov 2025: Apply growth scenario multipliers when enabled
    if hasattr(params, 'use_growth_scenarios') and params.use_growth_scenarios:
        from app.core.growth_scenarios import (
            GrowthScenario, MarketCondition, 
            GROWTH_SCENARIOS, MARKET_CONDITIONS
        )
        from app.models import GrowthScenarioType, MarketConditionType
        
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
        
        # Apply scenario multiplier to users (represents Month 1 boost)
        scenario_multiplier = scenario_config.month1_fomo_multiplier * market_config.fomo_multiplier
        acquired_users = max(1, int(acquired_users * scenario_multiplier * 0.3))  # 30% dampening
    
    # Issue #1 Fix: Apply retention model with separate cohort tracking
    # Dec 2025: Separate waitlist users from CAC-acquired users for accurate retention modeling
    # Dec 2025 v2: Use distributed acquisition with cohort-based retention for CAC users
    
    # Get waitlist users from parameters
    waitlist_users_acquired = getattr(params, 'starting_waitlist_users', 0)
    
    active_users = waitlist_users_acquired + acquired_users
    users_before_retention = waitlist_users_acquired + acquired_users
    retention_applied = False
    retention_rate = None
    waitlist_users_active = waitlist_users_acquired
    cac_users_acquired = acquired_users
    cac_users_active = acquired_users
    
    if params.apply_retention and hasattr(params, 'retention'):
        retention_applied = True
        platform_age = params.retention.platform_age_months
        
        # Select standard retention curve based on retention_model_type parameter
        retention_curve = VCOIN_RETENTION  # Default fallback
        if hasattr(params.retention, 'model_type'):
            model_type = params.retention.model_type
            # Map parameter enum value to RetentionModel enum
            if model_type.value in [m.value for m in RetentionModel]:
                retention_curve = RETENTION_CURVES.get(
                    RetentionModel(model_type.value),
                    VCOIN_RETENTION
                )
        
        # Apply WAITLIST_USER_RETENTION to waitlist users (gentler churn)
        if waitlist_users_acquired > 0:
            waitlist_users_acquired_total, waitlist_users_active = calculate_distributed_acquisition_with_retention(
                params, platform_age, WAITLIST_USER_RETENTION, is_waitlist=True
            )
        
        # Apply distributed acquisition with cohort retention to CAC users
        if getattr(params, 'use_distributed_marketing_budget', False):
            # Use cohort-based tracking for distributed budget
            cac_users_acquired, cac_users_active = calculate_distributed_acquisition_with_retention(
                params, platform_age, retention_curve, is_waitlist=False
            )
        else:
            # Legacy behavior: apply retention to total acquired users
            if acquired_users > 0:
                cac_users_active, cac_stats = apply_retention_to_snapshot(
                    acquired_users,
                    platform_age,
                    retention_curve
                )
                # Ensure at least some CAC users remain (minimum 10% of acquired)
                cac_users_active = max(cac_users_active, int(acquired_users * 0.10))
            cac_users_acquired = acquired_users
        
        # Combine both cohorts
        active_users = waitlist_users_active + cac_users_active
        users_before_retention = waitlist_users_acquired + cac_users_acquired
        retention_rate = (active_users / users_before_retention * 100) if users_before_retention > 0 else 0
    
    # Step 1b: Calculate Organic Growth (Dec 2025)
    # Must happen BEFORE modules so organic users are included in revenue calculations
    organic_users = 0
    organic_growth_result = None
    if params.organic_growth and params.organic_growth.enable_organic_growth:
        # For deterministic simulation, calculate organic growth based on active users
        organic_growth_result = calculate_organic_growth(
            params=params,
            current_users=active_users,
            month=simulation_month,
            total_users_acquired=total_acquired_from_cac + waitlist_users_acquired,
        )
        organic_users = organic_growth_result.total_organic_users
    
    # Step 1c: Calculate Referral Users (Dec 2025)
    # ISSUE #2 FIX: Referral users must be added BEFORE module calculations
    # They contribute to revenue generation just like organic users
    referral_users = 0
    referral_result_early = None
    if params.referral and getattr(params.referral, 'enable_referral', True):
        # Get viral coefficient from growth scenario if available
        viral_coefficient = 0.5  # Default
        if hasattr(params, 'use_growth_scenarios') and params.use_growth_scenarios:
            from app.core.growth_scenarios import GrowthScenario, GROWTH_SCENARIOS
            from app.models import GrowthScenarioType
            scenario_map = {
                GrowthScenarioType.CONSERVATIVE: GrowthScenario.CONSERVATIVE,
                GrowthScenarioType.BASE: GrowthScenario.BASE,
                GrowthScenarioType.BULLISH: GrowthScenario.BULLISH,
            }
            scenario_key = scenario_map.get(params.growth_scenario, GrowthScenario.BASE)
            scenario_config = GROWTH_SCENARIOS.get(scenario_key)
            if scenario_config:
                viral_coefficient = scenario_config.viral_coefficient
        
        # Use a reasonable default budget for early calculation
        # Budget will be refined later based on actual revenue
        early_referral_budget = 1000  # Conservative estimate
        
        # Calculate referral to get qualified_referrals count
        ref_data = calculate_referral(params, active_users + organic_users, viral_coefficient, early_referral_budget)
        referral_result_early = ref_data
        referral_users = ref_data.qualified_referrals
    
    # Combine paid + organic + referral users for all module calculations
    users = active_users + organic_users + referral_users
    
    # Update customer acquisition metrics to include organic and referral users
    # ISSUE #6 FIX: Calculate effective CAC including organic/referral users
    total_users_all_sources = customer_acquisition_base.total_users + organic_users + referral_users
    marketing_spend = params.marketing_budget
    effective_cac = marketing_spend / total_users_all_sources if total_users_all_sources > 0 else 0
    
    # Store base customer acquisition for later LTV update
    customer_acquisition_base_data = {
        'total_creator_cost': customer_acquisition_base.total_creator_cost,
        'consumer_acquisition_budget': customer_acquisition_base.consumer_acquisition_budget,
        'north_america_budget': customer_acquisition_base.north_america_budget,
        'global_low_income_budget': customer_acquisition_base.global_low_income_budget,
        'north_america_users': customer_acquisition_base.north_america_users,
        'global_low_income_users': customer_acquisition_base.global_low_income_users,
        'total_users': customer_acquisition_base.total_users,
        'blended_cac': customer_acquisition_base.blended_cac,
        'high_quality_creators_actual': customer_acquisition_base.high_quality_creators_actual,
        'mid_level_creators_actual': customer_acquisition_base.mid_level_creators_actual,
        'budget_shortfall': customer_acquisition_base.budget_shortfall,
        'budget_shortfall_amount': customer_acquisition_base.budget_shortfall_amount,
        'organic_users': organic_users,
        'total_users_with_organic': total_users_all_sources,
        'organic_percent': round((organic_users / users * 100), 2) if users > 0 else 0.0,
        'effective_cac': round(effective_cac, 2),
    }
    
    # Create initial customer acquisition (LTV will be added later after revenue is calculated)
    customer_acquisition = CustomerAcquisitionMetrics(**customer_acquisition_base_data)
    
    # Determine user source for summary
    if params.starting_users > 0:
        user_source = 'manual_input'
    elif hasattr(params, 'use_growth_scenarios') and params.use_growth_scenarios:
        user_source = 'growth_scenario'
    else:
        user_source = 'marketing_budget'
    
    # Build starting users summary with cohort tracking
    starting_users_summary = StartingUsersSummary(
        total_active_users=users,
        user_source=user_source,
        manual_starting_users=params.starting_users if params.starting_users > 0 else None,
        marketing_budget_usd=params.marketing_budget if user_source == 'marketing_budget' else None,
        acquired_from_marketing=customer_acquisition.total_users if user_source == 'marketing_budget' else None,
        high_quality_creators=customer_acquisition.high_quality_creators_actual,
        mid_level_creators=customer_acquisition.mid_level_creators_actual,
        north_america_consumers=customer_acquisition.north_america_users,
        global_low_income_consumers=customer_acquisition.global_low_income_users,
        retention_applied=retention_applied,
        users_before_retention=users_before_retention if retention_applied else None,
        users_after_retention=active_users if retention_applied else None,
        retention_rate=round(retention_rate, 1) if retention_rate is not None else None,
        # Cohort tracking (Dec 2025)
        waitlist_users_acquired=waitlist_users_acquired if waitlist_users_acquired > 0 else None,
        waitlist_users_active=waitlist_users_active if retention_applied and waitlist_users_acquired > 0 else None,
        waitlist_retention_rate=round((waitlist_users_active / waitlist_users_acquired * 100), 1) if retention_applied and waitlist_users_acquired > 0 else None,
        cac_users_acquired=cac_users_acquired if cac_users_acquired > 0 else None,
        cac_users_active=cac_users_active if retention_applied and cac_users_acquired > 0 else None,
        cac_retention_rate=round((cac_users_active / cac_users_acquired * 100), 1) if retention_applied and cac_users_acquired > 0 else None,
        # Organic growth (Dec 2025)
        organic_users_acquired=organic_users if organic_users > 0 else None,
        organic_percent_of_total=round((organic_users / users * 100), 1) if users > 0 and organic_users > 0 else None,
        # Referral users (Dec 2025 - Issue #2 Fix)
        referral_users_acquired=referral_users if referral_users > 0 else None,
        referral_percent_of_total=round((referral_users / users * 100), 1) if users > 0 and referral_users > 0 else None,
    )
    
    # Step 2a: Calculate 5A Policy first (Dec 2025)
    # 5A affects all other modules, so we calculate it early
    # We'll provide base values and update them after other calculations
    five_a_result = calculate_five_a(
        params=params,
        users=users,
        base_reward_pool=0,  # Will be updated after rewards calculation
        base_fee_revenue=0,  # Will be updated after module calculations
        staking_apy=params.staking_apy if hasattr(params, 'staking_apy') else 0.10,
        total_staked=0,  # Will be updated after staking calculation
        governance_power=0,  # Will be updated after governance calculation
    )
    
    # Extract 5A multipliers for module integration
    five_a_enabled = five_a_result.enabled
    five_a_fee_discount_avg = five_a_result.exchange_fee_discount_avg / 100 if five_a_enabled else 0.0
    five_a_visibility_boost_avg = five_a_result.content_visibility_boost_avg / 100 if five_a_enabled else 0.0
    five_a_creator_boost_avg = five_a_visibility_boost_avg  # Same as visibility for ad revenue
    five_a_apy_boost_avg = five_a_result.staking_apy_boost_avg / 100 if five_a_enabled else 0.0
    five_a_governance_boost_avg = five_a_result.governance_power_boost_avg / 100 if five_a_enabled else 0.0
    five_a_reward_multiplier = five_a_result.avg_compound_multiplier if five_a_enabled else 1.0
    
    # Step 2b: Calculate each module with 5A integration
    identity = calculate_identity(params, users, five_a_fee_discount=five_a_fee_discount_avg)
    content = calculate_content(params, users, five_a_visibility_boost=five_a_visibility_boost_avg)
    advertising = calculate_advertising(params, users, five_a_creator_boost=five_a_creator_boost_avg)
    exchange = calculate_exchange(params, users, five_a_fee_discount=five_a_fee_discount_avg)
    
    # Step 3: Calculate rewards with 5A reward multiplier
    rewards = calculate_rewards(params, users, five_a_reward_multiplier=five_a_reward_multiplier)
    
    # Step 3b: Calculate base revenue for buyback calculation
    # Buybacks use USD revenue, so we need to calculate it before recapture
    base_module_revenue = (
        identity.revenue + content.revenue +
        advertising.revenue + exchange.revenue +
        rewards.platform_fee_usd  # Platform fee is primary revenue
    )
    
    # Step 3b2: Calculate Future Module metrics (if enabled)
    # ISSUE #3 FIX: Calculate future modules BEFORE recapture so their revenue is included
    # HIGH-006 Fix: Use simulation_month parameter instead of hardcoded 1
    # This allows future modules to be tested in snapshot mode by setting
    # simulation_month >= module's launch_month
    current_month = simulation_month
    
    vchain_result = None
    marketplace_result = None
    business_hub_result = None
    cross_platform_result = None
    future_modules_revenue = 0
    future_modules_costs = 0
    
    if params.vchain and params.vchain.enable_vchain:
        vchain_data = calculate_vchain(params, current_month, users, params.token_price)
        vchain_result = filter_model_fields(vchain_data, VChainResult)
        future_modules_revenue += vchain_result.revenue
        future_modules_costs += vchain_result.costs
    
    if params.marketplace and params.marketplace.enable_marketplace:
        mp_data = calculate_marketplace(params, current_month, users, params.token_price)
        marketplace_result = filter_model_fields(mp_data, MarketplaceResult)
        future_modules_revenue += marketplace_result.revenue
        future_modules_costs += marketplace_result.costs
    
    if params.business_hub and params.business_hub.enable_business_hub:
        bh_data = calculate_business_hub(params, current_month, users, params.token_price)
        business_hub_result = filter_model_fields(bh_data, BusinessHubResult)
        future_modules_revenue += business_hub_result.revenue
        future_modules_costs += business_hub_result.costs
    
    if params.cross_platform and params.cross_platform.enable_cross_platform:
        cp_data = calculate_cross_platform(params, current_month, users, params.token_price)
        cross_platform_result = filter_model_fields(cp_data, CrossPlatformResult)
        future_modules_revenue += cross_platform_result.revenue
        future_modules_costs += cross_platform_result.costs
    
    # Step 3c: DYNAMIC CIRCULATING SUPPLY FIX
    # Calculate circulating supply based on simulation_month to include:
    # 1. Base vesting unlocks from all token categories at the given month
    # 2. Dynamic rewards distributed based on user count (capped at max schedule)
    # Pass users and token_price for dynamic rewards calculation
    circulating_supply = config.get_circulating_supply_at_month(
        simulation_month,
        users=users,
        token_price=params.token_price
    )
    
    # Also get the monthly unlock breakdown for the inflation dashboard
    monthly_unlock_breakdown = config.get_monthly_unlock_breakdown(
        simulation_month,
        users=users,
        token_price=params.token_price
    )
    
    # Step 4: Calculate recapture (Issue #10: now includes exchange)
    # Nov 2025: Now passes total_revenue_usd for revenue-based buybacks
    # Dec 2025: Now passes circulating_supply for dynamic supply-based caps
    # Dec 2025: Now passes 5A engagement boost for velocity multiplier
    # ISSUE #3 FIX: Include future modules revenue in recapture calculation
    total_revenue_for_recapture = base_module_revenue + future_modules_revenue
    
    recapture = calculate_recapture(
        params, identity, content, advertising, 
        exchange,  # Issue #10: Added exchange module
        rewards, users,
        total_revenue_usd=total_revenue_for_recapture,  # For revenue-based buybacks (includes future modules)
        circulating_supply=circulating_supply,  # For dynamic supply-based caps
        five_a_engagement_boost=five_a_visibility_boost_avg,  # 5A engagement boost
    )
    
    # Step 5: Create platform fees result from rewards data
    # Issue #15: Platform fee is revenue, NOT part of recapture
    platform_fees = PlatformFeesResult(
        reward_fee_vcoin=rewards.platform_fee_vcoin,
        reward_fee_usd=rewards.platform_fee_usd,
        fee_rate=PLATFORM_FEE_RATE,
    )
    
    # Step 5b (NEW): Calculate Staking metrics with 5A APY boost
    # === DYNAMIC STAKING CAP (December 2025) ===
    # User rewards are calculated first (priority for growth)
    # Staking is capped based on remaining budget at 7% APY
    # Cap = (remaining_budget * 12) / APY - ensures budget compliance
    max_monthly_emission = config.MONTHLY_EMISSION  # 5,833,333 VCoin
    user_rewards_used = rewards.gross_monthly_emission  # What user rewards already consumed
    remaining_for_staking = max(0, max_monthly_emission - user_rewards_used)
    
    staking_data = calculate_staking(
        params,
        users,
        monthly_emission=rewards.monthly_reward_pool,
        circulating_supply=circulating_supply,
        five_a_apy_boost=five_a_apy_boost_avg,
        max_staking_budget=remaining_for_staking,  # Used to calculate staking cap
    )
    staking_result = StakingResult(**staking_data)
    
    # ISSUE #7 FIX: Validate staking rewards against emission budget
    # Staking rewards should not exceed the remaining budget after user rewards
    # This is enforced by max_staking_budget parameter above
    # If staking_at_capacity is True, the pool is full and users can't stake more
    if staking_result.staking_at_capacity:
        # Staking pool is at capacity - this is expected and handled
        pass  # Logging or metrics can be added here if needed
    
    # Step 5c (NEW): Calculate Governance metrics with 5A governance boost
    governance_data = calculate_governance(
        params,
        stakers_count=staking_result.stakers_count,
        total_staked=staking_result.total_staked,
        circulating_supply=circulating_supply,
        five_a_governance_boost=five_a_governance_boost_avg,
    )
    # LOW-05: Use filter_model_fields utility
    governance_result = filter_model_fields(governance_data, GovernanceResult)
    
    # Step 5d (NEW): Calculate Liquidity metrics with 5A LP boost and governance factor
    # ISSUE #8 FIX: Governance health affects community LP participation
    governance_health = governance_result.governance_health_score / 100 if governance_result else 0.5
    
    liquidity_data = calculate_liquidity(
        params, 
        users, 
        monthly_volume=recapture.total_revenue_source_vcoin,
        circulating_supply=circulating_supply,
        five_a_lp_boost=five_a_visibility_boost_avg,  # 5A increases LP participation
        governance_factor=governance_health,  # ISSUE #8 FIX: Governance affects LP decisions
    )
    liquidity_result = LiquidityResult(**liquidity_data)
    
    # Step 5f (NEW): Calculate Token Metrics
    # Note: Future modules already calculated earlier (Step 3b2) before recapture
    transaction_volume = recapture.total_revenue_source_vcoin
    
    # === STAKING RATIO FOR VALUE ACCRUAL SCORING ===
    # 
    # Design Decision: We use staking_participation_rate (% of users who stake)
    # instead of the raw staking_ratio (staked_tokens / circulating_supply).
    # 
    # Rationale:
    # 1. With 100M+ circulating supply, raw staking ratio is always tiny (<1%)
    #    which would unfairly penalize the Value Accrual score
    # 2. Participation rate (15-60% of users staking) better reflects the
    #    platform's success in encouraging token lockup behavior
    # 3. This is a user-configurable parameter, allowing scenario modeling
    # 
    # The APY boost further adjusts the effective ratio:
    # - Higher APY (>10%) incentivizes more staking, boosting the ratio
    # - Lower APY (<10%) reduces staking attractiveness, reducing the ratio
    #
    staking_participation = getattr(params, 'staking_participation_rate', 0.15)
    staking_apy = params.staking_apy
    
    # LOW-04 Fix: APY boost calculation using named constants
    # Example: 10% APY = 1.0x, 20% APY = 1.5x, 30% APY = 2.0x
    apy_boost = 1.0 + (staking_apy - APY_BOOST_BASE_RATE) * APY_BOOST_MULTIPLIER
    apy_boost = max(APY_BOOST_MIN, min(APY_BOOST_MAX, apy_boost))
    
    # Effective staking ratio for Value Accrual scoring
    staking_ratio = min(STAKING_RATIO_CAP, staking_participation * apy_boost)
    
    velocity_data = calculate_token_velocity(
        transaction_volume=transaction_volume,
        circulating_supply=circulating_supply
    )
    
    # Calculate total revenue for real yield
    base_revenue = (
        identity.revenue + content.revenue +
        advertising.revenue + exchange.revenue +
        staking_result.revenue + platform_fees.reward_fee_usd
    )
    
    real_yield_data = calculate_real_yield(
        protocol_revenue=base_revenue,
        staked_supply=staking_result.total_staked,
        token_price=params.token_price
    )
    
    # Calculate comprehensive utility score based on real platform activity
    # Uses: module engagement, token velocity, revenue per user, feature adoption
    utility_score = calculate_utility_score(
        users=users,
        identity_result={'breakdown': identity.breakdown, 'revenue': identity.revenue},
        content_result={'breakdown': content.breakdown, 'revenue': content.revenue},
        advertising_result={'breakdown': advertising.breakdown, 'revenue': advertising.revenue},
        exchange_result={'breakdown': exchange.breakdown, 'revenue': exchange.revenue},
        recapture_result={
            'total_revenue_source_vcoin': recapture.total_revenue_source_vcoin,
            'recapture_rate': recapture.recapture_rate,
        },
        staking_result={'stakers_count': staking_result.stakers_count},
        total_revenue=base_revenue,
    )
    
    # Calculate ACTUAL burn rate from simulation results
    # Burns come from token flow (% of collected tokens burned)
    monthly_emission = rewards.monthly_reward_pool
    actual_burn_rate = recapture.burns / monthly_emission if monthly_emission > 0 else 0
    
    # For buyback: use the CONFIGURED buyback_percent directly
    # Since buybacks are now revenue-based (% of USD revenue used to buy tokens),
    # the configured rate IS the actual commitment to buybacks
    # This fixes the scoring issue where revenue-based buybacks were undervalued
    actual_buyback_rate = params.buyback_percent
    
    # For governance: use EFFECTIVE participation (voters + delegators)
    # This better represents total governance engagement
    effective_gov_participation = getattr(governance_result, 'effective_participation_rate', None)
    if effective_gov_participation is None:
        # Fallback to voting participation if effective not available
        effective_gov_participation = governance_result.voting_participation_rate if governance_result.voting_participation_rate else 0
    governance_participation = effective_gov_participation / 100
    
    value_accrual_data = calculate_value_accrual_score(
        burn_rate=actual_burn_rate,
        buyback_rate=actual_buyback_rate,
        staking_ratio=staking_ratio,
        utility_score=utility_score,
        governance_participation=governance_participation,
        liquidity_ratio=liquidity_result.liquidity_ratio / 100 if liquidity_result.liquidity_ratio else 0
    )
    
    # Step 5f-2: Calculate Gini coefficient for token distribution
    # Uses REALISTIC holder distribution based on ACTUAL VCoin tokenomics:
    # - Real vesting schedules for each allocation category
    # - Actual number of holders per category (team, investors, users, etc.)
    # - Month-aware unlocks (distribution improves over time as vesting occurs)
    # - User rewards earned through platform participation
    
    from app.core.metrics import generate_realistic_holder_distribution
    
    # Get simulation month from params (default to platformAgeMonths or 1)
    simulation_month = getattr(params, 'platform_age_months', 6)
    
    # Monthly rewards for user distribution calculation
    monthly_rewards = rewards.gross_monthly_emission if rewards else 5_833_333
    
    # Generate realistic holder balances based on actual tokenomics
    holder_balances = generate_realistic_holder_distribution(
        simulation_month=simulation_month,
        active_users=users,
        monthly_rewards_vcoin=monthly_rewards,
        avg_user_balance=getattr(params, 'avg_stake_amount', 2000),
    )
    
    # Calculate Gini from realistic distribution
    gini_data = calculate_gini_coefficient(holder_balances)
    gini_result = GiniResult(
        gini=gini_data.get('gini', 0.7),
        interpretation=gini_data.get('interpretation', 'Concentrated'),
        decentralization_score=gini_data.get('decentralization_score', 30),
        holder_count=gini_data.get('holder_count', 0),
        top_1_percent_concentration=gini_data.get('top_1_percent_concentration', 0),
        top_10_percent_concentration=gini_data.get('top_10_percent_concentration', 0),
    )
    
    # Step 5f-3: Calculate Treasury Runway
    # Estimate treasury balance from accumulated reserves
    treasury_balance = getattr(params, 'treasury_revenue_share', 0.20) * base_revenue * 12  # Year's accumulation
    treasury_tokens = config.SUPPLY.TREASURY_ALLOCATION  # 200M VCoin reserved
    treasury_balance_from_tokens = treasury_tokens * params.token_price
    total_treasury_balance = treasury_balance + treasury_balance_from_tokens * 0.1  # 10% liquid
    
    # Estimate monthly expenses for runway calculation (detailed costs calculated later)
    estimated_monthly_expenses = base_revenue * 0.7  # Assume ~70% of revenue goes to costs
    
    runway_data = calculate_runway(
        treasury_balance_usd=total_treasury_balance,
        monthly_expenses_usd=estimated_monthly_expenses,
        monthly_revenue_usd=base_revenue
    )
    runway_result = RunwayResult(
        runway_months=runway_data.get('runway_months', 0) if runway_data.get('runway_months') != float('inf') else 999,
        runway_years=runway_data.get('runway_years', 0) if runway_data.get('runway_years') != float('inf') else 83,
        is_sustainable=runway_data.get('is_sustainable', False),
        interpretation=runway_data.get('interpretation', ''),
        net_burn_monthly=runway_data.get('net_burn_monthly', 0),
        monthly_revenue=runway_data.get('monthly_revenue', 0),
        monthly_expenses=runway_data.get('monthly_expenses', 0),
        treasury_balance=runway_data.get('treasury_balance', 0),
        runway_health=runway_data.get('runway_health', 0),
        months_to_sustainability=runway_data.get('months_to_sustainability', 0) if runway_data.get('months_to_sustainability') != float('inf') else 999,
    )
    
    # Step 5f-4: Calculate Inflation metrics
    # CRITICAL FIX: Distinguish between REWARDS emission and TOTAL new tokens entering circulation
    #
    # Token supply dynamics:
    # 1. Rewards Emission = new tokens distributed as user incentives (inflationary)
    # 2. Vesting Unlocks = existing allocated tokens becoming liquid (not truly inflationary,
    #    but DOES increase circulating supply and create sell pressure)
    #
    # For accurate supply tracking, we need BOTH:
    # - "Emission" = rewards emission only (for reward mechanism transparency)
    # - "Net Supply Change" = ALL new tokens entering circulation (for market impact)
    
    # Get total monthly unlocks from all categories (calculated earlier)
    total_monthly_unlocks_vcoin = sum(monthly_unlock_breakdown.values())
    
    # Rewards emission (what the platform is distributing as incentives)
    rewards_emission_vcoin = rewards.gross_monthly_emission
    rewards_emission_usd = rewards_emission_vcoin * params.token_price
    
    # Vesting unlocks (tokens becoming liquid from vesting schedules)
    vesting_unlocks_vcoin = total_monthly_unlocks_vcoin - rewards_emission_vcoin
    vesting_unlocks_usd = vesting_unlocks_vcoin * params.token_price
    
    # Deflationary mechanisms
    monthly_burns = recapture.burns
    monthly_burns_usd = monthly_burns * params.token_price
    monthly_buybacks = recapture.buybacks
    monthly_buybacks_usd = recapture.buyback_usd_spent
    
    total_deflationary = monthly_burns + monthly_buybacks
    
    # ========================================================================
    # 5-YEAR SUPPLY DYNAMICS - FULL ECOSYSTEM MODEL
    # ========================================================================
    # VCoin has FIXED total supply of 1B - true inflation = 0%
    # This models the COMPLETE ecosystem impact on circulating supply
    
    import math
    
    # === STEP 1: Calculate 5-year gross unlocks from vesting ===
    tge_supply = config.SUPPLY.TGE_CIRCULATING  # ~114M at TGE
    gross_year5_supply = config.get_circulating_supply_at_month(60)  # ~810M unlocked by month 60
    total_5yr_unlocks = gross_year5_supply - tge_supply  # ~696M total unlocks
    
    # === STEP 2: Estimate 5-year SCALED burns based on user/revenue growth ===
    # Burns scale with transaction volume (which scales with users)
    # Year 1: base users, Year 5: ~7.6x users (from 20K to 154K)
    # Use geometric growth for realistic scaling
    
    current_monthly_burns = recapture.burns  # Current month burns
    current_monthly_buybacks = recapture.buybacks  # Current month buybacks
    
    # 5-year user growth multipliers (from 5-year projection)
    # Year 1: 1x, Year 2: 1.9x, Year 3: 2.8x, Year 4: 4.6x, Year 5: 7.6x
    yearly_growth_multipliers = [1.0, 1.9, 2.8, 4.6, 7.6]
    
    # Calculate scaled 5-year burns (burns scale with transaction volume)
    total_5yr_burns = 0
    total_5yr_buybacks = 0
    for year_mult in yearly_growth_multipliers:
        yearly_burns = current_monthly_burns * year_mult * 12
        yearly_buybacks = current_monthly_buybacks * year_mult * 12
        total_5yr_burns += yearly_burns
        total_5yr_buybacks += yearly_buybacks
    
    total_5yr_deflationary = total_5yr_burns + total_5yr_buybacks
    
    # === STEP 3: Estimate staking lock-ups (reduces effective circulating) ===
    # Staking participation typically grows: 10% Year 1 → 40% Year 5
    avg_staking_rate = 0.25  # 25% average staking over 5 years
    staked_tokens_avg = gross_year5_supply * avg_staking_rate
    
    # === STEP 4: Treasury accumulation (20% of revenue goes to treasury) ===
    # Estimate 5-year revenue based on growth (from projection: ~$36.66M total)
    # Treasury buys tokens at average price, estimate ~$3 avg price over 5 years
    estimated_5yr_revenue = base_revenue * sum(yearly_growth_multipliers) * 12
    treasury_accumulation_usd = estimated_5yr_revenue * 0.10  # 10% to treasury token buys
    avg_token_price_5yr = 3.0  # Estimated average price over 5 years
    treasury_tokens_bought = treasury_accumulation_usd / avg_token_price_5yr
    
    # === STEP 5: Lost/inaccessible tokens (industry standard ~2-3%) ===
    lost_tokens = gross_year5_supply * 0.025  # 2.5% become inaccessible
    
    # === STEP 6: Calculate NET circulating supply at Year 5 ===
    # Net = Gross Unlocks - Burns - Buybacks - Staked - Treasury - Lost
    net_year5_circulating = (
        gross_year5_supply 
        - total_5yr_burns 
        - total_5yr_buybacks 
        - treasury_tokens_bought
        - lost_tokens
    )
    # Note: Staked tokens are still "circulating" but locked, shown separately
    
    effective_year5_circulating = net_year5_circulating - staked_tokens_avg
    
    # === STEP 7: Calculate TRUE 5-year supply CAGR (with deflationary effects) ===
    if tge_supply > 0 and net_year5_circulating > 0:
        # NET CAGR accounts for all deflationary mechanisms
        net_supply_cagr = (net_year5_circulating / tge_supply) ** (1/5) - 1
        annual_supply_growth_rate = net_supply_cagr * 100
        
        # Gross CAGR (without deflationary effects, for comparison)
        gross_supply_cagr = (gross_year5_supply / tge_supply) ** (1/5) - 1
        gross_annual_rate = gross_supply_cagr * 100
        
        # Deflationary impact = how much the ecosystem reduces supply growth
        deflationary_impact = gross_annual_rate - annual_supply_growth_rate
    else:
        annual_supply_growth_rate = 0
        gross_annual_rate = 0
        deflationary_impact = 0
    
    # === STEP 8: Calculate ecosystem deflationary efficiency ===
    # What % of gross unlocks are offset by deflationary mechanisms?
    total_deflationary_5yr = total_5yr_burns + total_5yr_buybacks + treasury_tokens_bought + lost_tokens
    ecosystem_efficiency = (total_deflationary_5yr / total_5yr_unlocks * 100) if total_5yr_unlocks > 0 else 0
    
    # ========================================================================
    # MONTH 60 (YEAR 5 END) METRICS - Show post-vesting state
    # ========================================================================
    # At Month 60, all vesting is complete. Only burns/buybacks remain.
    # This shows the TRUE long-term tokenomics state.
    
    # Get Month 60 unlock breakdown (should be 0 - vesting complete)
    month_60_unlocks = config.get_monthly_unlock_breakdown(60)
    month_60_total_unlocks = sum(month_60_unlocks.values())
    
    # Month 60 circulating supply
    month_60_circulating = config.get_circulating_supply_at_month(60)
    
    # At Month 60, burns/buybacks scale with Year 5 activity (7.6x multiplier)
    year5_monthly_burns = current_monthly_burns * 7.6
    year5_monthly_buybacks = current_monthly_buybacks * 7.6
    month_60_deflationary = year5_monthly_burns + year5_monthly_buybacks
    
    # Month 60 net supply change (should be NEGATIVE = deflationary)
    month_60_net_change = month_60_total_unlocks - month_60_deflationary
    
    # For display: Use Month 60 values
    net_monthly_supply_change = month_60_net_change
    net_monthly_supply_change_usd = month_60_net_change * params.token_price
    
    # Calculate Month 60 rates
    dilution_rate = (month_60_total_unlocks / month_60_circulating * 100) if month_60_circulating > 0 else 0
    net_dilution_rate = (month_60_net_change / month_60_circulating * 100) if month_60_circulating > 0 else 0
    
    # Annual rate based on Month 60 (extrapolated)
    annual_dilution_rate = net_dilution_rate * 12
    
    # Rewards emission at Month 60 (final month of emission)
    month_60_rewards = month_60_unlocks.get('REWARDS', 0)
    rewards_emission_rate = (month_60_rewards / month_60_circulating * 100) if month_60_circulating > 0 else 0
    
    # Burn efficiency at Month 60
    burn_efficiency = (month_60_deflationary / month_60_total_unlocks * 100) if month_60_total_unlocks > 0 else 100  # 100% if no unlocks
    
    # Update display values for Month 60
    # These will be shown in the UI
    rewards_emission_vcoin = month_60_rewards
    rewards_emission_usd = month_60_rewards * params.token_price
    vesting_unlocks_vcoin = month_60_total_unlocks - month_60_rewards
    vesting_unlocks_usd = vesting_unlocks_vcoin * params.token_price
    total_monthly_unlocks_vcoin = month_60_total_unlocks
    
    # === STEP 9: Determine supply status and health at Month 60 ===
    # At Month 60, the token SHOULD be deflationary (burns > unlocks)
    is_deflationary = month_60_net_change < 0
    
    # Label based on Month 60 state
    if is_deflationary:
        deflation_pct = abs(annual_dilution_rate)
        if deflation_pct > 1:
            deflation_strength = "Deflationary 🔥"
        else:
            deflation_strength = "Mildly Deflationary"
    elif month_60_total_unlocks == 0:
        deflation_strength = "Pure Deflationary 🔥"
    else:
        deflation_strength = "Post-Vesting"
    
    # Supply Health Score based on ecosystem efficiency
    # Score = Ecosystem Efficiency (0-50) + Low CAGR Bonus (0-30) + Staking (0-20)
    
    # Ecosystem efficiency score (higher = better)
    efficiency_score = min(50, ecosystem_efficiency * 2.5)  # 20% efficiency = 50 points
    
    # Low CAGR bonus (lower growth = healthier for holders)
    if annual_supply_growth_rate < 10:
        cagr_score = 30
    elif annual_supply_growth_rate < 25:
        cagr_score = 25
    elif annual_supply_growth_rate < 40:
        cagr_score = 15
    else:
        cagr_score = max(0, 30 - annual_supply_growth_rate * 0.5)
    
    # Staking score (higher staking = more locked supply)
    staking_score = min(20, avg_staking_rate * 50)  # 40% staking = 20 points
    
    supply_health_score = min(100, efficiency_score + cagr_score + staking_score)
    if is_deflationary:
        supply_health_score = min(100, supply_health_score + 10)
    
    # Calculate total monthly unlocks from breakdown
    total_monthly_unlocks = sum(monthly_unlock_breakdown.values())
    
    # Use Month 60 values for the inflation panel display
    month_60_burns_usd = year5_monthly_burns * params.token_price
    month_60_buybacks_usd = year5_monthly_buybacks * params.token_price
    
    # ========================================================================
    # YEARLY SNAPSHOTS - For slider showing each year-end state
    # ========================================================================
    yearly_snapshots = []
    year_growth_multipliers = [1.0, 1.9, 2.8, 4.6, 7.6]  # User growth per year
    
    for year in range(1, 6):
        year_end_month = year * 12
        
        # Get unlock breakdown for this year-end month
        year_unlocks = config.get_monthly_unlock_breakdown(year_end_month)
        year_total_unlocks = sum(year_unlocks.values())
        year_rewards = year_unlocks.get('REWARDS', 0)
        year_vesting = year_total_unlocks - year_rewards
        
        # Circulating supply at year end
        year_circulating = config.get_circulating_supply_at_month(year_end_month)
        
        # Burns/buybacks scaled by year's growth multiplier
        year_mult = year_growth_multipliers[year - 1]
        year_burns = current_monthly_burns * year_mult
        year_buybacks = current_monthly_buybacks * year_mult
        year_deflationary = year_burns + year_buybacks
        
        # Net change
        year_net_change = year_total_unlocks - year_deflationary
        
        # Rates
        year_net_rate = (year_net_change / year_circulating * 100) if year_circulating > 0 else 0
        year_annual_rate = year_net_rate * 12
        
        # Status
        year_is_deflationary = year_net_change < 0
        if year_is_deflationary:
            year_status = "Deflationary 🔥"
        elif year_total_unlocks == 0:
            year_status = "Pure Deflationary 🔥"
        elif year_net_rate < 1:
            year_status = "Near Neutral"
        elif year_net_rate < 5:
            year_status = "Low Growth"
        elif year_net_rate < 10:
            year_status = "Moderate Growth"
        else:
            year_status = "High Growth"
        
        yearly_snapshots.append({
            'year': year,
            'month': year_end_month,
            'rewards_emission': round(year_rewards, 0),
            'vesting_unlocks': round(year_vesting, 0),
            'total_unlocks': round(year_total_unlocks, 0),
            'burns': round(year_burns, 0),
            'buybacks': round(year_buybacks, 0),
            'total_deflationary': round(year_deflationary, 0),
            'net_change': round(year_net_change, 0),
            'circulating_supply': round(year_circulating, 0),
            'monthly_rate': round(year_net_rate, 3),
            'annual_rate': round(year_annual_rate, 2),
            'is_deflationary': year_is_deflationary,
            'status': year_status,
        })
    
    inflation_result = InflationResult(
        # Month 60: Rewards emission (final month, may be 0 if emission complete)
        monthly_emission=rewards_emission_vcoin,  # Month 60 rewards
        monthly_emission_usd=rewards_emission_usd,
        annual_emission=rewards_emission_vcoin * 12,
        emission_rate=round(rewards_emission_rate, 3),
        # Month 60: Vesting unlocks (should be 0 - vesting complete)
        vesting_unlocks=vesting_unlocks_vcoin,  # Month 60 vesting (0)
        vesting_unlocks_usd=vesting_unlocks_usd,
        dilution_rate=round(dilution_rate, 3),
        rewards_emission_rate=round(rewards_emission_rate, 3),
        # Month 60: Deflationary mechanisms (scaled to Year 5 activity)
        monthly_burns=year5_monthly_burns,  # Year 5 scaled burns
        monthly_burns_usd=month_60_burns_usd,
        monthly_buybacks=year5_monthly_buybacks,  # Year 5 scaled buybacks
        monthly_buybacks_usd=month_60_buybacks_usd,
        total_deflationary=month_60_deflationary,  # Year 5 total deflationary
        # Month 60: Net supply change (should be NEGATIVE = deflationary)
        net_monthly_inflation=net_monthly_supply_change,  # Month 60 net change
        net_monthly_inflation_usd=net_monthly_supply_change_usd,
        net_inflation_rate=round(net_dilution_rate, 3),
        annual_net_inflation_rate=round(annual_dilution_rate, 2),
        # Supply metrics at Month 60
        circulating_supply=month_60_circulating,  # Month 60 circulating
        total_supply=config.SUPPLY.TOTAL,
        # Month 60 unlock breakdown
        monthly_unlocks_breakdown=month_60_unlocks,  # Month 60 breakdown
        total_monthly_unlocks=month_60_total_unlocks,  # Month 60 total (should be 0)
        tge_circulating=config.SUPPLY.TGE_CIRCULATING,
        # Health indicators
        is_deflationary=is_deflationary,
        deflation_strength=deflation_strength,
        supply_health_score=round(supply_health_score, 1),
        # Projections
        months_to_max_supply=config.SUPPLY.REWARDS_DURATION_MONTHS,
        projected_year1_inflation=round(annual_dilution_rate, 2),  # Actually dilution, not inflation
        # Year 5 projection uses actual vesting schedule
        projected_year5_supply=config.get_circulating_supply_at_month(60, users=users, token_price=params.token_price),
        # ISSUE #5 FIX: Track additional supply sources
        referral_bonus_distributed=referral_result_early.bonus_distributed_vcoin if referral_result_early else 0,
        points_tokens_distributed=getattr(params.points, 'points_pool_tokens', 10_000_000) if (params.points and getattr(params.points, 'enable_points', True)) else 0,
        # ISSUE #7 FIX: Track emission breakdown
        staking_rewards_from_emission=staking_result.total_monthly_rewards if staking_result else 0,
        user_rewards_from_emission=rewards.monthly_reward_pool,
        # Yearly snapshots for slider
        yearly_snapshots=yearly_snapshots,
    )
    
    # Step 5f-5: Calculate Whale Concentration Analysis
    # Calculate pool TVL from protocol owned + community LP
    if liquidity_result:
        liquidity_pool_usd = liquidity_result.protocol_owned_usd + liquidity_result.community_lp_usd
    else:
        liquidity_pool_usd = 500_000
    whale_data = calculate_whale_concentration(
        holder_balances=holder_balances,
        total_supply=circulating_supply,
        token_price=params.token_price,
        liquidity_pool_usd=liquidity_pool_usd
    )
    
    # Convert whale data to result models
    def to_top_holders_group(data: dict) -> TopHoldersGroup:
        return TopHoldersGroup(
            holders_count=data.get('holders_count', 0),
            amount_vcoin=data.get('amount_vcoin', 0),
            amount_usd=data.get('amount_usd', 0),
            percentage=data.get('percentage', 0),
            avg_balance=data.get('avg_balance', 0),
        )
    
    whale_analysis_result = WhaleAnalysisResult(
        holder_count=whale_data.get('holder_count', 0),
        total_supply=whale_data.get('total_supply', 0),
        total_held=whale_data.get('total_held', 0),
        token_price=whale_data.get('token_price', 0),
        top_10=to_top_holders_group(whale_data.get('top_10', {})),
        top_50=to_top_holders_group(whale_data.get('top_50', {})),
        top_100=to_top_holders_group(whale_data.get('top_100', {})),
        top_1_percent=to_top_holders_group(whale_data.get('top_1_percent', {})),
        top_5_percent=to_top_holders_group(whale_data.get('top_5_percent', {})),
        top_10_percent=to_top_holders_group(whale_data.get('top_10_percent', {})),
        whale_count=whale_data.get('whale_count', 0),
        large_holder_count=whale_data.get('large_holder_count', 0),
        medium_holder_count=whale_data.get('medium_holder_count', 0),
        small_holder_count=whale_data.get('small_holder_count', 0),
        whales=[WhaleInfo(**w) for w in whale_data.get('whales', [])],
        concentration_risk_score=whale_data.get('concentration_risk_score', 0),
        risk_level=whale_data.get('risk_level', 'Unknown'),
        risk_color=whale_data.get('risk_color', 'gray'),
        dump_scenarios=[DumpScenarioResult(**s) for s in whale_data.get('dump_scenarios', [])],
        recommendations=whale_data.get('recommendations', []),
    )
    
    # Step 5f-6: Calculate Attack Scenario Analysis
    # Get governance voting power from top 10 (from whale data)
    top_10_voting = whale_data.get('top_10', {}).get('percentage', 30)
    team_token_pct = (config.TOKEN_ALLOCATION.TEAM.percent + config.TOKEN_ALLOCATION.ADVISORS.percent) * 100  # Convert to %
    
    # Estimate daily volume from activity
    daily_volume_estimate = base_revenue * 30  # Rough estimate
    
    attack_data = calculate_attack_scenarios(
        token_price=params.token_price,
        circulating_supply=circulating_supply,
        liquidity_pool_usd=liquidity_pool_usd,
        daily_volume_usd=daily_volume_estimate,
        staking_tvl_usd=staking_result.total_staked_usd if staking_result else 100_000,
        governance_voting_power_top_10=top_10_voting,
        team_token_percentage=team_token_pct,
        vesting_remaining_months=48,  # Assume 4 years vesting
        oracle_type="pyth",  # Solana uses Pyth
        has_timelock=True,
        timelock_delay_hours=48,
        has_multisig=True,
        multisig_threshold=3,
        slippage_tolerance=0.5,
    )
    
    # Convert to result model
    attack_analysis_result = AttackAnalysisResult(
        vulnerability_score=attack_data.get('vulnerability_score', 50),
        risk_level=attack_data.get('risk_level', 'Moderate'),
        risk_color=attack_data.get('risk_color', 'amber'),
        total_potential_loss_usd=attack_data.get('total_potential_loss_usd', 0),
        avg_severity_score=attack_data.get('avg_severity_score', 50),
        market_cap=attack_data.get('market_cap', 0),
        liquidity_ratio=attack_data.get('liquidity_ratio', 0),
        volume_to_liquidity=attack_data.get('volume_to_liquidity', 0),
        security_features=SecurityFeatures(
            **attack_data.get('security_features', {})
        ),
        scenarios=[
            AttackScenarioDetail(
                name=s.get('name', ''),
                category=s.get('category', ''),
                description=s.get('description', ''),
                attack_vector=s.get('attack_vector', ''),
                probability=s.get('probability', 0),
                severity=s.get('severity', 'low'),
                potential_loss_usd=s.get('potential_loss_usd', 0),
                potential_loss_percent=s.get('potential_loss_percent', 0),
                mitigation_effectiveness=s.get('mitigation_effectiveness', 0),
                recovery_time_days=s.get('recovery_time_days', 0),
                required_capital=s.get('required_capital', 0),
                complexity=s.get('complexity', 'medium'),
            )
            for s in attack_data.get('scenarios', [])
        ],
        recommendations=attack_data.get('recommendations', []),
    )
    
    # Step 5f-7: Calculate Liquidity Farming Analysis
    # Use liquidity pool TVL and estimate daily rewards based on reward allocation
    lp_reward_allocation = 0.10  # 10% of rewards go to LP
    daily_lp_rewards = (rewards.gross_monthly_emission / 30) * lp_reward_allocation
    trading_fee_apr = 0.12  # 12% from trading fees (Solana DEX typical)
    
    farming_data = calculate_full_farming_analysis(
        vcoin_price=params.token_price,
        pool_tvl_usd=liquidity_pool_usd,
        daily_reward_vcoin=daily_lp_rewards,
        trading_fee_apr=trading_fee_apr,
    )
    
    # Convert to result models
    def to_farming_simulation(sim_data: dict) -> FarmingSimulation:
        monthly_data = sim_data.get('monthly_projections', [])
        return FarmingSimulation(
            initial_investment_usd=sim_data.get('initial_investment_usd', 1000),
            initial_vcoin_price=sim_data.get('initial_vcoin_price', params.token_price),
            lp_share_percent=sim_data.get('lp_share_percent', 0),
            monthly_projections=[
                FarmingSimulationMonth(**m) for m in monthly_data
            ],
            final_result=FarmingSimulationMonth(**sim_data['final_result']) if sim_data.get('final_result') else None,
        )
    
    # Safely get nested data with defaults
    apy_data = farming_data.get('apy', {})
    risk_data = farming_data.get('risk_metrics', {})
    
    liquidity_farming_result = LiquidityFarmingResult(
        apy=FarmingAPY(
            reward_apr=apy_data.get('reward_apr', 0),
            fee_apr=apy_data.get('fee_apr', 0),
            total_apr=apy_data.get('total_apr', 0),
            reward_apy=apy_data.get('reward_apy', 0),
            fee_apy=apy_data.get('fee_apy', 0),
            total_apy=apy_data.get('total_apy', 0),
            daily_reward_rate=apy_data.get('daily_reward_rate', 0),
            daily_total_rate=apy_data.get('daily_total_rate', 0),
            pool_tvl_usd=apy_data.get('pool_tvl_usd', 0),
            daily_reward_vcoin=apy_data.get('daily_reward_vcoin', 0),
            daily_reward_usd=apy_data.get('daily_reward_usd', 0),
            is_sustainable=apy_data.get('is_sustainable', True),
            example_1000_final=apy_data.get('example_1000_final', 1000),
            example_1000_profit=apy_data.get('example_1000_profit', 0),
        ),
        il_scenarios=[
            ILScenario(**s) for s in farming_data.get('il_scenarios', [])
        ],
        simulations={
            case: to_farming_simulation(sim_data)
            for case, sim_data in farming_data.get('simulations', {}).items()
        },
        risk_metrics=FarmingRiskMetrics(
            risk_score=risk_data.get('risk_score', 30),
            risk_level=risk_data.get('risk_level', 'Moderate'),
            il_breakeven_multiplier=risk_data.get('il_breakeven_multiplier', 1.5),
            il_breakeven_price_up=risk_data.get('il_breakeven_price_up', 0),
            il_breakeven_price_down=risk_data.get('il_breakeven_price_down', 0),
        ),
        recommendations=farming_data.get('recommendations', []),
    )
    
    # Step 5f-8: Calculate Game Theory Analysis
    # Get staking APY from staking_result
    staking_apy = staking_result.staking_apy if staking_result else 15
    # Get whale distribution for voting power - ensure we have at least some data
    whale_balances = [w.balance for w in whale_analysis_result.whales] if whale_analysis_result and whale_analysis_result.whales else [100, 50, 30]
    if not whale_balances:
        whale_balances = [100, 50, 30]  # Fallback default
    
    # Issue #5, #6 Fix: Use proper parameter fields instead of getattr fallback
    # lock_period_months is an int, early_unstake_penalty is stored as decimal (0.10) but game theory expects percent (10)
    game_theory_data = calculate_full_game_theory_analysis(
        staking_apy=staking_apy,
        expected_price_change=10,  # Assume 10% annual appreciation
        price_volatility=40,  # 40% annual volatility for crypto
        lock_period_months=params.lock_period_months,
        early_unstake_penalty=params.early_unstake_penalty * 100,  # Convert decimal to percent
        voting_power_distribution=whale_balances[:10],  # Top 10 holders
        proposal_value_usd=100_000,  # Average proposal value
    )
    
    # Convert to result models
    game_theory_result = GameTheoryResult(
        strategies={
            k: StrategyMetrics(
                return_percent=v.get('return', 0),
                risk_percent=v.get('risk', 0),
                risk_adjusted_return=v.get('rar', 0),
            )
            for k, v in game_theory_data.get('staking_equilibrium', {}).get('strategies', {}).items()
        },
        equilibrium=StakingEquilibrium(
            stake_probability=game_theory_data.get('staking_equilibrium', {}).get('equilibrium', {}).get('stake_probability', 0),
            sell_probability=game_theory_data.get('staking_equilibrium', {}).get('equilibrium', {}).get('sell_probability', 0),
            hold_probability=game_theory_data.get('staking_equilibrium', {}).get('equilibrium', {}).get('hold_probability', 0),
            dominant_strategy=game_theory_data.get('staking_equilibrium', {}).get('equilibrium', {}).get('dominant_strategy', 'hold'),
            is_stable=game_theory_data.get('staking_equilibrium', {}).get('equilibrium', {}).get('is_stable', True),
            deviation_incentive=game_theory_data.get('staking_equilibrium', {}).get('equilibrium', {}).get('deviation_incentive', 0),
        ),
        analysis=StakingAnalysis(
            best_strategy=game_theory_data.get('staking_equilibrium', {}).get('analysis', {}).get('best_strategy', 'stake'),
            interpretation=game_theory_data.get('staking_equilibrium', {}).get('analysis', {}).get('interpretation', ''),
            recommendation=game_theory_data.get('staking_equilibrium', {}).get('analysis', {}).get('recommendation', ''),
            staking_breakeven_price_drop=game_theory_data.get('staking_equilibrium', {}).get('analysis', {}).get('staking_breakeven_price_drop', 0),
        ),
        governance_participation=GovernanceParticipation(
            rational_participants=game_theory_data.get('governance_game', {}).get('participation', {}).get('rational_participants', 0),
            total_holders=game_theory_data.get('governance_game', {}).get('participation', {}).get('total_holders', 0),
            participation_rate=game_theory_data.get('governance_game', {}).get('participation', {}).get('participation_rate', 0),
            participating_power=game_theory_data.get('governance_game', {}).get('participation', {}).get('participating_power', 0),
            quorum_achievable=game_theory_data.get('governance_game', {}).get('participation', {}).get('quorum_achievable', True),
        ),
        voter_apathy=VoterApathy(
            apathetic_ratio=game_theory_data.get('governance_game', {}).get('apathy', {}).get('apathetic_ratio', 0),
            risk_level=game_theory_data.get('governance_game', {}).get('apathy', {}).get('risk_level', 'Low'),
            interpretation=game_theory_data.get('governance_game', {}).get('apathy', {}).get('interpretation', ''),
        ),
        min_coalition_size=game_theory_data.get('governance_game', {}).get('coalition', {}).get('min_coalition_size', 0),
        min_coalition_power=game_theory_data.get('governance_game', {}).get('coalition', {}).get('min_coalition_power', 0),
        coordination=CoordinationGameAnalysis(
            game_type=game_theory_data.get('coordination_game', {}).get('game_analysis', {}).get('game_type', ''),
            description=game_theory_data.get('coordination_game', {}).get('game_analysis', {}).get('description', ''),
            equilibrium=game_theory_data.get('coordination_game', {}).get('game_analysis', {}).get('equilibrium', ''),
            cooperation_probability=game_theory_data.get('coordination_game', {}).get('mixed_equilibrium', {}).get('cooperation_probability', 50),
        ),
        cooperation_sustainable=game_theory_data.get('coordination_game', {}).get('repeated_game', {}).get('cooperation_sustainable', True),
        health_score=game_theory_data.get('overall', {}).get('health_score', 50),
        primary_risk=game_theory_data.get('overall', {}).get('primary_risk', 'None'),
        recommendations=game_theory_data.get('coordination_game', {}).get('recommendations', []),
    )
    
    # Step 5f-9: Calculate Sensitivity Analysis (ISSUE #1 FIX)
    # Run stress tests to see how the platform handles various crisis scenarios
    base_metrics = {
        'token_price': params.token_price,
        'monthly_users': users,
        'retention_rate': retention_rate / 100 if retention_rate is not None else 0.22,
        'monthly_revenue': base_module_revenue + future_modules_revenue,
        'liquidity': liquidity_pool_usd,
        'cac': customer_acquisition.blended_cac,
    }
    
    stress_test_results = run_all_stress_tests(base_metrics)
    
    # Convert stress test results to SensitivityResult
    from app.models.results import SensitivityResult, StressTestScenarioResult
    
    sensitivity_result = SensitivityResult(
        stress_tests={
            scenario: StressTestScenarioResult(
                scenario=data['scenario'],
                scenario_name=data['scenario_name'],
                description=data['description'],
                immediate_impact=data['immediate_impact'],
                max_drawdown_percent=data['max_drawdown_percent'],
                recovery_months=data['recovery_months'],
                permanent_impact_percent=data['permanent_impact_percent'],
                total_revenue_loss=data['total_revenue_loss'],
            )
            for scenario, data in stress_test_results['scenarios'].items()
        },
        worst_scenario=stress_test_results['worst_scenario'],
        least_severe_scenario=stress_test_results['least_severe_scenario'],
        # Monte Carlo can be added later if needed
        monte_carlo_p5=0,
        monte_carlo_p50=0,
        monte_carlo_p95=0,
    )
    
    token_metrics_result = TokenMetricsResult(
        velocity=filter_model_fields(velocity_data, TokenVelocityResult),
        real_yield=filter_model_fields(real_yield_data, RealYieldResult),
        value_accrual=filter_model_fields(value_accrual_data, ValueAccrualResult),
        overall_health=round(
            (velocity_data.get('health_score', 50) + 
             value_accrual_data.get('total_score', 50)) / 2, 1
        ),
        gini=gini_result,
        runway=runway_result,
        inflation=inflation_result,
        whale_analysis=whale_analysis_result,
        attack_analysis=attack_analysis_result,
        liquidity_farming=liquidity_farming_result,
        game_theory=game_theory_result,
    )
    
    # Step 5g (NEW): Calculate Pre-Launch Module metrics
    prelaunch_result = None
    prelaunch_costs = 0
    
    # Referral module
    # ISSUE #2 FIX: Referral was calculated early to include users in revenue calculations
    # Now we recalculate with actual revenue-based budget for cost tracking
    referral_result = None
    points_result = None
    gasless_result = None
    
    if referral_result_early is not None:
        # CRIT-004 Fix: Only allocate referral budget when platform has positive revenue
        # Budget is 10% of module revenue, minimum $500, capped at $5,000 in early stage
        if base_module_revenue > 0:
            referral_budget = max(500, min(5000, base_module_revenue * 0.10))
        else:
            # Platform is losing money - don't spend on referrals
            referral_budget = 0
        
        # Recalculate with actual budget for accurate cost tracking
        # User counts remain the same as early calculation
        ref_data_refined = calculate_referral(
            params, 
            users,  # Use final user count (includes referrals)
            referral_result_early.viral_coefficient, 
            referral_budget
        )
        
        referral_result = ReferralResult(
            total_users=ref_data_refined.total_users,
            users_with_referrals=ref_data_refined.users_with_referrals,
            total_referrals=ref_data_refined.total_referrals,
            qualified_referrals=referral_result_early.qualified_referrals,  # Keep early count for consistency
            referrers_by_tier=ref_data_refined.referrers_by_tier,
            referrals_by_tier=ref_data_refined.referrals_by_tier,
            bonus_distributed_vcoin=ref_data_refined.bonus_distributed_vcoin,
            bonus_distributed_usd=ref_data_refined.bonus_distributed_usd,
            avg_bonus_per_referrer_vcoin=ref_data_refined.avg_bonus_per_referrer_vcoin,
            viral_coefficient=ref_data_refined.viral_coefficient,
            effective_referral_rate=ref_data_refined.effective_referral_rate,
            qualification_rate=ref_data_refined.qualification_rate,
            monthly_referral_cost_vcoin=ref_data_refined.monthly_referral_cost_vcoin,
            monthly_referral_cost_usd=ref_data_refined.monthly_referral_cost_usd,
            suspected_sybil_referrals=ref_data_refined.suspected_sybil_referrals,
            sybil_rejection_rate=ref_data_refined.sybil_rejection_rate,
            breakdown=ref_data_refined.breakdown,
        )
        prelaunch_costs += ref_data_refined.monthly_referral_cost_usd
    
    # Points module (pre-launch only, uses waitlist users)
    waitlist_users = getattr(params, 'starting_waitlist_users', 1000)
    if params.points and getattr(params.points, 'enable_points', True):
        pts_data = calculate_points(
            waitlist_users=waitlist_users,
            participation_rate=getattr(params.points, 'participation_rate', 0.80),
            sybil_rate=getattr(params.points, 'sybil_rejection_rate', 0.05),
            points_pool_tokens=getattr(params.points, 'points_pool_tokens', 10_000_000),
        )
        points_result = PointsResult(
            points_pool_tokens=pts_data.points_pool_tokens,
            points_pool_percent=pts_data.points_pool_percent,
            waitlist_users=pts_data.waitlist_users,
            participating_users=pts_data.participating_users,
            participation_rate=pts_data.participation_rate,
            total_points_distributed=pts_data.total_points_distributed,
            avg_points_per_user=pts_data.avg_points_per_user,
            median_points_estimate=pts_data.median_points_estimate,
            tokens_per_point=pts_data.tokens_per_point,
            avg_tokens_per_user=pts_data.avg_tokens_per_user,
            users_by_segment=pts_data.users_by_segment,
            points_by_segment=pts_data.points_by_segment,
            tokens_by_segment=pts_data.tokens_by_segment,
            suspected_sybil_users=pts_data.suspected_sybil_users,
            sybil_rejection_rate=pts_data.sybil_rejection_rate,
            points_rejected=pts_data.points_rejected,
            points_by_activity=pts_data.points_by_activity,
            top_1_percent_tokens=pts_data.top_1_percent_tokens,
            top_10_percent_tokens=pts_data.top_10_percent_tokens,
            bottom_50_percent_tokens=pts_data.bottom_50_percent_tokens,
            breakdown=pts_data.breakdown,
        )
    
    # Gasless module
    if params.gasless and getattr(params.gasless, 'enable_gasless', True):
        gas_data = calculate_gasless(
            users=users,
            token_price=params.token_price,
            new_user_rate=getattr(params.gasless, 'new_user_rate', 0.30),
            monthly_budget_usd=getattr(params.gasless, 'monthly_sponsorship_budget_usd', 5000.0),
        )
        gasless_result = GaslessResult(
            total_users=gas_data.total_users,
            new_users=gas_data.new_users,
            verified_users=gas_data.verified_users,
            premium_users=gas_data.premium_users,
            enterprise_users=gas_data.enterprise_users,
            total_sponsored_transactions=gas_data.total_sponsored_transactions,
            avg_transactions_per_user=gas_data.avg_transactions_per_user,
            base_fee_cost_usd=gas_data.base_fee_cost_usd,
            priority_fee_cost_usd=gas_data.priority_fee_cost_usd,
            account_creation_cost_usd=gas_data.account_creation_cost_usd,
            total_sponsorship_cost_usd=gas_data.total_sponsorship_cost_usd,
            new_user_cost_usd=gas_data.new_user_cost_usd,
            verified_user_cost_usd=gas_data.verified_user_cost_usd,
            premium_user_cost_usd=gas_data.premium_user_cost_usd,
            enterprise_user_cost_usd=gas_data.enterprise_user_cost_usd,
            avg_cost_per_user_usd=gas_data.avg_cost_per_user_usd,
            cost_per_transaction_usd=gas_data.cost_per_transaction_usd,
            monthly_sponsorship_budget_usd=gas_data.monthly_sponsorship_budget_usd,
            budget_utilization=gas_data.budget_utilization,
            sponsorship_cost_vcoin=gas_data.sponsorship_cost_vcoin,
            breakdown=gas_data.breakdown,
        )
        prelaunch_costs += gas_data.total_sponsorship_cost_usd
    
    # Create combined PreLaunchResult
    if referral_result or points_result or gasless_result:
        prelaunch_result = PreLaunchResult(
            referral=referral_result,
            points=points_result,
            gasless=gasless_result,
            total_prelaunch_cost_usd=prelaunch_costs,
            total_prelaunch_cost_vcoin=prelaunch_costs / params.token_price if params.token_price > 0 else 0,
            points_tokens_allocated=points_result.points_pool_tokens if points_result else 0,
            referral_bonus_distributed=referral_result.bonus_distributed_vcoin if referral_result else 0,
            referral_users_acquired=referral_result.qualified_referrals if referral_result else 0,
            waitlist_conversion_tokens=points_result.points_pool_tokens if points_result else 0,
        )
    
    # Step 6: Calculate totals
    # Issue #15: Platform fee is counted as revenue ONCE (not double-counted)
    # Nov 2025: Added staking revenue and future modules to totals
    total_revenue = (
        identity.revenue + 
        content.revenue + 
        advertising.revenue + 
        exchange.revenue +
        staking_result.revenue +  # NEW: Staking generates revenue
        governance_result.revenue +  # NEW: Governance revenue
        future_modules_revenue +  # NEW: Future modules revenue
        platform_fees.reward_fee_usd  # Platform fee is revenue (Issue #15)
    )
    
    # Calculate module costs
    # Nov 2025: Added staking costs and future modules to totals
    module_costs = (
        identity.costs + 
        content.costs + 
        advertising.costs + 
        exchange.costs +
        staking_result.costs +  # NEW: Staking infrastructure costs
        governance_result.costs +  # NEW: Governance costs
        future_modules_costs +  # NEW: Future modules costs
        rewards.op_costs
    )
    
    # Issue #13: Add compliance costs if enabled
    compliance_costs = 0
    if params.include_compliance_costs and hasattr(params, 'compliance'):
        compliance_costs = params.compliance.monthly_total
    
    # Add pre-launch costs (referral bonuses + gasless sponsorship)
    total_costs = module_costs + compliance_costs + prelaunch_costs
    
    total_profit = total_revenue - total_costs
    total_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    totals = TotalsResult(
        revenue=round(total_revenue, 2),
        costs=round(total_costs, 2),
        profit=round(total_profit, 2),
        margin=round(total_margin, 1),
    )
    
    # Step 6b: Create initial customer_acquisition (LTV/CAC will be updated after 5-year projection)
    # We need placeholder values here because base_result is needed for 5-year calculation
    # The correct LTV/CAC will be calculated FROM the actual simulation results
    arpu_base = total_revenue / users if users > 0 else 0
    
    # Placeholder values - will be overwritten with simulation-based values
    customer_acquisition = CustomerAcquisitionMetrics(
        **customer_acquisition_base_data,
        ltv_estimate=0.0,  # Will be calculated from 5-year simulation
        ltv_cac_ratio=0.0,  # Will be calculated from 5-year simulation
        payback_months=0.0,  # Will be calculated from 5-year simulation
    )
    
    # Step 6f (NEW - Dec 2025): Recalculate 5A with actual values
    # Now we have staking and governance results to provide real values
    if five_a_enabled:
        five_a_result = calculate_five_a(
            params=params,
            users=users,
            base_reward_pool=rewards.monthly_reward_pool,
            base_fee_revenue=total_revenue,
            staking_apy=params.staking_apy if hasattr(params, 'staking_apy') else 0.10,
            total_staked=staking_result.total_staked if staking_result else 0,
            governance_power=governance_result.total_vevcoin_supply if governance_result else 0,
        )
    
    # Create base result first (for 5-year calculation)
    base_result = SimulationResult(
        # Starting users summary at the top for easy reference
        starting_users_summary=starting_users_summary,
        identity=identity,
        content=content,
        advertising=advertising,
        exchange=exchange,
        rewards=rewards,
        recapture=recapture,
        customer_acquisition=customer_acquisition,
        totals=totals,
        platform_fees=platform_fees,
        # NEW: Nov 2025
        liquidity=liquidity_result,
        staking=staking_result,
        governance=governance_result,
        vchain=vchain_result,
        marketplace=marketplace_result,
        business_hub=business_hub_result,
        cross_platform=cross_platform_result,
        token_metrics=token_metrics_result,
        # NEW: Pre-Launch Modules (Nov 2025)
        prelaunch=prelaunch_result,
        # NEW: 5A Policy Gamification (Dec 2025)
        five_a=five_a_result,
        # NEW: Organic User Growth (Dec 2025)
        organic_growth=organic_growth_result,
        # NEW: Sensitivity Analysis (Dec 2025 - ISSUE #1 FIX)
        sensitivity=sensitivity_result,
        # Supply Dynamics (inflation/dilution metrics)
        inflation=inflation_result,
    )
    
    # Step 7 (NEW - Dec 2025): Calculate 5-year projections
    # This ensures export JSON matches UI exactly
    try:
        five_year_result = calculate_5_year_projections(
            base_result=base_result,
            params=params,
        )
        base_result.five_year_projections = five_year_result
        
        # Step 7b: NOW calculate LTV/CAC from ACTUAL simulation results
        # This ensures LTV/CAC matches the profit shown in 5-year projections
        if five_year_result and five_year_result.years:
            # Get actual 5-year totals from simulation
            total_5yr_revenue = sum(yr.total_revenue for yr in five_year_result.years)
            total_5yr_marketing = sum(yr.marketing_budget for yr in five_year_result.years)
            final_users = five_year_result.years[-1].end_users if five_year_result.years else users
            
            # Calculate REAL LTV from simulation:
            # LTV = Total Revenue / Users (not just month 1 ARPU!)
            # This is the actual value generated by each user over 5 years
            ltv_from_simulation = total_5yr_revenue / final_users if final_users > 0 else 0
            
            # Calculate REAL CAC from simulation:
            # Total marketing spend / Total users acquired
            cac_from_simulation = total_5yr_marketing / final_users if final_users > 0 else effective_cac
            
            # Calculate proper LTV/CAC ratio from simulation
            ltv_cac_from_simulation = ltv_from_simulation / cac_from_simulation if cac_from_simulation > 0 else 0
            
            # Calculate payback months based on actual simulation ARPU
            # Use Year 1 average revenue / users for monthly ARPU
            year1_revenue = five_year_result.years[0].total_revenue if five_year_result.years else total_revenue
            year1_users = five_year_result.years[0].avg_users if five_year_result.years else users
            actual_arpu = (year1_revenue / 12) / year1_users if year1_users > 0 else arpu_base
            payback_from_simulation = cac_from_simulation / actual_arpu if actual_arpu > 0 else 0
            
            # Log for debugging
            print(f"LTV/CAC from simulation: 5yr Revenue=${total_5yr_revenue:,.0f}, "
                  f"Users={final_users:,}, LTV=${ltv_from_simulation:.2f}, "
                  f"CAC=${cac_from_simulation:.2f}, Ratio={ltv_cac_from_simulation:.2f}x")
            
            # Update customer_acquisition with REAL values from simulation
            # Override effective_cac with the 5-year calculated CAC
            updated_base_data = {
                **customer_acquisition_base_data,
                'effective_cac': round(cac_from_simulation, 2),  # Use 5-year CAC, not initial
            }
            updated_customer_acquisition = CustomerAcquisitionMetrics(
                **updated_base_data,
                ltv_estimate=round(ltv_from_simulation, 2),
                ltv_cac_ratio=round(ltv_cac_from_simulation, 2),
                payback_months=round(payback_from_simulation, 1),
            )
            
            # Update base_result with correct LTV/CAC
            base_result.customer_acquisition = updated_customer_acquisition
            
    except Exception as e:
        # If calculation fails, log error but don't break simulation
        print(f"Warning: 5-year projection calculation failed: {e}")
        base_result.five_year_projections = None
    
    return base_result
