// Platform Maturity Types (NEW - Issue #2, #3, #7)
export type PlatformMaturity = 'launch' | 'growing' | 'established';
export type RetentionModelType = 'social_app' | 'crypto_app' | 'gaming' | 'utility' | 'custom';

// === TOKEN ALLOCATION TYPES (November 2025) ===

// Token allocation category names
export type TokenAllocationCategory = 
  | 'seed' 
  | 'private' 
  | 'public' 
  | 'team' 
  | 'advisors' 
  | 'treasury' 
  | 'rewards' 
  | 'liquidity' 
  | 'foundation' 
  | 'marketing';

// Token allocation configuration for a single category
export interface TokenAllocationCategoryConfig {
  name: string;
  percent: number;
  tokens: number;
  tge_percent: number;
  cliff_months?: number;
  vesting_months?: number;
  price_usd?: number;
  is_programmatic?: boolean;
  emission_months?: number;
  description: string;
}

// Category unlock information
export interface TokenCategoryUnlock {
  category: string;
  tokensUnlocked: number;
  cumulativeUnlocked: number;
  totalAllocation: number;
  percentUnlocked: number;
}

// Circulating supply at a specific month
export interface CirculatingSupplyResult {
  month: number;
  seedUnlock: number;
  privateUnlock: number;
  publicUnlock: number;
  teamUnlock: number;
  advisorsUnlock: number;
  treasuryUnlock: number;
  rewardsUnlock: number;
  liquidityUnlock: number;
  foundationUnlock: number;
  marketingUnlock: number;
  totalNewUnlocks: number;
  cumulativeCirculating: number;
  circulatingPercent: number;
  categoryBreakdown: Record<string, TokenCategoryUnlock>;
}

// Full vesting schedule result
export interface VestingScheduleResult {
  durationMonths: number;
  monthlySupply: CirculatingSupplyResult[];
  tgeCirculating: number;
  finalCirculating: number;
  maxCirculating: number;
  month25PercentCirculating: number;
  month50PercentCirculating: number;
  month75PercentCirculating: number;
  monthFullCirculating: number;
  seedCompletionMonth: number;
  privateCompletionMonth: number;
  publicCompletionMonth: number;
  teamCompletionMonth: number;
  advisorsCompletionMonth: number;
  foundationCompletionMonth: number;
  marketingCompletionMonth: number;
  rewardsCompletionMonth: number;
}

// Treasury accumulation tracking
export interface TreasuryResult {
  revenueContributionUsd: number;
  revenueContributionVcoin: number;
  buybackContributionVcoin: number;
  feeDistributionVcoin: number;
  totalAccumulatedVcoin: number;
  totalAccumulatedUsd: number;
  treasuryAllocation: number;
  treasuryReleased: number;
  treasuryAvailable: number;
  revenueShareRate: number;
}

// === GROWTH SCENARIO TYPES (November 2025) ===

// Growth scenario selection
export type GrowthScenario = 'conservative' | 'base' | 'bullish';

// Market condition affecting growth
export type MarketCondition = 'bear' | 'neutral' | 'bull';

// FOMO event types that trigger growth spikes
export type FomoEventType = 
  | 'tge_launch'        // Token Generation Event
  | 'partnership'       // Major partnership announcement
  | 'viral_moment'      // Viral content/trend
  | 'exchange_listing'  // CEX/DEX listing
  | 'influencer'        // Major influencer adoption
  | 'holiday'           // Holiday season boost
  | 'feature_launch'    // Major feature release
  | 'milestone';        // User/volume milestone

// FOMO event that occurred during simulation
export interface FomoEvent {
  month: number;
  eventType: FomoEventType;
  impactMultiplier: number;
  description: string;
  durationDays: number;
}

// Growth scenario configuration
export interface GrowthScenarioConfig {
  name: string;
  description: string;
  waitlistConversionRate: number;
  month1FomoMultiplier: number;
  monthlyGrowthRates: number[];
  month1Retention: number;
  month3Retention: number;
  month6Retention: number;
  month12Retention: number;
  viralCoefficient: number;
  tokenPriceStart: number;
  tokenPriceMonth6Multiplier: number;
  tokenPriceEndMultiplier: number;
  fomoEvents: FomoEvent[];
  expectedMonth1Users: number;
  expectedMonth12Mau: number;
}

