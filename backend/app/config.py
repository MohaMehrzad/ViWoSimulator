"""
Configuration constants matching the HTML CONFIG object.
These values ensure consistency between frontend and backend calculations.

Updated with 2024-2025 industry benchmarks and sources.
Addresses Issues #9 (cost scaling), #17 (documented activity rates).

=== SOLANA NETWORK INTEGRATION (November 2025) ===
All blockchain operations are built on Solana for:
- Ultra-low transaction costs (~$0.00025 per transaction)
- High throughput (65,000 TPS theoretical, 4,000+ sustained)
- Fast finality (~400ms block time)
- SPL Token standard for VCoin
- Native DEX integration (Jupiter, Raydium, Orca, Meteora)

Solana Network Stats (Nov 2025):
- Average transaction fee: 0.000005 SOL (~$0.00025 at $50 SOL)
- Priority fee (compute units): 0.00001-0.0001 SOL for congestion
- Rent-exempt minimum: 0.00089088 SOL for token accounts
- Block time: 400ms average
- Finality: 2-3 slots (~1 second)
"""

from dataclasses import dataclass
from typing import Dict


# === SOLANA NETWORK CONFIGURATION (November 2025) ===

@dataclass(frozen=True)
class SolanaNetworkConfig:
    """
    Solana network parameters as of November 2025.
    
    Sources:
    - https://solana.com/docs
    - https://explorer.solana.com
    - https://solscan.io/analytics
    """
    # Network identifiers
    NETWORK: str = "mainnet-beta"
    CLUSTER_URL: str = "https://api.mainnet-beta.solana.com"
    
    # Transaction costs (in SOL)
    BASE_TX_FEE_SOL: float = 0.000005  # 5,000 lamports base
    PRIORITY_FEE_SOL: float = 0.00001  # Average priority fee
    COMPUTE_UNIT_PRICE: int = 1000  # microlamports per compute unit
    
    # In USD (at $50 SOL price)
    SOL_PRICE_USD: float = 50.0
    BASE_TX_FEE_USD: float = 0.00025  # ~$0.00025 per transaction
    
    # Token Account costs
    TOKEN_ACCOUNT_RENT_SOL: float = 0.00203928  # Rent-exempt for SPL token account
    TOKEN_ACCOUNT_RENT_USD: float = 0.10  # ~$0.10 at $50 SOL
    
    # Block/Finality
    BLOCK_TIME_MS: int = 400  # Average block time
    SLOTS_PER_SECOND: float = 2.5
    FINALITY_SLOTS: int = 32  # For confirmed finality
    
    # Throughput
    MAX_TPS: int = 65000  # Theoretical maximum
    SUSTAINED_TPS: int = 4000  # Real-world sustained
    
    # SPL Token Program
    SPL_TOKEN_PROGRAM_ID: str = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
    SPL_TOKEN_2022_PROGRAM_ID: str = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"


@dataclass(frozen=True)
class SolanaDexConfig:
    """
    Solana DEX configurations for November 2025.
    
    Primary DEXs:
    - Jupiter: Aggregator (best prices)
    - Raydium: AMM with concentrated liquidity
    - Orca: AMM with Whirlpools (CLMM)
    - Meteora: Dynamic pools
    """
    # Jupiter Aggregator (primary routing)
    JUPITER_FEE_PERCENT: float = 0.0  # Free to use, no platform fee
    JUPITER_API_URL: str = "https://quote-api.jup.ag/v6"
    
    # Raydium
    RAYDIUM_SWAP_FEE: float = 0.0025  # 0.25% for standard pools
    RAYDIUM_CLMM_FEE: float = 0.0001  # 0.01% for concentrated liquidity
    
    # Orca
    ORCA_SWAP_FEE: float = 0.003  # 0.3% for standard pools
    ORCA_WHIRLPOOL_FEE: float = 0.0001  # 0.01% for Whirlpools
    
    # Meteora
    METEORA_DYNAMIC_FEE_MIN: float = 0.0001  # 0.01%
    METEORA_DYNAMIC_FEE_MAX: float = 0.01  # 1%
    
    # LP Fee tiers (common across DEXs)
    FEE_TIER_STABLE: float = 0.0001  # 0.01% - stablecoins
    FEE_TIER_STANDARD: float = 0.003  # 0.3% - standard pairs
    FEE_TIER_VOLATILE: float = 0.01  # 1% - volatile pairs
    
    # Slippage defaults
    DEFAULT_SLIPPAGE_BPS: int = 50  # 0.5% default slippage
    MAX_SLIPPAGE_BPS: int = 300  # 3% max slippage


