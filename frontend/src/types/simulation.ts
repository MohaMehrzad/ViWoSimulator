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

// === FUTURE MODULE PARAMETERS (November 2025) ===

export interface VChainParameters {
  enableVchain: boolean;
  vchainLaunchMonth: number;
  // Transaction fees
  vchainTxFeePercent: number;
  vchainMinTxFeeUsd?: number;
  vchainMaxTxFeeUsd?: number;
  // Bridge fees
  vchainBridgeFeePercent: number;
  // Gas abstraction
  vchainGasMarkupPercent: number;
  // Volume projections
  vchainMonthlyTxVolumeUsd: number;
  vchainMonthlyBridgeVolumeUsd: number;
  // Validator economics
  vchainValidatorApy: number;
  vchainMinValidatorStake: number;
  vchainValidatorCount: number;
  // Enterprise API
  vchainEnterpriseClients: number;
  vchainAvgEnterpriseRevenue: number;
}

export interface MarketplaceParameters {
  enableMarketplace: boolean;
  marketplaceLaunchMonth: number;
  // Commission rates
  marketplacePhysicalCommission: number;
  marketplaceDigitalCommission: number;
  marketplaceNftCommission: number;
  marketplaceServiceCommission: number;
  marketplaceMaxCommissionUsd?: number;
  // Payment processing
  marketplaceCryptoPaymentFee?: number;
  marketplaceEscrowFee?: number;
  // Volume projections
  marketplaceMonthlyGmvUsd: number;
  marketplaceGmvPhysicalPercent?: number;
  marketplaceGmvDigitalPercent?: number;
  marketplaceGmvNftPercent?: number;
  marketplaceGmvServicesPercent?: number;
  // Seller metrics
  marketplaceActiveSellers: number;
  marketplaceVerifiedSellerRate?: number;
  marketplaceStoreSubscriptionRate?: number;
  // Listing fees
  marketplaceFeaturedListingFee?: number;
  marketplaceStoreSubscriptionFee?: number;
  // Advertising
  marketplaceAdCpc?: number;
  marketplaceMonthlyAdClicks?: number;
}

export interface BusinessHubParameters {
  enableBusinessHub: boolean;
  businessHubLaunchMonth: number;
  // Freelancer platform
  freelancerJobPostingFee?: number;
  freelancerCommissionRate: number;
  freelancerEscrowFee?: number;
  freelancerMonthlyTransactionsUsd: number;
  freelancerActiveCount: number;
  // Startup launchpad
  startupMonthlyRegistrations?: number;
  startupRegistrationFee?: number;
  acceleratorParticipants?: number;
  acceleratorFee?: number;
  // Funding portal
  fundingPortalMonthlyVolume: number;
  fundingPlatformFee: number;
  investorNetworkMembers?: number;
  investorNetworkFee?: number;
  // Project management SaaS
  pmProfessionalUsers?: number;
  pmProfessionalFee?: number;
  pmBusinessUsers?: number;
  pmBusinessFee?: number;
  pmEnterpriseUsers?: number;
  pmEnterpriseFee?: number;
  // Learning academy
  academyMonthlyCoursesSales?: number;
  academyAvgCoursePrice?: number;
  academyPlatformShare?: number;
  academySubscriptionUsers?: number;
  academySubscriptionFee?: number;
}

export interface CrossPlatformParameters {
  enableCrossPlatform: boolean;
  crossPlatformLaunchMonth: number;
  // Content sharing subscriptions
  crossPlatformCreatorTierFee?: number;
  crossPlatformProfessionalTierFee?: number;
  crossPlatformAgencyTierFee?: number;
  crossPlatformCreatorSubscribers?: number;
  crossPlatformProfessionalSubscribers?: number;
  crossPlatformAgencySubscribers?: number;
  // Account renting
  crossPlatformRentalCommission: number;
  crossPlatformEscrowFee?: number;
  crossPlatformMonthlyRentalVolume: number;
  crossPlatformActiveRenters: number;
  crossPlatformActiveOwners: number;
  // Insurance
  crossPlatformInsuranceTakeRate?: number;
  crossPlatformInsuranceRate?: number;
  // Verification
  crossPlatformMonthlyVerifications?: number;
  crossPlatformVerificationFee?: number;
  crossPlatformPremiumVerifiedUsers?: number;
  crossPlatformPremiumVerifiedFee?: number;
  // Analytics
  crossPlatformAdvancedAnalyticsUsers?: number;
  crossPlatformAnalyticsFee?: number;
  crossPlatformApiUsers?: number;
  crossPlatformApiFee?: number;
  // Content licensing
  crossPlatformMonthlyLicenseVolume?: number;
  crossPlatformLicenseCommission?: number;
}

