import { 
  SimulationParameters, 
  Preset, 
  GrowthScenarioConfig, 
  MarketConditionConfig, 
  FomoEvent, 
  GrowthScenario, 
  MarketCondition,
  MarketCycleYearConfig,
  MarketCycle2025_2030,
} from '@/types/simulation';

/**
 * Default parameters updated with 2024-2025 industry benchmarks.
 * 
 * === SOLANA NETWORK INTEGRATION (November 2025) ===
 * All blockchain operations built on Solana mainnet-beta:
 * - Ultra-low transaction fees: ~$0.00025 per transaction
 * - High throughput: 4,000+ sustained TPS
 * - Fast finality: ~400ms block time
 * - SPL Token standard for VCoin
 * - DEX integration via Jupiter aggregator
 * 
 * Solana DEX Ecosystem:
 * - Jupiter: Aggregates 20+ DEXs for best prices
 * - Raydium: Concentrated Liquidity (CLMM) pools
 * - Orca Whirlpools: High-efficiency CLMM
 * - Meteora: Dynamic fee pools
 * - Phoenix: Order book DEX
 * 
 * Key changes from audit fixes:
 * - Issue #1: Added retention model (apply_retention, retention params)
 * - Issue #2: Realistic CAC ($75 NA, $25 Global, $8K HQ Creator)
 * - Issue #3: Realistic conversion rate (1.5% vs 4%)
 * - Issue #4: Realistic exchange metrics (10% adoption on Solana, $150 volume)
 * - Issue #5: Sustainable token economics (5% burn, 3% buyback)
 * - Issue #7: Platform maturity-adjusted CPM rates
 * - Issue #8: Realistic posts per user (0.6 average, only 10% are creators)
 * - Issue #11: Realistic profile sales (1/month, $25 avg)
 * - Issue #12: NFT mints reduced to 0.1%
 * - Issue #13: Compliance costs included
 * 
 * Nov 2025 Updates:
 * - Full Solana integration with Jupiter/Raydium/Orca
 * - Added Liquidity parameters for Solana DEXs (70%+ health target)
 * - Added Staking parameters for SPL staking (10% APY)
 * - Added Creator Economy (boost posts, premium DM)
 * - Updated burn/buyback rates for 25-35% recapture target
 */
