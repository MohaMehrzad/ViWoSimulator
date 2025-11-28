"""
Sensitivity Analysis Module - Stress Testing and Monte Carlo Sensitivity.

Provides:
1. Parameter Impact Matrix - How each parameter affects key metrics
2. Stress Test Scenarios - Predefined crisis scenarios
3. Monte Carlo Sensitivity - Probabilistic outcomes with P5/P50/P95
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import random
import math


class StressScenario(Enum):
    """Predefined stress test scenarios"""
    PRICE_CRASH = "price_crash"           # 80% token price drop
    CHURN_CRISIS = "churn_crisis"         # 50% increase in churn
    AD_COLLAPSE = "ad_collapse"           # 70% drop in ad revenue
    EXCHANGE_DELISTING = "exchange_delisting"  # Major exchange delisting
    REGULATORY_BAN = "regulatory_ban"     # Regulatory action
    LIQUIDITY_CRISIS = "liquidity_crisis" # 60% liquidity drain
    COMPETITOR_LAUNCH = "competitor_launch"  # Major competitor entry
    HACK_EVENT = "hack_event"             # Security breach


@dataclass
class StressTestConfig:
    """Configuration for a stress test scenario"""
    name: str
    description: str
    
    # Impact multipliers (1.0 = no change)
    price_multiplier: float = 1.0
    user_growth_multiplier: float = 1.0
    retention_multiplier: float = 1.0
    revenue_multiplier: float = 1.0
    liquidity_multiplier: float = 1.0
    cac_multiplier: float = 1.0
    
    # Duration
    recovery_months: int = 6
    permanent_impact_percent: float = 0.0  # Permanent damage after recovery


# Predefined stress scenarios
STRESS_SCENARIOS: Dict[StressScenario, StressTestConfig] = {
    StressScenario.PRICE_CRASH: StressTestConfig(
        name="Token Price Crash",
        description="80% crash in token price due to market panic",
        price_multiplier=0.2,
        user_growth_multiplier=0.5,
        retention_multiplier=0.7,
        revenue_multiplier=0.4,
        liquidity_multiplier=0.5,
        cac_multiplier=1.5,
        recovery_months=12,
        permanent_impact_percent=0.10,
    ),
    StressScenario.CHURN_CRISIS: StressTestConfig(
        name="User Churn Crisis",
        description="Major UX issue or competitor steals 50% of users",
        price_multiplier=0.7,
        user_growth_multiplier=0.3,
        retention_multiplier=0.5,
        revenue_multiplier=0.5,
        liquidity_multiplier=0.9,
        cac_multiplier=2.0,
        recovery_months=9,
        permanent_impact_percent=0.20,
    ),
    StressScenario.AD_COLLAPSE: StressTestConfig(
        name="Advertising Collapse",
        description="Ad market crash or policy change kills 70% of ad revenue",
        price_multiplier=0.85,
        user_growth_multiplier=0.9,
        retention_multiplier=0.95,
        revenue_multiplier=0.5,  # Other revenue streams continue
        liquidity_multiplier=0.95,
        cac_multiplier=1.2,
        recovery_months=6,
        permanent_impact_percent=0.05,
    ),
    StressScenario.EXCHANGE_DELISTING: StressTestConfig(
        name="Exchange Delisting",
        description="Delisted from major exchange (e.g., Binance)",
        price_multiplier=0.4,
        user_growth_multiplier=0.6,
        retention_multiplier=0.8,
        revenue_multiplier=0.7,
        liquidity_multiplier=0.3,
        cac_multiplier=1.8,
        recovery_months=12,
        permanent_impact_percent=0.15,
    ),
    StressScenario.REGULATORY_BAN: StressTestConfig(
        name="Regulatory Ban",
        description="Banned in major market (e.g., US or EU)",
        price_multiplier=0.5,
        user_growth_multiplier=0.4,
        retention_multiplier=0.6,
        revenue_multiplier=0.4,
        liquidity_multiplier=0.5,
        cac_multiplier=2.5,
        recovery_months=18,
        permanent_impact_percent=0.30,
    ),
    StressScenario.LIQUIDITY_CRISIS: StressTestConfig(
        name="Liquidity Crisis",
        description="60% of liquidity withdrawn, death spiral risk",
        price_multiplier=0.35,
        user_growth_multiplier=0.5,
        retention_multiplier=0.6,
        revenue_multiplier=0.5,
        liquidity_multiplier=0.4,
        cac_multiplier=2.0,
        recovery_months=6,
        permanent_impact_percent=0.10,
    ),
    StressScenario.COMPETITOR_LAUNCH: StressTestConfig(
        name="Major Competitor Launch",
        description="Well-funded competitor launches similar product",
        price_multiplier=0.75,
        user_growth_multiplier=0.5,
        retention_multiplier=0.7,
        revenue_multiplier=0.7,
        liquidity_multiplier=0.85,
        cac_multiplier=1.8,
        recovery_months=12,
        permanent_impact_percent=0.25,
    ),
    StressScenario.HACK_EVENT: StressTestConfig(
        name="Security Breach / Hack",
        description="Smart contract exploit or platform hack",
        price_multiplier=0.3,
        user_growth_multiplier=0.2,
        retention_multiplier=0.4,
        revenue_multiplier=0.3,
        liquidity_multiplier=0.2,
        cac_multiplier=3.0,
        recovery_months=6,
        permanent_impact_percent=0.40,
    ),
}


def run_stress_test(
    scenario: StressScenario,
    base_metrics: Dict[str, float],
    months_to_simulate: int = 24
) -> Dict[str, any]:
    """
    Run a stress test scenario.
    
    Args:
        scenario: The stress scenario to test
        base_metrics: Current baseline metrics (revenue, users, price, etc.)
        months_to_simulate: How many months to simulate recovery
    
    Returns:
        Dict with stress test results and recovery curve
    """
    config = STRESS_SCENARIOS[scenario]
    
    # Apply immediate impact
    impacted_metrics = {
        'token_price': base_metrics.get('token_price', 0.03) * config.price_multiplier,
        'monthly_users': base_metrics.get('monthly_users', 1000) * config.user_growth_multiplier,
        'retention_rate': base_metrics.get('retention_rate', 0.22) * config.retention_multiplier,
        'monthly_revenue': base_metrics.get('monthly_revenue', 10000) * config.revenue_multiplier,
        'liquidity': base_metrics.get('liquidity', 500000) * config.liquidity_multiplier,
        'cac': base_metrics.get('cac', 50) * config.cac_multiplier,
    }
    
    # Calculate recovery curve
    recovery_curve = []
    for month in range(months_to_simulate):
        # Recovery follows logistic curve
        if month < config.recovery_months:
            recovery_percent = month / config.recovery_months
            # Logistic recovery
            recovery_factor = 1 / (1 + math.exp(-10 * (recovery_percent - 0.5)))
        else:
            recovery_factor = 1.0 - config.permanent_impact_percent
        
        month_metrics = {}
        for key, impacted_value in impacted_metrics.items():
            base_value = base_metrics.get(key, impacted_value)
            if key == 'cac':
                # CAC recovery is inverse
                final_base = base_value
                month_metrics[key] = impacted_value - (impacted_value - final_base) * recovery_factor
            else:
                final_target = base_value * (1 - config.permanent_impact_percent)
                month_metrics[key] = impacted_value + (final_target - impacted_value) * recovery_factor
        
        recovery_curve.append({
            'month': month + 1,
            'recovery_percent': round(recovery_factor * 100, 1),
            **{k: round(v, 2) for k, v in month_metrics.items()}
        })
    
    # Calculate total impact
    total_revenue_loss = sum(
        base_metrics.get('monthly_revenue', 10000) - curve['monthly_revenue']
        for curve in recovery_curve
    )
    
    max_drawdown = {
        key: round((base_metrics.get(key, impacted_metrics[key]) - impacted_metrics[key]) 
                   / base_metrics.get(key, 1) * 100, 1)
        for key in impacted_metrics.keys()
        if key != 'cac'
    }
    
    return {
        'scenario': scenario.value,
        'scenario_name': config.name,
        'description': config.description,
        'immediate_impact': {k: round(v, 2) for k, v in impacted_metrics.items()},
        'max_drawdown_percent': max_drawdown,
        'recovery_months': config.recovery_months,
        'permanent_impact_percent': config.permanent_impact_percent * 100,
        'total_revenue_loss': round(total_revenue_loss, 2),
        'recovery_curve': recovery_curve,
        'base_metrics': base_metrics,
    }


def calculate_parameter_sensitivity(
    parameter_name: str,
    base_value: float,
    base_result: float,
    test_range: Tuple[float, float] = (-0.5, 0.5),
    steps: int = 10
) -> Dict[str, any]:
    """
    Calculate sensitivity of a result to a parameter change.
    
    Args:
        parameter_name: Name of the parameter
        base_value: Base/current value of the parameter
        base_result: Base/current result value
        test_range: Range to test as percentage change (-50% to +50%)
        steps: Number of steps to test
    
    Returns:
        Dict with sensitivity analysis
    """
    step_size = (test_range[1] - test_range[0]) / steps
    
    sensitivity_data = []
    for i in range(steps + 1):
        change_percent = test_range[0] + (i * step_size)
        new_value = base_value * (1 + change_percent)
        
        # Estimate result change (linear approximation)
        # In practice, this would call the actual simulation
        result_change = change_percent  # Placeholder - real impl would run sim
        
        sensitivity_data.append({
            'parameter_change_percent': round(change_percent * 100, 1),
            'parameter_value': round(new_value, 4),
            'result_change_percent': round(result_change * 100, 1),
        })
    
    # Calculate elasticity (% change in result / % change in parameter)
    elasticity = 1.0  # Placeholder - would be calculated from actual data
    
    return {
        'parameter': parameter_name,
        'base_value': base_value,
        'base_result': base_result,
        'sensitivity_data': sensitivity_data,
        'elasticity': elasticity,
        'impact_level': 'High' if abs(elasticity) > 1.5 else 'Medium' if abs(elasticity) > 0.5 else 'Low',
    }


def run_monte_carlo_sensitivity(
    base_params: Dict[str, float],
    param_ranges: Dict[str, Tuple[float, float]],
    iterations: int = 1000,
    seed: Optional[int] = None
) -> Dict[str, any]:
    """
    Run Monte Carlo sensitivity analysis.
    
    Args:
        base_params: Base parameter values
        param_ranges: Min/max ranges for each parameter
        iterations: Number of iterations to run
        seed: Random seed for reproducibility
    
    Returns:
        Dict with P5, P50, P95 outcomes and distribution data
    """
    if seed is not None:
        random.seed(seed)
    
    results = []
    
    for _ in range(iterations):
        # Sample parameters
        sampled_params = {}
        for param, base_val in base_params.items():
            if param in param_ranges:
                min_val, max_val = param_ranges[param]
                sampled_params[param] = random.uniform(min_val, max_val)
            else:
                sampled_params[param] = base_val
        
        # Calculate result (simplified - real impl would run full simulation)
        # This is a placeholder that combines parameters
        result = sum(sampled_params.values()) / len(sampled_params)
        results.append({
            'params': sampled_params.copy(),
            'result': result,
        })
    
    # Sort by result
    sorted_results = sorted(results, key=lambda x: x['result'])
    
    # Calculate percentiles
    p5_idx = int(iterations * 0.05)
    p25_idx = int(iterations * 0.25)
    p50_idx = int(iterations * 0.50)
    p75_idx = int(iterations * 0.75)
    p95_idx = int(iterations * 0.95)
    
    result_values = [r['result'] for r in sorted_results]
    
    return {
        'iterations': iterations,
        'percentiles': {
            'P5': round(result_values[p5_idx], 4),
            'P25': round(result_values[p25_idx], 4),
            'P50': round(result_values[p50_idx], 4),
            'P75': round(result_values[p75_idx], 4),
            'P95': round(result_values[p95_idx], 4),
        },
        'statistics': {
            'mean': round(sum(result_values) / len(result_values), 4),
            'min': round(min(result_values), 4),
            'max': round(max(result_values), 4),
            'std_dev': round(
                (sum((x - sum(result_values)/len(result_values))**2 for x in result_values) / len(result_values)) ** 0.5,
                4
            ),
        },
        'worst_case': sorted_results[p5_idx],
        'best_case': sorted_results[p95_idx],
        'base_case': sorted_results[p50_idx],
    }


def generate_impact_matrix(
    parameters: List[str],
    metrics: List[str]
) -> Dict[str, any]:
    """
    Generate parameter impact matrix showing how each parameter affects each metric.
    
    Args:
        parameters: List of parameter names
        metrics: List of metric names
    
    Returns:
        Dict with impact matrix
    """
    # Impact ratings: -3 (strong negative) to +3 (strong positive)
    # These are example values - real implementation would calculate from data
    
    default_impacts = {
        ('token_price', 'revenue'): 2,
        ('token_price', 'user_growth'): 1,
        ('token_price', 'staking'): 2,
        ('burn_rate', 'price'): 2,
        ('burn_rate', 'supply'): -3,
        ('buyback_rate', 'price'): 2,
        ('staking_apy', 'staking'): 3,
        ('staking_apy', 'sell_pressure'): -2,
        ('cac', 'user_growth'): -2,
        ('cac', 'profitability'): -2,
        ('retention', 'ltv'): 3,
        ('retention', 'revenue'): 2,
        ('ad_cpm', 'revenue'): 2,
        ('conversion_rate', 'revenue'): 3,
        ('liquidity', 'price_stability'): 2,
        ('liquidity', 'slippage'): -2,
    }
    
    matrix = {}
    for param in parameters:
        matrix[param] = {}
        for metric in metrics:
            impact = default_impacts.get((param, metric), 0)
            matrix[param][metric] = {
                'impact': impact,
                'level': 'High' if abs(impact) >= 2 else 'Medium' if abs(impact) >= 1 else 'Low',
                'direction': 'positive' if impact > 0 else 'negative' if impact < 0 else 'neutral',
            }
    
    return {
        'parameters': parameters,
        'metrics': metrics,
        'matrix': matrix,
    }


def run_all_stress_tests(
    base_metrics: Dict[str, float]
) -> Dict[str, any]:
    """
    Run all stress test scenarios and compare results.
    
    Args:
        base_metrics: Current baseline metrics
    
    Returns:
        Dict with all stress test results and comparison
    """
    results = {}
    
    for scenario in StressScenario:
        results[scenario.value] = run_stress_test(scenario, base_metrics)
    
    # Rank scenarios by severity
    severity_ranking = sorted(
        results.items(),
        key=lambda x: x[1]['total_revenue_loss'],
        reverse=True
    )
    
    return {
        'scenarios': results,
        'severity_ranking': [
            {
                'scenario': scenario,
                'revenue_loss': data['total_revenue_loss'],
                'recovery_months': data['recovery_months'],
                'permanent_impact': data['permanent_impact_percent'],
            }
            for scenario, data in severity_ranking
        ],
        'worst_scenario': severity_ranking[0][0],
        'least_severe_scenario': severity_ranking[-1][0],
    }

