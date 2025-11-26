"""
Rewards Module calculations.

Updated November 2025: Added dynamic reward allocation based on user growth.
Uses logarithmic scaling to ensure rewards grow proportionally with user base,
preventing token inflation while ensuring early users receive meaningful rewards.
"""

import math
from typing import Tuple, NamedTuple
from app.config import config
from app.models import SimulationParameters, RewardsResult

# Fixed platform fee rate (5% of rewards)
PLATFORM_FEE_RATE = 0.05


class DynamicAllocationResult(NamedTuple):
    """Result of dynamic allocation calculation"""
    allocation_percent: float  # Final allocation percentage (0-1)
    growth_factor: float  # User growth factor (0-1)
    per_user_monthly_vcoin: float  # VCoin per user per month
    per_user_monthly_usd: float  # USD equivalent per user per month
    allocation_capped: bool  # Whether per-user cap was applied


def calculate_dynamic_allocation(
    current_users: int,
    token_price: float,
    initial_users: int = 1000,
    target_users: int = 1_000_000,
    min_allocation: float = 0.05,
    max_allocation: float = 0.90,
    max_per_user_monthly_usd: float = 50.0,
    min_per_user_monthly_usd: float = 0.10,
    monthly_emission: int = None,
) -> DynamicAllocationResult:
    """
    Calculate dynamic reward allocation based on user growth.
    
    Uses a logarithmic scaling formula that:
    1. Starts at min_allocation (5%) for initial_users
    2. Grows to max_allocation (90%) as users reach target_users
    3. Applies safety caps to prevent unsustainable per-user rewards
    
    Formula:
        growth_factor = min(1.0, ln(current_users / initial_users) / ln(target_users / initial_users))
        allocation = min_allocation + (max_allocation - min_allocation) * growth_factor
    
    Args:
        current_users: Current active user count
        token_price: Current VCoin price in USD
        initial_users: Starting point for allocation scaling (growth_factor = 0)
        target_users: Point at which max allocation is reached (growth_factor = 1)
        min_allocation: Minimum allocation percentage (default 5%)
        max_allocation: Maximum allocation percentage (default 90%)
        max_per_user_monthly_usd: Maximum per-user reward in USD (inflation guard)
        min_per_user_monthly_usd: Minimum per-user reward in USD
        monthly_emission: Base monthly emission pool (defaults to config value)
    
    Returns:
        DynamicAllocationResult with allocation details
    """
    if monthly_emission is None:
        monthly_emission = config.MONTHLY_EMISSION
    
    # Ensure minimum users to prevent division issues
    current_users = max(1, current_users)
    initial_users = max(1, initial_users)
    target_users = max(initial_users + 1, target_users)
    
    # Calculate growth factor using logarithmic scaling
    # This provides a natural curve that slows growth as user base expands
    if current_users <= initial_users:
        growth_factor = 0.0
    elif current_users >= target_users:
        growth_factor = 1.0
    else:
        # Logarithmic scaling: ln(current/initial) / ln(target/initial)
        log_ratio = math.log(current_users / initial_users)
        log_max = math.log(target_users / initial_users)
        growth_factor = min(1.0, max(0.0, log_ratio / log_max))
    
    # Calculate base allocation from growth factor
    base_allocation = min_allocation + (max_allocation - min_allocation) * growth_factor
    
    # Calculate per-user reward at this allocation
    gross_emission = monthly_emission * base_allocation
    net_emission = gross_emission * (1 - PLATFORM_FEE_RATE)  # After 5% platform fee
    per_user_monthly_vcoin = net_emission / current_users if current_users > 0 else 0
    per_user_monthly_usd = per_user_monthly_vcoin * token_price
    
    # Apply per-user caps for inflation protection
    allocation_capped = False
    final_allocation = base_allocation
    
    # Cap: If per-user reward exceeds max, reduce allocation
    if per_user_monthly_usd > max_per_user_monthly_usd and current_users > 0:
        # Calculate allocation that would give exactly max_per_user_monthly_usd
        # per_user_usd = (monthly_emission * allocation * (1 - fee)) / users * price
        # Solving for allocation:
        required_net_emission = (max_per_user_monthly_usd / token_price) * current_users
        required_gross_emission = required_net_emission / (1 - PLATFORM_FEE_RATE)
        capped_allocation = required_gross_emission / monthly_emission
        
        # Apply the cap but don't go below minimum
        final_allocation = max(min_allocation, min(capped_allocation, base_allocation))
        allocation_capped = True
        
        # Recalculate per-user values with capped allocation
        gross_emission = monthly_emission * final_allocation
        net_emission = gross_emission * (1 - PLATFORM_FEE_RATE)
        per_user_monthly_vcoin = net_emission / current_users
        per_user_monthly_usd = per_user_monthly_vcoin * token_price
    
    # Floor: Ensure minimum per-user reward (may require increasing allocation)
    if per_user_monthly_usd < min_per_user_monthly_usd and current_users > 0:
        required_net_emission = (min_per_user_monthly_usd / token_price) * current_users
        required_gross_emission = required_net_emission / (1 - PLATFORM_FEE_RATE)
        floor_allocation = required_gross_emission / monthly_emission
        
        # Apply floor but don't exceed maximum
        if floor_allocation <= max_allocation:
            final_allocation = max(final_allocation, floor_allocation)
            
            # Recalculate per-user values
            gross_emission = monthly_emission * final_allocation
            net_emission = gross_emission * (1 - PLATFORM_FEE_RATE)
            per_user_monthly_vcoin = net_emission / current_users
            per_user_monthly_usd = per_user_monthly_vcoin * token_price
    
    return DynamicAllocationResult(
        allocation_percent=final_allocation,
        growth_factor=growth_factor,
        per_user_monthly_vcoin=per_user_monthly_vcoin,
        per_user_monthly_usd=per_user_monthly_usd,
        allocation_capped=allocation_capped,
    )


