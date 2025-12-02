"""
Rewards Module - Platform's PRIMARY Revenue Source (5% Fee)

=== CRITICAL: 5% PLATFORM FEE MODEL (November 2025) ===

This is the MAIN revenue stream for the platform. The fee structure is:

1. DAILY CALCULATION (before any distribution):
   - Calculate gross daily emission from reward pool
   - Platform takes 5% FIRST (before any user receives anything)
   - Remaining 95% distributed to users via algorithm

2. FEE FLOW:
   Reward Pool → Daily Emission → [5% Platform] → [95% Users]
   
3. Example at $0.03 token, 8% allocation:
   - Daily Gross: 15,556 VCoin ($466.67)
   - Platform Fee: 778 VCoin ($23.33/day = $700/month)
   - User Distribution: 14,778 VCoin ($443.34/day)

4. This fee scales automatically:
   - More users = higher allocation = more fee revenue
   - 1,000 users → ~$437/month platform fee
   - 100,000 users → ~$5,425/month platform fee
   - 1,000,000 users → ~$7,875/month platform fee

Uses logarithmic scaling for dynamic allocation to ensure rewards 
grow proportionally with user base while preventing token inflation.
"""

import math
from typing import NamedTuple
from app.config import config
from app.models import SimulationParameters, RewardsResult


# ============================================================================
# PLATFORM FEE CONFIGURATION
# ============================================================================

# MED-07 Fix: Import centralized PLATFORM_FEE_RATE from config
# Fixed platform fee rate - 5% of ALL reward emissions
# This is taken FIRST, BEFORE any distribution to users
# This is the PRIMARY revenue source for the platform
PLATFORM_FEE_RATE = config.PLATFORM_FEE_RATE  # 5% - centralized in config.py

# Days per month for calculations
DAYS_PER_MONTH = 30