export const DEFAULT_PARAMETERS: SimulationParameters = {
  // Platform Maturity (NEW)
  platformMaturity: 'launch',
  autoAdjustForMaturity: true,
  
  // Retention Model (NEW - Issue #1)
  applyRetention: true,
  retentionModelType: 'social_app',
  platformAgeMonths: 6,
  
  // Compliance Costs (NEW - Issue #13)
  includeComplianceCosts: false,  // Enable for realistic projections
  
  // Growth Scenario Settings (NEW - Nov 2025)
  // Note: Starting users are calculated from marketing budget, not a separate input
  growthScenario: 'base',
  marketCondition: 'neutral',
  enableFomoEvents: true,
  useGrowthScenarios: true,
  startingWaitlistUsers: 1000,     // Issue #4 Fix: Waitlist users for pre-launch simulation
  
  // Token Allocation / Vesting (NEW - Nov 2025)
  trackVestingSchedule: true,         // Track full 60-month vesting
  treasuryRevenueShare: 0.20,         // 20% of revenue to treasury
  
  // Core parameters
  tokenPrice: 0.03,
  marketingBudget: 150000,
  startingUsers: 0,
  
  // User acquisition (Issue #2 - Realistic CAC)
  northAmericaBudgetPercent: 0.35,
  globalLowIncomeBudgetPercent: 0.65,
  cacNorthAmericaConsumer: 75,      // Was $50, now $75
  cacGlobalLowIncomeConsumer: 25,   // Was $12, now $25
  highQualityCreatorCAC: 3000,      // High-quality creator CAC
  midLevelCreatorCAC: 500,          // Mid-level creator CAC
  highQualityCreatorsNeeded: 5,     // Number of HQ creators
  midLevelCreatorsNeeded: 15,       // Number of mid-level creators
  
  // Economic parameters (Updated Nov 2025)
  burnRate: 0.10,                   // 10% burn rate for recapture
  buybackPercent: 0.10,             // 10% buyback for recapture
  verificationRate: 0.02,           // Updated: 1.5% -> 2% (better product)
  postsPerUser: 9.7,                // Posts per user per month
  creatorPercentage: 0.15,          // Updated: 10% -> 15% (creator-focused)
  postsPerCreator: 6,               // NEW: 6 posts per creator (Issue #8)
  adFillRate: 0.20,                 // MED-FE-001 FIX: Renamed from adCPMMultiplier (20% fill rate for launch)
  rewardAllocationPercent: 0.08,
  
  // Dynamic Reward Allocation (NEW - Nov 2025)
  enableDynamicAllocation: true,    // Enable by default for realistic scaling
  initialUsersForAllocation: 1000,  // Starting point for allocation scaling
  targetUsersForMaxAllocation: 100000000, // User count for max allocation (100M)
  maxPerUserMonthlyUsd: 50.0,       // $50 max per-user reward (inflation guard)
  minPerUserMonthlyUsd: 0.10,       // $0.10 min per-user reward
  
  // Liquidity Parameters (NEW - Nov 2025)
  initialLiquidityUsd: 500000,      // $500K recommended for 70%+ health
  protocolOwnedLiquidity: 0.70,     // 70% POL target
  liquidityLockMonths: 24,          // 2 year lock
  targetLiquidityRatio: 0.15,       // 15%+ for health
  // MED-03: Configurable pool distribution
  liquidityPoolUsdcPercent: 0.40,   // 40% in VCoin/USDC
  liquidityPoolSolPercent: 0.35,    // 35% in VCoin/SOL
  liquidityPoolUsdtPercent: 0.25,   // 25% in VCoin/USDT
  // HIGH-FE-001: CLMM concentration factor for effective liquidity
  clmmConcentrationFactor: 4.0,     // 4x capital efficiency (range 2-10)
  
  // Staking Parameters (NEW - Nov 2025)
  // 
  // NEW-CALC-002 Documentation: Staking Ratio vs Participation Rate
  // --------------------------------------------------------------------
  // The Value Accrual score uses stakingParticipationRate (% of users who stake)
  // instead of raw stakingRatio (staked_tokens / circulating_supply).
  // 
  // Rationale:
  // 1. With 100M+ circulating supply, raw staking ratio is always tiny (<1%)
  //    which would unfairly penalize the Value Accrual score
  // 2. Participation rate (15-60% of users staking) better reflects platform
  //    success in encouraging token lockup behavior
  // 3. This is a user-configurable parameter for scenario modeling
  // 
  // The APY boost further adjusts the effective ratio for scoring:
  // - Higher APY (>10%) incentivizes more staking, boosting the ratio
  // - Lower APY (<10%) reduces staking attractiveness, reducing the ratio
  //
  stakingApy: 0.10,                 // 10% APY
  stakingParticipationRate: 0.10,   // 10% of users stake
  avgStakeAmount: 20000,            // Average 20,000 VCoin per staker
  stakerFeeDiscount: 0.10,          // 10% fee discount
  minStakeAmount: 1000,             // 1,000 VCoin minimum
  stakeLockDays: 180,               // 180 day lock (6 months)
  
  // Game Theory Parameters (Issue #5, #6 Fix)
  lockPeriodMonths: 3,              // Lock period for staking (3 months)
  earlyUnstakePenalty: 0.10,        // 10% penalty for early unstaking
  
  // Module toggles
  enableAdvertising: true,          // Advertising enabled by default
  enableExchange: true,
  enableNft: true,                  // NFT enabled by default
  
  // Future Modules (disabled by default)
  enableVchain: false,
  enableMarketplace: false,
  enableBusinessHub: false,
  enableCrossPlatform: false,
  
  // Identity Module pricing (USD)
  basicPrice: 0,
  verifiedPrice: 4,
  premiumPrice: 12,
  enterprisePrice: 59,
  transferFee: 2,
  saleCommission: 0.10,
  monthlySales: 1,                  // Was 8, now 1 (Issue #11)
  avgProfilePrice: 25,              // NEW: Was $100, now $25 (Issue #11)
  
  // Content Module pricing (VCoin) - Updated Nov 2025
  nftMintFeeVcoin: 50,              // Updated: 25 -> 50 for better recapture
  nftMintPercentage: 0.005,         // Updated: 0.5% (was 0.1%, increased for visible revenue)
  premiumContentVolumeVcoin: 1000,  // Increased for better revenue
  contentSaleVolumeVcoin: 500,      // Increased for better revenue
  // NOTE: contentSaleCommission removed - Content module is break-even by design
  
  // Advertising Module pricing (USD) - Updated Nov 2025
  bannerCPM: 0.50,                  // Updated: $0.50 (viable launch)
  videoCPM: 2.00,                   // Updated: $2.00 (viable launch)
  promotedPostFee: 1.00,
  campaignManagementFee: 20,
  adAnalyticsFee: 15,
  
  // Exchange/Wallet Module - Updated Nov 2025
  exchangeSwapFeePercent: 0.005,    // 0.5% swap fee (industry standard)
  exchangeWithdrawalFee: 1.50,
  exchangeUserAdoptionRate: 0.10,   // 10% for token platform
  exchangeAvgMonthlyVolume: 150,    // $150 avg volume
  exchangeWithdrawalsPerUser: 0.5,  // 0.5 withdrawals/user
  exchangeAvgSwapSize: 30,          // MED-04: $30 avg swap size
  
  // Reward Distribution
  textPostPoints: 3,
  imagePostPoints: 6,
  audioPostPoints: 10,
  shortVideoPoints: 15,
  postVideosPoints: 25,
  musicPoints: 20,
  podcastPoints: 30,
  audioBookPoints: 45,
  likePoints: 0.2,
  commentPoints: 2,
  sharePoints: 3,
  followPoints: 0.5,
  maxPostsPerDay: 15,
  maxLikesPerDay: 50,
  maxCommentsPerDay: 30,
  highQualityMultiplier: 1.5,
  verifiedMultiplier: 1.15,
  premiumMultiplier: 1.3,
  day7Decay: 40,
  day30Decay: 8,
  maxDailyRewardUSD: 15,
};

/**
 * Platform maturity presets - auto-adjust key parameters
 * Nov 2025: Made launch settings viable for profitability
 */
