"""
Pydantic models for simulation results.

Updated to include MonthlyProgressionResult for Issue #16.
Nov 2025: Added LiquidityResult, StakingResult, and Growth Scenario results.
Nov 2025: Added CirculatingSupplyResult and TreasuryResult for token allocation tracking.
"""

from pydantic import BaseModel, field_validator
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
    # CRIT-FE-001 Fix: Updated to match config.py (removed rewards from TGE)
    tge_circulating: int = 153_000_000
    final_circulating: int = 0
    max_circulating: int = 1_000_000_000
    
    # Key milestones
    month_25_percent_circulating: int = 0  # Month when 25% circulating
    month_50_percent_circulating: int = 0  # Month when 50% circulating
    month_75_percent_circulating: int = 0  # Month when 75% circulating
    month_full_circulating: int = 60  # Month when 100% circulating
    
    # Category completion months
    # CRIT-02/03 Fix: Private and Advisors vest M7-M24 (cliff 6 + vesting 18 = 24)
    seed_completion_month: int = 36
    private_completion_month: int = 24  # Fixed: was 18, but vesting ends at M24
    public_completion_month: int = 3
    team_completion_month: int = 48
    advisors_completion_month: int = 24  # Fixed: was 18, but vesting ends at M24
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
    
    # LOW-03 Fix: Validate event_type against FomoEventType enum values
    @field_validator('event_type')
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        """Validate that event_type matches a valid FomoEventType value"""
        from app.core.growth_scenarios import FomoEventType
        valid_types = [e.value for e in FomoEventType]
        if v not in valid_types:
            raise ValueError(
                f"Invalid event_type '{v}'. Must be one of: {', '.join(valid_types)}"
            )
        return v


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
    """
    Token recapture result.
    
    Updated Nov 2025: Buybacks now use USD REVENUE to purchase tokens from market.
    - Burns: % of collected VCoin fees destroyed (deflationary)
    - Buybacks: % of USD revenue used to buy VCoin from market (creates buy pressure)
    
    CRIT-002 Fix: Added effective_burn_rate to show actual burn as % of emission,
    not just the configured burn_rate which is applied to token velocity.
    """
    total_recaptured: float
    recapture_rate: float
    burns: float  # VCoin burned from collected fees
    treasury: float  # VCoin accumulated in treasury
    staking: float  # VCoin locked in staking
    buybacks: float  # VCoin acquired via buybacks (bought from market)
    buyback_usd_spent: float = 0  # USD spent on buybacks from protocol revenue
    total_revenue_source_vcoin: float
    total_transaction_fees_usd: float
    total_royalties_usd: float
    # CRIT-002 Fix: Effective burn rate shows actual burns as % of monthly emission
    # This differs from params.burn_rate which is applied to token velocity, not emission
    effective_burn_rate: float = 0  # Actual burn % of monthly emission (burns / emission)
    configured_burn_rate: float = 0  # User-configured burn rate for reference


# === GOVERNANCE RESULTS (Nov 2025) ===

class GovernanceResult(BaseModel):
    """veVCoin governance metrics"""
    revenue: float = 0
    costs: float = 0
    profit: float = 0
    
    # veVCoin metrics
    total_vevcoin_supply: float = 0
    total_vevcoin_supply_usd: float = 0
    vevcoin_of_circulating_percent: float = 0
    avg_vevcoin_per_staker: float = 0
    avg_lock_weeks: int = 0
    avg_boost_multiplier: float = 1.0
    
    # Direct Participation
    active_voters: int = 0
    active_voting_power: float = 0
    voting_participation_rate: float = 0
    
    # Delegation (NEW - Nov 2025)
    delegators: int = 0
    delegated_voting_power: float = 0
    delegation_rate: float = 0
    
    # Effective Participation (voters + delegators)
    total_participants: int = 0
    effective_participation_rate: float = 0
    
    # Tier distribution
    tier_distribution: Dict[str, int] = {}
    eligible_proposers: int = 0
    
    # Proposal activity
    expected_monthly_proposals: int = 0
    
    # Health metrics
    voting_power_concentration: float = 0
    decentralization_score: float = 0
    governance_health_score: float = 0


