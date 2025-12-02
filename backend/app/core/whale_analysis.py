"""
Whale Concentration Risk Analysis Module

2025 Industry Compliance: Tracks token concentration risks
and models whale dump scenarios.

Key Features:
- Top holder concentration tracking (Top 1%, 5%, 10%, 100)
- Whale dump scenario modeling
- Price impact estimation
- Concentration risk scoring
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import math


@dataclass
class WhaleHolder:
    """Represents a major token holder"""
    rank: int
    balance: float
    percentage: float
    category: str  # "whale", "large", "medium", "small"
    
    
@dataclass
class DumpScenario:
    """Results of a whale dump scenario"""
    scenario_name: str
    sellers_count: int
    sell_amount_vcoin: float
    sell_amount_usd: float
    sell_percentage: float  # % of their holdings sold
    price_impact_percent: float
    new_price: float
    liquidity_absorbed_percent: float
    market_cap_loss: float
    recovery_days_estimate: int
    severity: str  # "low", "medium", "high", "critical"


def calculate_whale_concentration(
    holder_balances: List[float],
    total_supply: float,
    token_price: float = 0.10,
    liquidity_pool_usd: float = 500_000,
) -> Dict:
    """
    Calculate comprehensive whale concentration metrics.
    
    Args:
        holder_balances: List of token balances (unsorted)
        total_supply: Total token supply
        token_price: Current token price in USD
        liquidity_pool_usd: Total liquidity in DEX pools
    
    Returns:
        Dict with concentration metrics and risk analysis
    """
    if not holder_balances or len(holder_balances) == 0:
        return _empty_result()
    
    # Sort descending (largest holders first)
    sorted_balances = sorted(holder_balances, reverse=True)
    n = len(sorted_balances)
    total_held = sum(sorted_balances)
    
    # Calculate top holder concentrations
    def get_concentration(top_n: int) -> Dict:
        top_holders = sorted_balances[:min(top_n, n)]
        amount = sum(top_holders)
        return {
            'holders_count': min(top_n, n),
            'amount_vcoin': amount,
            'amount_usd': amount * token_price,
            'percentage': (amount / total_supply * 100) if total_supply > 0 else 0,
            'avg_balance': amount / min(top_n, n) if top_n > 0 else 0,
        }
    
    # Top holder groups
    top_10 = get_concentration(10)
    top_50 = get_concentration(50)
    top_100 = get_concentration(100)
    
    # Percentile concentrations
    top_1_pct_idx = max(1, int(n * 0.01))
    top_5_pct_idx = max(1, int(n * 0.05))
    top_10_pct_idx = max(1, int(n * 0.10))
    
    top_1_percent = get_concentration(top_1_pct_idx)
    top_5_percent = get_concentration(top_5_pct_idx)
    top_10_percent = get_concentration(top_10_pct_idx)
    
    # Identify whale categories
    whales = []
    large_holders = []
    medium_holders = []
    small_holders = []
    
    for i, balance in enumerate(sorted_balances):
        pct = (balance / total_supply * 100) if total_supply > 0 else 0
        holder = WhaleHolder(
            rank=i + 1,
            balance=balance,
            percentage=pct,
            category="small"
        )
        
        if pct >= 1.0:  # 1%+ = whale
            holder.category = "whale"
            whales.append(holder)
        elif pct >= 0.1:  # 0.1-1% = large
            holder.category = "large"
            large_holders.append(holder)
        elif pct >= 0.01:  # 0.01-0.1% = medium
            holder.category = "medium"
            medium_holders.append(holder)
        else:
            small_holders.append(holder)
    
    # Calculate concentration risk score (0-100, higher = more risky)
    # Based on: top 10 concentration, whale count, Gini
    top_10_risk = min(100, top_10['percentage'] * 2)  # 50% top 10 = 100 risk
    whale_risk = min(100, len(whales) * 5)  # 20 whales = 100 risk (inverted - more whales = distributed)
    
    # Adjust: fewer whales with more % = higher risk
    if len(whales) > 0:
        avg_whale_pct = sum(w.percentage for w in whales) / len(whales)
        whale_concentration_risk = min(100, avg_whale_pct * 10)
    else:
        whale_concentration_risk = 0
    
    concentration_risk_score = (top_10_risk * 0.5 + whale_concentration_risk * 0.5)
    
    # Risk interpretation
    if concentration_risk_score >= 80:
        risk_level = "Critical"
        risk_color = "red"
    elif concentration_risk_score >= 60:
        risk_level = "High"
        risk_color = "orange"
    elif concentration_risk_score >= 40:
        risk_level = "Moderate"
        risk_color = "amber"
    else:
        risk_level = "Low"
        risk_color = "emerald"
    
    # Run dump scenarios
    dump_scenarios = run_dump_scenarios(
        sorted_balances[:100],  # Top 100 holders
        total_supply,
        token_price,
        liquidity_pool_usd
    )
    
    return {
        'holder_count': n,
        'total_supply': total_supply,
        'total_held': total_held,
        'token_price': token_price,
        
        # Top holder groups
        'top_10': top_10,
        'top_50': top_50,
        'top_100': top_100,
        
        # Percentile groups
        'top_1_percent': top_1_percent,
        'top_5_percent': top_5_percent,
        'top_10_percent': top_10_percent,
        
        # Whale breakdown
        'whale_count': len(whales),
        'large_holder_count': len(large_holders),
        'medium_holder_count': len(medium_holders),
        'small_holder_count': len(small_holders),
        
        'whales': [
            {
                'rank': w.rank,
                'balance': w.balance,
                'percentage': round(w.percentage, 4),
            } for w in whales[:20]  # Top 20 whales
        ],
        
        # Risk metrics
        'concentration_risk_score': round(concentration_risk_score, 1),
        'risk_level': risk_level,
        'risk_color': risk_color,
        
        # Dump scenarios
        'dump_scenarios': dump_scenarios,
        
        # Recommendations
        'recommendations': _generate_recommendations(
            concentration_risk_score,
            len(whales),
            top_10['percentage']
        ),
    }


def run_dump_scenarios(
    top_holders: List[float],
    total_supply: float,
    token_price: float,
    liquidity_pool_usd: float,
) -> List[Dict]:
    """
    Model various whale dump scenarios.
    
    Scenarios:
    1. Top 1 holder sells 50%
    2. Top 10 holders sell 25%
    3. Top 10 holders sell 50%
    4. Top 50 holders sell 10%
    5. Coordinated dump (top 100 sell 25%)
    """
    scenarios = []
    
    # Calculate price impact using constant product AMM formula
    # price_impact = sell_amount / (2 * liquidity_pool_usd)
    # More sophisticated: use square root price impact model
    def calculate_price_impact(sell_usd: float) -> float:
        if liquidity_pool_usd <= 0:
            return 100  # Complete crash
        
        # Uniswap v2 style: x * y = k
        # Price impact ≈ sell_amount / (liquidity + sell_amount)
        impact = (sell_usd / (liquidity_pool_usd + sell_usd)) * 100
        
        # Add slippage multiplier for larger sells
        if sell_usd > liquidity_pool_usd * 0.5:
            impact *= 1.5  # 50% more impact for large sells
        
        return min(99, impact)  # Cap at 99%
    
    def create_scenario(
        name: str,
        holders_to_sell: List[float],
        sell_percentage: float
    ) -> Dict:
        sell_amount = sum(holders_to_sell) * (sell_percentage / 100)
        sell_usd = sell_amount * token_price
        
        price_impact = calculate_price_impact(sell_usd)
        new_price = token_price * (1 - price_impact / 100)
        
        liquidity_absorbed = (sell_usd / liquidity_pool_usd * 100) if liquidity_pool_usd > 0 else 100
        market_cap_loss = total_supply * (token_price - new_price)
        
        # Estimate recovery time (days)
        # Based on: 1% recovery per day for small impacts, slower for larger
        if price_impact < 10:
            recovery_days = int(price_impact * 2)
        elif price_impact < 30:
            recovery_days = int(price_impact * 4)
        elif price_impact < 50:
            recovery_days = int(price_impact * 7)
        else:
            recovery_days = int(price_impact * 14)
        
        # Severity
        if price_impact >= 50:
            severity = "critical"
        elif price_impact >= 30:
            severity = "high"
        elif price_impact >= 15:
            severity = "medium"
        else:
            severity = "low"
        
        return {
            'scenario_name': name,
            'sellers_count': len(holders_to_sell),
            'sell_amount_vcoin': round(sell_amount, 2),
            'sell_amount_usd': round(sell_usd, 2),
            'sell_percentage': sell_percentage,
            'price_impact_percent': round(price_impact, 2),
            'new_price': round(new_price, 6),
            'liquidity_absorbed_percent': round(min(100, liquidity_absorbed), 1),
            'market_cap_loss': round(market_cap_loss, 2),
            'recovery_days_estimate': recovery_days,
            'severity': severity,
        }
    
    # Scenario 1: Top 1 sells 50%
    if len(top_holders) >= 1:
        scenarios.append(create_scenario(
            "Top 1 Holder Sells 50%",
            top_holders[:1],
            50
        ))
    
    # Scenario 2: Top 10 sell 25%
    if len(top_holders) >= 10:
        scenarios.append(create_scenario(
            "Top 10 Holders Sell 25%",
            top_holders[:10],
            25
        ))
    
    # Scenario 3: Top 10 sell 50%
    if len(top_holders) >= 10:
        scenarios.append(create_scenario(
            "Top 10 Holders Sell 50%",
            top_holders[:10],
            50
        ))
    
    # Scenario 4: Top 50 sell 10%
    if len(top_holders) >= 50:
        scenarios.append(create_scenario(
            "Top 50 Holders Sell 10%",
            top_holders[:50],
            10
        ))
    
    # Scenario 5: Coordinated dump
    scenarios.append(create_scenario(
        "Coordinated Dump (Top 100 Sell 25%)",
        top_holders[:min(100, len(top_holders))],
        25
    ))
    
    return scenarios


def _generate_recommendations(
    risk_score: float,
    whale_count: int,
    top_10_pct: float
) -> List[str]:
    """Generate actionable recommendations based on concentration metrics."""
    recommendations = []
    
    if risk_score >= 70:
        recommendations.append("🚨 Critical: Consider implementing vesting schedules for large holders")
        recommendations.append("🔒 Implement sell limits or time-locks for whale wallets")
    
    if top_10_pct > 50:
        recommendations.append("📊 Top 10 holders control >50% - encourage broader distribution")
        recommendations.append("💧 Increase liquidity to reduce price impact of large sells")
    
    if whale_count < 5 and top_10_pct > 30:
        recommendations.append("⚠️ Few whales with high concentration - monitor closely")
    
    if whale_count > 20:
        recommendations.append("✅ Good whale distribution - maintain through fair launches")
    
    if risk_score < 40:
        recommendations.append("✅ Healthy token distribution - maintain current strategy")
    
    return recommendations


def _empty_result() -> Dict:
    """Return empty result when no holders."""
    return {
        'holder_count': 0,
        'total_supply': 0,
        'total_held': 0,
        'token_price': 0,
        'top_10': {'holders_count': 0, 'amount_vcoin': 0, 'amount_usd': 0, 'percentage': 0, 'avg_balance': 0},
        'top_50': {'holders_count': 0, 'amount_vcoin': 0, 'amount_usd': 0, 'percentage': 0, 'avg_balance': 0},
        'top_100': {'holders_count': 0, 'amount_vcoin': 0, 'amount_usd': 0, 'percentage': 0, 'avg_balance': 0},
        'top_1_percent': {'holders_count': 0, 'amount_vcoin': 0, 'amount_usd': 0, 'percentage': 0, 'avg_balance': 0},
        'top_5_percent': {'holders_count': 0, 'amount_vcoin': 0, 'amount_usd': 0, 'percentage': 0, 'avg_balance': 0},
        'top_10_percent': {'holders_count': 0, 'amount_vcoin': 0, 'amount_usd': 0, 'percentage': 0, 'avg_balance': 0},
        'whale_count': 0,
        'large_holder_count': 0,
        'medium_holder_count': 0,
        'small_holder_count': 0,
        'whales': [],
        'concentration_risk_score': 0,
        'risk_level': 'Unknown',
        'risk_color': 'gray',
        'dump_scenarios': [],
        'recommendations': ['No holder data available'],
    }