# ============================================================================
# DYNAMIC ALLOCATION
# ============================================================================

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
    
    NOTE: The 5% platform fee is already factored into per-user calculations.
    """
    if monthly_emission is None:
        monthly_emission = config.MONTHLY_EMISSION
    
    # Ensure minimum users to prevent division issues
    current_users = max(1, current_users)
    initial_users = max(1, initial_users)
    target_users = max(initial_users + 1, target_users)
    
    # Calculate growth factor using logarithmic scaling
    if current_users <= initial_users:
        growth_factor = 0.0
    elif current_users >= target_users:
        growth_factor = 1.0
    else:
        log_ratio = math.log(current_users / initial_users)
        log_max = math.log(target_users / initial_users)
        growth_factor = min(1.0, max(0.0, log_ratio / log_max))
    
    # Calculate base allocation from growth factor
    base_allocation = min_allocation + (max_allocation - min_allocation) * growth_factor
    
    # Calculate per-user reward at this allocation
    # NOTE: Platform fee is taken FIRST, then remainder distributed
    gross_emission = monthly_emission * base_allocation
    net_emission = gross_emission * (1 - PLATFORM_FEE_RATE)  # After 5% platform fee
    per_user_monthly_vcoin = net_emission / current_users if current_users > 0 else 0
    per_user_monthly_usd = per_user_monthly_vcoin * token_price
    
    # Apply per-user caps for inflation protection
    allocation_capped = False
    final_allocation = base_allocation
    
    # Cap: If per-user reward exceeds max, reduce allocation
    if per_user_monthly_usd > max_per_user_monthly_usd and current_users > 0:
        required_net_emission = (max_per_user_monthly_usd / token_price) * current_users
        required_gross_emission = required_net_emission / (1 - PLATFORM_FEE_RATE)
        capped_allocation = required_gross_emission / monthly_emission
        
        final_allocation = max(min_allocation, min(capped_allocation, base_allocation))
        allocation_capped = True
        
        # Recalculate per-user values with capped allocation
        gross_emission = monthly_emission * final_allocation
        net_emission = gross_emission * (1 - PLATFORM_FEE_RATE)
        per_user_monthly_vcoin = net_emission / current_users
        per_user_monthly_usd = per_user_monthly_vcoin * token_price
    
    # Floor: Ensure minimum per-user reward
    if per_user_monthly_usd < min_per_user_monthly_usd and current_users > 0:
        required_net_emission = (min_per_user_monthly_usd / token_price) * current_users
        required_gross_emission = required_net_emission / (1 - PLATFORM_FEE_RATE)
        floor_allocation = required_gross_emission / monthly_emission
        
        if floor_allocation <= max_allocation:
            final_allocation = max(final_allocation, floor_allocation)
            
            gross_emission = monthly_emission * final_allocation
            net_emission = gross_emission * (1 - PLATFORM_FEE_RATE)
            per_user_monthly_vcoin = net_emission / current_users
            per_user_monthly_usd = per_user_monthly_vcoin * token_price
        else:
            # MED-06 Fix: Log warning when floor cannot be applied
            import logging
            logging.warning(
                f"MED-06: Floor allocation ({floor_allocation:.2%}) exceeds max_allocation "
                f"({max_allocation:.2%}). Minimum per-user reward of ${min_per_user_monthly_usd:.2f} "
                f"cannot be guaranteed for {current_users} users. Consider reducing min_per_user_monthly_usd "
                f"or increasing max_allocation."
            )
    
    return DynamicAllocationResult(
        allocation_percent=final_allocation,
        growth_factor=growth_factor,
        per_user_monthly_vcoin=per_user_monthly_vcoin,
        per_user_monthly_usd=per_user_monthly_usd,
        allocation_capped=allocation_capped,
    )


# ============================================================================
# DAILY FEE CALCULATION (Called before each distribution)
# ============================================================================

def calculate_daily_platform_fee(
    daily_gross_emission: float,
    token_price: float,
) -> dict:
    """
    Calculate the platform's 5% fee for a SINGLE DAY.
    
    This function represents what happens DAILY before reward distribution:
    1. Smart contract calculates daily emission
    2. 5% is IMMEDIATELY transferred to platform treasury
    3. Remaining 95% enters the distribution algorithm
    
    Args:
        daily_gross_emission: Total VCoin to be emitted today
        token_price: Current VCoin price in USD
    
    Returns:
        dict with fee breakdown for the day
    
    Example (at 8% allocation, $0.03 token):
        Input: daily_gross_emission = 15,556 VCoin
        Output:
            platform_fee_vcoin: 778 VCoin
            platform_fee_usd: $23.33
            user_distribution_vcoin: 14,778 VCoin
            user_distribution_usd: $443.34
    """
    # Platform takes 5% FIRST
    platform_fee_vcoin = daily_gross_emission * PLATFORM_FEE_RATE
    platform_fee_usd = platform_fee_vcoin * token_price
    
    # Users receive the remaining 95%
    user_distribution_vcoin = daily_gross_emission - platform_fee_vcoin
    user_distribution_usd = user_distribution_vcoin * token_price
    
    return {
        'daily_gross_emission': round(daily_gross_emission, 2),
        'platform_fee_rate': PLATFORM_FEE_RATE,
        'platform_fee_vcoin': round(platform_fee_vcoin, 2),
        'platform_fee_usd': round(platform_fee_usd, 4),
        'user_distribution_vcoin': round(user_distribution_vcoin, 2),
        'user_distribution_usd': round(user_distribution_usd, 4),
    }


# ============================================================================
# MAIN REWARDS CALCULATION
# ============================================================================

def calculate_rewards(params: SimulationParameters, users: int) -> RewardsResult:
    """
    Calculate Rewards module emission and platform fee.
    
    === CRITICAL: 5% PLATFORM FEE ===
    
    The platform fee is calculated and taken BEFORE any distribution:
    
    1. Calculate gross emission (daily or monthly)
    2. Platform takes 5% IMMEDIATELY → Platform Treasury
    3. Remaining 95% → Distribution Algorithm → Users
    
    This ensures the platform ALWAYS gets its 5% before any user rewards.
    
    Daily Flow (what happens each day):
    ┌─────────────────────────────────────────────────────────────┐
    │ Daily Gross Emission (from monthly pool)                     │
    │ e.g., 15,556 VCoin at 8% allocation                         │
    └─────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────────────────┐
    │ STEP 1: Platform Fee Extraction (5%)                        │
    │ 15,556 × 5% = 778 VCoin → Platform Treasury                 │
    └─────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────────────────┐
    │ STEP 2: User Distribution (95%)                             │
    │ 14,778 VCoin → Distribution Algorithm → Creators/Consumers  │
    └─────────────────────────────────────────────────────────────┘
    """
    # Check if module is enabled
    if not getattr(params, 'enable_rewards', True):
        return RewardsResult(
            monthly_emission=0,
            max_monthly_emission=0,
            emission_usd=0,
            op_costs=0,
            daily_emission=0,
            daily_reward_pool=0,
            daily_reward_pool_usd=0,
            monthly_reward_pool=0,
            allocation_percent=0,
            gross_monthly_emission=0,
            gross_emission_usd=0,
            platform_fee_vcoin=0,
            platform_fee_usd=0,
            is_dynamic_allocation=False,
            dynamic_allocation_percent=0,
            growth_factor=0,
            per_user_monthly_vcoin=0,
            per_user_monthly_usd=0,
            allocation_capped=False,
            effective_users=0,
        )
    
    # Maximum monthly emission (fixed cap from tokenomics)
    max_monthly_emission = config.MONTHLY_EMISSION
    
    # Check if dynamic allocation is enabled
    use_dynamic = getattr(params, 'enable_dynamic_allocation', False)
    
    # Initialize tracking variables
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
    
    # === GROSS EMISSION (before platform fee) ===
    gross_monthly_emission = int(max_monthly_emission * allocation_percent_decimal)
    gross_daily_emission = gross_monthly_emission / DAYS_PER_MONTH
    
    # === PLATFORM FEE: 5% taken FIRST, DAILY ===
    # This is calculated and extracted before ANY distribution
    daily_fee = calculate_daily_platform_fee(gross_daily_emission, params.token_price)
    
    # Monthly platform fee (sum of all daily fees)
    platform_fee_vcoin = gross_monthly_emission * PLATFORM_FEE_RATE
    platform_fee_usd = platform_fee_vcoin * params.token_price
    
    # === NET EMISSION: 95% to users ===
    net_monthly_emission = gross_monthly_emission - platform_fee_vcoin
    net_daily_emission = net_monthly_emission / DAYS_PER_MONTH
    
    # USD values
    emission_usd = net_monthly_emission * params.token_price
    gross_emission_usd = gross_monthly_emission * params.token_price
    
    # Operational costs (minimal for automated distribution on Solana)
    # ~$0.00025 per transaction, ~1000 distributions = $0.25/day = ~$8/month
    # Add buffer for monitoring, maintenance
    op_costs = 50  # $50/month for reward distribution operations
    
    # Daily reward pool (net - what users receive)
    daily_reward_pool = net_daily_emission
    daily_reward_pool_usd = daily_reward_pool * params.token_price
    
    # Monthly reward pool (net)
    monthly_reward_pool = net_monthly_emission
    
    # Allocation percentage for display
    allocation_percent_display = int(allocation_percent_decimal * 100)
    
    # Calculate per-user values if not already done via dynamic allocation
    if not is_dynamic_allocation and users > 0:
        per_user_monthly_vcoin = net_monthly_emission / users
        per_user_monthly_usd = per_user_monthly_vcoin * params.token_price
    
    # Per-user daily values
    per_user_daily_vcoin = per_user_monthly_vcoin / DAYS_PER_MONTH if users > 0 else 0
    per_user_daily_usd = per_user_daily_vcoin * params.token_price
    
    return RewardsResult(
        # Net emission (what users receive after 5% fee)
        monthly_emission=round(net_monthly_emission, 2),
        max_monthly_emission=max_monthly_emission,
        emission_usd=round(emission_usd, 2),
        op_costs=op_costs,
        
        # Daily values (net)
        daily_emission=round(net_daily_emission, 2),
        daily_reward_pool=round(daily_reward_pool, 2),
        daily_reward_pool_usd=round(daily_reward_pool_usd, 2),
        
        # Monthly pool (net)
        monthly_reward_pool=round(monthly_reward_pool, 2),
        allocation_percent=allocation_percent_display,
        
        # Gross emission (before 5% fee)
        gross_monthly_emission=round(gross_monthly_emission, 2),
        gross_emission_usd=round(gross_emission_usd, 2),
        
        # === PLATFORM FEE (5%) - PRIMARY REVENUE ===
        # This is taken DAILY, BEFORE distribution
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