# === FUTURE MODULE RESULTS (Nov 2025) ===

class VChainResult(BaseModel):
    """VChain cross-chain network result"""
    enabled: bool = False
    launched: bool = False
    months_active: int = 0
    growth_factor: float = 0
    
    revenue: float = 0
    tx_fee_revenue: float = 0
    bridge_fee_revenue: float = 0
    gas_markup_revenue: float = 0
    enterprise_api_revenue: float = 0
    
    monthly_tx_volume: float = 0
    monthly_bridge_volume: float = 0
    estimated_transactions: int = 0
    active_enterprise_clients: int = 0
    
    validators_active: int = 0
    total_validator_stake: float = 0
    
    costs: float = 0
    profit: float = 0
    margin: float = 0
    
    launch_month: int = 24
    months_until_launch: int = 0


class MarketplaceResult(BaseModel):
    """Marketplace physical/digital goods result"""
    enabled: bool = False
    launched: bool = False
    months_active: int = 0
    growth_factor: float = 0
    
    revenue: float = 0
    commission_revenue: float = 0
    physical_commission: float = 0
    digital_commission: float = 0
    nft_commission: float = 0
    services_commission: float = 0
    payment_processing_revenue: float = 0
    escrow_revenue: float = 0
    featured_revenue_usd: float = 0
    store_subscription_revenue_usd: float = 0
    ad_revenue: float = 0
    
    monthly_gmv: float = 0
    active_sellers: int = 0
    
    costs: float = 0
    profit: float = 0
    margin: float = 0
    
    launch_month: int = 18
    months_until_launch: int = 0


class BusinessHubResult(BaseModel):
    """Business Hub freelancer/startup result"""
    enabled: bool = False
    launched: bool = False
    months_active: int = 0
    growth_factor: float = 0
    
    revenue: float = 0
    freelancer_revenue: float = 0
    startup_revenue: float = 0
    funding_revenue: float = 0
    pm_saas_revenue: float = 0
    academy_revenue: float = 0
    
    active_freelancers: int = 0
    monthly_freelance_volume: float = 0
    monthly_funding_volume: float = 0
    pm_total_users: int = 0
    
    total_vcoin_revenue: float = 0
    
    costs: float = 0
    profit: float = 0
    margin: float = 0
    
    launch_month: int = 21
    months_until_launch: int = 0


class CrossPlatformResult(BaseModel):
    """Cross-platform content sharing result"""
    enabled: bool = False
    launched: bool = False
    months_active: int = 0
    growth_factor: float = 0
    
    revenue: float = 0
    subscription_revenue: float = 0
    rental_revenue: float = 0
    insurance_revenue: float = 0
    verification_revenue: float = 0
    analytics_revenue: float = 0
    license_revenue: float = 0
    
    total_subscribers: int = 0
    monthly_rental_volume: float = 0
    active_renters: int = 0
    active_owners: int = 0
    
    total_vcoin_revenue: float = 0
    
    costs: float = 0
    profit: float = 0
    margin: float = 0
    
    launch_month: int = 15
    months_until_launch: int = 0


# === TOKEN METRICS RESULTS (Nov 2025) ===

class TokenVelocityResult(BaseModel):
    """Token velocity metrics"""
    velocity: float = 0
    annualized_velocity: float = 0
    interpretation: str = ""
    health_score: float = 0
    days_to_turnover: float = 0
    transaction_volume: float = 0
    circulating_supply: float = 0


class RealYieldResult(BaseModel):
    """Real yield (revenue-based) metrics"""
    monthly_real_yield: float = 0
    annual_real_yield: float = 0
    interpretation: str = ""
    is_sustainable: bool = False
    yield_per_1000_usd: float = 0
    protocol_revenue: float = 0
    staked_value_usd: float = 0


class ValueAccrualResult(BaseModel):
    """Value accrual score"""
    total_score: float = 0
    grade: str = "F"
    interpretation: str = ""
    breakdown: Dict[str, float] = {}
    weights: Dict[str, float] = {}