// Market condition configuration
export interface MarketConditionConfig {
  name: string;
  description: string;
  growthMultiplier: number;
  retentionMultiplier: number;
  priceMultiplier: number;
  fomoMultiplier: number;
  cacMultiplier: number;
}

// Growth projection result
export interface GrowthProjectionResult {
  scenario: GrowthScenario;
  marketCondition: MarketCondition;
  startingWaitlist: number;
  monthlyMau: number[];
  monthlyAcquired: number[];
  monthlyChurned: number[];
  monthlyGrowthRates: number[];
  tokenPriceCurve: number[];
  tokenPriceStart: number;
  tokenPriceMonth6: number;
  tokenPriceEnd: number;
  fomoEvents: FomoEvent[];
  totalUsersAcquired: number;
  month1Users: number;
  month6Mau: number;
  finalMau: number;
  peakMau: number;
  growthPercentage: number;
  waitlistConversionRate: number;
  month1FomoMultiplier: number;
  viralCoefficient: number;
}

// === SOLANA NETWORK TYPES (November 2025) ===

// Solana DEX platforms
export type SolanaDex = 
  | 'raydium' 
  | 'raydium_clmm' 
  | 'orca' 
  | 'orca_whirlpool' 
  | 'meteora' 
  | 'phoenix' 
  | 'lifinity'
  | 'jupiter';

// Solana pool types
export type SolanaPoolType = 
  | 'constant_product'  // x*y=k standard AMM
  | 'concentrated'      // CLMM (Raydium, Orca Whirlpools)
  | 'stable'           // Stable swap curve
  | 'dynamic';         // Dynamic fees (Meteora)

// Solana network info
export interface SolanaNetworkInfo {
  network: 'mainnet-beta' | 'devnet' | 'testnet';
  baseTxFeeUsd: number;
  priorityFeeUsd: number;
  blockTimeMs: number;
  tokenProgram: 'spl-token' | 'token-2022';
}

// Solana pool configuration
export interface SolanaPoolInfo {
  name: string;
  dex: SolanaDex;
  type: SolanaPoolType;
  feeTier: number;
  share: number;
  liquidityUsd: number;
}

// Solana staking info
export interface SolanaStakingInfo {
  programType: string;
  framework: string;
  rewardFrequency: 'per_block' | 'per_epoch';
  autoCompoundEnabled: boolean;
  cooldownDays: number;
  instantUnstakePenalty: number;
}

// Simulation Parameters - Updated with all audit fixes
export interface SimulationParameters {
  // Platform Maturity (NEW)
  platformMaturity?: PlatformMaturity;
  autoAdjustForMaturity?: boolean;
  
  // Retention Model (NEW - Issue #1)
  applyRetention?: boolean;
  retentionModelType?: RetentionModelType;
  platformAgeMonths?: number;
  
  // Compliance (NEW - Issue #13)
  includeComplianceCosts?: boolean;
  
  // Growth Scenario Settings (NEW - Nov 2025)
  // Note: Starting users are calculated from marketing budget, not a separate input
  growthScenario?: GrowthScenario;
  marketCondition?: MarketCondition;
  enableFomoEvents?: boolean;
  useGrowthScenarios?: boolean;
  
  // Token Allocation / Vesting (NEW - Nov 2025)
  trackVestingSchedule?: boolean;
  treasuryRevenueShare?: number;
  
  // Core parameters
  tokenPrice: number;
  marketingBudget: number;
  startingUsers: number;
  
  // User acquisition (Issue #2)
  northAmericaBudgetPercent: number;
  globalLowIncomeBudgetPercent: number;
  cacNorthAmericaConsumer: number;
  cacGlobalLowIncomeConsumer: number;
  highQualityCreatorCAC: number;
  midLevelCreatorCAC: number;
  highQualityCreatorsNeeded: number;
  midLevelCreatorsNeeded: number;
  
  // Economic parameters (Issues #3, #5, #8)
  burnRate: number;
  buybackPercent: number;
  verificationRate: number;
  postsPerUser: number;
  creatorPercentage?: number;      // NEW - Issue #8
  postsPerCreator?: number;        // NEW - Issue #8
  adCPMMultiplier: number;
  rewardAllocationPercent: number;
  