def calculate_rewards(params: SimulationParameters, users: int) -> RewardsResult:
    """
    Calculate Rewards module emission and operational costs.
    Applies a 5% platform fee before distributing rewards to users.
    
    If dynamic allocation is enabled, the allocation percentage is calculated
    based on user growth using logarithmic scaling.
    """
    # Maximum monthly emission (fixed cap)
    max_monthly_emission = config.MONTHLY_EMISSION
    
    # Check if dynamic allocation is enabled
    use_dynamic = getattr(params, 'enable_dynamic_allocation', False)
    
    # Initialize dynamic allocation tracking variables
    is_dynamic_allocation = False
    dynamic_allocation_percent = 0.0
    growth_factor = 0.0
    per_user_monthly_vcoin = 0.0
    per_user_monthly_usd = 0.0
    allocation_capped = False
    effective_users = users
    
    if use_dynamic and users > 0:
        # Calculate dynamic allocation based on user growth
        dynamic_result = calculate_dynamic_allocation(
            current_users=users,
            token_price=params.token_price,
            initial_users=getattr(params, 'initial_users_for_allocation', 1000),
            target_users=getattr(params, 'target_users_for_max_allocation', 1_000_000),
            min_allocation=config.DYNAMIC_REWARD.MIN_ALLOCATION,
            max_allocation=config.DYNAMIC_REWARD.MAX_ALLOCATION,
            max_per_user_monthly_usd=getattr(params, 'max_per_user_monthly_usd', 50.0),
            min_per_user_monthly_usd=getattr(params, 'min_per_user_monthly_usd', 0.10),
            monthly_emission=max_monthly_emission,
        )
        
        # Use dynamic allocation
        allocation_percent_decimal = dynamic_result.allocation_percent
        is_dynamic_allocation = True
        dynamic_allocation_percent = dynamic_result.allocation_percent
        growth_factor = dynamic_result.growth_factor
        per_user_monthly_vcoin = dynamic_result.per_user_monthly_vcoin
        per_user_monthly_usd = dynamic_result.per_user_monthly_usd
        allocation_capped = dynamic_result.allocation_capped
    else:
        # Use static allocation from parameters
        allocation_percent_decimal = params.reward_allocation_percent
    
    # Gross monthly emission based on allocation percentage (before platform fee)
    gross_monthly_emission = int(max_monthly_emission * allocation_percent_decimal)
    
    # Platform fee: 5% of gross emission
    platform_fee_vcoin = gross_monthly_emission * PLATFORM_FEE_RATE
    platform_fee_usd = platform_fee_vcoin * params.token_price
    
    # Net monthly emission: 95% goes to creators/consumers
    net_monthly_emission = gross_monthly_emission - platform_fee_vcoin
    
    # Daily emission (net - what users receive)
    daily_emission = net_monthly_emission / 30
    
    # Emission value in USD (net)
    emission_usd = net_monthly_emission * params.token_price
    
    # Gross emission in USD
    gross_emission_usd = gross_monthly_emission * params.token_price
    
    # Operational costs (MVP: minimal for automated distribution)
    op_costs = 50  # Fixed low cost for smart contract automation
    
    # Daily reward pool (net)
    daily_reward_pool = daily_emission
    daily_reward_pool_usd = daily_reward_pool * params.token_price
    
    # Monthly reward pool (net)
    monthly_reward_pool = net_monthly_emission
    
    # Allocation percentage for display (convert to integer percentage)
    allocation_percent_display = int(allocation_percent_decimal * 100)
    
    # Calculate per-user values if not already done via dynamic allocation
    if not is_dynamic_allocation and users > 0:
        per_user_monthly_vcoin = net_monthly_emission / users
        per_user_monthly_usd = per_user_monthly_vcoin * params.token_price
    
    return RewardsResult(
        monthly_emission=round(net_monthly_emission, 2),
        max_monthly_emission=max_monthly_emission,
        emission_usd=round(emission_usd, 2),
        op_costs=op_costs,
        daily_emission=round(daily_emission, 2),
        daily_reward_pool=round(daily_reward_pool, 2),
        daily_reward_pool_usd=round(daily_reward_pool_usd, 2),
        monthly_reward_pool=round(monthly_reward_pool, 2),
        allocation_percent=allocation_percent_display,
        # Gross emission fields
        gross_monthly_emission=round(gross_monthly_emission, 2),
        gross_emission_usd=round(gross_emission_usd, 2),
        platform_fee_vcoin=round(platform_fee_vcoin, 2),
        platform_fee_usd=round(platform_fee_usd, 2),
        # Dynamic allocation fields
        is_dynamic_allocation=is_dynamic_allocation,
        dynamic_allocation_percent=round(dynamic_allocation_percent, 4),
        growth_factor=round(growth_factor, 4),
        per_user_monthly_vcoin=round(per_user_monthly_vcoin, 2),
        per_user_monthly_usd=round(per_user_monthly_usd, 4),
        allocation_capped=allocation_capped,
        effective_users=effective_users,
    )
