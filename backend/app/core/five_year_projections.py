"""
Five-year projection calculations for backend.

Ported from frontend Year5Overview.tsx to ensure export JSON
matches UI exactly. All calculations use the same logic as the
frontend display.

Dec 2025: Backend implementation of complex 5-year projections.
"""

import math
from typing import Dict, List, Any, Optional, Tuple
from app.models import SimulationParameters, SimulationResult
from app.models.results import YearlyProjection, FiveYearProjectionResult
from app.core.growth_constants import (
    GROWTH_SCENARIOS,
    MARKET_CONDITIONS,
    MARKET_CYCLE_2026_2030,
    FUTURE_MODULE_DEFAULTS,
)


# ARPU bounds based on industry benchmarks for social/crypto apps
MIN_ARPU = 0.10  # $0.10/user/month floor (freemium baseline)
MAX_ARPU = 5.00  # $5.00/user/month ceiling (mature platform)

# Maximum token price revenue boost to prevent unrealistic compounding
MAX_TOKEN_REVENUE_BOOST = 5.0


def get_marketing_budget_for_year(
    year: int,
    params: SimulationParameters
) -> Tuple[float, float]:
    """
    Calculate marketing budget for a specific year based on multipliers.
    
    Year 1: Base marketing_budget
    Year 2: Year 1 * year2Multiplier (default 2x)
    Year 3: Year 2 * year3Multiplier (default 2x = 4x of Y1)
    Year 4: Year 3 * year4Multiplier (default 2x = 8x of Y1)
    Year 5: Year 4 * year5Multiplier (default 2x = 16x of Y1)
    
    Returns:
        (budget, cumulative_multiplier)
    """
    base_budget = params.marketing_budget or 150000
    
    # Default to 2x (doubling each year) for realistic growth
    year2_mult = params.marketing_budget_year2_multiplier if hasattr(params, 'marketing_budget_year2_multiplier') else 2.0
    year3_mult = params.marketing_budget_year3_multiplier if hasattr(params, 'marketing_budget_year3_multiplier') else 2.0
    year4_mult = params.marketing_budget_year4_multiplier if hasattr(params, 'marketing_budget_year4_multiplier') else 2.0
    year5_mult = params.marketing_budget_year5_multiplier if hasattr(params, 'marketing_budget_year5_multiplier') else 2.0
    
    if year <= 1:
        return (base_budget, 1.0)
    
    year2_budget = base_budget * year2_mult
    if year == 2:
        return (year2_budget, year2_mult)
    
    year3_budget = year2_budget * year3_mult
    if year == 3:
        return (year3_budget, year2_mult * year3_mult)
    
    year4_budget = year3_budget * year4_mult
    if year == 4:
        return (year4_budget, year2_mult * year3_mult * year4_mult)
    
    year5_budget = year4_budget * year5_mult
    return (year5_budget, year2_mult * year3_mult * year4_mult * year5_mult)


def calculate_user_growth_price_multiplier(
    current_users: int,
    baseline_users: int,
    elasticity: float = 0.35,
    max_multiplier: float = 3.0
) -> Tuple[float, float, float]:
    """
    Calculate token price multiplier based on user growth with logarithmic dampening.
    
    Based on research:
    - Blockchain gaming: ~2.4x elasticity (12% DAU growth = 29% value increase)
    - Friend.tech: Strong correlation but needs dampening
    - Metcalfe's Law: Overstated for crypto; use dampened version
    
    Args:
        current_users: Current active user count
        baseline_users: Baseline users (Year 1) for comparison
        elasticity: How much growth translates to price (0.35 = 35%)
        max_multiplier: Maximum price multiplier cap
    
    Returns:
        (multiplier, user_growth_ratio, dampening_factor)
    """
    if baseline_users <= 0 or current_users <= 0:
        return (1.0, 1.0, 1.0)
    
    user_growth_ratio = current_users / baseline_users
    
    # No positive impact if users haven't grown
    if user_growth_ratio <= 1.0:
        return (1.0, user_growth_ratio, 1.0)
    
    # Logarithmic dampening based on user scale
    # At 1K users: dampening = 1.0, At 100K: 0.50, At 1M: 0.25
    log_users = math.log10(max(current_users, 1000))
    dampening_factor = 1.0 / (1.0 + 0.25 * (log_users - 3))  # log10(1000) = 3
    dampening_factor = max(0.1, min(1.0, dampening_factor))
    
    # Calculate impact: (growth_ratio - 1) * elasticity * dampening
    raw_growth_factor = user_growth_ratio - 1.0
    dampened_impact = raw_growth_factor * elasticity * dampening_factor
    
    # Final multiplier, capped
    multiplier = min(1.0 + dampened_impact, max_multiplier)
    
    return (multiplier, user_growth_ratio, dampening_factor)