// === GOVERNANCE RESULT (November 2025) ===

export interface GovernanceResult {
  revenue: number;
  costs: number;
  profit: number;
  totalVevcoinSupply: number;
  totalVevcoinSupplyUsd: number;
  vevcoinOfCirculatingPercent: number;
  avgVevcoinPerStaker: number;
  avgLockWeeks: number;
  avgBoostMultiplier: number;
  // Direct participation
  activeVoters: number;
  activeVotingPower: number;
  votingParticipationRate: number;
  // Delegation (NEW - Nov 2025)
  delegators: number;
  delegatedVotingPower: number;
  delegationRate: number;
  // Effective participation (voters + delegators)
  totalParticipants: number;
  effectiveParticipationRate: number;
  // Distribution
  tierDistribution: Record<string, number>;
  eligibleProposers: number;
  expectedMonthlyProposals: number;
  votingPowerConcentration: number;
  decentralizationScore: number;
  governanceHealthScore: number;
}

// === FUTURE MODULE RESULTS (November 2025) ===

export interface VChainResult {
  enabled: boolean;
  launched: boolean;
  monthsActive: number;
  growthFactor: number;
  revenue: number;
  txFeeRevenue: number;
  bridgeFeeRevenue: number;
  gasMarkupRevenue: number;
  enterpriseApiRevenue: number;
  monthlyTxVolume: number;
  monthlyBridgeVolume: number;
  estimatedTransactions: number;
  activeEnterpriseClients: number;
  validatorsActive: number;
  totalValidatorStake: number;
  costs: number;
  profit: number;
  margin: number;
  launchMonth: number;
  monthsUntilLaunch: number;
}

export interface MarketplaceResult {
  enabled: boolean;
  launched: boolean;
  monthsActive: number;
  growthFactor: number;
  revenue: number;
  commissionRevenue: number;
  physicalCommission: number;
  digitalCommission: number;
  nftCommission: number;
  servicesCommission: number;
  monthlyGmv: number;
  activeSellers: number;
  costs: number;
  profit: number;
  margin: number;
  launchMonth: number;
  monthsUntilLaunch: number;
}

export interface BusinessHubResult {
  enabled: boolean;
  launched: boolean;
  monthsActive: number;
  growthFactor: number;
  revenue: number;
  freelancerRevenue: number;
  startupRevenue: number;
  fundingRevenue: number;
  pmSaasRevenue: number;
  academyRevenue: number;
  activeFreelancers: number;
  monthlyFreelanceVolume: number;
  monthlyFundingVolume: number;
  pmTotalUsers: number;
  totalVcoinRevenue: number;
  costs: number;
  profit: number;
  margin: number;
  launchMonth: number;
  monthsUntilLaunch: number;
}

export interface CrossPlatformResult {
  enabled: boolean;
  launched: boolean;
  monthsActive: number;
  growthFactor: number;
  revenue: number;
  subscriptionRevenue: number;
  rentalRevenue: number;
  insuranceRevenue: number;
  verificationRevenue: number;
  analyticsRevenue: number;
  licenseRevenue: number;
  totalSubscribers: number;
  monthlyRentalVolume: number;
  activeRenters: number;
  activeOwners: number;
  totalVcoinRevenue: number;
  costs: number;
  profit: number;
  margin: number;
  launchMonth: number;
  monthsUntilLaunch: number;
}

// === TOKEN METRICS RESULT (November 2025) ===

export interface TokenVelocityResult {
  velocity: number;
  annualizedVelocity: number;
  interpretation: string;
  healthScore: number;
  daysToTurnover: number;
  transactionVolume: number;
  circulatingSupply: number;
}

