"""
Monte Carlo simulation engine.
Runs many iterations with randomized parameters to understand probability distributions.
"""

import numpy as np
from typing import Callable, Optional, List
from app.models import (
    SimulationParameters,
    SimulationResult,
    MonteCarloResult,
    PercentileResults,
    StatisticsResult,
)
from app.core.deterministic import run_deterministic_simulation


def add_noise_to_parameters(
    params: SimulationParameters, 
    rng: np.random.Generator
) -> SimulationParameters:
    """
    Add random noise to parameters for Monte Carlo variation.
    Uses appropriate distributions for each parameter type.
    Bounds are relative to base values (0.5x to 2x) to prevent extreme skew.
    """
    # Create a copy of params as dict
    param_dict = params.model_dump()
    
    # Token price - log-normal distribution (prices tend to be log-normal)
    # Clip to 0.5x to 2x of base price
    param_dict['token_price'] = np.clip(
        params.token_price * rng.lognormal(0, 0.15),
        params.token_price * 0.5,
        params.token_price * 2.0
    )
    
    # User acquisition rates - normal distribution with relative bounds
    # Clip to 0.5x to 2x of base value (prevents extreme revenue skew)
    param_dict['verification_rate'] = np.clip(
        params.verification_rate * rng.normal(1, 0.15),
        params.verification_rate * 0.5,
        params.verification_rate * 2.0
    )
    
    # Activity rates - normal distribution with relative bounds
    param_dict['posts_per_user'] = max(1, int(np.clip(
        params.posts_per_user * rng.normal(1, 0.2),
        params.posts_per_user * 0.5,
        params.posts_per_user * 2.0
    )))
    param_dict['ad_cpm_multiplier'] = np.clip(
        params.ad_cpm_multiplier * rng.normal(1, 0.2),
        max(0.05, params.ad_cpm_multiplier * 0.5),
        min(1.0, params.ad_cpm_multiplier * 2.0)
    )
    
    # CAC variation - relative bounds to prevent extreme skew
    param_dict['cac_north_america_consumer'] = np.clip(
        params.cac_north_america_consumer * rng.normal(1, 0.15),
        max(5, params.cac_north_america_consumer * 0.7),
        params.cac_north_america_consumer * 1.5
    )
    param_dict['cac_global_low_income_consumer'] = np.clip(
        params.cac_global_low_income_consumer * rng.normal(1, 0.15),
        max(2, params.cac_global_low_income_consumer * 0.7),
        params.cac_global_low_income_consumer * 1.5
    )
    
    # Burn and buyback - relative bounds with small variance
    param_dict['burn_rate'] = np.clip(
        params.burn_rate * rng.normal(1, 0.1),
        max(0, params.burn_rate * 0.7),
        min(0.5, params.burn_rate * 1.5)
    )
    param_dict['buyback_percent'] = np.clip(
        params.buyback_percent * rng.normal(1, 0.1),
        max(0, params.buyback_percent * 0.7),
        min(0.5, params.buyback_percent * 1.5)
    )
    
    return SimulationParameters(**param_dict)


def run_monte_carlo_simulation(
    params: SimulationParameters,
    iterations: int = 1000,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    seed: Optional[int] = None
) -> MonteCarloResult:
    """
    Run Monte Carlo simulation with specified iterations.
    
    Args:
        params: Base simulation parameters
        iterations: Number of simulation iterations
        progress_callback: Optional callback for progress updates
        seed: Random seed for reproducibility
    
    Returns:
        MonteCarloResult with percentiles, distributions, and statistics
    """
    rng = np.random.default_rng(seed)
    
    # Storage for results
    revenues: List[float] = []
    profits: List[float] = []
    recapture_rates: List[float] = []
    all_results: List[SimulationResult] = []
    
    for i in range(iterations):
        # Add noise to parameters
        varied_params = add_noise_to_parameters(params, rng)
        
        # Run simulation
        result = run_deterministic_simulation(varied_params)
        
        # Store results
        revenues.append(result.totals.revenue)
        profits.append(result.totals.profit)
        recapture_rates.append(result.recapture.recapture_rate)
        all_results.append(result)
        
        # Progress callback
        if progress_callback and (i + 1) % max(1, iterations // 100) == 0:
            progress_callback(i + 1, iterations)
    
    # Convert to numpy arrays for percentile calculations
    revenues_arr = np.array(revenues)
    profits_arr = np.array(profits)
    recapture_arr = np.array(recapture_rates)
    
    # Issue #4 Fix: Use simple percentage-based index calculation instead of np.percentile on indices
    # This correctly selects the 5th, 50th, and 95th percentile results from the sorted array
    p5_idx = max(0, int(0.05 * iterations) - 1)
    p50_idx = int(0.50 * iterations)
    p95_idx = min(iterations - 1, int(0.95 * iterations))
    
    # Sort results by revenue to get percentile results
    sorted_indices = np.argsort(revenues_arr)
    
    percentiles = PercentileResults(
        p5=all_results[sorted_indices[p5_idx]],
        p50=all_results[sorted_indices[p50_idx]],
        p95=all_results[sorted_indices[p95_idx]],
    )
    
    # Calculate statistics
    statistics = StatisticsResult(
        mean={
            'revenue': float(np.mean(revenues_arr)),
            'profit': float(np.mean(profits_arr)),
            'recaptureRate': float(np.mean(recapture_arr)),
        },
        std={
            'revenue': float(np.std(revenues_arr)),
            'profit': float(np.std(profits_arr)),
            'recaptureRate': float(np.std(recapture_arr)),
        },
    )
    
    # Sample distributions for visualization (max 100 points)
    sample_size = min(100, iterations)
    sample_indices = rng.choice(iterations, sample_size, replace=False)
    
    distributions = {
        'revenue': [revenues[i] for i in sample_indices],
        'profit': [profits[i] for i in sample_indices],
        'recaptureRate': [recapture_rates[i] for i in sample_indices],
    }
    
    return MonteCarloResult(
        iterations=iterations,
        percentiles=percentiles,
        distributions=distributions,
        statistics=statistics,
    )