  // Dynamic Reward Allocation (NEW - Nov 2025)
  enableDynamicAllocation?: boolean;
  initialUsersForAllocation?: number;
  targetUsersForMaxAllocation?: number;
  maxPerUserMonthlyUsd?: number;
  minPerUserMonthlyUsd?: number;
  
  // Liquidity Parameters (NEW - Nov 2025)
  initialLiquidityUsd?: number;
  protocolOwnedLiquidity?: number;
  liquidityLockMonths?: number;
  targetLiquidityRatio?: number;
  
  // Staking Parameters (NEW - Nov 2025)
  stakingApy?: number;
  stakerFeeDiscount?: number;
  minStakeAmount?: number;
  stakeLockDays?: number;
  
  // Creator Economy Parameters (NEW - Nov 2025)
  platformCreatorFee?: number;
  boostPostFeeVcoin?: number;
  premiumDmFeeVcoin?: number;
  premiumReactionFeeVcoin?: number;
  
  // Module toggles
  enableAdvertising: boolean;
  enableMessaging: boolean;
  enableCommunity: boolean;
  enableExchange: boolean;
  enableNft?: boolean;             // NEW - Issue #12
  
  // Identity Module pricing (USD) - Issue #11
  basicPrice: number;
  verifiedPrice: number;
  premiumPrice: number;
  enterprisePrice: number;
  transferFee: number;
  saleCommission: number;
  monthlySales: number;
  avgProfilePrice?: number;        // NEW - Issue #11
  
  // Content Module pricing (VCoin) - Issue #12
  textPostFeeVcoin: number;
  imagePostFeeVcoin: number;
  videoPostFeeVcoin: number;
  nftMintFeeVcoin: number;
  nftMintPercentage?: number;      // NEW - Issue #12
  premiumContentVolumeVcoin: number;
  contentSaleVolumeVcoin: number;
  contentSaleCommission: number;
  
  // Community Module pricing (USD)
  smallCommunityFee: number;
  mediumCommunityFee: number;
  largeCommunityFee: number;
  enterpriseCommunityFee: number;
  eventHostingFee: number;
  communityVerificationFee: number;
  communityAnalyticsFee: number;
  
  // Advertising Module pricing (USD) - Issue #7
  bannerCPM: number;
  videoCPM: number;
  promotedPostFee: number;
  campaignManagementFee: number;
  adAnalyticsFee: number;
  
  // Messaging Module pricing (USD)
  encryptedDMFee: number;
  groupChatFee: number;
  fileTransferFee: number;
  voiceCallFee: number;
  messageStorageFee: number;
  messagingPremiumFee: number;
  
  // Exchange/Wallet Module - Issue #4
  exchangeSwapFeePercent: number;
  exchangeWithdrawalFee: number;
  exchangeUserAdoptionRate: number;
  exchangeAvgMonthlyVolume: number;
  exchangeWithdrawalsPerUser: number;
  
  // Reward Distribution
  textPostPoints: number;
  imagePostPoints: number;
  audioPostPoints: number;
  shortVideoPoints: number;
  postVideosPoints: number;
  musicPoints: number;
  podcastPoints: number;
  audioBookPoints: number;
  likePoints: number;
  commentPoints: number;
  sharePoints: number;
  followPoints: number;
  maxPostsPerDay: number;
  maxLikesPerDay: number;
  maxCommentsPerDay: number;
  highQualityMultiplier: number;
  verifiedMultiplier: number;
  premiumMultiplier: number;
  day7Decay: number;
  day30Decay: number;
  maxDailyRewardUSD: number;
}

// Module Results
export interface ModuleResult {
  revenue: number;
  costs: number;
  profit: number;
  margin: number;
  breakdown: Record<string, number | boolean | string>;
}

// Recapture Results
export interface RecaptureResult {
  totalRecaptured: number;
  recaptureRate: number;
  burns: number;
  treasury: number;
  staking: number;
  buybacks: number;
  totalRevenueSourceVcoin: number;
  totalTransactionFeesUsd: number;
  totalRoyaltiesUsd: number;
}