export const MATURITY_ADJUSTMENTS = {
  launch: {
    cacMultiplier: 1.3,
    conversionRate: 0.015,
    adFillRate: 0.20,
    bannerCpm: 0.50,
    videoCpm: 2.00,
    profileSalesMonthly: 1,
    avgProfilePrice: 20,
    nftPercentage: 0.001,
    creatorPercentage: 0.12,
  },
  growing: {
    cacMultiplier: 1.15,
    conversionRate: 0.025,
    adFillRate: 0.40,
    bannerCpm: 3.00,
    videoCpm: 10.00,
    profileSalesMonthly: 8,
    avgProfilePrice: 60,
    nftPercentage: 0.005,
    creatorPercentage: 0.15,
  },
  established: {
    cacMultiplier: 1.0,
    conversionRate: 0.04,
    adFillRate: 0.70,
    bannerCpm: 8.00,
    videoCpm: 25.00,
    profileSalesMonthly: 20,
    avgProfilePrice: 100,
    nftPercentage: 0.01,
    creatorPercentage: 0.18,
  },
};

export const PRESETS: Preset[] = [
  {
    name: 'conservative',
    label: 'Lean Bootstrap ($50K/yr)',
    icon: '🌱',
    description: 'Conservative growth with minimal spend, realistic for seed stage',
    parameters: {
      tokenPrice: 0.03,
      marketingBudget: 50000,
      platformMaturity: 'launch',
      northAmericaBudgetPercent: 0.30,
      globalLowIncomeBudgetPercent: 0.70,
      cacNorthAmericaConsumer: 80,
      cacGlobalLowIncomeConsumer: 30,
      highQualityCreatorCAC: 5000,
      highQualityCreatorsNeeded: 2,
      midLevelCreatorCAC: 1000,
      midLevelCreatorsNeeded: 10,
      burnRate: 0.02,
      buybackPercent: 0.01,
      verificationRate: 0.01,
      postsPerUser: 0.4,
      adFillRate: 0.15,                // Increased from 0.08 to show ad revenue
      rewardAllocationPercent: 0.06,
      nftMintFeeVcoin: 25,
      nftMintPercentage: 0.005,        // 0.5% NFT mints (increased from 0.1%)
      premiumContentVolumeVcoin: 200,
      contentSaleVolumeVcoin: 100,
      // Module toggles (explicit)
      enableAdvertising: false,
      enableExchange: true,
      enableNft: true,
      // Ad rates for lean scenario
      bannerCPM: 0.50,
      videoCPM: 2.00,
    },
  },
  {
    name: 'base',
    label: 'Base Case ($150K/yr)',
    icon: '⚖️',
    description: 'Balanced growth strategy for Series A',
    parameters: {
      ...DEFAULT_PARAMETERS,
      // Ensure NFT produces visible revenue when enabled
      nftMintPercentage: 0.005,        // 0.5% NFT mints (increased from 0.1%)
    },
  },
  {
    name: 'aggressive',
    label: 'Growth Phase ($250K/yr)',
    icon: '🚀',
    description: 'Aggressive acquisition for established platform',
    parameters: {
      tokenPrice: 0.03,
      marketingBudget: 250000,
      platformMaturity: 'growing',
      northAmericaBudgetPercent: 0.40,
      globalLowIncomeBudgetPercent: 0.60,
      cacNorthAmericaConsumer: 70,
      cacGlobalLowIncomeConsumer: 22,
      highQualityCreatorCAC: 10000,
      highQualityCreatorsNeeded: 5,
      midLevelCreatorCAC: 2000,
      midLevelCreatorsNeeded: 25,
      burnRate: 0.04,
      buybackPercent: 0.03,
      verificationRate: 0.02,
      postsPerUser: 0.8,
      adFillRate: 0.35,                // Better fill rate for growing platform
      rewardAllocationPercent: 0.10,
      bannerCPM: 2.00,
      videoCPM: 6.00,
      nftMintFeeVcoin: 30,
      nftMintPercentage: 0.01,         // 1% NFT mints for growing platform
      premiumContentVolumeVcoin: 1500,
      contentSaleVolumeVcoin: 800,
      verifiedPrice: 5,
      premiumPrice: 15,
      // Module toggles (explicit)
      enableAdvertising: true,         // Enabled for growth phase
      enableExchange: true,
      enableNft: true,                 // Enabled for growth phase
    },
  },
  {
    name: 'bull',
    label: 'Year 2+ Scale ($400K/yr)',
    icon: '📈',
    description: 'Established platform with strong brand',
    parameters: {
      tokenPrice: 0.06,
      marketingBudget: 400000,
      platformMaturity: 'established',
      northAmericaBudgetPercent: 0.45,
      globalLowIncomeBudgetPercent: 0.55,
      cacNorthAmericaConsumer: 60,
      cacGlobalLowIncomeConsumer: 20,
      highQualityCreatorCAC: 12000,
      highQualityCreatorsNeeded: 8,
      midLevelCreatorCAC: 2500,
      midLevelCreatorsNeeded: 40,
      burnRate: 0.05,
      buybackPercent: 0.04,
      verificationRate: 0.03,
      postsPerUser: 1.0,
      adFillRate: 0.60,                // 60% fill rate for established platform
      rewardAllocationPercent: 0.12,
      bannerCPM: 8.00,
      videoCPM: 25.00,
      nftMintFeeVcoin: 35,
      nftMintPercentage: 0.02,         // 2% NFT mints for established platform
      premiumContentVolumeVcoin: 5000,
      contentSaleVolumeVcoin: 3000,
      verifiedPrice: 5,
      premiumPrice: 15,
      monthlySales: 15,
      avgProfilePrice: 80,
      // Module toggles (all enabled for scale)
      enableAdvertising: true,
      enableExchange: true,
      enableNft: true,
    },
  },
];

// === TOKEN ALLOCATION (November 2025) ===
// Official VCoin tokenomics with 10 allocation categories
import type { TokenAllocationCategoryConfig } from '@/types/simulation';