export interface RealYieldResult {
  monthlyRealYield: number;
  annualRealYield: number;
  interpretation: string;
  isSustainable: boolean;
  yieldPer1000Usd: number;
  protocolRevenue: number;
  stakedValueUsd: number;
}

export interface ValueAccrualResult {
  totalScore: number;
  grade: string;
  interpretation: string;
  breakdown: Record<string, number>;
  weights: Record<string, number>;
}

// === GINI & RUNWAY METRICS (December 2025 - 2025 Audit Compliance) ===

export interface GiniResult {
  gini: number;  // 0=equal, 1=concentrated
  interpretation: string;
  decentralizationScore: number;
  holderCount: number;
  top1PercentConcentration: number;
  top10PercentConcentration: number;
}

export interface RunwayResult {
  runwayMonths: number;
  runwayYears: number;
  isSustainable: boolean;
  interpretation: string;
  netBurnMonthly: number;
  monthlyRevenue: number;
  monthlyExpenses: number;
  treasuryBalance: number;
  runwayHealth: number;
  monthsToSustainability: number;
}

export interface InflationResult {
  // Emission
  monthlyEmission: number;
  monthlyEmissionUsd: number;
  annualEmission: number;
  emissionRate: number;
  // Deflationary
  monthlyBurns: number;
  monthlyBurnsUsd: number;
  monthlyBuybacks: number;
  monthlyBuybacksUsd: number;
  totalDeflationary: number;
  // Net inflation
  netMonthlyInflation: number;
  netMonthlyInflationUsd: number;
  netInflationRate: number;
  annualNetInflationRate: number;
  // Supply
  circulatingSupply: number;
  totalSupply: number;
  // Health
  isDeflationary: boolean;
  deflationStrength: string;
  supplyHealthScore: number;
  // Projections
  monthsToMaxSupply: number;
  projectedYear1Inflation: number;
  projectedYear5Supply: number;
}

// === WHALE ANALYSIS RESULTS (December 2025 - 2025 Audit Compliance) ===

export interface TopHoldersGroup {
  holdersCount: number;
  amountVcoin: number;
  amountUsd: number;
  percentage: number;
  avgBalance: number;
}

export interface WhaleInfo {
  rank: number;
  balance: number;
  percentage: number;
}