// Rewards Results
export interface RewardsResult {
  monthlyEmission: number;
  maxMonthlyEmission: number;
  emissionUsd: number;
  opCosts: number;
  dailyEmission: number;
  dailyRewardPool: number;
  dailyRewardPoolUsd: number;
  monthlyRewardPool: number;
  allocationPercent: number;
  grossMonthlyEmission: number;
  grossEmissionUsd: number;
  platformFeeVcoin: number;
  platformFeeUsd: number;
  // Dynamic allocation fields (NEW - Nov 2025)
  isDynamicAllocation?: boolean;
  dynamicAllocationPercent?: number;
  growthFactor?: number;
  perUserMonthlyVcoin?: number;
  perUserMonthlyUsd?: number;
  allocationCapped?: boolean;
  effectiveUsers?: number;
}

// Platform Fees Results
export interface PlatformFeesResult {
  rewardFeeVcoin: number;
  rewardFeeUsd: number;
  feeRate: number;
}

// Liquidity Results (NEW - Nov 2025) - Solana DEX Integration
export interface LiquidityResult {
  // Core metrics
  initialLiquidity: number;
  protocolOwnedPercent: number;
  protocolOwnedUsd: number;
  communityLpUsd: number;
  marketCap: number;
  liquidityRatio: number;
  
  // Slippage data (with CLMM concentration factor)
  slippage1k: number;
  slippage5k: number;
  slippage10k: number;
  slippage50k: number;
  slippage100k: number;
  
  // Pool info
  poolCount: number;
  lockMonths: number;
  
  // Health metrics
  healthScore: number;
  healthStatus: string;
  healthColor: string;
  healthIcon: string;
  
  // Volume metrics
  estimatedMonthlyVolume: number;
  volumeLiquidityRatio: number;
  
  // Pressure analysis
  buyPressureUsd: number;
  sellPressureUsd: number;
  netPressureUsd: number;
  pressureRatio: number;
  
  // Recommendations
  meets70Target: boolean;
  recommendedLiquidity: number;
  
  // === SOLANA-SPECIFIC (November 2025) ===
  network?: 'solana';
  primaryDex?: SolanaDex;
  primaryPoolType?: SolanaPoolType;
  concentrationFactor?: number;  // CLMM capital efficiency (2-10x)
  effectiveLiquidity?: number;   // After concentration factor
  
  // Pool details
  pools?: SolanaPoolInfo[];
  
  // Jupiter aggregation
  jupiterEnabled?: boolean;
  jupiterRoutes?: number;
  dexAggregator?: string;
  
  // Economics
  weightedPoolFee?: number;
  estimatedLpEarnings?: number;
  lpCreationCostUsd?: number;
  
  // Solana advantages
  txCostPerSwap?: number;
  avgFinalityMs?: number;
  mevProtection?: boolean;
}

// Staking Results (NEW - Nov 2025) - Solana SPL Token Staking
export interface StakingResult {
  // === PLATFORM REVENUE & PROFIT ===
  revenue: number;        // Total platform revenue from staking
  costs: number;          // Infrastructure costs
  profit: number;         // Net profit
  margin: number;         // Profit margin %
  
  // Revenue breakdown
  protocolFeeFromRewardsUsd: number;   // 5% of staking rewards
  protocolFeeFromRewardsVcoin: number;
  unstakePenaltyUsd: number;            // Early unstake fees
  unstakePenaltyVcoin: number;
  txFeeRevenueUsd: number;              // Transaction fee revenue
  txFeeRevenueVcoin: number;
  totalRevenueVcoin: number;
  
  // Core metrics
  stakingApy: number;
  stakerFeeDiscount: number;
  minStakeAmount: number;
  lockDays: number;
  
  // Participation
  stakersCount: number;
  participationRate: number;
  avgStakeAmount: number;
  
  // Totals
  totalStaked: number;
  totalStakedUsd: number;
  stakingRatio: number;
  
  // Rewards (paid to stakers, net after protocol fee)
  totalMonthlyRewards: number;
  totalMonthlyRewardsUsd: number;
  rewardsPerStaker: number;
  rewardsPerStakerUsd: number;
  effectiveMonthlyYield: number;
  
  // Tier distribution
  tierDistribution: Record<string, number>;
  
  // Platform impact
  totalFeeSavingsUsd: number;
  lockedSupplyPercent: number;
  reducedSellPressure: number;
  reducedSellPressureUsd: number;
  
  // Health
  stakingStatus: string;
  isHealthy: boolean;
  
