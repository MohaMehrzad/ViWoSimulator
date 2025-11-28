"""
Liquidity Module - Token liquidity health and price impact calculations.

=== SOLANA DEX INTEGRATION (November 2025) ===

Built for Solana's high-performance DEX ecosystem:

Primary DEXs:
- Raydium: Concentrated Liquidity Market Maker (CLMM)
  - Fee tiers: 0.01%, 0.05%, 0.25%, 1%
  - Best for: Stablecoin pairs, high-volume trading
  - Features: Permissionless pool creation

- Orca Whirlpools: Concentrated Liquidity AMM
  - Fee tiers: 0.01%, 0.05%, 0.30%, 1%
  - Best for: DeFi integrations, efficient capital
  - Features: SDK for easy integration

- Meteora: Dynamic AMM
  - Dynamic fees: 0.01% - 1% based on volatility
  - Best for: Volatile pairs, new tokens
  - Features: Auto-rebalancing pools

- Phoenix: Order book DEX
  - Maker fee: 0%
  - Taker fee: 0.05%
  - Best for: Large trades, institutional

Pool Types on Solana:
1. Constant Product (x*y=k) - Traditional AMM
2. Concentrated Liquidity (CLMM) - Capital efficient
3. Stable Pools - For correlated assets
4. Dynamic Pools - Volatility-adjusted fees

Liquidity health scoring:
- Liquidity/Market Cap ratio (40% weight)
- Slippage on trades (30% weight)  
- Protocol-owned liquidity (20% weight)
- Pool diversity across DEXs (10% weight)

Target: 70%+ liquidity health score for sustainable token economy.

Solana-specific advantages:
- ~$0.00025 per swap transaction
- 400ms block time for instant swaps
- Jupiter aggregates all DEX liquidity
- No MEV sandwich attacks (priority fees)
"""

from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum
from app.models import SimulationParameters
from app.config import config


class SolanaDex(Enum):
    """Solana DEX platforms"""
    RAYDIUM = "raydium"
    RAYDIUM_CLMM = "raydium_clmm"
    ORCA = "orca"
    ORCA_WHIRLPOOL = "orca_whirlpool"
    METEORA = "meteora"
    PHOENIX = "phoenix"
    LIFINITY = "lifinity"


class PoolType(Enum):
    """Types of liquidity pools on Solana"""
    CONSTANT_PRODUCT = "constant_product"  # x*y=k
    CONCENTRATED = "concentrated"  # CLMM
    STABLE = "stable"  # Stable swap
    DYNAMIC = "dynamic"  # Dynamic fees


# Solana DEX fee structures (November 2025)
SOLANA_DEX_FEES = {
    SolanaDex.RAYDIUM: {"standard": 0.0025, "stable": 0.0001},
    SolanaDex.RAYDIUM_CLMM: {"low": 0.0001, "medium": 0.0005, "high": 0.0025, "max": 0.01},
    SolanaDex.ORCA: {"standard": 0.003, "stable": 0.0001},
    SolanaDex.ORCA_WHIRLPOOL: {"tick_1": 0.0001, "tick_8": 0.0005, "tick_64": 0.003, "tick_128": 0.01},
    SolanaDex.METEORA: {"min": 0.0001, "max": 0.01},  # Dynamic
    SolanaDex.PHOENIX: {"maker": 0.0, "taker": 0.0005},
    SolanaDex.LIFINITY: {"standard": 0.002},
}


@dataclass
class LiquidityPool:
    """Represents a single liquidity pool on Solana"""
    name: str
    token_amount: float
    paired_asset_usd: float
    pool_share: float  # % of total liquidity
    is_protocol_owned: bool
    # Solana-specific fields
    dex: SolanaDex = SolanaDex.RAYDIUM
    pool_type: PoolType = PoolType.CONSTANT_PRODUCT
    fee_tier: float = 0.003  # 0.3% default
    tick_spacing: Optional[int] = None  # For CLMM pools
    pool_address: Optional[str] = None


@dataclass
class SolanaPoolConfig:
    """Configuration for creating a Solana liquidity pool"""
    dex: SolanaDex
    pool_type: PoolType
    fee_tier: float
    initial_price: float
    min_price: Optional[float] = None  # For CLMM
    max_price: Optional[float] = None  # For CLMM
    tick_spacing: int = 64  # For Whirlpools