export interface DumpScenarioResult {
  scenarioName: string;
  sellersCount: number;
  sellAmountVcoin: number;
  sellAmountUsd: number;
  sellPercentage: number;
  priceImpactPercent: number;
  newPrice: number;
  liquidityAbsorbedPercent: number;
  marketCapLoss: number;
  recoveryDaysEstimate: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface WhaleAnalysisResult {
  holderCount: number;
  totalSupply: number;
  totalHeld: number;
  tokenPrice: number;
  
  // Top holder groups
  top10: TopHoldersGroup;
  top50: TopHoldersGroup;
  top100: TopHoldersGroup;
  
  // Percentile groups
  top1Percent: TopHoldersGroup;
  top5Percent: TopHoldersGroup;
  top10Percent: TopHoldersGroup;
  
  // Whale breakdown
  whaleCount: number;
  largeHolderCount: number;
  mediumHolderCount: number;
  smallHolderCount: number;
  
  whales: WhaleInfo[];
  
  // Risk metrics
  concentrationRiskScore: number;
  riskLevel: string;
  riskColor: string;
  
  // Dump scenarios
  dumpScenarios: DumpScenarioResult[];
  
  // Recommendations
  recommendations: string[];
}

// === ATTACK ANALYSIS RESULTS (December 2025 - 2025 Audit Compliance) ===

export interface AttackScenarioDetail {
  name: string;
  category: string;
  description: string;
  attackVector: string;
  probability: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  potentialLossUsd: number;
  potentialLossPercent: number;
  mitigationEffectiveness: number;
  recoveryTimeDays: number;
  requiredCapital: number;
  complexity: string;
}

export interface SecurityFeatures {
  hasTimelock: boolean;
  timelockDelayHours: number;
  hasMultisig: boolean;
  multisigThreshold: number;
  oracleType: string;
}

export interface AttackAnalysisResult {
  vulnerabilityScore: number;
  riskLevel: string;
  riskColor: string;
  totalPotentialLossUsd: number;
  avgSeverityScore: number;
  marketCap: number;
  liquidityRatio: number;
  volumeToLiquidity: number;
  securityFeatures: SecurityFeatures;
  scenarios: AttackScenarioDetail[];
  recommendations: string[];
}

// === LIQUIDITY FARMING RESULTS (December 2025 - 2025 Audit Compliance) ===

export interface ILScenario {
  scenario: string;
  priceChangePercent: number;
  finalPrice: number;
  impermanentLossPercent: number;
  interpretation: string;
}

export interface FarmingAPY {
  rewardApr: number;
  feeApr: number;
  totalApr: number;
  rewardApy: number;
  feeApy: number;
  totalApy: number;
  dailyRewardRate: number;
  dailyTotalRate: number;
  poolTvlUsd: number;
  dailyRewardVcoin: number;
  dailyRewardUsd: number;
  isSustainable: boolean;
  example1000Final: number;
  example1000Profit: number;
}

export interface FarmingRiskMetrics {
  riskScore: number;
  riskLevel: string;
  ilBreakevenMultiplier: number;
  ilBreakevenPriceUp: number;
  ilBreakevenPriceDown: number;
}

export interface FarmingSimulationMonth {
  month: number;
  vcoinPrice: number;
  priceChangePercent: number;
  holdValueUsd: number;
  lpPositionValueUsd: number;
  cumulativeRewardsUsd: number;
  cumulativeFeesUsd: number;
  totalValueUsd: number;
  impermanentLossPercent: number;
  impermanentLossUsd: number;
  netVsHoldingUsd: number;
  totalPnlUsd: number;
  totalPnlPercent: number;
}

export interface FarmingSimulation {
  initialInvestmentUsd: number;
  initialVcoinPrice: number;
  lpSharePercent: number;
  monthlyProjections: FarmingSimulationMonth[];
  finalResult?: FarmingSimulationMonth;
}

export interface LiquidityFarmingResult {
  apy: FarmingAPY;
  ilScenarios: ILScenario[];
  simulations: Record<string, FarmingSimulation>;  // bull_case, bear_case, stable_case
  riskMetrics: FarmingRiskMetrics;
  recommendations: string[];
}

// === GAME THEORY RESULTS (December 2025 - 2025 Audit Compliance) ===

export interface StrategyMetrics {
  returnPercent: number;
  riskPercent: number;
  riskAdjustedReturn: number;
}

export interface StakingEquilibrium {
  stakeProbability: number;
  sellProbability: number;
  holdProbability: number;
  dominantStrategy: string;
  isStable: boolean;
  deviationIncentive: number;
}

export interface StakingAnalysis {
  bestStrategy: string;
  interpretation: string;
  recommendation: string;
  stakingBreakevenPriceDrop: number;
}

export interface GovernanceParticipation {
  rationalParticipants: number;
  totalHolders: number;
  participationRate: number;
  participatingPower: number;
  quorumAchievable: boolean;
}

export interface VoterApathy {
  apatheticRatio: number;
  riskLevel: string;
  interpretation: string;
}

export interface CoordinationGameAnalysis {
  gameType: string;
  description: string;
  equilibrium: string;
  cooperationProbability: number;
}

export interface GameTheoryResult {
  strategies: Record<string, StrategyMetrics>;
  equilibrium: StakingEquilibrium;
  analysis: StakingAnalysis;
  governanceParticipation: GovernanceParticipation;
  voterApathy: VoterApathy;
  minCoalitionSize: number;
  minCoalitionPower: number;
  coordination: CoordinationGameAnalysis;
  cooperationSustainable: boolean;
  healthScore: number;
  primaryRisk: string;
  recommendations: string[];
}

export interface TokenMetricsResult {
  velocity: TokenVelocityResult;
  realYield: RealYieldResult;
  valueAccrual: ValueAccrualResult;
  overallHealth: number;
  // New 2025 Compliance Metrics
  gini?: GiniResult;
  runway?: RunwayResult;
  inflation?: InflationResult;
  whaleAnalysis?: WhaleAnalysisResult;
  attackAnalysis?: AttackAnalysisResult;
  liquidityFarming?: LiquidityFarmingResult;
  gameTheory?: GameTheoryResult;
}

// === MARKET CYCLE TYPES (November 2025) ===

export interface MarketCycleYearConfig {
  year: number;
  phase: string;
  growthMultiplier: number;
  retentionMultiplier: number;
  priceMultiplier: number;
  description: string;
}

export type MarketCycle2025_2030 = Record<number, MarketCycleYearConfig>;

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

// NEW-LOW-002 FIX: Staking tier type definitions
export type StakingTierKey = 'bronze' | 'silver' | 'gold' | 'platinum';
export type StakingTierDistribution = Record<StakingTierKey, number>;

// Governance tier type definitions
export type GovernanceTierKey = 'community' | 'delegate' | 'council';
export type GovernanceTierDistribution = Record<GovernanceTierKey, number>;

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
  adFillRate: number;              // MED-FE-001 FIX: Renamed from adCPMMultiplier (% of ad slots filled)
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
  // MED-03 FIX: Configurable liquidity pool distribution
  liquidityPoolUsdcPercent?: number;  // % in VCoin/USDC pool (default 40%)
  liquidityPoolSolPercent?: number;   // % in VCoin/SOL pool (default 35%)
  liquidityPoolUsdtPercent?: number;  // % in VCoin/USDT pool (default 25%)
  // HIGH-FE-001 FIX: CLMM capital efficiency factor
  clmmConcentrationFactor?: number;   // CLMM concentration factor (default 4.0, range 2-10)
  