  // Annual projections
  annualRewardsTotal: number;
  annualRewardsUsd: number;
  
  // === SOLANA-SPECIFIC (November 2025) ===
  network?: 'solana';
  programType?: string;  // 'spl_token_staking'
  framework?: string;    // 'anchor'
  
  // On-chain costs
  stakeAccountRentSol?: number;
  stakeAccountRentUsd?: number;
  totalStakeAccountsCostUsd?: number;
  stakingTxCostUsd?: number;
  monthlyTxCostsUsd?: number;
  
  // Reward distribution
  rewardFrequency?: 'per_block' | 'per_epoch';
  blocksPerMonth?: number;
  rewardsPerBlock?: number;
  
  // Compound options
  autoCompoundEnabled?: boolean;
  dailyCompoundApy?: number;
  compoundBoost?: number;
  
  // Unstaking
  cooldownEpochs?: number;
  cooldownDays?: number;
  instantUnstakeAvailable?: boolean;
  instantUnstakePenalty?: number;
  
  // Solana cost savings vs Ethereum
  ethEquivalentTxCost?: number;
  solanaSavings?: number;
  
  // Governance (future)
  governanceEnabled?: boolean;
  governancePlatform?: string;
  voteEscrowPlanned?: boolean;
}

// Customer Acquisition Metrics
export interface CustomerAcquisitionMetrics {
  totalCreatorCost: number;
  consumerAcquisitionBudget: number;
  northAmericaBudget: number;
  globalLowIncomeBudget: number;
  northAmericaUsers: number;
  globalLowIncomeUsers: number;
  totalUsers: number;
  blendedCAC: number;
}

// Full Simulation Result
export interface SimulationResult {
  identity: ModuleResult;
  content: ModuleResult;
  community: ModuleResult;
  advertising: ModuleResult;
  messaging: ModuleResult;
  exchange: ModuleResult;
  rewards: RewardsResult;
  recapture: RecaptureResult;
  customerAcquisition: CustomerAcquisitionMetrics;
  totals: {
    revenue: number;
    costs: number;
    profit: number;
    margin: number;
  };
  platformFees: PlatformFeesResult;
  // NEW - Nov 2025
  liquidity?: LiquidityResult;
  staking?: StakingResult;
}

// Monte Carlo Results
export interface MonteCarloResult {
  iterations: number;
  percentiles: {
    p5: SimulationResult;
    p50: SimulationResult;
    p95: SimulationResult;
  };
  distributions: {
    revenue: number[];
    profit: number[];
    recaptureRate: number[];
  };
  statistics: {
    mean: { revenue: number; profit: number; recaptureRate: number };
    std: { revenue: number; profit: number; recaptureRate: number };
  };
}

// Agent-Based Results
export interface AgentResult {
  id: string;
  type: 'creator' | 'consumer' | 'whale' | 'bot';
  rewardsEarned: number;
  tokensSpent: number;
  tokensStaked: number;
  activity: number;
  flagged: boolean;
}

export interface AgentBasedResult {
  totalAgents: number;
  agentBreakdown: Record<string, number>;
  marketDynamics: {
    buyPressure: number;
    sellPressure: number;
    priceImpact: number;
  };
  systemMetrics: {
    totalRewardsDistributed: number;
    totalRecaptured: number;
    netCirculation: number;
    platformFeeCollected: number;
    platformFeeUsd: number;
  };
  topAgents: AgentResult[];
  flaggedBots: number;
}

// Monthly Progression Results (NEW - Issue #16)
export interface MonthlyMetrics {
  month: number;
  usersAcquired: number;
  usersChurned: number;
  activeUsers: number;
  totalAcquiredLifetime: number;
  retentionRate: number;
  revenue: number;
  costs: number;
  profit: number;
  margin: number;
  identityRevenue: number;
  contentRevenue: number;
  communityRevenue: number;
  advertisingRevenue: number;
  messagingRevenue: number;
  exchangeRevenue: number;
  platformFeeRevenue: number;
  tokensDistributed: number;
  tokensRecaptured: number;
  recaptureRate: number;
  netEmission: number;
  cacEffective: number;
  ltvEstimate: number;
  marketingSpend: number;
  arpu: number;
  arr: number;
  cohortBreakdown: Record<number, number>;
  // Growth scenario fields (NEW - Nov 2025)
  tokenPrice?: number;
  growthRate?: number;
  scenarioMultiplier?: number;
  fomoEvent?: FomoEvent | null;
  // Dynamic allocation fields (NEW - Nov 2025)
  dynamicAllocationPercent?: number;
  dynamicGrowthFactor?: number;
  perUserMonthlyVcoin?: number;
  perUserMonthlyUsd?: number;
  allocationCapped?: boolean;
  // Token allocation / vesting fields (NEW - Nov 2025)
  circulatingSupply?: number;
  circulatingPercent?: number;
  newUnlocks?: number;
  // Treasury fields (NEW - Nov 2025)
  treasuryRevenueUsd?: number;
  treasuryAccumulatedUsd?: number;
}