class GiniResult(BaseModel):
    """Token distribution fairness metrics (Gini coefficient)"""
    gini: float = 0.7  # 0=equal, 1=concentrated
    interpretation: str = "Concentrated"
    decentralization_score: float = 30.0  # 100 - gini*100
    holder_count: int = 0
    top_1_percent_concentration: float = 0.0
    top_10_percent_concentration: float = 0.0


class RunwayResult(BaseModel):
    """Treasury runway analysis"""
    runway_months: float = 0
    runway_years: float = 0
    is_sustainable: bool = False
    interpretation: str = ""
    net_burn_monthly: float = 0
    monthly_revenue: float = 0
    monthly_expenses: float = 0
    treasury_balance: float = 0
    runway_health: float = 0
    months_to_sustainability: float = 0


class InflationResult(BaseModel):
    """
    Token inflation metrics - tracks supply dynamics over time.
    
    Key metrics:
    - Gross inflation: Total new tokens entering circulation (emission)
    - Net inflation: Emission - Burns - Buybacks
    - Inflation rate: Net inflation as % of circulating supply
    """
    # Emission (new tokens entering)
    monthly_emission: float = 0  # VCoin minted this month
    monthly_emission_usd: float = 0
    annual_emission: float = 0
    emission_rate: float = 0  # As % of circulating
    
    # Deflationary mechanisms
    monthly_burns: float = 0  # VCoin burned
    monthly_burns_usd: float = 0
    monthly_buybacks: float = 0  # VCoin bought back from market
    monthly_buybacks_usd: float = 0
    total_deflationary: float = 0  # Burns + Buybacks
    
    # Net inflation
    net_monthly_inflation: float = 0  # Emission - Burns - Buybacks
    net_monthly_inflation_usd: float = 0
    net_inflation_rate: float = 0  # As % of circulating supply
    annual_net_inflation_rate: float = 0
    
    # Supply metrics
    circulating_supply: float = 0
    total_supply: float = 1_000_000_000
    
    # Health indicators
    is_deflationary: bool = False  # True if net inflation < 0
    deflation_strength: str = ""  # "Strong", "Moderate", "Weak", or inflation levels
    supply_health_score: float = 50  # 0-100, higher = healthier
    
    # Projections
    months_to_max_supply: int = 60  # Months until emission stops
    projected_year1_inflation: float = 0
    projected_year5_supply: float = 0
    runway_health: float = 0
    months_to_sustainability: float = 0


class DumpScenarioResult(BaseModel):
    """Result of a whale dump scenario"""
    scenario_name: str = ""
    sellers_count: int = 0
    sell_amount_vcoin: float = 0
    sell_amount_usd: float = 0
    sell_percentage: float = 0
    price_impact_percent: float = 0
    new_price: float = 0
    liquidity_absorbed_percent: float = 0
    market_cap_loss: float = 0
    recovery_days_estimate: int = 0
    severity: str = "low"  # low, medium, high, critical


class TopHoldersGroup(BaseModel):
    """Metrics for a group of top holders"""
    holders_count: int = 0
    amount_vcoin: float = 0
    amount_usd: float = 0
    percentage: float = 0
    avg_balance: float = 0


class WhaleInfo(BaseModel):
    """Information about a single whale"""
    rank: int = 0
    balance: float = 0
    percentage: float = 0


class WhaleAnalysisResult(BaseModel):
    """
    Comprehensive whale concentration risk analysis.
    2025 Industry Compliance metric.
    """
    # Basic counts
    holder_count: int = 0
    total_supply: float = 0
    total_held: float = 0
    token_price: float = 0
    
    # Top holder groups
    top_10: TopHoldersGroup = TopHoldersGroup()
    top_50: TopHoldersGroup = TopHoldersGroup()
    top_100: TopHoldersGroup = TopHoldersGroup()
    
    # Percentile groups
    top_1_percent: TopHoldersGroup = TopHoldersGroup()
    top_5_percent: TopHoldersGroup = TopHoldersGroup()
    top_10_percent: TopHoldersGroup = TopHoldersGroup()
    
    # Whale breakdown
    whale_count: int = 0
    large_holder_count: int = 0
    medium_holder_count: int = 0
    small_holder_count: int = 0
    
    whales: List[WhaleInfo] = []
    
    # Risk metrics
    concentration_risk_score: float = 0  # 0-100
    risk_level: str = "Unknown"
    risk_color: str = "gray"
    
    # Dump scenarios
    dump_scenarios: List[DumpScenarioResult] = []
    
    # Recommendations
    recommendations: List[str] = []