  // Staking Parameters (NEW - Nov 2025)
  stakingApy?: number;
  stakingParticipationRate?: number;  // NEW: % of users who stake (affects Value Accrual)
  avgStakeAmount?: number;             // NEW: Average stake per staker in VCoin
  stakerFeeDiscount?: number;
  minStakeAmount?: number;
  stakeLockDays?: number;
  stakingProtocolFee?: number;
  
  // Governance Parameters (NEW - Nov 2025)
  governanceProposalFee?: number;
  governanceBadgePrice?: number;
  governancePremiumFee?: number;
  governanceMinVevcoinToVote?: number;
  governanceMinVevcoinToPropose?: number;
  governanceVotingPeriodDays?: number;
  // Governance participation (affects Value Accrual)
  governanceParticipationRate?: number;  // % of stakers who actively vote
  governanceDelegationRate?: number;     // % of non-voters who delegate
  governanceAvgLockWeeks?: number;       // Average veVCoin lock duration
  governanceProposalsPerMonth?: number;  // Expected proposals per month
  
  // Creator Economy Parameters (NEW - Nov 2025)
  // Dynamic Boost Post Fee - scales based on users and token price
  boostPostTargetUsd?: number;
  boostPostMinUsd?: number;
  boostPostMaxUsd?: number;
  boostPostScaleUsers?: number;
  // Other premium features
  premiumDmFeeVcoin?: number;
  premiumReactionFeeVcoin?: number;
  
  // Module toggles - Core modules (default enabled)
  enableIdentity?: boolean;
  enableContent?: boolean;
  enableRewards?: boolean;
  enableStaking?: boolean;
  enableLiquidity?: boolean;
  enableGovernance?: boolean;
  // Optional modules
  enableAdvertising: boolean;
  enableExchange: boolean;
  enableNft?: boolean;             // NFT enabled by default
  // Future modules are toggled via their nested parameter objects
  enableVchain?: boolean;
  enableMarketplace?: boolean;
  enableBusinessHub?: boolean;
  enableCrossPlatform?: boolean;
  
  // Future Module Parameters (NEW - Nov 2025)
  vchain?: VChainParameters;
  marketplace?: MarketplaceParameters;
  businessHub?: BusinessHubParameters;
  crossPlatform?: CrossPlatformParameters;
  
  // Pre-Launch Module Parameters (NEW - Nov 2025)
  referral?: ReferralParameters;
  points?: PointsParameters;
  gasless?: GaslessParameters;
  
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
  nftMintFeeVcoin: number;
  nftMintPercentage?: number;      // NEW - Issue #12
  premiumContentVolumeVcoin: number;
  contentSaleVolumeVcoin: number;
  contentSaleCommission: number;
  