export interface MonthlyProgressionResult {
  durationMonths: number;
  monthlyData: MonthlyMetrics[];
  totalUsersAcquired: number;
  peakActiveUsers: number;
  finalActiveUsers: number;
  averageRetentionRate: number;
  totalRevenue: number;
  totalCosts: number;
  totalProfit: number;
  averageMargin: number;
  cagrUsers: number;
  cagrRevenue: number;
  totalTokensDistributed: number;
  totalTokensRecaptured: number;
  overallRecaptureRate: number;
  monthsToProfitability: number | null;
  cumulativeProfitCurve: number[];
  retentionCurve: Record<number, number>;
  // Growth scenario fields (NEW - Nov 2025)
  growthProjection?: GrowthProjectionResult;
  scenarioUsed?: GrowthScenario | null;
  marketConditionUsed?: MarketCondition | null;
  fomoEventsTriggered?: FomoEvent[];
  tokenPriceFinal?: number;
  // Token allocation / vesting (NEW - Nov 2025)
  vestingSchedule?: VestingScheduleResult;
  finalCirculatingSupply?: number;
  finalCirculatingPercent?: number;
  // Treasury tracking (NEW - Nov 2025)
  treasuryResult?: TreasuryResult;
  totalTreasuryAccumulatedUsd?: number;
  totalTreasuryAccumulatedVcoin?: number;
}

// WebSocket Message Types
export type SimulationType = 'deterministic' | 'monte_carlo' | 'agent_based' | 'monthly_progression';

// Percentile key for Monte Carlo results
export type PercentileKey = 'p5' | 'p50' | 'p95';

export interface SimulationRequest {
  type: SimulationType;
  parameters: SimulationParameters;
  options?: {
    iterations?: number;      // For Monte Carlo
    duration?: number;        // For Agent-Based and Monthly Progression (months)
    agentCount?: number;      // For Agent-Based
    includeSeasonality?: boolean;  // For Monthly Progression
    marketSaturationFactor?: number;  // For Monthly Progression
    useGrowthScenarios?: boolean;  // For Monthly Progression with growth scenarios
  };
}

export interface SimulationProgress {
  type: 'progress';
  current: number;
  total: number;
  percentage: number;
  partialResult?: Partial<SimulationResult | MonteCarloResult | AgentBasedResult | MonthlyProgressionResult>;
}

export interface SimulationComplete {
  type: 'complete';
  result: SimulationResult | MonteCarloResult | AgentBasedResult | MonthlyProgressionResult;
}

export interface SimulationError {
  type: 'error';
  message: string;
  details?: string;
}

export type WebSocketMessage = SimulationProgress | SimulationComplete | SimulationError;

// Preset configurations
export type PresetName = 'conservative' | 'base' | 'aggressive' | 'bull';

export interface Preset {
  name: PresetName;
  label: string;
  icon: string;
  description: string;
  parameters: Partial<SimulationParameters>;
}

// Retention Curve (NEW - Issue #1)
export interface RetentionCurveData {
  name: string;
  description: string;
  rates: Record<number, number>;  // month -> retention rate
}

// Platform Maturity Tier (NEW)
export interface MaturityTier {
  id: PlatformMaturity;
  name: string;
  description: string;
  adjustments: {
    cacMultiplier: number;
    conversionRate: number;
    adFillRate: number;
    bannerCpm: number;
    videoCpm: number;
    profileSalesMonthly: number;
    avgProfilePrice: number;
    nftPercentage: number;
    creatorPercentage: number;
  };
}