@dataclass(frozen=True)
class SolanaStakingConfig:
    """
    Solana native staking and SPL staking pool configurations.
    """
    # Native SOL staking (for reference)
    SOL_STAKING_APY: float = 0.07  # ~7% for native SOL staking
    
    # SPL Token Staking (for VCoin)
    MIN_STAKE_DURATION_SLOTS: int = 216000  # ~1 day in slots
    UNSTAKE_COOLDOWN_EPOCHS: int = 1  # 1 epoch cooldown
    EPOCH_DURATION_SLOTS: int = 432000  # ~2 days per epoch
    
    # Stake Pool Program
    STAKE_POOL_PROGRAM_ID: str = "SPoo1Ku8WFXoNDMHPsrGSTSG1Y47rzgn41SLUNakuHy"
    
    # Reward distribution
    REWARD_FREQUENCY: str = "per_block"  # Rewards calculated per block
    COMPOUND_FREQUENCY: str = "daily"  # Auto-compound frequency


@dataclass(frozen=True)
class SupplyConfig:
    TOTAL: int = 1_000_000_000
    TGE_CIRCULATING: int = 158_800_000
    LIQUIDITY: int = 100_000_000
    REWARDS_ALLOCATION: int = 700_000_000
    REWARDS_DURATION_MONTHS: int = 120


@dataclass(frozen=True)
class FeeDistributionConfig:
    BURN: float = 0.20
    TREASURY: float = 0.50
    REWARDS: float = 0.30


@dataclass(frozen=True)
class StakingConfig:
    GENERAL_STAKING_CAP_PERCENT: float = 0.15
    IDENTITY_PREMIUM_MULTIPLIER: int = 5
    CONTENT_BOOST_MULTIPLIER: int = 3
    ADVERTISING_CAMPAIGN_MULTIPLIER: int = 10
    MESSAGING_PREMIUM_MULTIPLIER: int = 5
    IDENTITY_CAP_PERCENT: float = 0.40


@dataclass(frozen=True)
class AbsoluteCapsConfig:
    """
    Issue #5 fix: More conservative caps for sustainable tokenomics.
    """
    MAX_RECAPTURE_RATE: float = 0.80  # Was 0.95, reduced to 80%
    MONTHLY_BURN_LIMIT: float = 0.05  # Was 0.10, reduced to 5%
    MONTHLY_BUYBACK_LIMIT: float = 0.03  # Was 0.05, reduced to 3%
    MONTHLY_STAKING_LIMIT: float = 0.10  # Was 0.15, reduced to 10%


@dataclass(frozen=True)
class CostScalingConfig:
    """
    Issue #9 fix: Realistic cost scaling.
    
    Uses a hybrid model:
    - Small base cost (MVP infrastructure)
    - Per-user cost that kicks in after threshold
    - Scales realistically with growth
    
    Formula: BASE + max(0, users - THRESHOLD) * PER_USER
    
    === SOLANA COST ADVANTAGE (November 2025) ===
    Infrastructure costs are significantly lower on Solana:
    - Transaction fees: ~$0.00025 (vs $0.50-50+ on Ethereum)
    - RPC: Free tiers available (Helius, QuickNode, Alchemy)
    - State rent: One-time ~$0.10 per token account
    - No gas price volatility
    """
    BASE: float           # Minimal fixed cost (shared infrastructure)
    PER_USER: float       # Cost per user above threshold
    THRESHOLD: int = 100  # Users before per-user costs kick in
    PER_POST: float = 0   # Optional: cost per post
    # Solana-specific costs (per transaction)
    SOLANA_TX_COST: float = 0.00025  # USD per Solana transaction


@dataclass(frozen=True)
class MarketplaceConfig:
    """
    Issue #11 fix: Realistic marketplace assumptions.
    """
    AVG_PROFILE_PRICE_USD: int = 25  # Was $100, now $25 for launch
    AVG_NFT_PRICE_USD: int = 15  # Was $50, now $15 for 2024 market


@dataclass(frozen=True)
class SpecialRecaptureConfig:
    """Special recapture rates for specific transaction types"""
    FILE_FEES: float = 0.70  # 70% recapture on file transfers