export const TOKEN_ALLOCATION: Record<string, TokenAllocationCategoryConfig> = {
  SEED: {
    name: 'Seed Round',
    percent: 0.04,
    tokens: 40_000_000,
    tge_percent: 0.0,
    cliff_months: 12,
    vesting_months: 24,
    price_usd: 0.005,
    description: 'Early-stage investors (highest risk, lowest price)',
  },
  PRIVATE: {
    name: 'Private Round',
    percent: 0.04,
    tokens: 40_000_000,
    tge_percent: 0.10,
    cliff_months: 6,
    vesting_months: 18,
    price_usd: 0.007,
    description: 'Strategic investors and VCs',
  },
  PUBLIC: {
    name: 'Public Sale',
    percent: 0.08,
    tokens: 80_000_000,
    tge_percent: 0.50,
    cliff_months: 0,
    vesting_months: 3,
    price_usd: 0.010,
    description: 'Community token sale (IDO/ICO)',
  },
  TEAM: {
    name: 'Team',
    percent: 0.15,
    tokens: 150_000_000,
    tge_percent: 0.0,
    cliff_months: 12,
    vesting_months: 36,
    price_usd: 0.03,
    description: 'Core team members and employees',
  },
  ADVISORS: {
    name: 'Advisors',
    percent: 0.03,
    tokens: 30_000_000,
    tge_percent: 0.0,
    cliff_months: 6,
    vesting_months: 18,
    price_usd: 0.03,
    description: 'Strategic advisors and consultants',
  },
  TREASURY: {
    name: 'Treasury/DAO',
    percent: 0.20,
    tokens: 200_000_000,
    tge_percent: 0.0,
    is_programmatic: true,
    description: 'Protocol treasury and governance',
  },
  REWARDS: {
    name: 'Ecosystem & Rewards',
    percent: 0.35,
    tokens: 350_000_000,
    tge_percent: 0.0,
    is_programmatic: true,
    emission_months: 60,
    description: 'User incentives, staking rewards, grants',
  },
  LIQUIDITY: {
    name: 'Liquidity',
    percent: 0.05,
    tokens: 50_000_000,
    tge_percent: 1.0,
    description: 'DEX/CEX liquidity pools (locked 12 months)',
  },
  MARKETING: {
    name: 'Marketing & Growth',
    percent: 0.06,
    tokens: 60_000_000,
    tge_percent: 0.25,
    cliff_months: 3,
    vesting_months: 18,
    price_usd: 0.03,
    description: 'Marketing campaigns and partnerships',
  },
};

// TGE Circulating Supply Breakdown (December 2025 - WhitePaper v1.4)
// TGE includes first month ecosystem distribution per tokenomics tool
export const TGE_BREAKDOWN = {
  SEED: 0,                 // 0% TGE (4% allocation, 40M tokens)
  PRIVATE: 4_000_000,      // 10% of 40M
  PUBLIC: 40_000_000,      // 50% of 80M
  TEAM: 0,                 // 0% TGE (15% allocation, 150M tokens)
  ADVISORS: 0,             // 0% TGE (3% allocation, 30M tokens)
  TREASURY: 0,             // Governance-controlled (20% allocation, 200M tokens)
  REWARDS: 5_833_333,      // 1st month ecosystem (350M / 60 months)
  LIQUIDITY: 50_000_000,   // 100% at TGE (5% allocation, 50M tokens, locked 12mo)
  MARKETING: 15_000_000,   // 25% of 60M
  TOTAL: 114_833_333,      // 4M + 40M + 50M + 15M + 5.83M = 114.83M (11.48%)
};