class AttackScenarioDetail(BaseModel):
    """Details of a single attack scenario"""
    name: str = ""
    category: str = ""
    description: str = ""
    attack_vector: str = ""
    probability: float = 0
    severity: str = "low"
    potential_loss_usd: float = 0
    potential_loss_percent: float = 0
    mitigation_effectiveness: float = 0
    recovery_time_days: int = 0
    required_capital: float = 0
    complexity: str = "medium"


class SecurityFeatures(BaseModel):
    """Protocol security features"""
    has_timelock: bool = False
    timelock_delay_hours: int = 0
    has_multisig: bool = False
    multisig_threshold: int = 0
    oracle_type: str = "chainlink"


class AttackAnalysisResult(BaseModel):
    """
    Economic attack vulnerability analysis.
    2025 Industry Compliance metric.
    """
    vulnerability_score: float = 50  # 0-100
    risk_level: str = "Moderate"
    risk_color: str = "amber"
    total_potential_loss_usd: float = 0
    avg_severity_score: float = 50
    
    # Market metrics
    market_cap: float = 0
    liquidity_ratio: float = 0
    volume_to_liquidity: float = 0
    
    # Security features
    security_features: SecurityFeatures = SecurityFeatures()
    
    # Attack scenarios
    scenarios: List[AttackScenarioDetail] = []
    
    # Recommendations
    recommendations: List[str] = []


class ILScenario(BaseModel):
    """Impermanent loss scenario"""
    scenario: str = ""
    price_change_percent: float = 0
    final_price: float = 0
    impermanent_loss_percent: float = 0
    interpretation: str = ""


class FarmingAPY(BaseModel):
    """Farming APY breakdown"""
    reward_apr: float = 0
    fee_apr: float = 0
    total_apr: float = 0
    reward_apy: float = 0
    fee_apy: float = 0
    total_apy: float = 0
    daily_reward_rate: float = 0
    daily_total_rate: float = 0
    pool_tvl_usd: float = 0
    daily_reward_vcoin: float = 0
    daily_reward_usd: float = 0
    is_sustainable: bool = True
    example_1000_final: float = 1000
    example_1000_profit: float = 0


class FarmingRiskMetrics(BaseModel):
    """Farming risk assessment"""
    risk_score: float = 30
    risk_level: str = "Moderate"
    il_breakeven_multiplier: float = 1.5
    il_breakeven_price_up: float = 0
    il_breakeven_price_down: float = 0


class FarmingSimulationMonth(BaseModel):
    """Single month in farming simulation"""
    month: int = 0
    vcoin_price: float = 0
    price_change_percent: float = 0
    hold_value_usd: float = 0
    lp_position_value_usd: float = 0
    cumulative_rewards_usd: float = 0
    cumulative_fees_usd: float = 0
    total_value_usd: float = 0
    impermanent_loss_percent: float = 0
    impermanent_loss_usd: float = 0
    net_vs_holding_usd: float = 0
    total_pnl_usd: float = 0
    total_pnl_percent: float = 0


class FarmingSimulation(BaseModel):
    """Complete farming simulation for one scenario"""
    initial_investment_usd: float = 1000
    initial_vcoin_price: float = 0.1
    lp_share_percent: float = 0
    monthly_projections: List[FarmingSimulationMonth] = []
    final_result: Optional[FarmingSimulationMonth] = None


class LiquidityFarmingResult(BaseModel):
    """
    Liquidity farming analysis results.
    2025 Industry Compliance metric.
    """
    apy: FarmingAPY = FarmingAPY()
    il_scenarios: List[ILScenario] = []
    simulations: Dict[str, FarmingSimulation] = {}  # bull_case, bear_case, stable_case
    risk_metrics: FarmingRiskMetrics = FarmingRiskMetrics()
    recommendations: List[str] = []


