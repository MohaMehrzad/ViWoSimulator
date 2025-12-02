"""
Liquidity Farming / Mining Simulation Module

2025 Industry Compliance: Models LP rewards, impermanent loss,
and farming APY projections.

Key Features:
1. Impermanent Loss (IL) Calculator
2. LP Reward Simulations  
3. Farming APY Projections
4. Risk/Reward Analysis
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import math


@dataclass
class FarmingPool:
    """Represents a liquidity farming pool"""
    name: str
    pair: str  # e.g., "VCOIN/USDC"
    tvl_usd: float
    daily_rewards_vcoin: float
    fee_apr: float  # Trading fees APR
    reward_apr: float  # Token rewards APR
    total_apr: float
    il_risk: str  # low, medium, high


def calculate_impermanent_loss(
    initial_price: float,
    final_price: float,
) -> Dict:
    """
    Calculate impermanent loss for a 50/50 LP position.
    
    IL Formula: 2 * sqrt(price_ratio) / (1 + price_ratio) - 1
    
    Args:
        initial_price: Starting token price
        final_price: Ending token price
    
    Returns:
        Dict with IL metrics
    """
    if initial_price <= 0 or final_price <= 0:
        return {
            'impermanent_loss_percent': 0,
            'price_change_percent': 0,
            'interpretation': 'Invalid prices',
            'breakeven_apr_needed': 0,
        }
    
    price_ratio = final_price / initial_price
    price_change_percent = (price_ratio - 1) * 100
    
    # IL formula
    if price_ratio == 1:
        il = 0
    else:
        il = 2 * math.sqrt(price_ratio) / (1 + price_ratio) - 1
    
    il_percent = il * 100  # Negative value = loss
    
    # Interpretation
    if abs(il_percent) < 1:
        interpretation = "Negligible IL"
    elif abs(il_percent) < 5:
        interpretation = "Minor IL"
    elif abs(il_percent) < 10:
        interpretation = "Moderate IL"
    elif abs(il_percent) < 25:
        interpretation = "Significant IL"
    else:
        interpretation = "Severe IL"
    
    # Calculate APR needed to breakeven on IL over 1 year
    # Need to earn at least |IL|% to break even
    breakeven_apr = abs(il_percent)
    
    return {
        'impermanent_loss_percent': round(il_percent, 4),
        'impermanent_loss_abs': round(abs(il_percent), 4),
        'price_change_percent': round(price_change_percent, 2),
        'price_ratio': round(price_ratio, 4),
        'interpretation': interpretation,
        'breakeven_apr_needed': round(breakeven_apr, 2),
        'is_gain': il_percent > 0,
    }


def calculate_il_scenarios(
    current_price: float,
) -> List[Dict]:
    """
    Calculate IL for various price change scenarios.
    
    Returns scenarios for -75%, -50%, -25%, +25%, +50%, +100%, +200%
    """
    scenarios = []
    price_changes = [
        (-75, "Price -75%"),
        (-50, "Price -50%"),
        (-25, "Price -25%"),
        (25, "Price +25%"),
        (50, "Price +50%"),
        (100, "Price +100%"),
        (200, "Price +200%"),
        (400, "Price +400%"),
    ]
    
    for change_pct, label in price_changes:
        final_price = current_price * (1 + change_pct / 100)
        il_data = calculate_impermanent_loss(current_price, final_price)
        
        scenarios.append({
            'scenario': label,
            'price_change_percent': change_pct,
            'final_price': round(final_price, 6),
            'impermanent_loss_percent': il_data['impermanent_loss_percent'],
            'interpretation': il_data['interpretation'],
        })
    
    return scenarios


def calculate_farming_apy(
    pool_tvl_usd: float,
    daily_reward_vcoin: float,
    vcoin_price: float,
    trading_fee_apr: float = 0.10,  # 10% from trading fees
    time_horizon_days: int = 365,
) -> Dict:
    """
    Calculate farming APY with compounding.
    
    Args:
        pool_tvl_usd: Total value locked in the pool
        daily_reward_vcoin: Daily VCoin rewards distributed
        vcoin_price: Current VCoin price
        trading_fee_apr: Annual trading fee return (as decimal)
        time_horizon_days: Investment horizon
    
    Returns:
        Dict with APY calculations
    """
    if pool_tvl_usd <= 0:
        return _empty_farming_result()
    
    # Daily reward value
    daily_reward_usd = daily_reward_vcoin * vcoin_price
    
    # Daily return rate
    daily_reward_rate = daily_reward_usd / pool_tvl_usd
    daily_fee_rate = trading_fee_apr / 365
    daily_total_rate = daily_reward_rate + daily_fee_rate
    
    # APR (simple)
    reward_apr = daily_reward_rate * 365 * 100
    fee_apr = trading_fee_apr * 100
    total_apr = reward_apr + fee_apr
    
    # APY (compound daily)
    reward_apy = ((1 + daily_reward_rate) ** 365 - 1) * 100
    fee_apy = ((1 + daily_fee_rate) ** 365 - 1) * 100
    total_apy = ((1 + daily_total_rate) ** 365 - 1) * 100
    
    # Project returns for time horizon
    final_value_multiplier = (1 + daily_total_rate) ** time_horizon_days
    
    # Calculate dollar returns for $1000 investment
    initial_investment = 1000
    final_value = initial_investment * final_value_multiplier
    profit = final_value - initial_investment
    
    # Sustainability check
    # If rewards are >100% APY, likely unsustainable
    is_sustainable = reward_apr < 100
    
    return {
        # APR (non-compounded)
        'reward_apr': round(reward_apr, 2),
        'fee_apr': round(fee_apr, 2),
        'total_apr': round(total_apr, 2),
        
        # APY (compounded daily)
        'reward_apy': round(reward_apy, 2),
        'fee_apy': round(fee_apy, 2),
        'total_apy': round(total_apy, 2),
        
        # Daily rates
        'daily_reward_rate': round(daily_reward_rate * 100, 4),
        'daily_total_rate': round(daily_total_rate * 100, 4),
        
        # Pool metrics
        'pool_tvl_usd': round(pool_tvl_usd, 2),
        'daily_reward_vcoin': round(daily_reward_vcoin, 2),
        'daily_reward_usd': round(daily_reward_usd, 2),
        
        # Projections
        'time_horizon_days': time_horizon_days,
        'final_value_multiplier': round(final_value_multiplier, 4),
        'example_1000_final': round(final_value, 2),
        'example_1000_profit': round(profit, 2),
        
        # Sustainability
        'is_sustainable': is_sustainable,
        'sustainability_warning': None if is_sustainable else 'High APY may not be sustainable long-term',
    }


def simulate_lp_position(
    initial_investment_usd: float,
    initial_vcoin_price: float,
    pool_tvl_usd: float,
    daily_reward_vcoin: float,
    trading_fee_apr: float,
    price_scenarios: List[Dict],  # List of {month: x, price: y}
) -> Dict:
    """
    Simulate an LP position over time with varying prices.
    
    Tracks:
    - Position value
    - Accumulated rewards
    - Impermanent loss
    - Net P&L
    """
    # Initial position setup (50/50 split)
    initial_vcoin_amount = (initial_investment_usd / 2) / initial_vcoin_price
    initial_stable_amount = initial_investment_usd / 2
    
    # Calculate LP share
    lp_share = initial_investment_usd / pool_tvl_usd if pool_tvl_usd > 0 else 0
    
    results = []
    cumulative_rewards_vcoin = 0
    cumulative_rewards_usd = 0
    cumulative_fees_usd = 0
    
    for scenario in price_scenarios:
        month = scenario.get('month', 0)
        current_price = scenario.get('price', initial_vcoin_price)
        
        # Calculate IL at this price
        il_data = calculate_impermanent_loss(initial_vcoin_price, current_price)
        
        # Value if just holding (no LP)
        hold_value = (initial_vcoin_amount * current_price) + initial_stable_amount
        
        # LP position value (affected by IL)
        lp_position_value = initial_investment_usd * (1 + il_data['impermanent_loss_percent'] / 100)
        
        # Adjust for new pool TVL (assume grows with price)
        price_ratio = current_price / initial_vcoin_price
        estimated_new_tvl = pool_tvl_usd * math.sqrt(price_ratio)  # Rough estimate
        
        # Accumulated rewards (simplified: assume constant emission)
        days_elapsed = month * 30
        period_rewards_vcoin = daily_reward_vcoin * lp_share * 30  # Monthly
        cumulative_rewards_vcoin += period_rewards_vcoin
        cumulative_rewards_usd = cumulative_rewards_vcoin * current_price
        
        # Accumulated fees
        monthly_fee_return = trading_fee_apr / 12
        cumulative_fees_usd += initial_investment_usd * monthly_fee_return
        
        # Total value
        total_value = lp_position_value + cumulative_rewards_usd + cumulative_fees_usd
        
        # Net P&L vs holding
        net_vs_holding = total_value - hold_value
        
        results.append({
            'month': month,
            'vcoin_price': round(current_price, 4),
            'price_change_percent': round((current_price / initial_vcoin_price - 1) * 100, 2),
            
            # Values
            'hold_value_usd': round(hold_value, 2),
            'lp_position_value_usd': round(lp_position_value, 2),
            'cumulative_rewards_usd': round(cumulative_rewards_usd, 2),
            'cumulative_fees_usd': round(cumulative_fees_usd, 2),
            'total_value_usd': round(total_value, 2),
            
            # P&L
            'impermanent_loss_percent': il_data['impermanent_loss_percent'],
            'impermanent_loss_usd': round(initial_investment_usd * il_data['impermanent_loss_percent'] / 100, 2),
            'net_vs_holding_usd': round(net_vs_holding, 2),
            'total_pnl_usd': round(total_value - initial_investment_usd, 2),
            'total_pnl_percent': round((total_value / initial_investment_usd - 1) * 100, 2),
        })
    
    return {
        'initial_investment_usd': initial_investment_usd,
        'initial_vcoin_price': initial_vcoin_price,
        'lp_share_percent': round(lp_share * 100, 6),
        'monthly_projections': results,
        'final_result': results[-1] if results else None,
    }


def calculate_full_farming_analysis(
    vcoin_price: float,
    pool_tvl_usd: float,
    daily_reward_vcoin: float,
    trading_fee_apr: float = 0.10,
    monthly_emission_vcoin: float = 0,
) -> Dict:
    """
    Complete farming analysis including APY, IL scenarios, and simulations.
    """
    # Calculate farming APY
    apy_data = calculate_farming_apy(
        pool_tvl_usd=pool_tvl_usd,
        daily_reward_vcoin=daily_reward_vcoin,
        vcoin_price=vcoin_price,
        trading_fee_apr=trading_fee_apr,
    )
    
    # Calculate IL scenarios
    il_scenarios = calculate_il_scenarios(vcoin_price)
    
    # Simulate LP position over 12 months with different price paths
    # Bull case: +100% over 12 months
    bull_prices = [
        {'month': i, 'price': vcoin_price * (1 + (i / 12) * 1.0)}
        for i in range(1, 13)
    ]
    
    # Bear case: -50% over 12 months
    bear_prices = [
        {'month': i, 'price': vcoin_price * (1 - (i / 12) * 0.5)}
        for i in range(1, 13)
    ]
    
    # Stable case: ±10% volatility
    stable_prices = [
        {'month': i, 'price': vcoin_price * (1 + 0.05 * math.sin(i * 0.5))}
        for i in range(1, 13)
    ]
    
    simulations = {
        'bull_case': simulate_lp_position(
            initial_investment_usd=1000,
            initial_vcoin_price=vcoin_price,
            pool_tvl_usd=pool_tvl_usd,
            daily_reward_vcoin=daily_reward_vcoin,
            trading_fee_apr=trading_fee_apr,
            price_scenarios=bull_prices,
        ),
        'bear_case': simulate_lp_position(
            initial_investment_usd=1000,
            initial_vcoin_price=vcoin_price,
            pool_tvl_usd=pool_tvl_usd,
            daily_reward_vcoin=daily_reward_vcoin,
            trading_fee_apr=trading_fee_apr,
            price_scenarios=bear_prices,
        ),
        'stable_case': simulate_lp_position(
            initial_investment_usd=1000,
            initial_vcoin_price=vcoin_price,
            pool_tvl_usd=pool_tvl_usd,
            daily_reward_vcoin=daily_reward_vcoin,
            trading_fee_apr=trading_fee_apr,
            price_scenarios=stable_prices,
        ),
    }
    
    # Calculate risk metrics
    # IL break-even: how much price change can we tolerate?
    # At 50% APY, you can tolerate roughly 2x price change
    il_breakeven_multiplier = 1 + apy_data['total_apy'] / 100
    
    # Risk score (0-100, higher = riskier)
    risk_score = _calculate_farming_risk_score(
        apy=apy_data['total_apy'],
        tvl=pool_tvl_usd,
        daily_rewards=daily_reward_vcoin * vcoin_price,
    )
    
    # Recommendations
    recommendations = _generate_farming_recommendations(
        apy_data=apy_data,
        risk_score=risk_score,
        tvl=pool_tvl_usd,
    )
    
    return {
        'apy': apy_data,
        'il_scenarios': il_scenarios,
        'simulations': simulations,
        'risk_metrics': {
            'risk_score': round(risk_score, 1),
            'risk_level': 'Low' if risk_score < 30 else 'Moderate' if risk_score < 60 else 'High',
            'il_breakeven_multiplier': round(il_breakeven_multiplier, 2),
            'il_breakeven_price_up': round(vcoin_price * il_breakeven_multiplier, 4),
            'il_breakeven_price_down': round(vcoin_price / il_breakeven_multiplier, 4),
        },
        'recommendations': recommendations,
    }


def _calculate_farming_risk_score(
    apy: float,
    tvl: float,
    daily_rewards: float,
) -> float:
    """Calculate farming risk score (0-100)."""
    score = 30  # Base score
    
    # High APY = higher risk (unsustainability)
    if apy > 200:
        score += 30
    elif apy > 100:
        score += 20
    elif apy > 50:
        score += 10
    
    # Low TVL = higher risk (IL impact, manipulation)
    if tvl < 100_000:
        score += 25
    elif tvl < 500_000:
        score += 15
    elif tvl < 1_000_000:
        score += 5
    
    # High reward-to-TVL ratio = emission dilution risk
    if daily_rewards > 0 and tvl > 0:
        reward_ratio = (daily_rewards * 365) / tvl
        if reward_ratio > 2:
            score += 15
        elif reward_ratio > 1:
            score += 5
    
    return max(0, min(100, score))


def _generate_farming_recommendations(
    apy_data: Dict,
    risk_score: float,
    tvl: float,
) -> List[str]:
    """Generate farming recommendations."""
    recs = []
    
    if apy_data['total_apy'] > 100:
        recs.append("⚠️ High APY (>100%) - Consider taking profits regularly as this may not be sustainable")
    
    if not apy_data['is_sustainable']:
        recs.append("🔴 Reward APY exceeds 100% - High risk of IL outpacing rewards if price drops")
    
    if tvl < 500_000:
        recs.append("💧 Low TVL pool - Higher slippage and IL risk, consider smaller positions")
    
    if risk_score >= 60:
        recs.append("🚨 High risk score - Only invest what you can afford to lose")
    elif risk_score >= 30:
        recs.append("⚡ Moderate risk - Monitor position regularly and set exit targets")
    else:
        recs.append("✅ Lower risk profile - Still monitor for market changes")
    
    # General advice
    recs.append("📊 Consider IL calculator before entering - breakeven typically requires >30% APY for volatile pairs")
    recs.append("🔄 Compound rewards regularly to maximize returns")
    
    return recs


def _empty_farming_result() -> Dict:
    """Return empty result when TVL is 0."""
    return {
        'reward_apr': 0,
        'fee_apr': 0,
        'total_apr': 0,
        'reward_apy': 0,
        'fee_apy': 0,
        'total_apy': 0,
        'daily_reward_rate': 0,
        'daily_total_rate': 0,
        'pool_tvl_usd': 0,
        'daily_reward_vcoin': 0,
        'daily_reward_usd': 0,
        'time_horizon_days': 365,
        'final_value_multiplier': 1,
        'example_1000_final': 1000,
        'example_1000_profit': 0,
        'is_sustainable': True,
        'sustainability_warning': 'No TVL data',
    }