@dataclass(frozen=True)
class DynamicRewardConfig:
    """
    Dynamic Reward Allocation Configuration (November 2025)
    
    Implements a logarithmic scaling formula that adjusts reward allocation
    based on user growth, ensuring:
    - Rewards never grow faster than user base
    - Per-user reward value remains sustainable
    - Token inflation is controlled
    
    Formula:
        growth_factor = min(1.0, ln(current_users / initial_users) / ln(target_users / initial_users))
        allocation = MIN_ALLOCATION + (MAX_ALLOCATION - MIN_ALLOCATION) * growth_factor
    
    Expected Scaling (with defaults):
        | Users     | Growth Factor | Allocation % | Per-User VCoin/Month |
        |-----------|---------------|--------------|---------------------|
        | 1,000     | 0.00          | 5%           | 291,667             |
        | 10,000    | 0.33          | 33%          | 192,500             |
        | 100,000   | 0.67          | 62%          | 36,167              |
        | 500,000   | 0.90          | 82%          | 9,567               |
        | 1,000,000 | 1.00          | 90%          | 5,250               |
    """
    # Allocation bounds
    MIN_ALLOCATION: float = 0.05  # 5% minimum - ensures early users receive meaningful rewards
    MAX_ALLOCATION: float = 0.90  # 90% maximum - cap regardless of user count
    
    # User thresholds for scaling
    INITIAL_USERS: int = 1000  # Starting point (growth_factor = 0)
    TARGET_USERS: int = 1_000_000  # Maximum allocation point (growth_factor = 1)
    
    # Safety mechanisms
    MAX_PER_USER_MONTHLY_USD: float = 50.0  # Cap per-user reward in USD equivalent
    MIN_PER_USER_MONTHLY_USD: float = 0.10  # Floor to ensure some reward
    
    # Inflation guard - maximum monthly emission increase rate
    MAX_MONTHLY_EMISSION_INCREASE: float = 0.20  # 20% max month-over-month increase
    
    # Smoothing factor for allocation changes (0-1, higher = more aggressive)
    SMOOTHING_FACTOR: float = 0.3  # Dampens sudden allocation changes