def calculate_5_year_projections(
    base_result: SimulationResult,
    params: SimulationParameters,
) -> FiveYearProjectionResult:
    """
    Calculate 5-year (60-month) projections using the same logic as frontend.
    
    This is the main calculation function that produces revenue/user projections
    matching what users see in the UI.
    
    Args:
        base_result: Current simulation result (Month 1 or 6)
        params: Simulation parameters
    
    Returns:
        FiveYearProjectionResult with yearly breakdown
    """
    # Get scenario and market configs
    scenario_key = params.growth_scenario or 'base'
    market_key = params.market_condition or 'neutral'
    
    scenario_config = GROWTH_SCENARIOS.get(scenario_key, GROWTH_SCENARIOS['base'])
    market_config = MARKET_CONDITIONS.get(market_key, MARKET_CONDITIONS['neutral'])
    
    projections = []
    
    # Use total users with organic if available
    base_users = max(1, 
        base_result.customer_acquisition.total_users_with_organic 
        if hasattr(base_result.customer_acquisition, 'total_users_with_organic') 
        else base_result.customer_acquisition.total_users
    )
    base_revenue = base_result.totals.revenue
    base_token_price = params.token_price
    
    # Calculate ARPU from base results with bounds checking
    # This is the key fix: use per-user economics instead of scale-factor exponentiation
    raw_arpu = base_revenue / base_users if base_users > 0 else 0
    base_arpu = max(MIN_ARPU, min(MAX_ARPU, raw_arpu))
    
    current_users = base_users
    current_token_price = base_token_price
    
    for year in range(1, 6):  # Years 1-5
        start_month = (year - 1) * 12 + 1
        end_month = year * 12
        start_users = current_users
        start_price = current_token_price
        
        # Get market cycle data for calendar year
        calendar_year = 2026 + year - 1
        cycle_data = MARKET_CYCLE_2026_2030.get(calendar_year, {
            "year": calendar_year,
            "phase": "neutral",
            "growth_multiplier": 1.0,
            "retention_multiplier": 1.0,
            "price_multiplier": 1.0,
            "description": "",
        })
        cycle_multiplier = cycle_data.get("growth_multiplier", 1.0)
        
        # Get marketing budget for this year
        year_marketing_budget, marketing_multiplier = get_marketing_budget_for_year(year, params)
        
        # Calculate effective CAC (blended from NA and Global)
        na_percent = params.north_america_budget_percent or 0.35
        global_percent = params.global_low_income_budget_percent or 0.65
        na_cac = params.cac_north_america_consumer or 75
        global_cac = params.cac_global_low_income_consumer or 25
        effective_cac = na_percent * na_cac + global_percent * global_cac
        
        # Calculate marketing-driven user acquisition for years 2-5
        # Year 1 users come from baseResult, years 2-5 add from marketing budget
        # Apply diminishing returns: CAC increases and efficiency decreases in later years
        marketing_users_this_year = 0
        if year > 1 and year_marketing_budget > 0 and effective_cac > 0:
            # Diminishing returns on marketing efficiency:
            # Year 2: 85% efficiency, Year 3: 70%, Year 4: 60%, Year 5: 50%
            cac_efficiency = 1.0 / (year ** 0.4)
            
            # Marketing budget drives additional user acquisition with diminishing efficiency
            marketing_users_this_year = int(year_marketing_budget / effective_cac * cac_efficiency)
        
        # Calculate user growth price impact at START of year
        enable_price_impact = params.enable_user_growth_price_impact if hasattr(params, 'enable_user_growth_price_impact') else True
        elasticity = params.user_growth_price_elasticity if hasattr(params, 'user_growth_price_elasticity') else 0.35
        max_price_multiplier = params.user_growth_price_max_multiplier if hasattr(params, 'user_growth_price_max_multiplier') else 3.0
        
        user_growth_price_multiplier = 1.0
        user_growth_ratio = 1.0
        
        if enable_price_impact and year > 1:
            # Calculate based on start-of-year users vs Year 1 baseline
            multiplier, ratio, _ = calculate_user_growth_price_multiplier(
                start_users,
                base_users,
                elasticity,
                max_price_multiplier
            )
            user_growth_price_multiplier = multiplier
            user_growth_ratio = ratio
            
            # Apply user growth boost to token price at start of year
            current_token_price *= user_growth_price_multiplier
        
        year_revenue = 0.0
        year_profit = 0.0
        year_core_revenue = 0.0
        year_future_revenue = 0.0
        active_modules_set = set()
        
        # Month-by-month calculation within the year
        for month in range(start_month, end_month + 1):
            # Calculate monthly growth rate
            if year == 1:
                month_index = month - 1
                monthly_growth_rates = scenario_config.get("monthly_growth_rates", [0.05] * 12)
                monthly_growth_rate = (monthly_growth_rates[month_index] if month_index < len(monthly_growth_rates) else 0.05) * cycle_multiplier
            else:
                # Check if organic growth is enabled
                organic_enabled = False
                if hasattr(params, 'organic_growth') and params.organic_growth:
                    if isinstance(params.organic_growth, dict):
                        organic_enabled = params.organic_growth.get('enable_organic_growth', False)
                    elif hasattr(params.organic_growth, 'enable_organic_growth'):
                        organic_enabled = params.organic_growth.enable_organic_growth
                
                if organic_enabled:
                    # With organic growth enabled: REALISTIC social platform growth
                    monthly_rates = [0, 0.065, 0.075, 0.060, 0.050]
                    base_monthly_rate = monthly_rates[year - 1] if year - 1 < len(monthly_rates) else 0.05
                else:
                    # Without organic: Only marketing-driven growth (much slower)
                    monthly_rates = [0, 0.030, 0.025, 0.020, 0.015]
                    base_monthly_rate = monthly_rates[year - 1] if year - 1 < len(monthly_rates) else 0.02
                
                monthly_growth_rate = base_monthly_rate * cycle_multiplier
            
            if month > 1:
                # Apply monthly compounding growth
                current_users = round(current_users * (1 + monthly_growth_rate))
                
                # Add marketing-driven users (distributed across the year)
                if year > 1 and marketing_users_this_year > 0:
                    month_in_year = ((month - 1) % 12) + 1
                    distribution = {
                        1: 0.2333, 2: 0.1667, 3: 0.1000,
                        4: 0.0667, 5: 0.0667, 6: 0.0667,
                        7: 0.0556, 8: 0.0556, 9: 0.0556,
                        10: 0.0444, 11: 0.0444, 12: 0.0444,
                    }
                    monthly_marketing_users = int(marketing_users_this_year * distribution.get(month_in_year, 0))
                    current_users += monthly_marketing_users
            
            # Token price growth
            if year <= 2:
                price_growth_rate = ((cycle_data.get("price_multiplier", 1.0) - 1) / 12)
            else:
                price_growth_rate = (0.05 * cycle_data.get("price_multiplier", 1.0)) / 12
            current_token_price *= (1 + price_growth_rate)
            
            # Token price affects revenue: ~50% of revenue is token-denominated
            token_price_ratio = current_token_price / base_token_price
            raw_token_revenue_boost = 0.5 * (token_price_ratio - 1) + 1  # 50% of revenue scales with price
            token_revenue_boost = min(MAX_TOKEN_REVENUE_BOOST, raw_token_revenue_boost)
            
            # Platform maturity multiplier
            # Year 1: 1.0x, Year 2: 1.12x, Year 3: 1.24x, Year 4: 1.36x, Year 5: 1.48x
            maturity_multiplier = 1 + min(0.5, (year - 1) * 0.12)
            
            # FIXED: Use ARPU-based linear calculation
            # Revenue = users × ARPU × maturity × token boost
            month_core_revenue = current_users * base_arpu * maturity_multiplier * token_revenue_boost
            year_core_revenue += month_core_revenue
            
            # Calculate future module revenue
            month_future_revenue = 0.0
            
            # VChain
            vchain_defaults = FUTURE_MODULE_DEFAULTS.get("vchain", {})
            vchain_launch_month = vchain_defaults.get("vchain_launch_month", 24)
            # Check both flat parameter (from frontend) and nested parameter (from backend)
            enable_vchain = False
            if hasattr(params, 'enable_vchain') and params.enable_vchain:
                enable_vchain = True
            elif hasattr(params, 'vchain') and params.vchain and params.vchain.enable_vchain:
                enable_vchain = True
            
            if enable_vchain and month >= vchain_launch_month:
                months_active = month - vchain_launch_month + 1
                ramp_up = min(1.0, months_active / 12)
                base_volume = 25_000_000 * ramp_up
                revenue = base_volume * 0.002 + base_volume * 0.3 * 0.001 + base_volume * 0.1 * 0.08
                month_future_revenue += revenue
                active_modules_set.add('VChain')
            
            # Marketplace
            marketplace_defaults = FUTURE_MODULE_DEFAULTS.get("marketplace", {})
            marketplace_launch_month = marketplace_defaults.get("marketplace_launch_month", 18)
            # Check both flat parameter (from frontend) and nested parameter (from backend)
            enable_marketplace = False
            if hasattr(params, 'enable_marketplace') and params.enable_marketplace:
                enable_marketplace = True
            elif hasattr(params, 'marketplace') and params.marketplace and params.marketplace.enable_marketplace:
                enable_marketplace = True
            
            if enable_marketplace and month >= marketplace_launch_month:
                months_active = month - marketplace_launch_month + 1
                ramp_up = min(1.0, months_active / 12)
                gmv = current_users * 5 * ramp_up
                revenue = gmv * 0.4 * 0.08 + gmv * 0.6 * 0.15
                month_future_revenue += revenue
                active_modules_set.add('Marketplace')
            
            # Business Hub
            business_hub_defaults = FUTURE_MODULE_DEFAULTS.get("business_hub", {})
            business_hub_launch_month = business_hub_defaults.get("business_hub_launch_month", 21)
            # Check both flat parameter (from frontend) and nested parameter (from backend)
            enable_business_hub = False
            if hasattr(params, 'enable_business_hub') and params.enable_business_hub:
                enable_business_hub = True
            elif hasattr(params, 'business_hub') and params.business_hub and params.business_hub.enable_business_hub:
                enable_business_hub = True
            
            if enable_business_hub and month >= business_hub_launch_month:
                months_active = month - business_hub_launch_month + 1
                ramp_up = min(1.0, months_active / 12)
                freelancers = current_users * 0.02 * ramp_up
                revenue = freelancers * 500 * 0.12 + current_users * 0.05 * ramp_up * 15
                month_future_revenue += revenue
                active_modules_set.add('Business Hub')
            
            # Cross-Platform
            cross_platform_defaults = FUTURE_MODULE_DEFAULTS.get("cross_platform", {})
            cross_platform_launch_month = cross_platform_defaults.get("cross_platform_launch_month", 15)
            # Check both flat parameter (from frontend) and nested parameter (from backend)
            enable_cross_platform = False
            if hasattr(params, 'enable_cross_platform') and params.enable_cross_platform:
                enable_cross_platform = True
            elif hasattr(params, 'cross_platform') and params.cross_platform and params.cross_platform.enable_cross_platform:
                enable_cross_platform = True
            
            if enable_cross_platform and month >= cross_platform_launch_month:
                months_active = month - cross_platform_launch_month + 1
                ramp_up = min(1.0, months_active / 12)
                revenue = current_users * 0.03 * ramp_up * 10 + current_users * 0.01 * ramp_up * 50 * 0.15
                month_future_revenue += revenue
                active_modules_set.add('Cross-Platform')
            
            year_future_revenue += month_future_revenue
            month_total_revenue = month_core_revenue + month_future_revenue
            
            # Costs include operational costs (25% of revenue) plus marketing spend
            month_operational_costs = month_total_revenue * 0.25
            year_revenue += month_total_revenue
            year_profit += month_total_revenue - month_operational_costs
        
        # Subtract marketing budget from profit (it's an expense)
        year_profit_after_marketing = year_profit - year_marketing_budget
        
        # Update end-of-year user growth ratio for reporting
        end_of_year_growth_ratio = current_users / base_users
        
        # Create yearly projection
        projection = YearlyProjection(
            year=year,
            start_month=start_month,
            end_month=end_month,
            start_users=start_users,
            end_users=current_users,
            avg_users=round((start_users + current_users) / 2),
            total_revenue=round(year_revenue, 2),
            total_profit=round(year_profit_after_marketing, 2),
            avg_margin=round((year_profit_after_marketing / year_revenue * 100) if year_revenue > 0 else 0, 1),
            token_price_start=round(start_price, 6),
            token_price_end=round(current_token_price, 6),
            core_modules_revenue=round(year_core_revenue, 2),
            future_modules_revenue=round(year_future_revenue, 2),
            active_modules=list(active_modules_set),
            market_cycle=cycle_data.get("phase", "neutral"),
            cycle_multiplier=round(cycle_multiplier, 2),
            marketing_budget=round(year_marketing_budget, 2),
            marketing_multiplier=round(marketing_multiplier, 2),
            user_growth_price_multiplier=round(user_growth_price_multiplier, 6),
            user_growth_ratio=round(end_of_year_growth_ratio, 2),
        )
        projections.append(projection)
    
    # Calculate summary
    total_revenue = sum(p.total_revenue for p in projections)
    total_profit = sum(p.total_profit for p in projections)
    peak_users = max(p.end_users for p in projections)
    final_users = projections[-1].end_users if projections else 0
    final_token_price = projections[-1].token_price_end if projections else base_token_price
    
    summary = {
        "totalRevenue": round(total_revenue, 2),
        "totalProfit": round(total_profit, 2),
        "peakActiveUsers": peak_users,
        "finalActiveUsers": final_users,
        "estimatedFinalTokenPrice": round(final_token_price, 6),
        "note": "Backend-calculated projections matching frontend UI exactly.",
    }
    
    return FiveYearProjectionResult(
        available=True,
        source="calculated",
        years=projections,
        summary=summary,
    )
