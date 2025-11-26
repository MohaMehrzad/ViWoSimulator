"""
REST API endpoints for simulations.

Updated to include monthly progression endpoint (Issue #16).
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.models import (
    SimulationParameters,
    MonteCarloOptions,
    AgentBasedOptions,
    MonthlyProgressionOptions,
    SimulationResult,
    MonteCarloResult,
    AgentBasedResult,
    MonthlyProgressionResult,
    PlatformMaturity,
    MATURITY_ADJUSTMENTS,
)
from app.core.deterministic import run_deterministic_simulation
from app.core.monte_carlo import run_monte_carlo_simulation
from app.core.agent_based import run_agent_based_simulation
from app.core.monthly_progression import run_monthly_progression_simulation, run_growth_scenario_simulation
from app.core.growth_scenarios import (
    GrowthScenario,
    MarketCondition,
    GROWTH_SCENARIOS,
    MARKET_CONDITIONS,
    get_all_scenario_comparison,
)
from app.core.retention import (
    VCOIN_RETENTION,
    SOCIAL_APP_RETENTION,
    CRYPTO_APP_RETENTION,
    GAMING_RETENTION,
    UTILITY_RETENTION,
)
from app.services.simulation_runner import SimulationRunner
import uuid

router = APIRouter()
simulation_runner = SimulationRunner()


@router.post("/simulate/deterministic", response_model=SimulationResult)
async def simulate_deterministic(params: SimulationParameters):
    """
    Run a deterministic simulation with the given parameters.
    Returns immediate results - same inputs always produce same outputs.
    
    Now includes:
    - Retention model (Issue #1)
    - Platform maturity adjustments (Issue #2, #3, #7)
    - Compliance costs (Issue #13)
    """
    try:
        result = run_deterministic_simulation(params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate/monte-carlo", response_model=MonteCarloResult)
async def simulate_monte_carlo(options: MonteCarloOptions):
    """
    Run a Monte Carlo simulation synchronously.
    Best for small iteration counts (< 500).
    """
    try:
        result = run_monte_carlo_simulation(
            options.parameters, 
            options.iterations
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate/monte-carlo/start")
async def start_monte_carlo(options: MonteCarloOptions):
    """
    Start a Monte Carlo simulation asynchronously.
    Returns a job ID for WebSocket tracking.
    """
    try:
        job_id = str(uuid.uuid4())
        simulation_runner.start_monte_carlo(
            job_id, 
            options.parameters, 
            options.iterations
        )
        return {"jobId": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate/agent-based", response_model=AgentBasedResult)
async def simulate_agent_based(options: AgentBasedOptions):
    """
    Run an agent-based simulation synchronously.
    Best for small agent counts (< 500).
    """
    try:
        result = run_agent_based_simulation(
            options.parameters,
            options.agent_count,
            options.duration_months
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate/agent-based/start")
async def start_agent_based(options: AgentBasedOptions):
    """
    Start an agent-based simulation asynchronously.
    Returns a job ID for WebSocket tracking.
    """
    try:
        job_id = str(uuid.uuid4())
        simulation_runner.start_agent_based(
            job_id,
            options.parameters,
            options.agent_count,
            options.duration_months
        )
        return {"jobId": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate/monthly-progression")
async def simulate_monthly_progression(options: MonthlyProgressionOptions):
    """
    Run a monthly progression simulation (Issue #16).
    
    Projects the platform growth over 6-60 months with:
    - Cohort-based retention tracking
    - Seasonality adjustments
    - CAC inflation as market saturates
    - Month-by-month financial projections
    
    If use_growth_scenarios is enabled, uses growth scenario projections:
    - Conservative, Base, Bullish scenarios
    - FOMO event triggers
    - Token price projections
    - Market condition multipliers
    
    Returns detailed monthly data including:
    - Active users after retention
    - Revenue, costs, profit per month
    - Token distribution and recapture
    - LTV/CAC ratios
    - Cumulative profit curve
    - (If growth scenarios) Token price curve and FOMO events
    """
    try:
        # Check if we should use growth scenarios
        use_growth = options.use_growth_scenarios or options.parameters.use_growth_scenarios
        
        if use_growth:
            result = run_growth_scenario_simulation(
                options.parameters,
                min(options.duration_months, 12),  # Growth scenarios max 12 months
                options.include_seasonality,
            )
        else:
            result = run_monthly_progression_simulation(
                options.parameters,
                options.duration_months,
                options.include_seasonality,
                options.market_saturation_factor,
            )
        
        # Build base monthly data
        monthly_data_list = []
        for m in result.monthly_data:
            month_dict = {
                "month": m.month,
                "users_acquired": m.users_acquired,
                "users_churned": m.users_churned,
                "active_users": m.active_users,
                "total_acquired_lifetime": m.total_acquired_lifetime,
                "retention_rate": m.retention_rate,
                "revenue": m.revenue,
                "costs": m.costs,
                "profit": m.profit,
                "margin": m.margin,
                "identity_revenue": m.identity_revenue,
                "content_revenue": m.content_revenue,
                "community_revenue": m.community_revenue,
                "advertising_revenue": m.advertising_revenue,
                "messaging_revenue": m.messaging_revenue,
                "exchange_revenue": m.exchange_revenue,
                "platform_fee_revenue": m.platform_fee_revenue,
                "tokens_distributed": m.tokens_distributed,
                "tokens_recaptured": m.tokens_recaptured,
                "recapture_rate": m.recapture_rate,
                "net_emission": m.net_emission,
                "cac_effective": m.cac_effective,
                "ltv_estimate": m.ltv_estimate,
                "marketing_spend": m.marketing_spend,
                "arpu": m.arpu,
                "arr": m.arr,
                "cohort_breakdown": m.cohort_breakdown,
                # Growth scenario fields
                "token_price": getattr(m, 'token_price', 0.03),
                "growth_rate": getattr(m, 'growth_rate', 0.0),
                "scenario_multiplier": getattr(m, 'scenario_multiplier', 1.0),
                "fomo_event": m.fomo_event.to_dict() if hasattr(m, 'fomo_event') and m.fomo_event else None,
                # Dynamic allocation fields (NEW - Nov 2025)
                "dynamic_allocation_percent": getattr(m, 'dynamic_allocation_percent', 0.0),
                "dynamic_growth_factor": getattr(m, 'dynamic_growth_factor', 0.0),
                "per_user_monthly_vcoin": getattr(m, 'per_user_monthly_vcoin', 0.0),
                "per_user_monthly_usd": getattr(m, 'per_user_monthly_usd', 0.0),
                "allocation_capped": getattr(m, 'allocation_capped', False),
            }
            monthly_data_list.append(month_dict)
        
        # Build response
        response = {
            "duration_months": result.duration_months,
            "monthly_data": monthly_data_list,
            "total_users_acquired": result.total_users_acquired,
            "peak_active_users": result.peak_active_users,
            "final_active_users": result.final_active_users,
            "average_retention_rate": result.average_retention_rate,
            "total_revenue": result.total_revenue,
            "total_costs": result.total_costs,
            "total_profit": result.total_profit,
            "average_margin": result.average_margin,
            "cagr_users": result.cagr_users,
            "cagr_revenue": result.cagr_revenue,
            "total_tokens_distributed": result.total_tokens_distributed,
            "total_tokens_recaptured": result.total_tokens_recaptured,
            "overall_recapture_rate": result.overall_recapture_rate,
            "months_to_profitability": result.months_to_profitability,
            "cumulative_profit_curve": result.cumulative_profit_curve,
            "retention_curve": result.retention_curve,
        }
        
        # Add growth scenario data if available
        if use_growth and result.growth_projection:
            gp = result.growth_projection
            response["growth_projection"] = {
                "scenario": gp.scenario,
                "market_condition": gp.market_condition,
                "starting_waitlist": gp.starting_waitlist,
                "monthly_mau": gp.monthly_mau,
                "monthly_acquired": gp.monthly_acquired,
                "monthly_churned": gp.monthly_churned,
                "monthly_growth_rates": gp.monthly_growth_rates,
                "token_price_curve": gp.token_price_curve,
                "token_price_start": gp.token_price_start,
                "token_price_month6": gp.token_price_month6,
                "token_price_end": gp.token_price_end,
                "fomo_events": [
                    {
                        "month": e.month,
                        "event_type": e.event_type,
                        "impact_multiplier": e.impact_multiplier,
                        "description": e.description,
                        "duration_days": e.duration_days,
                    }
                    for e in gp.fomo_events
                ],
                "total_users_acquired": gp.total_users_acquired,
                "month1_users": gp.month1_users,
                "month6_mau": gp.month6_mau,
                "final_mau": gp.final_mau,
                "peak_mau": gp.peak_mau,
                "growth_percentage": gp.growth_percentage,
                "waitlist_conversion_rate": gp.waitlist_conversion_rate,
                "month1_fomo_multiplier": gp.month1_fomo_multiplier,
                "viral_coefficient": gp.viral_coefficient,
            }
            response["scenario_used"] = result.scenario_used
            response["market_condition_used"] = result.market_condition_used
            response["token_price_final"] = result.token_price_final
            response["fomo_events_triggered"] = [
                e.to_dict() for e in result.fomo_events_triggered
            ] if result.fomo_events_triggered else []
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/retention-curves")
async def get_retention_curves():
    """
    Get available retention curves and their data points.
    Useful for displaying retention model options in the UI.
    """
    curves = {
        "vcoin": {
            "name": VCOIN_RETENTION.name,
            "description": VCOIN_RETENTION.description,
            "rates": VCOIN_RETENTION.monthly_rates,
        },
        "social_app": {
            "name": SOCIAL_APP_RETENTION.name,
            "description": SOCIAL_APP_RETENTION.description,
            "rates": SOCIAL_APP_RETENTION.monthly_rates,
        },
        "crypto_app": {
            "name": CRYPTO_APP_RETENTION.name,
            "description": CRYPTO_APP_RETENTION.description,
            "rates": CRYPTO_APP_RETENTION.monthly_rates,
        },
        "gaming": {
            "name": GAMING_RETENTION.name,
            "description": GAMING_RETENTION.description,
            "rates": GAMING_RETENTION.monthly_rates,
        },
        "utility": {
            "name": UTILITY_RETENTION.name,
            "description": UTILITY_RETENTION.description,
            "rates": UTILITY_RETENTION.monthly_rates,
        },
    }
    return curves


@router.get("/platform-maturity-tiers")
async def get_platform_maturity_tiers():
    """
    Get platform maturity tier definitions and their parameter adjustments.
    Useful for showing users what each tier means.
    """
    return {
        "tiers": [
            {
                "id": "launch",
                "name": "Launch Phase",
                "description": "0-6 months: New platform with limited brand recognition",
                "adjustments": MATURITY_ADJUSTMENTS[PlatformMaturity.LAUNCH],
            },
            {
                "id": "growing",
                "name": "Growth Phase",
                "description": "6-18 months: Gaining traction, improving metrics",
                "adjustments": MATURITY_ADJUSTMENTS[PlatformMaturity.GROWING],
            },
            {
                "id": "established",
                "name": "Established",
                "description": "18+ months: Mature platform with industry-standard rates",
                "adjustments": MATURITY_ADJUSTMENTS[PlatformMaturity.ESTABLISHED],
            },
        ]
    }


@router.get("/presets")
async def get_presets():
    """Get all available preset configurations"""
    from app.core.presets import PRESETS
    return PRESETS


@router.get("/growth-scenarios")
async def get_growth_scenarios():
    """
    Get available growth scenario configurations.
    
    Returns the three scenarios (Conservative, Base, Bullish) with:
    - Expected growth rates
    - FOMO event schedules
    - Token price projections
    - Retention benchmarks
    """
    scenarios = {}
    for scenario_enum, config in GROWTH_SCENARIOS.items():
        scenarios[scenario_enum.value] = {
            "name": config.name,
            "description": config.description,
            "waitlist_conversion_rate": config.waitlist_conversion_rate,
            "month1_fomo_multiplier": config.month1_fomo_multiplier,
            "monthly_growth_rates": config.monthly_growth_rates,
            "month1_retention": config.month1_retention,
            "month3_retention": config.month3_retention,
            "month6_retention": config.month6_retention,
            "month12_retention": config.month12_retention,
            "viral_coefficient": config.viral_coefficient,
            "token_price_start": config.token_price_start,
            "token_price_month6_multiplier": config.token_price_month6_multiplier,
            "token_price_end_multiplier": config.token_price_end_multiplier,
            "expected_month1_users": config.expected_month1_users,
            "expected_month12_mau": config.expected_month12_mau,
            "fomo_events": [e.to_dict() for e in config.fomo_events],
        }
    return scenarios


@router.get("/market-conditions")
async def get_market_conditions():
    """
    Get available market condition configurations.
    
    Returns Bear, Neutral, and Bull market multipliers.
    """
    conditions = {}
    for condition_enum, config in MARKET_CONDITIONS.items():
        conditions[condition_enum.value] = {
            "name": config.name,
            "description": config.description,
            "growth_multiplier": config.growth_multiplier,
            "retention_multiplier": config.retention_multiplier,
            "price_multiplier": config.price_multiplier,
            "fomo_multiplier": config.fomo_multiplier,
            "cac_multiplier": config.cac_multiplier,
        }
    return conditions


@router.get("/growth-scenarios/compare")
async def compare_growth_scenarios(
    market_condition: str = "bull",
    starting_waitlist: int = 1000,
    token_price: float = 0.03,
):
    """
    Compare all three growth scenarios under the same market condition.
    
    Useful for showing side-by-side comparison in the UI.
    """
    try:
        # Map string to enum
        condition_map = {
            "bear": MarketCondition.BEAR,
            "neutral": MarketCondition.NEUTRAL,
            "bull": MarketCondition.BULL,
        }
        condition = condition_map.get(market_condition.lower(), MarketCondition.BULL)
        
        comparison = get_all_scenario_comparison(
            condition, starting_waitlist, token_price
        )
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulate/status/{job_id}")
async def get_simulation_status(job_id: str):
    """Get the status of an async simulation"""
    status = simulation_runner.get_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return status
