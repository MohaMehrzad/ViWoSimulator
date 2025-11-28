"""
Pydantic models for simulation results.

Updated to include MonthlyProgressionResult for Issue #16.
Nov 2025: Added LiquidityResult, StakingResult, and Growth Scenario results.
Nov 2025: Added CirculatingSupplyResult and TreasuryResult for token allocation tracking.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional, Any


# === TOKEN ALLOCATION RESULTS (Nov 2025) ===

class TokenCategoryUnlock(BaseModel):
    """Unlock information for a single token category"""
    category: str
    tokens_unlocked: int
    cumulative_unlocked: int
    total_allocation: int
    percent_unlocked: float


class CirculatingSupplyResult(BaseModel):
    """
    Circulating supply tracking result for vesting schedule.
    Tracks token unlocks from all 10 allocation categories over 60 months.
    """
    month: int
    
    # Per-category unlocks for this month
    seed_unlock: int = 0
    private_unlock: int = 0
    public_unlock: int = 0
    team_unlock: int = 0
    advisors_unlock: int = 0
    treasury_unlock: int = 0
    rewards_unlock: int = 0
    liquidity_unlock: int = 0
    foundation_unlock: int = 0
    marketing_unlock: int = 0
    
    # Totals
    total_new_unlocks: int = 0
    cumulative_circulating: int = 0
    circulating_percent: float = 0.0  # Percentage of total supply
    
    # Detailed breakdown
    category_breakdown: Dict[str, TokenCategoryUnlock] = {}


class TreasuryResult(BaseModel):
    """
    Treasury/DAO accumulation tracking.
    Treasury receives portion of platform revenue.
    """
    # Revenue contribution
    revenue_contribution_usd: float = 0.0  # USD from platform revenue
    revenue_contribution_vcoin: float = 0.0  # VCoin equivalent
    
    # Buyback contribution
    buyback_contribution_vcoin: float = 0.0  # Tokens from buybacks
    
    # Fee distribution
    fee_distribution_vcoin: float = 0.0  # From transaction fees
    
    # Totals
    total_accumulated_vcoin: float = 0.0
    total_accumulated_usd: float = 0.0
    
    # Treasury allocation status
    treasury_allocation: int = 200_000_000  # Total allocation
    treasury_released: int = 0  # Released via governance
    treasury_available: int = 200_000_000  # Available for release
    
    # Revenue share rate
    revenue_share_rate: float = 0.20  # 20% of revenue to treasury


class VestingScheduleResult(BaseModel):
    """
    Complete vesting schedule simulation result.
    60-month vesting with all 10 allocation categories.
    """
    duration_months: int = 60
    
    # Monthly circulating supply data
    monthly_supply: List[CirculatingSupplyResult] = []
    
    # Summary statistics
    tge_circulating: int = 158_833_333
    final_circulating: int = 0
    max_circulating: int = 1_000_000_000
    
    # Key milestones
    month_25_percent_circulating: int = 0  # Month when 25% circulating
    month_50_percent_circulating: int = 0  # Month when 50% circulating
    month_75_percent_circulating: int = 0  # Month when 75% circulating
    month_full_circulating: int = 60  # Month when 100% circulating
    
    # Category completion months
    seed_completion_month: int = 36
    private_completion_month: int = 18
    public_completion_month: int = 3
    team_completion_month: int = 48
    advisors_completion_month: int = 18
    foundation_completion_month: int = 27
    marketing_completion_month: int = 21
    rewards_completion_month: int = 60


# === GROWTH SCENARIO TYPES (Nov 2025) ===

class FomoEventResult(BaseModel):
    """A FOMO event that occurred during simulation"""
    month: int
    event_type: str  # 'tge_launch', 'partnership', 'viral_moment', etc.
    impact_multiplier: float
    description: str
    duration_days: int = 14


class GrowthProjectionResult(BaseModel):
    """Complete growth projection result for a scenario"""
    scenario: str  # 'conservative', 'base', 'bullish'
    market_condition: str  # 'bear', 'neutral', 'bull'
    starting_waitlist: int
    
    # Monthly metrics
    monthly_mau: List[int]
    monthly_acquired: List[int]
    monthly_churned: List[int]
    monthly_growth_rates: List[float]
    
    # Token price projections
    token_price_curve: List[float]
    token_price_start: float
    token_price_month6: float
    token_price_end: float
    
    # FOMO events
    fomo_events: List[FomoEventResult]
    
    # Summary stats
    total_users_acquired: int
    month1_users: int
    month6_mau: int
    final_mau: int
    peak_mau: int
    growth_percentage: float
    
    # Scenario config info
    waitlist_conversion_rate: float
    month1_fomo_multiplier: float
    viral_coefficient: float


class ModuleResult(BaseModel):
    """Result for a single module"""
    revenue: float
    costs: float
    profit: float
    margin: float
    breakdown: Dict[str, Any]  # Changed to Any to support nested types


class RecaptureResult(BaseModel):
    """Token recapture result"""
    total_recaptured: float
    recapture_rate: float
    burns: float
    treasury: float
    staking: float
    buybacks: float
    total_revenue_source_vcoin: float
    total_transaction_fees_usd: float
    total_royalties_usd: float


# === NEW: Liquidity Results (Nov 2025) ===

class LiquidityResult(BaseModel):
    """Liquidity pool health and metrics"""
    # Core metrics
    initial_liquidity: float
    protocol_owned_percent: float
    protocol_owned_usd: float
    community_lp_usd: float
    market_cap: float
    liquidity_ratio: float  # As percentage
    
    # Slippage data
    slippage_1k: float
    slippage_5k: float
    slippage_10k: float
    slippage_50k: float
    slippage_100k: float
    
    # Pool info
    pool_count: int
    lock_months: int
    
    # Health metrics
    health_score: float  # 0-100
    health_status: str  # Healthy, Moderate, At Risk, Critical
    health_color: str
    health_icon: str
    
    # Volume metrics
    estimated_monthly_volume: float
    volume_liquidity_ratio: float
    
    # Pressure analysis
    buy_pressure_usd: float
    sell_pressure_usd: float
    net_pressure_usd: float
    pressure_ratio: float
    
    # Recommendations
    meets_70_target: bool
    recommended_liquidity: float


# === NEW: Staking Results (Nov 2025) ===

class StakingResult(BaseModel):
    """Staking pool metrics and rewards - now generates platform revenue"""
    # === PLATFORM REVENUE & PROFIT ===
    revenue: float = 0  # Total platform revenue from staking
    costs: float = 0  # Infrastructure costs
    profit: float = 0  # Net profit
    margin: float = 0  # Profit margin %
    
    # Revenue breakdown
    protocol_fee_from_rewards_usd: float = 0  # 5% of staking rewards
    protocol_fee_from_rewards_vcoin: float = 0
    unstake_penalty_usd: float = 0  # Early unstake fees
    unstake_penalty_vcoin: float = 0
    tx_fee_revenue_usd: float = 0  # Transaction fee revenue
    tx_fee_revenue_vcoin: float = 0
    total_revenue_vcoin: float = 0
    
    # Core metrics
    staking_apy: float  # As percentage
    staker_fee_discount: float  # As percentage
    min_stake_amount: float
    lock_days: int
    
    # Participation
    stakers_count: int
    participation_rate: float  # As percentage
    avg_stake_amount: float
    
    # Totals
    total_staked: float
    total_staked_usd: float
    staking_ratio: float  # As percentage of circulating
    
    # Rewards (paid to stakers, net after protocol fee)
    total_monthly_rewards: float
    total_monthly_rewards_usd: float
    rewards_per_staker: float
    rewards_per_staker_usd: float
    effective_monthly_yield: float  # As percentage
    
    # Tier distribution
    tier_distribution: Dict[str, int]
    
    # Platform impact
    total_fee_savings_usd: float
    locked_supply_percent: float
    reduced_sell_pressure: float
    reduced_sell_pressure_usd: float
    
    # Health
    staking_status: str  # Healthy, Moderate, Low
    is_healthy: bool
    
    # Annual projections
    annual_rewards_total: float
    annual_rewards_usd: float


class RewardsResult(BaseModel):
    """Rewards module result"""
    monthly_emission: float  # Net emission after platform fee (what users receive)
    max_monthly_emission: float
    emission_usd: float  # USD value of net emission
    op_costs: float
    daily_emission: float  # Net daily emission
    daily_reward_pool: float
    daily_reward_pool_usd: float
    monthly_reward_pool: float
    allocation_percent: int
    # Gross emission fields (before platform fee)
    gross_monthly_emission: float  # Total emission before 5% fee
    gross_emission_usd: float  # USD value of gross emission
    platform_fee_vcoin: float  # 5% platform fee in VCoin
    platform_fee_usd: float  # 5% platform fee in USD
    # Dynamic allocation fields (NEW - Nov 2025)
    is_dynamic_allocation: bool = False  # Whether dynamic allocation was used
    dynamic_allocation_percent: float = 0.0  # Calculated dynamic allocation (0-1)
    growth_factor: float = 0.0  # User growth factor (0-1)
    per_user_monthly_vcoin: float = 0.0  # VCoin per user per month
    per_user_monthly_usd: float = 0.0  # USD equivalent per user per month
    allocation_capped: bool = False  # Whether per-user cap was applied
    effective_users: int = 0  # User count used for calculation


class PlatformFeesResult(BaseModel):
    """Platform fees from reward distribution"""
    reward_fee_vcoin: float  # 5% of monthly emission in VCoin
    reward_fee_usd: float  # USD value of the fee
    fee_rate: float  # The fee rate (0.05)


class CustomerAcquisitionMetrics(BaseModel):
    """Customer acquisition breakdown"""
    total_creator_cost: float
    consumer_acquisition_budget: float
    north_america_budget: float
    global_low_income_budget: float
    north_america_users: int
    global_low_income_users: int
    total_users: int
    blended_cac: float


class TotalsResult(BaseModel):
    """Total results across all modules"""
    revenue: float
    costs: float
    profit: float
    margin: float


class SimulationResult(BaseModel):
    """Complete simulation result"""
    identity: ModuleResult
    content: ModuleResult
    community: ModuleResult
    advertising: ModuleResult
    messaging: ModuleResult
    exchange: ModuleResult  # Exchange/Wallet module for crypto trading fees
    rewards: RewardsResult
    recapture: RecaptureResult
    customer_acquisition: CustomerAcquisitionMetrics
    totals: TotalsResult
    platform_fees: PlatformFeesResult
    # NEW: Liquidity and Staking (Nov 2025)
    liquidity: Optional[LiquidityResult] = None
    staking: Optional[StakingResult] = None


class PercentileResults(BaseModel):
    """Percentile breakdown for Monte Carlo"""
    p5: SimulationResult
    p50: SimulationResult
    p95: SimulationResult


class StatisticsResult(BaseModel):
    """Statistical summary"""
    mean: Dict[str, float]
    std: Dict[str, float]


class MonteCarloResult(BaseModel):
    """Monte Carlo simulation result"""
    iterations: int
    percentiles: PercentileResults
    distributions: Dict[str, List[float]]
    statistics: StatisticsResult


class AgentResult(BaseModel):
    """Individual agent result"""
    id: str
    type: str  # 'creator', 'consumer', 'whale', 'bot'
    rewards_earned: float
    tokens_spent: float
    tokens_staked: float
    activity: float
    flagged: bool


class MarketDynamics(BaseModel):
    """Market dynamics from agent simulation"""
    buy_pressure: float
    sell_pressure: float
    price_impact: float


class SystemMetrics(BaseModel):
    """System-level metrics from agent simulation"""
    total_rewards_distributed: float  # Net rewards to users (after platform fee)
    total_recaptured: float
    net_circulation: float
    platform_fee_collected: float  # 5% platform fee collected
    platform_fee_usd: float  # USD value of platform fee


class AgentBasedResult(BaseModel):
    """Agent-based simulation result"""
    total_agents: int
    agent_breakdown: Dict[str, int]
    market_dynamics: MarketDynamics
    system_metrics: SystemMetrics
    top_agents: List[AgentResult]
    flagged_bots: int


# === NEW: Monthly Progression Results (Issue #16) ===

class MonthlyMetricsResult(BaseModel):
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
    
    # Cohort breakdown
    cohort_breakdown: Dict[int, int] = {}
    
    # Growth scenario fields (NEW - Nov 2025)
    fomo_event: Optional[FomoEventResult] = None
    token_price: float = 0.03  # Current token price
    scenario_multiplier: float = 1.0  # Growth scenario impact
    growth_rate: float = 0.0  # Monthly growth rate
    
    # Dynamic allocation fields (NEW - Nov 2025)
    dynamic_allocation_percent: float = 0.0  # Current allocation percentage
    dynamic_growth_factor: float = 0.0  # User growth factor (0-1)
    per_user_monthly_vcoin: float = 0.0  # VCoin per user per month
    per_user_monthly_usd: float = 0.0  # USD equivalent per user per month
    allocation_capped: bool = False  # Whether per-user cap was applied
    
    # Token allocation fields (NEW - Nov 2025)
    circulating_supply: int = 0  # Total circulating supply at this month
    circulating_percent: float = 0.0  # Percentage of total supply
    new_unlocks: int = 0  # New tokens unlocked this month
    
    # Treasury fields (NEW - Nov 2025)
    treasury_revenue_usd: float = 0.0  # Revenue going to treasury
    treasury_accumulated_usd: float = 0.0  # Cumulative treasury balance


class MonthlyProgressionResult(BaseModel):
    """Complete result of monthly progression simulation"""
    duration_months: int
    monthly_data: List[MonthlyMetricsResult]
    
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
    scenario_used: Optional[str] = None  # 'conservative', 'base', 'bullish', or None
    market_condition_used: Optional[str] = None  # 'bear', 'neutral', 'bull', or None
    fomo_events_triggered: List[FomoEventResult] = []
    token_price_final: float = 0.03
    
    # Token allocation / vesting (NEW - Nov 2025)
    vesting_schedule: Optional[VestingScheduleResult] = None
    final_circulating_supply: int = 0
    final_circulating_percent: float = 0.0
    
    # Treasury tracking (NEW - Nov 2025)
    treasury_result: Optional[TreasuryResult] = None
    total_treasury_accumulated_usd: float = 0.0
    total_treasury_accumulated_vcoin: float = 0.0


class WebSocketProgress(BaseModel):
    """Progress update for WebSocket streaming"""
    type: str = "progress"
    current: int
    total: int
    percentage: float
    partial_result: Optional[Any] = None


class WebSocketComplete(BaseModel):
    """Completion message for WebSocket streaming"""
    type: str = "complete"
    result: Any


class WebSocketError(BaseModel):
    """Error message for WebSocket streaming"""
    type: str = "error"
    message: str
    details: Optional[str] = None