  // Advertising Module pricing (USD) - Issue #7
  bannerCPM: number;
  videoCPM: number;
  promotedPostFee: number;
  campaignManagementFee: number;
  adAnalyticsFee: number;
  
  // Exchange/Wallet Module - Issue #4
  exchangeSwapFeePercent: number;
  exchangeWithdrawalFee: number;
  exchangeUserAdoptionRate: number;
  exchangeAvgMonthlyVolume: number;
  exchangeWithdrawalsPerUser: number;
  // MED-04 FIX: Configurable average swap size
  exchangeAvgSwapSize?: number;  // Average swap size in USD (default $30)
  
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

// === MODULE BREAKDOWN TYPES (NEW-HIGH-002 FIX) ===

// Secondary AMM pool info for exchange module
export interface SecondaryAmmInfo {
  name: string;
  share: number;
  fee: number;
}

// Typed breakdown for Exchange module
export interface ExchangeBreakdown {
  swapFeeRevenue: number;
  withdrawalFeeRevenue: number;
  totalTradingVolume: number;
  totalWithdrawals: number;
  activeExchangeUsers: number;
  infrastructureCost: number;
  blockchainCosts: number;
  liquidityCosts: number;
  isLossLeader?: boolean;
  strategicNote?: string;
  // Solana-specific fields
  network?: string;
  dexAggregator?: string;
  totalSolanaTxs?: number;
  totalSolanaFeesUsd?: number;
  solanaSavings?: number;
  secondaryAmms?: SecondaryAmmInfo[];
}

// Module Results
export interface ModuleResult {
  revenue: number;
  costs: number;
  profit: number;
  margin: number;
  breakdown: Record<string, unknown>;  // Updated to allow nested objects
}

// Typed Exchange Module Result
export interface ExchangeModuleResult extends Omit<ModuleResult, 'breakdown'> {
  breakdown: ExchangeBreakdown;
}

// Recapture Results
export interface RecaptureResult {
  totalRecaptured: number;
  recaptureRate: number;
  burns: number;  // VCoin burned from collected fees
  treasury: number;  // VCoin accumulated in treasury
  staking: number;  // VCoin locked in staking
  buybacks: number;  // VCoin acquired via buybacks (bought from market with revenue)
  buybackUsdSpent: number;  // USD spent on buybacks from protocol revenue
  totalRevenueSourceVcoin: number;
  totalTransactionFeesUsd: number;
  totalRoyaltiesUsd: number;
  // Effective vs Configured Burn Rate (NEW - Audit Fix CRIT-FE-002)
  effectiveBurnRate?: number;  // Actual burn rate after token velocity adjustment
  configuredBurnRate?: number; // User-configured burn rate
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
  
  // Early unstake tracking (NEW - Audit Fix)
  earlyUnstakeRate?: number;
  earlyUnstakePenaltyRate?: number;
  earlyUnstakersCount?: number;
  expectedEarlyUnstakeRewardLoss?: number;
  
