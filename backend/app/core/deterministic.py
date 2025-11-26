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

MONEY FLOW DOCUMENTATION (Issue #15):
1. Module Revenue (USD) -> Totals revenue
2. Module Costs (USD) -> Totals costs
3. Platform Fee (5% of rewards) -> Added to revenue (NOT double-counted)
4. Compliance Costs -> Added to total costs
5. Recapture (VCoin only) -> Tracked separately, NOT revenue
"""

from app.models import (
    SimulationParameters,
    SimulationResult,
    CustomerAcquisitionMetrics,
    TotalsResult,
    PlatformFeesResult,
    LiquidityResult,
    StakingResult,
)
from app.core.modules.identity import calculate_identity
from app.core.modules.content import calculate_content
from app.core.modules.community import calculate_community
from app.core.modules.advertising import calculate_advertising
from app.core.modules.messaging import calculate_messaging
from app.core.modules.exchange import calculate_exchange
from app.core.modules.rewards import calculate_rewards, PLATFORM_FEE_RATE
from app.core.modules.recapture import calculate_recapture
from app.core.modules.liquidity import calculate_liquidity
from app.core.modules.staking import calculate_staking
from app.core.retention import apply_retention_to_snapshot, VCOIN_RETENTION
from app.config import config


def calculate_customer_acquisition(params: SimulationParameters) -> CustomerAcquisitionMetrics:
    """
    Calculate customer acquisition breakdown from marketing budget.
    Uses segmented acquisition model: creators + consumers across regions.
    
    Issue #2 fix: Uses updated realistic CAC values.
    """
    total_budget = params.marketing_budget
    
    # Creator costs (using updated realistic CAC from Issue #2)
    high_creator_cost = params.high_quality_creators_needed * params.high_quality_creator_cac
    mid_creator_cost = params.mid_level_creators_needed * params.mid_level_creator_cac
    total_creator_cost = high_creator_cost + mid_creator_cost
    
    # Consumer budget (remaining after creators)
    consumer_budget = max(0, total_budget - total_creator_cost)
    
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
    
    # Total users includes creators
    total_creators = params.high_quality_creators_needed + params.mid_level_creators_needed
    total_users = total_creators + na_users + global_users
    
    # Blended CAC
    blended_cac = total_budget / total_users if total_users > 0 else 0
    
    return CustomerAcquisitionMetrics(
        total_creator_cost=round(total_creator_cost, 2),
        consumer_acquisition_budget=round(consumer_budget, 2),
        north_america_budget=round(na_budget, 2),
        global_low_income_budget=round(global_budget, 2),
        north_america_users=na_users,
        global_low_income_users=global_users,
        total_users=total_users,
        blended_cac=round(blended_cac, 2),
    )


def run_deterministic_simulation(params: SimulationParameters) -> SimulationResult:
    """
    Run a complete deterministic simulation.
    Same inputs always produce same outputs.
    
    Key updates for 2025:
    - Issue #1: Applies retention model if enabled
    - Issue #9: Uses linear cost scaling
    - Issue #10: Includes exchange in recapture
    - Issue #13: Includes compliance costs
    - Nov 2025: Applies growth scenario multipliers when enabled
    """
    # Step 1: Calculate customer acquisition to get user count
    customer_acquisition = calculate_customer_acquisition(params)
    acquired_users = customer_acquisition.total_users
    
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
    
    # Issue #1 Fix: Apply retention model
    active_users = acquired_users
    if params.apply_retention and hasattr(params, 'retention'):
        platform_age = params.retention.platform_age_months
        active_users, retention_stats = apply_retention_to_snapshot(
            acquired_users,
            platform_age,
            VCOIN_RETENTION
        )
        # Ensure at least some users remain (minimum 10% of acquired)
        active_users = max(active_users, int(acquired_users * 0.10))
    
    users = active_users
    
    # Step 2: Calculate each module
    identity = calculate_identity(params, users)
    content = calculate_content(params, users)
    community = calculate_community(params, users)
    advertising = calculate_advertising(params, users)
    messaging = calculate_messaging(params, users)
    exchange = calculate_exchange(params, users)
    
    # Step 3: Calculate rewards
    rewards = calculate_rewards(params, users)
    
    # Step 4: Calculate recapture (Issue #10: now includes exchange)
    recapture = calculate_recapture(
        params, identity, content, community, advertising, messaging, 
        exchange,  # Issue #10: Added exchange module
        rewards, users
    )
    
    # Step 5: Create platform fees result from rewards data
    # Issue #15: Platform fee is revenue, NOT part of recapture
    platform_fees = PlatformFeesResult(
        reward_fee_vcoin=rewards.platform_fee_vcoin,
        reward_fee_usd=rewards.platform_fee_usd,
        fee_rate=PLATFORM_FEE_RATE,
    )
    
    # Step 5b (NEW): Calculate Liquidity metrics
    circulating_supply = config.SUPPLY.TGE_CIRCULATING
    liquidity_data = calculate_liquidity(
        params, 
        users, 
        monthly_volume=recapture.total_revenue_source_vcoin,
        circulating_supply=circulating_supply
    )
    liquidity_result = LiquidityResult(**liquidity_data)
    
    # Step 5c (NEW): Calculate Staking metrics
    staking_data = calculate_staking(
        params,
        users,
        monthly_emission=rewards.monthly_reward_pool,
        circulating_supply=circulating_supply
    )
    staking_result = StakingResult(**staking_data)
    
    # Step 6: Calculate totals
    # Issue #15: Platform fee is counted as revenue ONCE (not double-counted)
    # Nov 2025: Added staking revenue to totals
    total_revenue = (
        identity.revenue + 
        content.revenue + 
        community.revenue + 
        advertising.revenue + 
        messaging.revenue +
        exchange.revenue +
        staking_result.revenue +  # NEW: Staking generates revenue
        platform_fees.reward_fee_usd  # Platform fee is revenue (Issue #15)
    )
    
    # Calculate module costs
    # Nov 2025: Added staking costs to totals
    module_costs = (
        identity.costs + 
        content.costs + 
        community.costs + 
        advertising.costs + 
        messaging.costs + 
        exchange.costs +
        staking_result.costs +  # NEW: Staking infrastructure costs
        rewards.op_costs
    )
    
    # Issue #13: Add compliance costs if enabled
    compliance_costs = 0
    if params.include_compliance_costs and hasattr(params, 'compliance'):
        compliance_costs = params.compliance.monthly_total
    
    total_costs = module_costs + compliance_costs
    
    total_profit = total_revenue - total_costs
    total_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    totals = TotalsResult(
        revenue=round(total_revenue, 2),
        costs=round(total_costs, 2),
        profit=round(total_profit, 2),
        margin=round(total_margin, 1),
    )
    
    return SimulationResult(
        identity=identity,
        content=content,
        community=community,
        advertising=advertising,
        messaging=messaging,
        exchange=exchange,
        rewards=rewards,
        recapture=recapture,
        customer_acquisition=customer_acquisition,
        totals=totals,
        platform_fees=platform_fees,
        # NEW: Nov 2025
        liquidity=liquidity_result,
        staking=staking_result,
    )