def calculate_price_impact(
    trade_amount_usd: float,
    liquidity_usd: float,
    pool_type: PoolType = PoolType.CONSTANT_PRODUCT,
    concentration_factor: float = 1.0
) -> float:
    """
    Calculate price impact for a trade using Solana AMM formulas.
    
    === SOLANA DEX FORMULAS (November 2025) ===
    
    Constant Product (Raydium Standard, Orca Standard):
        price_impact = trade_amount / (liquidity + trade_amount)
    
    Concentrated Liquidity (Raydium CLMM, Orca Whirlpools):
        price_impact = trade_amount / (liquidity * concentration_factor + trade_amount)
        - Concentration factor: 2-10x for typical ranges
        - More capital efficient, lower slippage
    
    Stable Pools:
        price_impact = trade_amount / (liquidity * 100 + trade_amount)
        - Near 1:1 swaps for correlated assets
    
    Args:
        trade_amount_usd: Size of trade in USD
        liquidity_usd: Total liquidity in the pool (USD)
        pool_type: Type of Solana AMM pool
        concentration_factor: Capital efficiency for CLMM (1-10x)
    
    Returns:
        Price impact as decimal (0.01 = 1% slippage)
    """
    if liquidity_usd <= 0:
        return 1.0  # 100% slippage if no liquidity
    
    if pool_type == PoolType.CONSTANT_PRODUCT:
        # Standard AMM formula (Raydium, Orca standard pools)
        impact = trade_amount_usd / (liquidity_usd + trade_amount_usd)
    
    elif pool_type == PoolType.CONCENTRATED:
        # CLMM formula (Raydium CLMM, Orca Whirlpools)
        # Concentrated liquidity is more capital efficient
        effective_liquidity = liquidity_usd * concentration_factor
        impact = trade_amount_usd / (effective_liquidity + trade_amount_usd)
    
    elif pool_type == PoolType.STABLE:
        # Stable swap curve (Saber, stable pools)
        # Very low slippage for correlated assets
        effective_liquidity = liquidity_usd * 100  # High amplification
        impact = trade_amount_usd / (effective_liquidity + trade_amount_usd)
    
    elif pool_type == PoolType.DYNAMIC:
        # Dynamic pools (Meteora)
        # Similar to constant product but with dynamic fees
        impact = trade_amount_usd / (liquidity_usd + trade_amount_usd)
    
    else:
        # Default to constant product
        impact = trade_amount_usd / (liquidity_usd + trade_amount_usd)
    
    return min(impact, 1.0)  # Cap at 100%


def calculate_jupiter_route_impact(
    trade_amount_usd: float,
    total_liquidity_usd: float,
    num_pools: int = 1
) -> float:
    """
    Calculate price impact when Jupiter aggregator routes across multiple pools.
    
    Jupiter splits trades across multiple DEXs to minimize slippage.
    For large trades, this significantly reduces price impact.
    
    Args:
        trade_amount_usd: Size of trade
        total_liquidity_usd: Total available liquidity across all pools
        num_pools: Number of pools Jupiter can route through
    
    Returns:
        Effective price impact after routing optimization
    """
    if num_pools <= 1:
        return calculate_price_impact(trade_amount_usd, total_liquidity_usd)
    
    # Jupiter optimally splits trades
    # Simplified: each pool gets trade/sqrt(num_pools)
    split_factor = num_pools ** 0.5
    effective_trade = trade_amount_usd / split_factor
    
    # Each pool handles smaller trades
    per_pool_liquidity = total_liquidity_usd / num_pools
    impact = calculate_price_impact(effective_trade, per_pool_liquidity)
    
    return impact


def calculate_slippage_for_sizes(liquidity_usd: float) -> Dict[str, float]:
    """
    Calculate slippage for standard trade sizes.
    
    Returns dict with slippage for $1K, $5K, $10K, $50K, $100K trades.
    """
    sizes = {
        'slippage_1k': 1000,
        'slippage_5k': 5000,
        'slippage_10k': 10000,
        'slippage_50k': 50000,
        'slippage_100k': 100000,
    }
    
    return {
        key: round(calculate_price_impact(size, liquidity_usd) * 100, 2)
        for key, size in sizes.items()
    }