class StrategyMetrics(BaseModel):
    """Metrics for a single strategy"""
    return_percent: float = 0
    risk_percent: float = 0
    risk_adjusted_return: float = 0


class StakingEquilibrium(BaseModel):
    """Staking vs selling equilibrium analysis"""
    stake_probability: float = 0
    sell_probability: float = 0
    hold_probability: float = 0
    dominant_strategy: str = "hold"
    is_stable: bool = True
    deviation_incentive: float = 0


class StakingAnalysis(BaseModel):
    """Analysis of staking decision"""
    best_strategy: str = "stake"
    interpretation: str = ""
    recommendation: str = ""
    staking_breakeven_price_drop: float = 0


class GovernanceParticipation(BaseModel):
    """Governance participation metrics"""
    rational_participants: int = 0
    total_holders: int = 0
    participation_rate: float = 0
    participating_power: float = 0
    quorum_achievable: bool = True


class VoterApathy(BaseModel):
    """Voter apathy analysis"""
    apathetic_ratio: float = 0
    risk_level: str = "Low"
    interpretation: str = ""


class CoordinationGameAnalysis(BaseModel):
    """Coordination game analysis"""
    game_type: str = ""
    description: str = ""
    equilibrium: str = ""
    cooperation_probability: float = 50


class GameTheoryResult(BaseModel):
    """
    Game theory analysis results.
    2025 Industry Compliance metric.
    """
    # Staking equilibrium
    strategies: Dict[str, StrategyMetrics] = {}
    equilibrium: StakingEquilibrium = StakingEquilibrium()
    analysis: StakingAnalysis = StakingAnalysis()
    
    # Governance game
    governance_participation: GovernanceParticipation = GovernanceParticipation()
    voter_apathy: VoterApathy = VoterApathy()
    min_coalition_size: int = 0
    min_coalition_power: float = 0
    
    # Coordination game
    coordination: CoordinationGameAnalysis = CoordinationGameAnalysis()
    cooperation_sustainable: bool = True
    
    # Overall
    health_score: float = 50
    primary_risk: str = "None"
    recommendations: List[str] = []


class TokenMetricsResult(BaseModel):
    """Complete token metrics"""
    velocity: TokenVelocityResult = TokenVelocityResult()
    real_yield: RealYieldResult = RealYieldResult()
    value_accrual: ValueAccrualResult = ValueAccrualResult()
    overall_health: float = 0
    # New metrics for 2025 compliance
    gini: Optional[GiniResult] = None
    runway: Optional[RunwayResult] = None
    inflation: Optional['InflationResult'] = None
    whale_analysis: Optional[WhaleAnalysisResult] = None
    attack_analysis: Optional[AttackAnalysisResult] = None
    liquidity_farming: Optional[LiquidityFarmingResult] = None
    game_theory: Optional[GameTheoryResult] = None


# === SENSITIVITY ANALYSIS RESULTS (Nov 2025) ===

class StressTestScenarioResult(BaseModel):
    """Result of a single stress test scenario"""
    scenario: str
    scenario_name: str
    description: str
    immediate_impact: Dict[str, float]
    max_drawdown_percent: Dict[str, float]
    recovery_months: int
    permanent_impact_percent: float
    total_revenue_loss: float