class Config:
    """Main configuration class with all constants"""
    
    SUPPLY = SupplyConfig()
    FEE_DISTRIBUTION = FeeDistributionConfig()
    STAKING = StakingConfig()
    ABSOLUTE_CAPS = AbsoluteCapsConfig()
    MARKETPLACE = MarketplaceConfig()
    SPECIAL_RECAPTURE = SpecialRecaptureConfig()
    
    # === DYNAMIC REWARD ALLOCATION (November 2025) ===
    DYNAMIC_REWARD = DynamicRewardConfig()
    
    # === SOLANA NETWORK (November 2025) ===
    SOLANA = SolanaNetworkConfig()
    SOLANA_DEX = SolanaDexConfig()
    SOLANA_STAKING = SolanaStakingConfig()
    
    # Monthly emission from rewards pool
    MONTHLY_EMISSION: int = 5_833_333
    
    # Fee collection rate for VCoin transactions
    FEE_COLLECTION_RATE: float = 0.10
    
    # Module revenue share percentages
    MODULE_REVENUE_SHARE: Dict[str, float] = {
        'IDENTITY': 0.05,
        'CONTENT': 0.40,
        'REWARDS': 0.20,
        'COMMUNITY': 0.10,
        'ADVERTISING': 0.15,
        'MESSAGING': 0.10,
    }
    
    # User distribution defaults
    # Issue #12: NFT percentage balanced for visible revenue while realistic
    USER_DISTRIBUTION = {
        'IDENTITY_TIERS': {'BASIC': 0.00, 'VERIFIED': 0.75, 'PREMIUM': 0.20, 'ENTERPRISE': 0.05},
        'CONTENT_TYPES': {'TEXT': 0.65, 'IMAGE': 0.30, 'VIDEO': 0.045, 'NFT': 0.005},  # NFT: 0.5% (visible but realistic)
        'COMMUNITY_SIZES': {'SMALL': 0.50, 'MEDIUM': 0.30, 'LARGE': 0.15, 'ENTERPRISE': 0.05},
        'AD_FORMATS': {'BANNER': 0.70, 'VIDEO': 0.30},
    }
    
    # === ACTIVITY RATES - Issue #17: Now fully documented ===
    ACTIVITY_RATES = {
        # ----- Profile/Identity Activity -----
        # Source: Namecheap domain/profile marketplace data 2024
        # Very few users transfer/sell profiles on new platforms
        'PROFILE_TRANSFERS': 0.02,  # 2% of upgraded users transfer monthly (was 10%)
        
        # ----- Subscription Rates -----
        # Source: Spotify, YouTube, Twitter/X public data 2024
        # New platforms see 0.5-2% paid conversion
        'PREMIUM_SUBSCRIBERS': 0.015,  # 1.5% subscribe to premium (was 5%)
        
        # ----- Content Creation -----
        # Source: Instagram/TikTok creator studies 2024
        # Only 5-10% of users actively post content
        'CREATOR_PERCENTAGE': 0.10,  # 10% of users are creators
        'POSTS_PER_CREATOR': 6,  # Active creators post 6 times/month
        'BOOSTED_POSTS': 0.05,  # 5% of posts are boosted (was 10%)
        
        # ----- Advertising -----
        # Source: Meta Ads Manager, Google Ads benchmarks 2024
        'PROMOTED_POSTS': 0.03,  # 3% of posts get promoted (was 5%)
        'ADVERTISERS': 0.005,  # 0.5% of users are advertisers (was 2%)
        'AD_ANALYTICS_SUBSCRIBERS': 0.10,  # 10% of advertisers use analytics
        'ADS_PER_USER': 30,  # Users see 30 ads/month (was 50)
        
        # ----- Community -----
        # Source: Discord, Reddit community analytics 2024
        'USERS_PER_COMMUNITY': 15,  # Average community size (was 10)
        'COMMUNITY_EVENTS': 0.15,  # 15% of communities host events (was 20%)
        'VERIFIED_COMMUNITIES': 0.05,  # 5% are verified (was 10%)
        'COMMUNITY_ANALYTICS_ELIGIBLE': 0.10,  # 10% eligible for analytics (was 15%)
        
        # ----- Messaging -----
        # Source: WhatsApp, Telegram usage studies 2024
        'MESSAGES_PER_USER': 50,  # 50 messages/user/month (was 100)
        'REGULAR_MESSAGES': 0.85,  # 85% are regular messages
        'ENCRYPTED_MESSAGES': 0.15,  # 15% are encrypted (was 20%)
        'GROUP_CHAT_USERS': 0.20,  # 20% create group chats (was 30%)
        'FILES_PER_USER': 3,  # 3 files/user/month (was 5)
        'CALL_USERS': 0.05,  # 5% make calls (was 10%)
        'AVG_CALL_MINUTES': 15,  # 15 min avg call (was 30)
        'STORAGE_SUBSCRIBERS': 0.10,  # 10% need extra storage (was 20%)
        'MESSAGING_PREMIUM_USERS': 0.08,  # 8% use premium features (was 15%)
        
        # ----- Exchange/Wallet -----
        # Source: Coinbase, Binance retail user data 2024
        # Most social platform users don't actively trade crypto
        'EXCHANGE_ADOPTION': 0.05,  # 5% use exchange features (was 15%)
        'TRADING_FREQUENCY': 0.3,  # 30% of exchange users trade monthly
        'WITHDRAWAL_FREQUENCY': 0.2,  # 20% withdraw monthly (most HODL)
    }
    
    # === COST SCALING - Issue #9: Realistic scaling for all platform sizes ===
    # 
    # Uses hybrid model with minimal base + per-user scaling:
    # - BASE: Minimal shared infrastructure (using serverless/cloud pay-per-use)
    # - PER_USER: Marginal cost per user (scales with usage)
    # - THRESHOLD: Free tier before per-user costs apply
    #
    # === SOLANA NETWORK COST ADVANTAGES (November 2025) ===
    # - Transaction fees: ~$0.00025 per tx (vs $0.50-50+ on Ethereum)
    # - RPC costs: Free tiers from Helius, QuickNode, Alchemy
    # - No gas price volatility - predictable costs
    # - State rent: One-time ~$0.10 per token account
    # - DEX routing via Jupiter: Free aggregation
    #
    # For a platform with 1,000 users on Solana:
    #   Identity: $10 + (1000-100) * $0.01 = $19/month
    #   Content:  $20 + (1000-100) * $0.02 = $38/month
    #   Exchange: $5 + (100 exchange users - 25) * $0.01 = $5.75/month
    #   Blockchain costs: 1000 users * 10 txs * $0.00025 = $2.50/month
    #
    COST_SCALING = {
        'IDENTITY': CostScalingConfig(
            BASE=10,          # $10/month base (serverless auth, free tier storage)
            PER_USER=0.01,    # $0.01/user/month above threshold
            THRESHOLD=100,    # First 100 users free tier
            SOLANA_TX_COST=0.00025,  # Solana tx cost for identity verification
        ),
        'CONTENT': CostScalingConfig(
            BASE=20,          # $20/month base (CDN free tier, basic storage)
            PER_USER=0.02,    # $0.02/user/month
            THRESHOLD=100,
            PER_POST=0.002,   # $0.002/post (processing, transcoding)
            SOLANA_TX_COST=0.00025,  # Solana tx for on-chain content registry
        ),
        'ADVERTISING': CostScalingConfig(
            BASE=5,           # $5/month base (ad serving is mostly profit)
            PER_USER=0.005,   # $0.005/user
            THRESHOLD=100,
            SOLANA_TX_COST=0.00025,
        ),
        'COMMUNITY': CostScalingConfig(
            BASE=5,           # $5/month base
            PER_USER=0.005,   # $0.005/user
            THRESHOLD=100,
            SOLANA_TX_COST=0.00025,
        ),
        'MESSAGING': CostScalingConfig(
            BASE=10,          # $10/month base (message queue, storage)
            PER_USER=0.01,    # $0.01/user
            THRESHOLD=100,
            SOLANA_TX_COST=0.00025,  # Solana tx for encrypted message keys
        ),
        'REWARDS': CostScalingConfig(
            BASE=10,          # $10/month base (Solana program execution)
            PER_USER=0.003,   # $0.003/user
            THRESHOLD=100,
            SOLANA_TX_COST=0.00025,  # Solana tx for reward distribution
        ),
        'EXCHANGE': CostScalingConfig(
            BASE=5,           # $5/month base (Helius RPC free tier, minimal infra)
            PER_USER=0.01,    # $0.01/user (includes Solana tx costs)
            THRESHOLD=25,     # Low threshold - exchange scales excellently on Solana
            SOLANA_TX_COST=0.00025,  # Jupiter swap tx cost
        ),
    }
    
    # === SOLANA-SPECIFIC OPERATIONAL COSTS ===
    SOLANA_COSTS = {
        # RPC Provider costs (monthly)
        'RPC_FREE_TIER_REQUESTS': 100_000_000,  # Helius free tier: 100M requests
        'RPC_PAID_TIER_USD': 99,  # Helius Growth plan: $99/month
        'RPC_ENTERPRISE_USD': 499,  # Helius Business: $499/month
        
        # DEX Integration costs
        'JUPITER_ROUTING': 0,  # Free - Jupiter is free to use
        'RAYDIUM_LP_CREATION': 0.3,  # ~0.3 SOL for new pool
        'ORCA_WHIRLPOOL_CREATION': 0.5,  # ~0.5 SOL for new Whirlpool
        
        # Token operations (in USD)
        'TOKEN_MINT_COST': 0.0015,  # Create new token mint
        'TOKEN_ACCOUNT_COST': 0.10,  # Create associated token account
        'TRANSFER_COST': 0.00025,  # SPL token transfer
        
        # Staking program costs
        'STAKE_POOL_CREATION': 5.0,  # One-time: create stake pool
        'STAKE_ACCOUNT_RENT': 0.10,  # Per staker account
    }
    
    # Cap config for recapture mechanisms
    CAPS = {
        'ADVERTISING_BUYBACK': 0.80,
        'ADVERTISING_DEPOSITS': 0.25,
        'IDENTITY_STAKING': 0.40,
        'CONTENT_STAKING': 0.40,
        'COMMUNITY_STAKING': 0.40,
        'MESSAGING_STAKING': 0.40,
    }
    
    # === COMPLIANCE COST DEFAULTS ===
    # Issue #13: Regulatory costs that are often overlooked
    # Note: These scale with platform size - smaller platforms have lower costs
    COMPLIANCE_DEFAULTS = {
        'KYC_AML_MONTHLY': 500,       # $500/month minimum for KYC provider
        'LEGAL_MONTHLY': 1000,        # $1K/month for basic legal
        'INSURANCE_MONTHLY': 500,     # $500/month basic insurance
        'AUDIT_QUARTERLY': 2500,      # $2.5K/quarter for audits
        'GDPR_MONTHLY': 250,          # $250/month privacy compliance
    }
    
    @classmethod
    def get_linear_cost(cls, module: str, users: int, posts: int = 0) -> float:
        """
        Calculate costs using realistic scaling model.
        
        Issue #9 fix: Costs now scale appropriately for all platform sizes.
        Small platforms have low costs, costs grow with user base.
        """
        if module not in cls.COST_SCALING:
            return 0
        
        scaling = cls.COST_SCALING[module]
        
        # Base cost (minimal infrastructure)
        base = scaling.BASE
        
        # Per-user cost (only for users above threshold)
        users_above_threshold = max(0, users - scaling.THRESHOLD)
        user_cost = users_above_threshold * scaling.PER_USER
        
        # Per-post cost (if applicable)
        post_cost = posts * scaling.PER_POST if scaling.PER_POST else 0
        
        return base + user_cost + post_cost
    
    @classmethod
    def round(cls, value: float, decimals: int = 2) -> float:
        """Round value to specified decimal places"""
        return round(value, decimals)


# Global config instance
config = Config()