// Configuration constants (December 2025 - WhitePaper v1.4)
export const CONFIG = {
  SUPPLY: {
    TOTAL: 1_000_000_000,
    TGE_CIRCULATING: 114_833_333,  // Includes 1st month ecosystem distribution
    LIQUIDITY: 50_000_000,  // 5% allocation (50M tokens), locked 12 months
    REWARDS_ALLOCATION: 350_000_000,  // 35% - dynamic allocation capped at max schedule
    REWARDS_DURATION_MONTHS: 60,  // 5 years
    TREASURY_ALLOCATION: 200_000_000,  // 20% - governance-controlled
  },
  
  // Monthly emission from rewards pool (350M / 60 months)
  MONTHLY_EMISSION: 5_833_333,
  
  // Treasury revenue share (percentage of platform revenue going to treasury)
  TREASURY_REVENUE_SHARE: 0.20,  // 20% of revenue to treasury
  
  FEE_DISTRIBUTION: {
    BURN: 0.20,
    TREASURY: 0.50,
    REWARDS: 0.30,
  },
  
  FEE_COLLECTION_RATE: 0.10,
  
  // === SOLANA NETWORK CONFIGURATION (November 2025) ===
  SOLANA: {
    // Network info
    NETWORK: 'mainnet-beta',
    CLUSTER_URL: 'https://api.mainnet-beta.solana.com',
    
    // Transaction costs (in USD at ~$50 SOL)
    BASE_TX_FEE_USD: 0.00025,
    PRIORITY_FEE_USD: 0.0001,
    TOKEN_ACCOUNT_RENT_USD: 0.10,
    
    // Performance
    BLOCK_TIME_MS: 400,
    FINALITY_SLOTS: 32,
    SUSTAINED_TPS: 4000,
    
    // Token program
    TOKEN_PROGRAM: 'spl-token',
    TOKEN_STANDARD: 'SPL Token',
  },
  
  // === SOLANA DEX CONFIGURATION ===
  SOLANA_DEX: {
    // Primary aggregator
    JUPITER: {
      PLATFORM_FEE: 0,  // Free to use
      API_URL: 'https://quote-api.jup.ag/v6',
      VERSION: 'v6',
    },
    
    // AMM pools
    RAYDIUM: {
      STANDARD_FEE: 0.0025,  // 0.25%
      CLMM_FEE_LOW: 0.0001,  // 0.01%
      CLMM_FEE_MEDIUM: 0.0005,  // 0.05%
      CLMM_FEE_HIGH: 0.0025,  // 0.25%
    },
    ORCA: {
      STANDARD_FEE: 0.003,  // 0.30%
      WHIRLPOOL_FEE: 0.0001,  // 0.01% minimum
    },
    METEORA: {
      DYNAMIC_FEE_MIN: 0.0001,  // 0.01%
      DYNAMIC_FEE_MAX: 0.01,  // 1%
    },
    
    // Slippage defaults
    DEFAULT_SLIPPAGE_BPS: 50,  // 0.5%
    MAX_SLIPPAGE_BPS: 300,  // 3%
  },
  
  // === SOLANA STAKING ===
  SOLANA_STAKING: {
    PROGRAM_TYPE: 'spl_token_staking',
    FRAMEWORK: 'anchor',
    STAKE_ACCOUNT_RENT_SOL: 0.00203928,
    EPOCH_DURATION_DAYS: 2,
    BLOCKS_PER_DAY: 216000,
    REWARD_FREQUENCY: 'per_block',
    INSTANT_UNSTAKE_PENALTY: 0.02,  // 2%
  },
  
  STAKING: {
    GENERAL_STAKING_CAP_PERCENT: 0.15,
    IDENTITY_PREMIUM_MULTIPLIER: 5,
    CONTENT_BOOST_MULTIPLIER: 3,
    ADVERTISING_CAMPAIGN_MULTIPLIER: 10,
    MESSAGING_PREMIUM_MULTIPLIER: 5,
    IDENTITY_CAP_PERCENT: 0.40,
  },
  
  SPECIAL_RECAPTURE: {
    FILE_FEES: 0.70,
  },
  
  MODULE_REVENUE_SHARE: {
    IDENTITY: 0.05,
    CONTENT: 0.40,
    REWARDS: 0.20,
    ADVERTISING: 0.15,
  },
  
  // Issue #5: More conservative caps
  ABSOLUTE_CAPS: {
    MAX_RECAPTURE_RATE: 0.80,       // Was 0.95
    MONTHLY_BURN_LIMIT: 0.05,       // Was 0.10
    MONTHLY_BUYBACK_LIMIT: 0.03,    // Was 0.05
    MONTHLY_STAKING_LIMIT: 0.10,    // Was 0.15
  },
  
  // Issue #12: NFT percentage balanced for visible revenue while realistic
  USER_DISTRIBUTION: {
    IDENTITY_TIERS: { BASIC: 0.00, VERIFIED: 0.75, PREMIUM: 0.20, ENTERPRISE: 0.05 },
    CONTENT_TYPES: { TEXT: 0.65, IMAGE: 0.30, VIDEO: 0.045, NFT: 0.005 },  // NFT: 0.5%
    COMMUNITY_SIZES: { SMALL: 0.50, MEDIUM: 0.30, LARGE: 0.15, ENTERPRISE: 0.05 },
    AD_FORMATS: { BANNER: 0.70, VIDEO: 0.30 },
  },
  
  // Issue #17: Documented activity rates
  ACTIVITY_RATES: {
    PROFILE_TRANSFERS: 0.02,
    PREMIUM_SUBSCRIBERS: 0.015,
    CREATOR_PERCENTAGE: 0.10,
    POSTS_PER_CREATOR: 6,
    BOOSTED_POSTS: 0.05,
    PROMOTED_POSTS: 0.03,
    ADVERTISERS: 0.005,
    AD_ANALYTICS_SUBSCRIBERS: 0.10,
    ADS_PER_USER: 30,
    EXCHANGE_ADOPTION: 0.05,
  },
  
  // Issue #9: Cost scaling (updated Nov 2025 - Solana network optimization)
  // Solana advantages: ~$0.00025/tx, free RPC tiers, no gas volatility
  COST_SCALING: {
    IDENTITY: { BASE: 10, PER_USER: 0.01, THRESHOLD: 100, SOLANA_TX: 0.00025 },
    CONTENT: { BASE: 20, PER_USER: 0.02, THRESHOLD: 100, PER_POST: 0.002, SOLANA_TX: 0.00025 },
    ADVERTISING: { BASE: 5, PER_USER: 0.005, THRESHOLD: 100, SOLANA_TX: 0.00025 },
    REWARDS: { BASE: 10, PER_USER: 0.003, THRESHOLD: 100, SOLANA_TX: 0.00025 },
    EXCHANGE: { BASE: 5, PER_USER: 0.01, THRESHOLD: 25, SOLANA_TX: 0.00025 },  // Jupiter DEX routing
  },
  
  // Issue #11: Realistic marketplace
  MARKETPLACE: {
    AVG_PROFILE_PRICE_USD: 25,
    AVG_NFT_PRICE_USD: 15,
  },
  
  CAPS: {
    ADVERTISING_BUYBACK: 0.80,
    ADVERTISING_DEPOSITS: 0.25,
    IDENTITY_STAKING: 0.40,
    CONTENT_STAKING: 0.40,
  },
  
  // Issue #13: Compliance cost defaults (scaled for early-stage)
  COMPLIANCE_DEFAULTS: {
    KYC_AML_MONTHLY: 500,
    LEGAL_MONTHLY: 1000,
    INSURANCE_MONTHLY: 500,
    AUDIT_QUARTERLY: 2500,
    GDPR_MONTHLY: 250,
  },
  
  // Retention curves (Issue #1)
  RETENTION_CURVES: {
    social_app: { 1: 0.25, 3: 0.12, 6: 0.08, 12: 0.04 },
    crypto_app: { 1: 0.20, 3: 0.08, 6: 0.05, 12: 0.025 },
    gaming: { 1: 0.30, 3: 0.12, 6: 0.06, 12: 0.03 },
    utility: { 1: 0.40, 3: 0.25, 6: 0.18, 12: 0.12 },
    vcoin: { 1: 0.22, 3: 0.10, 6: 0.06, 12: 0.03 },
  },
};

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8001';

