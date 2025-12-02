"""
Configuration constants matching the HTML CONFIG object.
These values ensure consistency between frontend and backend calculations.

Updated with 2024-2025 industry benchmarks and sources.
Addresses Issues #9 (cost scaling), #17 (documented activity rates).

=== TOKEN ALLOCATION (November 2025) ===
Official VCoin tokenomics with 10 allocation categories:
- Total Supply: 1,000,000,000 VCoin
- TGE Circulating: 153,000,000 VCoin (HIGH-01 Fix)
- 60-month vesting schedule for most categories
- 5-year reward emission (350M tokens)

=== ROUNDING CONVENTIONS (LOW-02) ===
The following rounding precision standards are used throughout the simulator:
- Token Prices: 4 decimal places (e.g., $0.0500)
- Revenue/Costs (USD): 2 decimal places (e.g., $1,234.56)
- Percentages: 1-2 decimal places (e.g., 15.5%, 0.155)
- Token Counts: 0 decimal places (integers)
- User Counts: 0 decimal places (integers)

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

from dataclasses import dataclass, field
from typing import Dict, Optional


# === ROUNDING PRECISION CONSTANTS (LOW-001 Fix) ===

@dataclass(frozen=True)
class RoundingPrecision:
    """
    LOW-001 Fix: Standardized rounding precision across the simulator.
    
    Use these constants for consistent rounding:
    - TOKEN_PRICE: For VCoin prices (e.g., $0.0300)
    - USD_AMOUNT: For dollar amounts (e.g., $1,234.56)
    - PERCENTAGE: For percentages (e.g., 15.50%)
    - TOKEN_COUNT: For token quantities (integers)
    - USER_COUNT: For user counts (integers)
    
    Example usage:
        price = round(raw_price, ROUNDING.TOKEN_PRICE)
        revenue = round(raw_revenue, ROUNDING.USD_AMOUNT)
    """
    TOKEN_PRICE: int = 4    # 4 decimals for token prices ($0.0300)
    USD_AMOUNT: int = 2     # 2 decimals for USD amounts ($1,234.56)
    PERCENTAGE: int = 2     # 2 decimals for percentages (15.50%)
    TOKEN_COUNT: int = 0    # Integer for token counts
    USER_COUNT: int = 0     # Integer for user counts
    RATE: int = 4           # 4 decimals for rates/ratios (0.0500)


# === TOKEN ALLOCATION CONFIGURATION (November 2025) ===

@dataclass(frozen=True)
class TokenAllocationCategory:
    """
    Configuration for a single token allocation category.
    
    Attributes:
        name: Category name (e.g., 'Seed Round', 'Team')
        percent: Percentage of total supply (0.0-1.0)
        tokens: Total tokens allocated
        tge_percent: Percentage unlocked at TGE (0.0-1.0)
        cliff_months: Months before vesting starts (after TGE)
        vesting_months: Duration of vesting period AFTER cliff ends.
                       Total unlock period = cliff_months + vesting_months.
                       Example: cliff=6, vesting=18 means tokens unlock M7-M24.
        price_usd: Token price for this round (if applicable)
        is_programmatic: Whether release is programmatic (Treasury/Rewards)
        emission_months: For rewards, the emission duration
        description: Category description
    
    HIGH-02 Fix: Updated vesting_months docstring to match actual code behavior.
    """
    name: str
    percent: float
    tokens: int
    tge_percent: float = 0.0
    cliff_months: int = 0
    vesting_months: int = 0
    price_usd: float = 0.03
    is_programmatic: bool = False
    emission_months: int = 0
    description: str = ""


@dataclass(frozen=True)
class TokenAllocationConfig:
    """
    Official VCoin Token Allocation (November 2025)
    
    Total Supply: 1,000,000,000 VCoin (1 Billion)
    
    Allocation Breakdown:
    - Seed Round:        2% (20M)  - Early investors, highest risk
    - Private Round:     3% (30M)  - Strategic investors and VCs
    - Public Sale:       5% (50M)  - Community token sale (IDO/ICO)
    - Team:             10% (100M) - Core team members and employees
    - Advisors:          5% (50M)  - Strategic advisors and consultants
    - Treasury/DAO:     20% (200M) - Protocol treasury and governance
    - Ecosystem/Rewards: 35% (350M) - User incentives, staking rewards, grants
    - Liquidity:        10% (100M) - DEX/CEX liquidity pools
    - Foundation:        2% (20M)  - Foundation operations and reserve
    - Marketing/Growth:  8% (80M)  - Marketing campaigns and partnerships
    
    TOTAL: 100% (1,000,000,000)
    """
    
    SEED: TokenAllocationCategory = field(default_factory=lambda: TokenAllocationCategory(
        name="Seed Round",
        percent=0.02,
        tokens=20_000_000,
        tge_percent=0.0,
        cliff_months=12,
        vesting_months=24,
        price_usd=0.01,
        description="Early-stage investors (highest risk, lowest price)"
    ))
    
    PRIVATE: TokenAllocationCategory = field(default_factory=lambda: TokenAllocationCategory(
        name="Private Round",
        percent=0.03,
        tokens=30_000_000,
        tge_percent=0.10,
        cliff_months=6,
        vesting_months=18,
        price_usd=0.015,
        description="Strategic investors and VCs"
    ))
    
    PUBLIC: TokenAllocationCategory = field(default_factory=lambda: TokenAllocationCategory(
        name="Public Sale",
        percent=0.05,
        tokens=50_000_000,
        tge_percent=0.50,
        cliff_months=0,
        vesting_months=3,
        price_usd=0.02,
        description="Community token sale (IDO/ICO)"
    ))
    
    TEAM: TokenAllocationCategory = field(default_factory=lambda: TokenAllocationCategory(
        name="Team",
        percent=0.10,
        tokens=100_000_000,
        tge_percent=0.0,
        cliff_months=12,
        vesting_months=36,
        price_usd=0.03,
        description="Core team members and employees"
    ))
    
    ADVISORS: TokenAllocationCategory = field(default_factory=lambda: TokenAllocationCategory(
        name="Advisors",
        percent=0.05,
        tokens=50_000_000,
        tge_percent=0.0,
        cliff_months=6,
        vesting_months=18,
        price_usd=0.03,
        description="Strategic advisors and consultants"
    ))
    
    TREASURY: TokenAllocationCategory = field(default_factory=lambda: TokenAllocationCategory(
        name="Treasury/DAO",
        percent=0.20,
        tokens=200_000_000,
        tge_percent=0.0,
        is_programmatic=True,
        description="Protocol treasury and governance"
    ))
    
    REWARDS: TokenAllocationCategory = field(default_factory=lambda: TokenAllocationCategory(
        name="Ecosystem & Rewards",
        percent=0.35,
        tokens=350_000_000,
        tge_percent=0.0,
        is_programmatic=True,
        emission_months=60,
        description="User incentives, staking rewards, grants"
    ))
    
    LIQUIDITY: TokenAllocationCategory = field(default_factory=lambda: TokenAllocationCategory(
        name="Liquidity",
        percent=0.10,
        tokens=100_000_000,
        tge_percent=1.0,
        description="DEX/CEX liquidity pools"
    ))
    
    FOUNDATION: TokenAllocationCategory = field(default_factory=lambda: TokenAllocationCategory(
        name="Foundation",
        percent=0.02,
        tokens=20_000_000,
        tge_percent=0.25,
        cliff_months=3,
        vesting_months=24,
        price_usd=0.03,
        description="Foundation operations and reserve"
    ))
    
    MARKETING: TokenAllocationCategory = field(default_factory=lambda: TokenAllocationCategory(
        name="Marketing & Growth",
        percent=0.08,
        tokens=80_000_000,
        tge_percent=0.25,
        cliff_months=3,
        vesting_months=18,
        price_usd=0.03,
        description="Marketing campaigns and partnerships"
    ))
    
    def get_all_categories(self) -> Dict[str, TokenAllocationCategory]:
        """Get all allocation categories as a dictionary"""
        return {
            'SEED': self.SEED,
            'PRIVATE': self.PRIVATE,
            'PUBLIC': self.PUBLIC,
            'TEAM': self.TEAM,
            'ADVISORS': self.ADVISORS,
            'TREASURY': self.TREASURY,
            'REWARDS': self.REWARDS,
            'LIQUIDITY': self.LIQUIDITY,
            'FOUNDATION': self.FOUNDATION,
            'MARKETING': self.MARKETING,
        }
    
    def validate_allocations(self) -> bool:
        """
        Validate that all allocation percentages sum to exactly 100%.
        
        Raises:
            ValueError: If allocations don't sum to 100% (within 0.1% tolerance)
        
        Returns:
            True if validation passes
        """
        total = sum(cat.percent for cat in self.get_all_categories().values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(
                f"Token allocations sum to {total*100:.2f}%, not 100%. "
                f"Please verify allocation percentages."
            )
        return True
    
    def get_tge_circulating(self) -> int:
        """
        Calculate total tokens circulating at TGE.
        
        HIGH-01 Fix: TGE (Token Generation Event) only includes allocation unlocks,
        not rewards emission. Rewards emission starts at month 1, not TGE.
        
        Returns:
            Total TGE circulating: 153,000,000 VCoin
            - PRIVATE: 3,000,000 (10% of 30M)
            - PUBLIC: 25,000,000 (50% of 50M)
            - LIQUIDITY: 100,000,000 (100% of 100M)
            - FOUNDATION: 5,000,000 (25% of 20M)
            - MARKETING: 20,000,000 (25% of 80M)
        """
        total = 0
        for cat in self.get_all_categories().values():
            total += int(cat.tokens * cat.tge_percent)
        # HIGH-01 Fix: Removed rewards emission - it starts month 1, not TGE
        return total
    
    def get_monthly_unlock(self, category_key: str, month: int) -> int:
        """
        Calculate tokens unlocking for a category in a specific month.
        
        Args:
            category_key: Category key (e.g., 'SEED', 'TEAM')
            month: Month number (0 = TGE, 1 = first month after TGE)
        
        Returns:
            Number of tokens unlocking in that month
        """
        categories = self.get_all_categories()
        if category_key not in categories:
            return 0
        
        cat = categories[category_key]
        
        # TGE unlock
        if month == 0:
            return int(cat.tokens * cat.tge_percent)
        
        # Programmatic releases (Treasury, Rewards)
        if cat.is_programmatic:
            if category_key == 'REWARDS' and cat.emission_months > 0:
                if month <= cat.emission_months:
                    return cat.tokens // cat.emission_months
            return 0
        
        # Vesting unlock
        # NOTE: vesting_months = actual duration of vesting (NOT including cliff)
        # Total unlock period = cliff_months + vesting_months
        if cat.vesting_months == 0:
            return 0
        
        # Before cliff ends (no unlocks during cliff)
        if month <= cat.cliff_months:
            return 0
        
        # Calculate vesting end: cliff + vesting duration
        vesting_end_month = cat.cliff_months + cat.vesting_months
        
        # After full vesting
        if month > vesting_end_month:
            return 0
        
        # During vesting period
        tokens_after_tge = cat.tokens - int(cat.tokens * cat.tge_percent)
        # vesting_months IS the actual vesting duration
        if cat.vesting_months > 0:
            return tokens_after_tge // cat.vesting_months
        
        return 0


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
    """
    Token supply configuration matching official tokenomics.
    
    Updated November 2025:
    - Total Supply: 1,000,000,000 (unchanged)
    - Rewards Allocation: 350,000,000 (35%, was 70%)
    - Rewards Duration: 60 months (5 years, was 10 years)
    - TGE Circulating: 153,000,000 (HIGH-01 Fix: was 158,833,333 - incorrectly included rewards)
    - Treasury Allocation: 200,000,000 (20%, NEW)
    """
    TOTAL: int = 1_000_000_000
    TGE_CIRCULATING: int = 153_000_000  # HIGH-01 Fix: Removed rewards (only allocation unlocks)
    LIQUIDITY: int = 100_000_000
    REWARDS_ALLOCATION: int = 350_000_000  # 35% - Updated from 700M
    REWARDS_DURATION_MONTHS: int = 60  # 5 years - Updated from 120
    TREASURY_ALLOCATION: int = 200_000_000  # 20% - NEW


@dataclass(frozen=True)
class FeeDistributionConfig:
    """
    Fee distribution split for collected VCoin transaction fees.
    
    WP-006 Fix: Documentation clarifying the difference between:
    
    1. FeeDistributionConfig (THIS CLASS):
       - Defines how COLLECTED transaction fees are DISTRIBUTED
       - BURN: 20% of collected fees are burned (deflationary)
       - TREASURY: 50% of collected fees go to DAO treasury
       - REWARDS: 30% of collected fees redistributed to users
       - These apply AFTER fees are collected from the economy
    
    2. params.burn_rate (SimulationParameters):
       - User-configurable burn rate (default 5%)
       - Applied to TOKEN VELOCITY (tokens flowing through economy)
       - NOT applied to emission - applied to spend rate
       - Example: 5% burn_rate on 50% velocity = 2.5% effective burn of emission
    
    The effective burn rate displayed to users (CRIT-002) shows the actual
    deflationary impact as a percentage of monthly emission, which differs
    from both of these rates due to token velocity dynamics.
    
    Total = 1.0 (100%)
    """
    BURN: float = 0.20      # 20% burned (deflationary)
    TREASURY: float = 0.50  # 50% to DAO treasury
    REWARDS: float = 0.30   # 30% redistributed


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
    
    MED-05 Fix: Removed unused SOLANA_TX_COST field.
    Solana tx costs are now handled directly in modules that need them.
    """
    BASE: float           # Minimal fixed cost (shared infrastructure)
    PER_USER: float       # Cost per user above threshold
    THRESHOLD: int = 100  # Users before per-user costs kick in
    PER_POST: float = 0   # Optional: cost per post
    # MED-05: Removed SOLANA_TX_COST - unused in get_linear_cost()
    # Solana tx costs are handled directly in exchange.py, staking.py, etc.


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
        |-----------|---------------|--------------|----------------------|
        | 1,000     | 0.00          | 5%           | ~292                 |
        | 10,000    | 0.33          | 33%          | ~193                 |
        | 100,000   | 0.67          | 62%          | ~36                  |
        | 500,000   | 0.90          | 82%          | ~10                  |
        | 1,000,000 | 1.00          | 90%          | ~5                   |
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
    
    # === LOW-001 Fix: Standardized rounding precision ===
    ROUNDING = RoundingPrecision()
    
    # === TOKEN ALLOCATION (November 2025) ===
    TOKEN_ALLOCATION = TokenAllocationConfig()
    
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
    
    # Monthly emission from rewards pool (350M / 60 months)
    # Base monthly emission (integer truncated)
    MONTHLY_EMISSION: int = 5_833_333
    # Remainder tokens to add to final month (350M - 5,833,333 * 60 = 20)
    MONTHLY_EMISSION_REMAINDER: int = 20
    
    @classmethod
    def get_monthly_emission(cls, month: int, total_months: int = 60) -> int:
        """
        Get the monthly emission for a specific month.
        The final month includes the remainder to ensure exact 350M distribution.
        
        Args:
            month: Month number (1-60)
            total_months: Total vesting months (default 60)
        
        Returns:
            Monthly emission in VCoin
        """
        if month == total_months:
            return cls.MONTHLY_EMISSION + cls.MONTHLY_EMISSION_REMAINDER
        return cls.MONTHLY_EMISSION
    
    # Fee collection rate for VCoin transactions
    FEE_COLLECTION_RATE: float = 0.10
    
    # MED-07 Fix: Centralized platform fee rate (was duplicated in rewards.py and deterministic.py)
    # 5% of ALL reward emissions goes to platform treasury
    PLATFORM_FEE_RATE: float = 0.05
    
    # Treasury revenue share (percentage of platform revenue going to treasury)
    TREASURY_REVENUE_SHARE: float = 0.20  # 20% of revenue to treasury
    
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
    # MED-05: Removed SOLANA_TX_COST from CostScalingConfig - unused in get_linear_cost()
    # Solana tx costs (~$0.00025) are handled directly in modules (exchange.py, staking.py)
    COST_SCALING = {
        'IDENTITY': CostScalingConfig(
            BASE=10,          # $10/month base (serverless auth, free tier storage)
            PER_USER=0.01,    # $0.01/user/month above threshold
            THRESHOLD=100,    # First 100 users free tier
        ),
        'CONTENT': CostScalingConfig(
            BASE=20,          # $20/month base (CDN free tier, basic storage)
            PER_USER=0.02,    # $0.02/user/month
            THRESHOLD=100,
            PER_POST=0.002,   # $0.002/post (processing, transcoding)
        ),
        'ADVERTISING': CostScalingConfig(
            BASE=5,           # $5/month base (ad serving is mostly profit)
            PER_USER=0.005,   # $0.005/user
            THRESHOLD=100,
        ),
        'COMMUNITY': CostScalingConfig(
            BASE=5,           # $5/month base
            PER_USER=0.005,   # $0.005/user
            THRESHOLD=100,
        ),
        'MESSAGING': CostScalingConfig(
            BASE=10,          # $10/month base (message queue, storage)
            PER_USER=0.01,    # $0.01/user
            THRESHOLD=100,
        ),
        'REWARDS': CostScalingConfig(
            BASE=10,          # $10/month base (Solana program execution)
            PER_USER=0.003,   # $0.003/user
            THRESHOLD=100,
        ),
        'EXCHANGE': CostScalingConfig(
            BASE=5,           # $5/month base (Helius RPC free tier, minimal infra)
            PER_USER=0.01,    # $0.01/user (includes Solana tx costs)
            THRESHOLD=25,     # Low threshold - exchange scales excellently on Solana
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
    
    @classmethod
    def get_circulating_supply_at_month(cls, month: int) -> int:
        """
        Calculate total circulating supply at a given month.
        
        Args:
            month: Month number (0 = TGE, 1 = first month after TGE, etc.)
        
        Returns:
            Total circulating supply in VCoin
        """
        total = 0
        allocation = cls.TOKEN_ALLOCATION
        
        for key in ['SEED', 'PRIVATE', 'PUBLIC', 'TEAM', 'ADVISORS', 
                    'TREASURY', 'REWARDS', 'LIQUIDITY', 'FOUNDATION', 'MARKETING']:
            for m in range(month + 1):
                total += allocation.get_monthly_unlock(key, m)
        
        return total


# Global config instance
config = Config()