class SensitivityResult(BaseModel):
    """Complete sensitivity analysis result"""
    stress_tests: Dict[str, StressTestScenarioResult] = {}
    worst_scenario: str = ""
    least_severe_scenario: str = ""
    monte_carlo_p5: float = 0
    monte_carlo_p50: float = 0
    monte_carlo_p95: float = 0


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
    
    # Early unstake impact tracking
    early_unstake_rate: float = 0  # As percentage
    early_unstake_penalty_rate: float = 0  # As percentage
    early_unstakers_count: int = 0
    expected_early_unstake_reward_loss: float = 0
    
    # === SOLANA-SPECIFIC DATA ===
    network: str = 'solana'
    program_type: str = 'spl_token_staking'
    framework: str = 'anchor'
    
    # On-chain costs
    stake_account_rent_sol: float = 0
    stake_account_rent_usd: float = 0
    total_stake_accounts_cost_usd: float = 0
    staking_tx_cost_usd: float = 0
    monthly_tx_costs_usd: float = 0
    
    # Reward distribution
    reward_frequency: str = 'per_block'
    blocks_per_month: int = 0
    rewards_per_block: float = 0
    
    # Compound options
    auto_compound_enabled: bool = True
    daily_compound_apy: float = 0
    compound_boost: float = 0
    
    # Unstaking
    cooldown_epochs: int = 0
    cooldown_days: float = 0
    instant_unstake_available: bool = True
    instant_unstake_penalty: float = 0
    
    # Solana advantages
    eth_equivalent_tx_cost: float = 0
    solana_savings: float = 0
    
    # Governance (future)
    governance_enabled: bool = False
    governance_platform: str = 'realms'
    vote_escrow_planned: bool = True
    
    # Reward funding source (WP-005 & MED-002 Fix)
    reward_funding_source: str = 'emission_allocation'
    reward_funding_details: Optional[str] = None
    rewards_exceed_module_income: bool = False
    sustainability_warning: Optional[str] = None


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
    # Issue #6: Added fields for budget constraint handling
    high_quality_creators_actual: int = 0
    mid_level_creators_actual: int = 0
    budget_shortfall: bool = False
    budget_shortfall_amount: float = 0.0


class TotalsResult(BaseModel):
    """Total results across all modules"""
    revenue: float
    costs: float
    profit: float
    margin: float


# === PRE-LAUNCH MODULE RESULTS (Nov 2025) ===
# NOTE: These must be defined before SimulationResult which references them

class ReferralResult(BaseModel):
    """
    Result of referral module calculations.
    Tracks tiered referral program metrics and costs.
    """
    # User segments
    total_users: int = 0
    users_with_referrals: int = 0
    total_referrals: int = 0
    qualified_referrals: int = 0
    
    # Tier distribution
    referrers_by_tier: Dict[str, int] = {}
    referrals_by_tier: Dict[str, int] = {}
    
    # Token economics
    bonus_distributed_vcoin: float = 0.0
    bonus_distributed_usd: float = 0.0
    avg_bonus_per_referrer_vcoin: float = 0.0
    
    # Viral metrics
    viral_coefficient: float = 0.5
    effective_referral_rate: float = 0.0
    qualification_rate: float = 0.70
    
    # Cost to platform
    monthly_referral_cost_vcoin: float = 0.0
    monthly_referral_cost_usd: float = 0.0
    
    # Anti-sybil metrics
    suspected_sybil_referrals: int = 0
    sybil_rejection_rate: float = 0.05
    
    # Breakdown
    breakdown: Dict[str, Any] = {}


class PointsResult(BaseModel):
    """
    Result of pre-launch points system calculations.
    Models points distribution and TGE token conversion.
    """
    # Pool configuration
    points_pool_tokens: int = 10_000_000
    points_pool_percent: float = 0.01
    
    # Participation metrics
    waitlist_users: int = 0
    participating_users: int = 0
    participation_rate: float = 0.80
    
    # Points distribution
    total_points_distributed: int = 0
    avg_points_per_user: float = 0.0
    median_points_estimate: float = 0.0
    
    # Token conversion
    tokens_per_point: float = 0.0
    avg_tokens_per_user: float = 0.0
    
    # Segment breakdown
    users_by_segment: Dict[str, int] = {}
    points_by_segment: Dict[str, int] = {}
    tokens_by_segment: Dict[str, float] = {}
    
    # Anti-gaming metrics
    suspected_sybil_users: int = 0
    sybil_rejection_rate: float = 0.05
    points_rejected: int = 0
    
    # Activity breakdown
    points_by_activity: Dict[str, int] = {}
    
    # Top earner estimates
    top_1_percent_tokens: float = 0.0
    top_10_percent_tokens: float = 0.0
    bottom_50_percent_tokens: float = 0.0
    
    # Breakdown
    breakdown: Dict[str, Any] = {}