// === GROWTH SCENARIO CONFIGURATIONS (November 2025) ===

/**
 * FOMO Events for each scenario
 * Based on research for March 2026 - March 2027 token launch window
 * 
 * LOW-FE-002 FIX: Documented magic numbers
 * 
 * @property {number} impactMultiplier - Multiplier applied to user growth during event
 *   - 1.0-1.5: Minor impact (feature launches, small milestones)
 *   - 1.5-2.5: Moderate impact (partnerships, exchange listings)
 *   - 2.5-5.0: Major impact (viral moments, tier-1 listings)
 *   - 5.0-12.0: Exceptional impact (TGE launch, major viral events)
 * 
 * @property {number} durationDays - Event duration, typically 14 days (2 weeks)
 *   - 14 days accounts for: initial hype (3-4 days), sustained attention (7 days),
 *     and gradual decline (3-4 days) based on typical crypto news cycles
 * 
 * @property {number} month - Month when event triggers (1-12)
 *   - TGE always month 1
 *   - Holiday events month 11 (Black Friday/Cyber Monday timing)
 *   - Major milestones strategically spaced for momentum
 */
export const FOMO_EVENTS: Record<GrowthScenario, FomoEvent[]> = {
  conservative: [
    { month: 1, eventType: 'tge_launch', impactMultiplier: 2.5, description: 'Token Generation Event - modest launch', durationDays: 14 },
    { month: 4, eventType: 'feature_launch', impactMultiplier: 1.3, description: 'V2 feature release', durationDays: 14 },
    { month: 8, eventType: 'partnership', impactMultiplier: 1.4, description: 'Partnership with niche platform', durationDays: 14 },
    { month: 11, eventType: 'holiday', impactMultiplier: 1.2, description: 'Holiday season marketing push', durationDays: 14 },
  ],
  base: [
    { month: 1, eventType: 'tge_launch', impactMultiplier: 5.0, description: 'Token Generation Event - strong launch', durationDays: 14 },
    { month: 2, eventType: 'influencer', impactMultiplier: 1.8, description: 'Mid-tier crypto influencer endorsements', durationDays: 14 },
    { month: 4, eventType: 'exchange_listing', impactMultiplier: 2.0, description: 'Tier-2 CEX listing', durationDays: 14 },
    { month: 6, eventType: 'milestone', impactMultiplier: 1.5, description: '10K active users milestone', durationDays: 14 },
    { month: 8, eventType: 'partnership', impactMultiplier: 1.6, description: 'Strategic Web3 partnership', durationDays: 14 },
    { month: 11, eventType: 'holiday', impactMultiplier: 1.4, description: 'Holiday campaign with bonus rewards', durationDays: 14 },
    { month: 12, eventType: 'feature_launch', impactMultiplier: 1.3, description: 'Major platform upgrade', durationDays: 14 },
  ],
  bullish: [
    { month: 1, eventType: 'tge_launch', impactMultiplier: 12.0, description: 'Viral Token Generation Event', durationDays: 14 },
    { month: 1, eventType: 'influencer', impactMultiplier: 3.0, description: 'Top-tier crypto influencer adoption', durationDays: 14 },
    { month: 2, eventType: 'viral_moment', impactMultiplier: 2.5, description: 'Viral content moment', durationDays: 14 },
    { month: 3, eventType: 'exchange_listing', impactMultiplier: 3.0, description: 'Tier-1 CEX listing (Binance/Coinbase)', durationDays: 14 },
    { month: 5, eventType: 'milestone', impactMultiplier: 2.0, description: '50K active users milestone', durationDays: 14 },
    { month: 6, eventType: 'partnership', impactMultiplier: 2.5, description: 'Major Web2 platform partnership', durationDays: 14 },
    { month: 8, eventType: 'feature_launch', impactMultiplier: 1.8, description: 'Revolutionary AI feature launch', durationDays: 14 },
    { month: 10, eventType: 'milestone', impactMultiplier: 1.6, description: '100K users milestone', durationDays: 14 },
    { month: 11, eventType: 'holiday', impactMultiplier: 1.5, description: 'Holiday season viral campaign', durationDays: 14 },
    { month: 12, eventType: 'exchange_listing', impactMultiplier: 2.0, description: 'Additional major exchange listings', durationDays: 14 },
  ],
};

/**
 * Growth Scenario Configurations
 * Based on research data for March 2026 - March 2027 token launch window:
 * - Bitcoin halving cycle (18 months post-halving)
 * - Global crypto users: 850M-1B projected
 * - Solana ecosystem growth
 * - SocialFi market trends
 */