def calculate_liquidity_ratio(
    liquidity_usd: float,
    token_price: float,
    circulating_supply: float
) -> float:
    """
    Calculate liquidity to market cap ratio.
    
    Target: 15%+ for healthy liquidity
    Minimum: 5% for tradeable token
    """
    market_cap = token_price * circulating_supply
    if market_cap <= 0:
        return 0.0
    
    return liquidity_usd / market_cap


def calculate_health_score(
    liquidity_ratio: float,
    slippage_10k: float,
    protocol_owned_percent: float,
    pool_count: int
) -> float:
    """
    Calculate overall liquidity health score (0-100).
    
    Formula:
    - Ratio score (40%): min(ratio / 0.20, 1) * 40
    - Slippage score (30%): max(0, 1 - slippage / 0.02) * 30
    - POL score (20%): protocol_owned_percent * 20
    - Diversity score (10%): min(pool_count / 3, 1) * 10
    
    Target: 70+ for healthy liquidity
    """
    # Ratio component (40% weight)
    # Target: 20% liquidity ratio = full score
    ratio_score = min(liquidity_ratio / 0.20, 1.0) * 40
    
    # Slippage component (30% weight)
    # Target: <2% slippage on $10K trade
    slippage_decimal = slippage_10k / 100  # Convert from percentage
    slippage_score = max(0, 1 - slippage_decimal / 0.02) * 30
    
    # Protocol-owned liquidity component (20% weight)
    pol_score = protocol_owned_percent * 20
    
    # Pool diversity component (10% weight)
    # Target: 3+ pools for full diversity score
    diversity_score = min(pool_count / 3, 1.0) * 10
    
    total_score = ratio_score + slippage_score + pol_score + diversity_score
    
    return round(min(total_score, 100), 1)


def get_health_status(score: float) -> Dict[str, str]:
    """Get health status label and color based on score."""
    if score >= 70:
        return {'label': 'Healthy', 'color': 'emerald', 'icon': '✅'}
    elif score >= 50:
        return {'label': 'Moderate', 'color': 'amber', 'icon': '⚠️'}
    elif score >= 30:
        return {'label': 'At Risk', 'color': 'orange', 'icon': '🚨'}
    else:
        return {'label': 'Critical', 'color': 'red', 'icon': '❌'}


