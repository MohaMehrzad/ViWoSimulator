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
    GovernanceResult,
    VChainResult,
    MarketplaceResult,
    BusinessHubResult,
    CrossPlatformResult,
    TokenMetricsResult,
)
from app.models.results import (
    TokenVelocityResult, 
    RealYieldResult, 
    ValueAccrualResult,
    ReferralResult,
    PointsResult,
    GaslessResult,
    PreLaunchResult,
)
from app.core.modules.identity import calculate_identity
from app.core.modules.content import calculate_content
from app.core.modules.advertising import calculate_advertising
from app.core.modules.exchange import calculate_exchange
from app.core.modules.rewards import calculate_rewards, PLATFORM_FEE_RATE
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
from app.core.metrics import (
    calculate_token_velocity,
    calculate_real_yield,
    calculate_value_accrual_score,
    calculate_utility_score,
)
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
    advertising = calculate_advertising(params, users)
    exchange = calculate_exchange(params, users)
    
    # Step 3: Calculate rewards
    rewards = calculate_rewards(params, users)
    
    # Step 3b: Calculate base revenue for buyback calculation
    # Buybacks use USD revenue, so we need to calculate it before recapture
    base_module_revenue = (
        identity.revenue + content.revenue +
        advertising.revenue + exchange.revenue +
        rewards.platform_fee_usd  # Platform fee is primary revenue
    )
    
    # Step 4: Calculate recapture (Issue #10: now includes exchange)
    # Nov 2025: Now passes total_revenue_usd for revenue-based buybacks
    recapture = calculate_recapture(
        params, identity, content, advertising, 
        exchange,  # Issue #10: Added exchange module
        rewards, users,
        total_revenue_usd=base_module_revenue  # NEW: For revenue-based buybacks
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
    
    # Step 5d (NEW): Calculate Governance metrics
    governance_data = calculate_governance(
        params,
        stakers_count=staking_result.stakers_count,
        total_staked=staking_result.total_staked,
        circulating_supply=circulating_supply
    )
    governance_result = GovernanceResult(**{
        k: v for k, v in governance_data.items() 
        if k in GovernanceResult.model_fields
    })
    
    # Step 5e (NEW): Calculate Future Module metrics (if enabled)
    # Default to month 1 for deterministic (snapshot) simulation
    current_month = 1
    
    vchain_result = None
    marketplace_result = None
    business_hub_result = None
    cross_platform_result = None
    future_modules_revenue = 0
    future_modules_costs = 0
    
    if params.vchain and params.vchain.enable_vchain:
        vchain_data = calculate_vchain(params, current_month, users, params.token_price)
        vchain_result = VChainResult(**{
            k: v for k, v in vchain_data.items() 
            if k in VChainResult.model_fields
        })
        future_modules_revenue += vchain_result.revenue
        future_modules_costs += vchain_result.costs
    
    if params.marketplace and params.marketplace.enable_marketplace:
        mp_data = calculate_marketplace(params, current_month, users, params.token_price)
        marketplace_result = MarketplaceResult(**{
            k: v for k, v in mp_data.items() 
            if k in MarketplaceResult.model_fields
        })
        future_modules_revenue += marketplace_result.revenue
        future_modules_costs += marketplace_result.costs
    
    if params.business_hub and params.business_hub.enable_business_hub:
        bh_data = calculate_business_hub(params, current_month, users, params.token_price)
        business_hub_result = BusinessHubResult(**{
            k: v for k, v in bh_data.items() 
            if k in BusinessHubResult.model_fields
        })
        future_modules_revenue += business_hub_result.revenue
        future_modules_costs += business_hub_result.costs
    
    if params.cross_platform and params.cross_platform.enable_cross_platform:
        cp_data = calculate_cross_platform(params, current_month, users, params.token_price)
        cross_platform_result = CrossPlatformResult(**{
            k: v for k, v in cp_data.items() 
            if k in CrossPlatformResult.model_fields
        })
        future_modules_revenue += cross_platform_result.revenue
        future_modules_costs += cross_platform_result.costs
    
    # Step 5f (NEW): Calculate Token Metrics
    transaction_volume = recapture.total_revenue_source_vcoin
    
    # For staking ratio in Value Accrual: use the CONFIGURED participation rate
    # The raw staking_ratio (staked / circulating) is always tiny with 100M supply
    # The user's configured rate better represents their commitment to staking
    staking_participation = getattr(params, 'staking_participation_rate', 0.15)
    staking_apy = params.staking_apy
    
    # Boost the effective staking ratio based on APY (higher APY = more effective)
    # 10% APY = 1.0x, 20% APY = 1.5x, 30% APY = 2.0x
    apy_boost = 1.0 + (staking_apy - 0.10) * 5
    apy_boost = max(0.5, min(2.0, apy_boost))
    
    # Use participation rate as the staking_ratio for Value Accrual scoring
    # This reflects the % of users staking, which is what matters for token lockup
    staking_ratio = min(0.60, staking_participation * apy_boost)
    
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
    
    token_metrics_result = TokenMetricsResult(
        velocity=TokenVelocityResult(**{
            k: v for k, v in velocity_data.items()
            if k in TokenVelocityResult.model_fields
        }),
        real_yield=RealYieldResult(**{
            k: v for k, v in real_yield_data.items()
            if k in RealYieldResult.model_fields
        }),
        value_accrual=ValueAccrualResult(**{
            k: v for k, v in value_accrual_data.items()
            if k in ValueAccrualResult.model_fields
        }),
        overall_health=round(
            (velocity_data.get('health_score', 50) + 
             value_accrual_data.get('total_score', 50)) / 2, 1
        )
    )
    
    # Step 5g (NEW): Calculate Pre-Launch Module metrics
    prelaunch_result = None
    prelaunch_costs = 0
    
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
    
    referral_result = None
    points_result = None
    gasless_result = None
    
    # Referral module
    # Budget is 10% of module revenue, minimum $500, capped at $5,000 in early stage
    referral_budget = max(500, min(5000, base_module_revenue * 0.10))
    
    if params.referral and getattr(params.referral, 'enable_referral', True):
        ref_data = calculate_referral(params, users, viral_coefficient, referral_budget)
        referral_result = ReferralResult(
            total_users=ref_data.total_users,
            users_with_referrals=ref_data.users_with_referrals,
            total_referrals=ref_data.total_referrals,
            qualified_referrals=ref_data.qualified_referrals,
            referrers_by_tier=ref_data.referrers_by_tier,
            referrals_by_tier=ref_data.referrals_by_tier,
            bonus_distributed_vcoin=ref_data.bonus_distributed_vcoin,
            bonus_distributed_usd=ref_data.bonus_distributed_usd,
            avg_bonus_per_referrer_vcoin=ref_data.avg_bonus_per_referrer_vcoin,
            viral_coefficient=ref_data.viral_coefficient,
            effective_referral_rate=ref_data.effective_referral_rate,
            qualification_rate=ref_data.qualification_rate,
            monthly_referral_cost_vcoin=ref_data.monthly_referral_cost_vcoin,
            monthly_referral_cost_usd=ref_data.monthly_referral_cost_usd,
            suspected_sybil_referrals=ref_data.suspected_sybil_referrals,
            sybil_rejection_rate=ref_data.sybil_rejection_rate,
            breakdown=ref_data.breakdown,
        )
        prelaunch_costs += ref_data.monthly_referral_cost_usd
    
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
    
    return SimulationResult(
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
    )