export const GROWTH_SCENARIOS: Record<GrowthScenario, GrowthScenarioConfig> = {
  conservative: {
    name: 'Conservative',
    description: 'Cautious growth with focus on retention over acquisition. Assumes modest marketing budget, organic-first approach, and potential market headwinds.',
    waitlistConversionRate: 0.40,
    month1FomoMultiplier: 2.5,
    monthlyGrowthRates: [0.25, 0.10, 0.00, -0.05, -0.03, 0.02, 0.03, 0.05, 0.02, 0.01, 0.04, 0.03],
    month1Retention: 0.18,
    month3Retention: 0.08,
    month6Retention: 0.04,
    month12Retention: 0.02,
    viralCoefficient: 0.3,
    tokenPriceStart: 0.03,
    tokenPriceMonth6Multiplier: 0.66,
    tokenPriceEndMultiplier: 1.0,
    fomoEvents: FOMO_EVENTS.conservative,
    expectedMonth1Users: 3300,
    expectedMonth12Mau: 3000,
  },
  base: {
    name: 'Base',
    description: 'Balanced growth scenario based on comparable SocialFi launches. Assumes solid execution, reasonable marketing spend, and neutral-to-positive market conditions.',
    waitlistConversionRate: 0.50,
    month1FomoMultiplier: 5.0,
    monthlyGrowthRates: [0.40, 0.25, 0.15, 0.20, 0.10, 0.12, 0.08, 0.10, 0.06, 0.05, 0.08, 0.07],
    month1Retention: 0.22,
    month3Retention: 0.10,
    month6Retention: 0.06,
    month12Retention: 0.035,
    viralCoefficient: 0.5,
    tokenPriceStart: 0.03,
    tokenPriceMonth6Multiplier: 2.0,
    tokenPriceEndMultiplier: 3.5,
    fomoEvents: FOMO_EVENTS.base,
    expectedMonth1Users: 5800,
    expectedMonth12Mau: 14500,
  },
  bullish: {
    name: 'Bullish',
    description: 'Aggressive growth scenario assuming viral adoption, strong market conditions (bull market), major partnerships, and successful influencer campaigns.',
    waitlistConversionRate: 0.60,
    month1FomoMultiplier: 12.0,
    monthlyGrowthRates: [0.80, 0.50, 0.35, 0.25, 0.30, 0.25, 0.15, 0.18, 0.12, 0.15, 0.12, 0.18],
    month1Retention: 0.28,
    month3Retention: 0.15,
    month6Retention: 0.10,
    month12Retention: 0.06,
    viralCoefficient: 0.8,
    tokenPriceStart: 0.03,
    tokenPriceMonth6Multiplier: 4.0,
    tokenPriceEndMultiplier: 7.0,
    fomoEvents: FOMO_EVENTS.bullish,
    expectedMonth1Users: 12800,
    expectedMonth12Mau: 62500,
  },
};

/**
 * Market Condition Configurations
 * Affects growth rates, retention, and token price trajectories
 */
export const MARKET_CONDITIONS: Record<MarketCondition, MarketConditionConfig> = {
  bear: {
    name: 'Bear Market',
    description: 'Crypto winter conditions - reduced interest, lower liquidity, higher CAC, risk-off sentiment.',
    growthMultiplier: 0.6,
    retentionMultiplier: 0.8,
    priceMultiplier: 0.5,
    fomoMultiplier: 0.7,
    cacMultiplier: 1.5,
  },
  neutral: {
    name: 'Neutral Market',
    description: 'Sideways market - stable conditions, balanced interest, normal acquisition costs.',
    growthMultiplier: 1.0,
    retentionMultiplier: 1.0,
    priceMultiplier: 1.0,
    fomoMultiplier: 1.0,
    cacMultiplier: 1.0,
  },
  bull: {
    name: 'Bull Market',
    description: 'Crypto bull run - high interest, increased liquidity, lower CAC, risk-on sentiment, FOMO amplified.',
    growthMultiplier: 1.5,
    retentionMultiplier: 1.1,
    priceMultiplier: 2.0,
    fomoMultiplier: 1.5,
    cacMultiplier: 0.7,
  },
};

/**
 * Default growth scenario parameters
 * Note: Starting users come from marketing budget calculations
 */
export const DEFAULT_GROWTH_SCENARIO_PARAMS = {
  growthScenario: 'base' as GrowthScenario,
  marketCondition: 'neutral' as MarketCondition,
  enableFomoEvents: true,
  useGrowthScenarios: true,
};

/**
 * Growth scenario summary table for quick reference
 * Based on 1,000 waitlist users under Bull market conditions
 */
export const GROWTH_SCENARIO_SUMMARY = {
  conservative: {
    month1Users: '~3,300',
    month12Mau: '~3,000',
    tokenPriceChange: '0.66x → 1.0x',
    description: 'Slow, steady, retention-focused',
  },
  base: {
    month1Users: '~5,800',
    month12Mau: '~14,500',
    tokenPriceChange: '2x → 3.5x',
    description: 'Balanced SocialFi benchmark',
  },
  bullish: {
    month1Users: '~12,800',
    month12Mau: '~62,500',
    tokenPriceChange: '4x → 7x',
    description: 'Viral adoption, bull market',
  },
};

// === 5-YEAR MARKET CYCLE ANALYSIS (2025-2030) ===
/**
 * Bitcoin Halving April 2024 - Market cycle analysis for 2025-2030
 * Based on historical halving cycles and 2024-2025 market conditions
 */