class GaslessResult(BaseModel):
    """
    Result of gasless onboarding calculations.
    Models sponsored transaction costs for user tiers.
    """
    # User tier distribution
    total_users: int = 0
    new_users: int = 0
    verified_users: int = 0
    premium_users: int = 0
    enterprise_users: int = 0
    
    # Transaction estimates
    total_sponsored_transactions: int = 0
    avg_transactions_per_user: float = 0.0
    
    # Cost breakdown
    base_fee_cost_usd: float = 0.0
    priority_fee_cost_usd: float = 0.0
    account_creation_cost_usd: float = 0.0
    total_sponsorship_cost_usd: float = 0.0
    
    # Per-tier costs
    new_user_cost_usd: float = 0.0
    verified_user_cost_usd: float = 0.0
    premium_user_cost_usd: float = 0.0
    enterprise_user_cost_usd: float = 0.0
    
    # Cost per user metrics
    avg_cost_per_user_usd: float = 0.0
    cost_per_transaction_usd: float = 0.0
    
    # Budget metrics
    monthly_sponsorship_budget_usd: float = 5000.0
    budget_utilization: float = 0.0
    
    # VCoin equivalent
    sponsorship_cost_vcoin: float = 0.0
    
    # Breakdown
    breakdown: Dict[str, Any] = {}


class PreLaunchResult(BaseModel):
    """
    Combined result for all pre-launch modules.
    Aggregates referral, points, and gasless metrics.
    """
    referral: Optional[ReferralResult] = None
    points: Optional[PointsResult] = None
    gasless: Optional[GaslessResult] = None
    
    # Summary metrics
    total_prelaunch_cost_usd: float = 0.0
    total_prelaunch_cost_vcoin: float = 0.0
    
    # Token impact
    points_tokens_allocated: int = 0
    referral_bonus_distributed: float = 0.0
    
    # Growth impact
    referral_users_acquired: int = 0
    waitlist_conversion_tokens: int = 0


class StartingUsersSummary(BaseModel):
    """
    Summary of starting/initial user counts for easy reference.
    Added to make user counts clearly visible at the top level of results.
    """
    # Total active users used in simulation
    total_active_users: int
    
    # Source of users
    user_source: str  # 'manual_input', 'marketing_budget', 'growth_scenario'
    
    # If from manual input
    manual_starting_users: Optional[int] = None
    
    # If from marketing budget calculation
    marketing_budget_usd: Optional[float] = None
    acquired_from_marketing: Optional[int] = None
    
    # User breakdown
    high_quality_creators: int = 0
    mid_level_creators: int = 0
    north_america_consumers: int = 0
    global_low_income_consumers: int = 0
    
    # Retention adjustment (if applied)
    retention_applied: bool = False
    users_before_retention: Optional[int] = None
    users_after_retention: Optional[int] = None
    retention_rate: Optional[float] = None


class SimulationResult(BaseModel):
    """Complete simulation result"""
    # NEW: Starting users summary at the top for easy reference
    starting_users_summary: Optional[StartingUsersSummary] = None
    
    identity: ModuleResult
    content: ModuleResult
    advertising: ModuleResult
    exchange: ModuleResult  # Exchange/Wallet module for crypto trading fees
    rewards: RewardsResult
    recapture: RecaptureResult
    customer_acquisition: CustomerAcquisitionMetrics
    totals: TotalsResult
    platform_fees: PlatformFeesResult
    # NEW: Liquidity and Staking (Nov 2025)
    liquidity: Optional[LiquidityResult] = None
    staking: Optional[StakingResult] = None
    # NEW: Governance (Nov 2025)
    governance: Optional[GovernanceResult] = None
    # NEW: Future Modules (Nov 2025)
    vchain: Optional[VChainResult] = None
    marketplace: Optional[MarketplaceResult] = None
    business_hub: Optional[BusinessHubResult] = None
    cross_platform: Optional[CrossPlatformResult] = None
    # NEW: Token Metrics (Nov 2025)
    token_metrics: Optional[TokenMetricsResult] = None
    # NEW: Pre-Launch Modules (Nov 2025)
    prelaunch: Optional[PreLaunchResult] = None
    # NEW: Sensitivity Analysis (Nov 2025)
    sensitivity: Optional[SensitivityResult] = None


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
    advertising_revenue: float
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