def calculate_liquidity(
    params: SimulationParameters,
    users: int,
    monthly_volume: float = 0,
    circulating_supply: float = 100_000_000
) -> dict:
    """
    Calculate complete liquidity metrics for Solana DEXs.
    
    === SOLANA DEX INTEGRATION (November 2025) ===
    
    Pool Strategy:
    1. Primary: VCoin/USDC on Raydium CLMM (0.25% fee tier)
    2. Secondary: VCoin/SOL on Orca Whirlpool (0.30% fee tier)  
    3. Tertiary: VCoin/USDT on Meteora (dynamic fees)
    
    Jupiter aggregates all pools for best execution.
    
    Args:
        params: Simulation parameters
        users: Total active users
        monthly_volume: Estimated monthly trading volume in VCoin
        circulating_supply: Current circulating token supply
    
    Returns:
        Dict with all liquidity metrics, health score, and Solana-specific data
    """
    # Get parameters
    initial_liquidity = params.initial_liquidity_usd
    pol_percent = params.protocol_owned_liquidity
    token_price = params.token_price
    
    # Calculate market cap
    market_cap = token_price * circulating_supply
    
    # Calculate liquidity ratio
    liquidity_ratio = calculate_liquidity_ratio(
        initial_liquidity, 
        token_price, 
        circulating_supply
    )
    
    # === SOLANA POOL CONFIGURATION ===
    # Determine pool strategy based on liquidity size
    if initial_liquidity >= 500000:
        # Large liquidity: Multi-DEX strategy
        pools = [
            LiquidityPool(
                name="VCoin/USDC",
                token_amount=initial_liquidity * 0.4 / token_price,
                paired_asset_usd=initial_liquidity * 0.4,
                pool_share=0.40,
                is_protocol_owned=True,
                dex=SolanaDex.RAYDIUM_CLMM,
                pool_type=PoolType.CONCENTRATED,
                fee_tier=0.0025,
            ),
            LiquidityPool(
                name="VCoin/SOL",
                token_amount=initial_liquidity * 0.35 / token_price,
                paired_asset_usd=initial_liquidity * 0.35,
                pool_share=0.35,
                is_protocol_owned=True,
                dex=SolanaDex.ORCA_WHIRLPOOL,
                pool_type=PoolType.CONCENTRATED,
                fee_tier=0.003,
            ),
            LiquidityPool(
                name="VCoin/USDT",
                token_amount=initial_liquidity * 0.25 / token_price,
                paired_asset_usd=initial_liquidity * 0.25,
                pool_share=0.25,
                is_protocol_owned=True,
                dex=SolanaDex.METEORA,
                pool_type=PoolType.DYNAMIC,
                fee_tier=0.002,
            ),
        ]
        pool_count = 3
        concentration_factor = 4.0  # 4x capital efficiency from CLMM
        
    elif initial_liquidity >= 200000:
        # Medium liquidity: Dual pool
        pools = [
            LiquidityPool(
                name="VCoin/USDC",
                token_amount=initial_liquidity * 0.6 / token_price,
                paired_asset_usd=initial_liquidity * 0.6,
                pool_share=0.60,
                is_protocol_owned=True,
                dex=SolanaDex.RAYDIUM_CLMM,
                pool_type=PoolType.CONCENTRATED,
                fee_tier=0.0025,
            ),
            LiquidityPool(
                name="VCoin/SOL",
                token_amount=initial_liquidity * 0.4 / token_price,
                paired_asset_usd=initial_liquidity * 0.4,
                pool_share=0.40,
                is_protocol_owned=True,
                dex=SolanaDex.ORCA_WHIRLPOOL,
                pool_type=PoolType.CONCENTRATED,
                fee_tier=0.003,
            ),
        ]
        pool_count = 2
        concentration_factor = 3.0
        
    else:
        # Small liquidity: Single concentrated pool
        pools = [
            LiquidityPool(
                name="VCoin/USDC",
                token_amount=initial_liquidity / token_price,
                paired_asset_usd=initial_liquidity,
                pool_share=1.0,
                is_protocol_owned=True,
                dex=SolanaDex.RAYDIUM_CLMM,
                pool_type=PoolType.CONCENTRATED,
                fee_tier=0.0025,
            ),
        ]
        pool_count = 1
        concentration_factor = 2.0
    
    # Calculate slippage with CLMM advantages
    slippage_data = calculate_slippage_for_sizes(
        initial_liquidity * concentration_factor  # Effective liquidity
    )
    slippage_10k = slippage_data['slippage_10k']
    
    # Calculate health score
    health_score = calculate_health_score(
        liquidity_ratio,
        slippage_10k,
        pol_percent,
        pool_count
    )
    
    # Get health status
    health_status = get_health_status(health_score)
    
    # Calculate pool breakdown
    protocol_owned_usd = initial_liquidity * pol_percent
    community_lp_usd = initial_liquidity * (1 - pol_percent)
    
    # Estimate daily volume based on users
    # Solana users tend to trade more frequently due to low fees
    estimated_daily_volume = users * 0.75 * token_price  # $0.75 per user/day (higher than ETH)
    estimated_monthly_volume = estimated_daily_volume * 30
    
    # Volume/liquidity ratio (healthy: 10-50% monthly)
    volume_liquidity_ratio = (
        estimated_monthly_volume / initial_liquidity 
        if initial_liquidity > 0 else 0
    )
    
    # Buy/Sell pressure estimate
    # Calculate allocation percentage (dynamic or static)
    use_dynamic = getattr(params, 'enable_dynamic_allocation', False)
    
    if use_dynamic and users > 0:
        from app.core.modules.rewards import calculate_dynamic_allocation
        from app.config import config
        dynamic_result = calculate_dynamic_allocation(
            current_users=users,
            token_price=token_price,
            initial_users=getattr(params, 'initial_users_for_allocation', 1000),
            target_users=getattr(params, 'target_users_for_max_allocation', 1_000_000),
            max_per_user_monthly_usd=getattr(params, 'max_per_user_monthly_usd', 50.0),
            min_per_user_monthly_usd=getattr(params, 'min_per_user_monthly_usd', 0.10),
            monthly_emission=config.MONTHLY_EMISSION,
        )
        allocation_percent = dynamic_result.allocation_percent
    else:
        allocation_percent = params.reward_allocation_percent
    
    monthly_emission_usd = config.MONTHLY_EMISSION * token_price * allocation_percent
    sell_pressure = monthly_emission_usd * 0.40  # 40% sold
    buy_pressure = (
        protocol_owned_usd * 0.001 +  # LP rewards
        monthly_emission_usd * params.buyback_percent  # Buybacks
    )
    
    net_pressure = buy_pressure - sell_pressure
    pressure_ratio = buy_pressure / sell_pressure if sell_pressure > 0 else 1.0
    
    # === SOLANA-SPECIFIC CALCULATIONS ===
    # LP token creation cost (one-time)
    lp_creation_cost = pool_count * 0.5  # ~0.5 SOL per pool at ~$50/SOL = ~$25
    
    # Estimated LP fee earnings (monthly)
    weighted_fee = sum(p.fee_tier * p.pool_share for p in pools)
    lp_fee_earnings = estimated_monthly_volume * weighted_fee
    
    # Jupiter routing data
    jupiter_routes = pool_count * 2  # Each pool can be routed in/out
    
    return {
        # Core metrics
        'initial_liquidity': round(initial_liquidity, 2),
        'protocol_owned_percent': round(pol_percent * 100, 1),
        'protocol_owned_usd': round(protocol_owned_usd, 2),
        'community_lp_usd': round(community_lp_usd, 2),
        'market_cap': round(market_cap, 2),
        'liquidity_ratio': round(liquidity_ratio * 100, 2),
        
        # Slippage data (with CLMM efficiency)
        **slippage_data,
        
        # Pool info
        'pool_count': pool_count,
        'lock_months': params.liquidity_lock_months,
        
        # Health metrics
        'health_score': health_score,
        'health_status': health_status['label'],
        'health_color': health_status['color'],
        'health_icon': health_status['icon'],
        
        # Volume metrics
        'estimated_monthly_volume': round(estimated_monthly_volume, 2),
        'volume_liquidity_ratio': round(volume_liquidity_ratio * 100, 2),
        
        # Pressure analysis
        'buy_pressure_usd': round(buy_pressure, 2),
        'sell_pressure_usd': round(sell_pressure, 2),
        'net_pressure_usd': round(net_pressure, 2),
        'pressure_ratio': round(pressure_ratio, 2),
        
        # Recommendations
        'meets_70_target': health_score >= 70,
        'recommended_liquidity': round(market_cap * 0.15, 2),
        
        # === SOLANA-SPECIFIC DATA ===
        'network': 'solana',
        'primary_dex': pools[0].dex.value,
        'primary_pool_type': pools[0].pool_type.value,
        'concentration_factor': concentration_factor,
        'effective_liquidity': round(initial_liquidity * concentration_factor, 2),
        
        # Pool details
        'pools': [
            {
                'name': p.name,
                'dex': p.dex.value,
                'type': p.pool_type.value,
                'fee_tier': p.fee_tier,
                'share': p.pool_share,
                'liquidity_usd': round(p.paired_asset_usd * 2, 2),  # Total value locked
            }
            for p in pools
        ],
        
        # Jupiter aggregation
        'jupiter_enabled': True,
        'jupiter_routes': jupiter_routes,
        'dex_aggregator': 'jupiter_v6',
        
        # Economics
        'weighted_pool_fee': round(weighted_fee * 100, 3),  # As percentage
        'estimated_lp_earnings': round(lp_fee_earnings, 2),
        'lp_creation_cost_usd': round(lp_creation_cost * 50, 2),  # At $50/SOL
        
        # Solana advantages
        'tx_cost_per_swap': 0.00025,  # $0.00025
        'avg_finality_ms': 400,
        'mev_protection': True,  # Priority fees prevent sandwich attacks
    }