export const MARKET_CYCLE_2025_2030: MarketCycle2025_2030 = {
  2025: {
    year: 2025,
    phase: 'Early Bull / Post-Halving Rally',
    growthMultiplier: 1.3,
    retentionMultiplier: 1.1,
    priceMultiplier: 1.5,
    description: 'Bitcoin halving (April 2024) effect in full swing. Increased crypto interest, new users entering market. Altcoin season typically begins 12-18 months post-halving.',
  },
  2026: {
    year: 2026,
    phase: 'Peak Bull / Altcoin Season',
    growthMultiplier: 1.6,
    retentionMultiplier: 1.15,
    priceMultiplier: 2.5,
    description: 'Peak of bull cycle expected. Maximum FOMO, highest valuations. Social tokens and SocialFi projects see maximum interest. Token launch timing optimal (March 2026 TGE).',
  },
  2027: {
    year: 2027,
    phase: 'Late Bull / Distribution',
    growthMultiplier: 1.2,
    retentionMultiplier: 1.0,
    priceMultiplier: 1.8,
    description: 'Distribution phase begins. Smart money taking profits. New user acquisition slows but platform maturity increases. Focus on retention and utility over speculation.',
  },
  2028: {
    year: 2028,
    phase: 'Bear / Accumulation',
    growthMultiplier: 0.7,
    retentionMultiplier: 0.85,
    priceMultiplier: 0.5,
    description: 'Next halving approaches (expected April 2028). Bear market conditions. CAC increases, retention becomes critical. Building phase - focus on product and community.',
  },
  2029: {
    year: 2029,
    phase: 'Recovery / New Cycle Begins',
    growthMultiplier: 1.1,
    retentionMultiplier: 1.0,
    priceMultiplier: 1.0,
    description: 'Post-halving recovery begins. Market sentiment improving. Platform is mature with established user base. Positioned for next growth cycle.',
  },
  2030: {
    year: 2030,
    phase: 'Early Bull / Mature Platform',
    growthMultiplier: 1.4,
    retentionMultiplier: 1.1,
    priceMultiplier: 1.5,
    description: 'New bull cycle in progress. Platform has 4+ years of operation. Established brand, lower CAC, high retention. Expansion into new markets and features.',
  },
};

// === FUTURE MODULE DEFAULT PARAMETERS (2026-2028) ===
/**
 * Default configurations for future modules
 * All disabled by default - enable individually when ready
 */
export const FUTURE_MODULE_DEFAULTS = {
  vchain: {
    enableVchain: false,
    vchainLaunchMonth: 24,
    vchainTxFeePercent: 0.002,
    vchainBridgeFeePercent: 0.001,
    vchainGasMarkupPercent: 0.08,
    vchainMonthlyTxVolumeUsd: 25_000_000,
    vchainMonthlyBridgeVolumeUsd: 50_000_000,
    vchainValidatorApy: 0.10,
    vchainMinValidatorStake: 100000,
    vchainValidatorCount: 100,
    vchainEnterpriseClients: 10,
    vchainAvgEnterpriseRevenue: 5000,
  },
  marketplace: {
    enableMarketplace: false,
    marketplaceLaunchMonth: 18,
    marketplacePhysicalCommission: 0.08,  // 8% (industry: 8-15%)
    marketplaceDigitalCommission: 0.15,   // 15% (industry: 15-30%)
    marketplaceNftCommission: 0.025,      // 2.5%
    marketplaceServiceCommission: 0.08,   // 8%
    marketplaceMonthlyGmvUsd: 5_000_000,
    marketplaceActiveSellers: 1000,
  },
  businessHub: {
    enableBusinessHub: false,
    businessHubLaunchMonth: 21,
    freelancerCommissionRate: 0.12,       // 12% (industry: 10-20%)
    freelancerMonthlyTransactionsUsd: 500_000,
    freelancerActiveCount: 5000,
    fundingPortalMonthlyVolume: 2_000_000,
    fundingPlatformFee: 0.04,             // 4%
  },
  crossPlatform: {
    enableCrossPlatform: false,
    crossPlatformLaunchMonth: 15,
    crossPlatformRentalCommission: 0.15,  // 15% (industry: 15-20%)
    crossPlatformMonthlyRentalVolume: 500_000,
    crossPlatformActiveRenters: 5000,
    crossPlatformActiveOwners: 1000,
  },
};

/**
 * Validated commission rates based on industry benchmarks
 * Source: Amazon, eBay, Upwork, Fiverr, App Store, Steam (Nov 2025)
 */
export const VALIDATED_COMMISSION_RATES = {
  // Marketplace
  physicalGoods: { min: 0.05, max: 0.15, default: 0.08, benchmark: 'Amazon 8-15%' },
  digitalGoods: { min: 0.08, max: 0.25, default: 0.15, benchmark: 'Steam/App Store 15-30%' },
  nftSales: { min: 0.01, max: 0.10, default: 0.025, benchmark: 'OpenSea 2.5%' },
  services: { min: 0.03, max: 0.15, default: 0.08, benchmark: 'Similar to physical goods' },
  
  // Freelancer
  freelancerEarnings: { min: 0.08, max: 0.20, default: 0.12, benchmark: 'Upwork 10-20%, Fiverr 20%' },
  
  // Cross-Platform
  accountRental: { min: 0.10, max: 0.25, default: 0.15, benchmark: 'Influencer platforms 15-20%' },
  contentLicensing: { min: 0.10, max: 0.30, default: 0.20, benchmark: 'Getty/Shutterstock 15-50%' },
};