  // Reward funding source (NEW - Audit Fix WP-005 & MED-002)
  rewardFundingSource?: string;
  rewardFundingDetails?: string;
  rewardsExceedModuleIncome?: boolean;
  sustainabilityWarning?: string | null;
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
// === PRE-LAUNCH MODULE TYPES (Nov 2025) ===

export interface ReferralResult {
  totalUsers: number;
  usersWithReferrals: number;
  totalReferrals: number;
  qualifiedReferrals: number;
  referrersByTier: Record<string, number>;
  referralsByTier: Record<string, number>;
  bonusDistributedVcoin: number;
  bonusDistributedUsd: number;
  avgBonusPerReferrerVcoin: number;
  viralCoefficient: number;
  effectiveReferralRate: number;
  qualificationRate: number;
  monthlyReferralCostVcoin: number;
  monthlyReferralCostUsd: number;
  suspectedSybilReferrals: number;
  sybilRejectionRate: number;
  breakdown: Record<string, unknown>;
}

export interface PointsResult {
  pointsPoolTokens: number;
  pointsPoolPercent: number;
  waitlistUsers: number;
  participatingUsers: number;
  participationRate: number;
  totalPointsDistributed: number;
  avgPointsPerUser: number;
  medianPointsEstimate: number;
  tokensPerPoint: number;
  avgTokensPerUser: number;
  usersBySegment: Record<string, number>;
  pointsBySegment: Record<string, number>;
  tokensBySegment: Record<string, number>;
  suspectedSybilUsers: number;
  sybilRejectionRate: number;
  pointsRejected: number;
  pointsByActivity: Record<string, number>;
  top1PercentTokens: number;
  top10PercentTokens: number;
  bottom50PercentTokens: number;
  breakdown: Record<string, unknown>;
}

export interface GaslessResult {
  totalUsers: number;
  newUsers: number;
  verifiedUsers: number;
  premiumUsers: number;
  enterpriseUsers: number;
  totalSponsoredTransactions: number;
  avgTransactionsPerUser: number;
  baseFeeCostUsd: number;
  priorityFeeCostUsd: number;
  accountCreationCostUsd: number;
  totalSponsorshipCostUsd: number;
  newUserCostUsd: number;
  verifiedUserCostUsd: number;
  premiumUserCostUsd: number;
  enterpriseUserCostUsd: number;
  avgCostPerUserUsd: number;
  costPerTransactionUsd: number;
  monthlySponsorshipBudgetUsd: number;
  budgetUtilization: number;
  sponsorshipCostVcoin: number;
  breakdown: Record<string, unknown>;
}

export interface PreLaunchResult {
  referral?: ReferralResult;
  points?: PointsResult;
  gasless?: GaslessResult;
  totalPrelaunchCostUsd: number;
  totalPrelaunchCostVcoin: number;
  pointsTokensAllocated: number;
  referralBonusDistributed: number;
  referralUsersAcquired: number;
  waitlistConversionTokens: number;
}

// Pre-Launch Parameters
export interface ReferralParameters {
  enableReferral: boolean;
  qualificationRate: number;
  activeReferrerRate: number;
  sybilRejectionRate: number;
  starterBonusVcoin: number;
  builderBonusVcoin: number;
  ambassadorBonusVcoin: number;
  qualificationDays: number;
  minPostsRequired: number;
}

export interface PointsParameters {
  enablePoints: boolean;
  pointsPoolTokens: number;
  participationRate: number;
  sybilRejectionRate: number;
  waitlistSignupPoints: number;
  socialFollowPoints: number;
  dailyCheckinPoints: number;
  inviteJoinPoints: number;
  inviteVerifyPoints: number;
  betaTestingPoints: number;
}

export interface GaslessParameters {
  enableGasless: boolean;
  newUserFreeTransactions: number;
  verifiedUserMonthlyTransactions: number;
  premiumUnlimited: boolean;
  monthlySponsorshipBudgetUsd: number;
  baseTransactionCostUsd: number;
  priorityFeeUsd: number;
  accountCreationCostUsd: number;
  newUserRate: number;
}

// Starting Users Summary - Dec 2025
// Shows clearly where starting users come from
export interface StartingUsersSummary {
  totalActiveUsers: number;
  userSource: 'manual_input' | 'marketing_budget' | 'growth_scenario';
  manualStartingUsers?: number | null;
  marketingBudgetUsd?: number | null;
  acquiredFromMarketing?: number | null;
  highQualityCreators: number;
  midLevelCreators: number;
  northAmericaConsumers: number;
  globalLowIncomeConsumers: number;
  retentionApplied: boolean;
  usersBeforeRetention?: number | null;
  usersAfterRetention?: number | null;
  retentionRate?: number | null;
}

export interface SimulationResult {
  // Starting users summary at the top for easy reference (Dec 2025)
  startingUsersSummary?: StartingUsersSummary;
  identity: ModuleResult;
  content: ModuleResult;
  advertising: ModuleResult;
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
  governance?: GovernanceResult;
  vchain?: VChainResult;
  marketplace?: MarketplaceResult;
  businessHub?: BusinessHubResult;
  crossPlatform?: CrossPlatformResult;
  tokenMetrics?: TokenMetricsResult;
  // Pre-Launch Modules (Nov 2025)
  prelaunch?: PreLaunchResult;
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
  advertisingRevenue: number;
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
