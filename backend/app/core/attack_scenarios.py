"""
Economic Attack Simulation Module

2025 Industry Compliance: Models various DeFi attack vectors
and their potential impact on the token economy.

Attack Types Modeled:
1. Flash Loan Attacks - Exploit price oracles or liquidity
2. Sandwich Attacks - Front/back-running trades
3. MEV (Maximal Extractable Value) - Validator/sequencer extraction
4. Rug Pull Risk - Team/whale dump scenarios
5. Oracle Manipulation - Price feed attacks
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import math


@dataclass
class AttackScenario:
    """Base class for attack scenarios"""
    name: str
    category: str  # flash_loan, sandwich, mev, rug_pull, oracle
    description: str
    probability: float  # 0-1, likelihood of this attack
    severity: str  # low, medium, high, critical
    potential_loss_usd: float
    potential_loss_percent: float
    mitigation_effectiveness: float  # 0-100, how well current setup prevents this
    recovery_time_days: int
    

def calculate_attack_scenarios(
    token_price: float,
    circulating_supply: float,
    liquidity_pool_usd: float,
    daily_volume_usd: float,
    staking_tvl_usd: float,
    governance_voting_power_top_10: float,  # % of votes held by top 10
    team_token_percentage: float,
    vesting_remaining_months: int,
    oracle_type: str = "chainlink",  # chainlink, twap, centralized
    has_timelock: bool = True,
    timelock_delay_hours: int = 48,
    has_multisig: bool = True,
    multisig_threshold: int = 3,
    slippage_tolerance: float = 0.5,  # %
) -> Dict:
    """
    Calculate comprehensive attack scenario analysis.
    
    Returns vulnerability scores and specific attack simulations.
    """
    market_cap = token_price * circulating_supply
    
    # Calculate base vulnerability metrics
    liquidity_ratio = liquidity_pool_usd / market_cap if market_cap > 0 else 0
    volume_to_liquidity = daily_volume_usd / liquidity_pool_usd if liquidity_pool_usd > 0 else 0
    
    attack_scenarios = []
    
    # === 1. FLASH LOAN ATTACKS ===
    flash_loan_scenarios = _calculate_flash_loan_attacks(
        token_price=token_price,
        liquidity_pool_usd=liquidity_pool_usd,
        oracle_type=oracle_type,
        market_cap=market_cap,
    )
    attack_scenarios.extend(flash_loan_scenarios)
    
    # === 2. SANDWICH ATTACKS ===
    sandwich_scenarios = _calculate_sandwich_attacks(
        daily_volume_usd=daily_volume_usd,
        liquidity_pool_usd=liquidity_pool_usd,
        slippage_tolerance=slippage_tolerance,
    )
    attack_scenarios.extend(sandwich_scenarios)
    
    # === 3. MEV EXTRACTION ===
    mev_scenarios = _calculate_mev_extraction(
        daily_volume_usd=daily_volume_usd,
        staking_tvl_usd=staking_tvl_usd,
    )
    attack_scenarios.extend(mev_scenarios)
    
    # === 4. RUG PULL RISK ===
    rug_pull_scenarios = _calculate_rug_pull_risk(
        team_token_percentage=team_token_percentage,
        vesting_remaining_months=vesting_remaining_months,
        liquidity_pool_usd=liquidity_pool_usd,
        market_cap=market_cap,
        has_timelock=has_timelock,
        has_multisig=has_multisig,
    )
    attack_scenarios.extend(rug_pull_scenarios)
    
    # === 5. ORACLE MANIPULATION ===
    oracle_scenarios = _calculate_oracle_manipulation(
        oracle_type=oracle_type,
        liquidity_pool_usd=liquidity_pool_usd,
        staking_tvl_usd=staking_tvl_usd,
    )
    attack_scenarios.extend(oracle_scenarios)
    
    # === 6. GOVERNANCE ATTACKS ===
    governance_scenarios = _calculate_governance_attacks(
        governance_voting_power_top_10=governance_voting_power_top_10,
        has_timelock=has_timelock,
        timelock_delay_hours=timelock_delay_hours,
        market_cap=market_cap,
    )
    attack_scenarios.extend(governance_scenarios)
    
    # Calculate overall risk scores
    total_potential_loss = sum(s['potential_loss_usd'] for s in attack_scenarios)
    avg_severity_score = _calculate_severity_score(attack_scenarios)
    
    # Overall vulnerability score (0-100, higher = more vulnerable)
    vulnerability_score = _calculate_vulnerability_score(
        liquidity_ratio=liquidity_ratio,
        oracle_type=oracle_type,
        has_timelock=has_timelock,
        has_multisig=has_multisig,
        governance_concentration=governance_voting_power_top_10,
        team_tokens=team_token_percentage,
    )
    
    # Risk level
    if vulnerability_score >= 70:
        risk_level = "Critical"
        risk_color = "red"
    elif vulnerability_score >= 50:
        risk_level = "High"
        risk_color = "orange"
    elif vulnerability_score >= 30:
        risk_level = "Moderate"
        risk_color = "amber"
    else:
        risk_level = "Low"
        risk_color = "emerald"
    
    # Generate recommendations
    recommendations = _generate_attack_recommendations(
        vulnerability_score=vulnerability_score,
        attack_scenarios=attack_scenarios,
        has_timelock=has_timelock,
        has_multisig=has_multisig,
        oracle_type=oracle_type,
    )
    
    return {
        'vulnerability_score': round(vulnerability_score, 1),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'total_potential_loss_usd': round(total_potential_loss, 2),
        'avg_severity_score': round(avg_severity_score, 1),
        
        # Metrics used
        'market_cap': market_cap,
        'liquidity_ratio': round(liquidity_ratio * 100, 2),
        'volume_to_liquidity': round(volume_to_liquidity, 2),
        
        # Security features
        'security_features': {
            'has_timelock': has_timelock,
            'timelock_delay_hours': timelock_delay_hours,
            'has_multisig': has_multisig,
            'multisig_threshold': multisig_threshold,
            'oracle_type': oracle_type,
        },
        
        # Attack scenarios by category
        'scenarios': attack_scenarios,
        'scenarios_by_category': _group_by_category(attack_scenarios),
        
        # Recommendations
        'recommendations': recommendations,
    }


def _calculate_flash_loan_attacks(
    token_price: float,
    liquidity_pool_usd: float,
    oracle_type: str,
    market_cap: float,
) -> List[Dict]:
    """Model flash loan attack scenarios."""
    scenarios = []
    
    # Oracle vulnerability factor
    oracle_vuln = {
        'centralized': 0.8,
        'twap': 0.4,
        'chainlink': 0.15,
        'pyth': 0.15,
    }.get(oracle_type.lower(), 0.5)
    
    # Scenario 1: Oracle price manipulation
    # Attacker uses flash loan to manipulate AMM price, drain lending protocol
    manipulation_amount = liquidity_pool_usd * 0.5  # 50% of pool
    price_impact = manipulation_amount / (liquidity_pool_usd * 2)
    potential_profit = manipulation_amount * price_impact * oracle_vuln
    
    scenarios.append({
        'name': 'Oracle Price Manipulation',
        'category': 'flash_loan',
        'description': 'Flash loan to manipulate AMM price and exploit price-dependent protocols',
        'attack_vector': 'Borrow large amount → Manipulate AMM price → Exploit oracle-dependent protocol → Repay loan',
        'probability': 0.15 * oracle_vuln,
        'severity': 'critical' if oracle_vuln > 0.5 else 'high',
        'potential_loss_usd': round(potential_profit, 2),
        'potential_loss_percent': round(potential_profit / market_cap * 100, 2) if market_cap > 0 else 0,
        'mitigation_effectiveness': (1 - oracle_vuln) * 100,
        'recovery_time_days': 7,
        'required_capital': 0,  # Flash loans are free
        'complexity': 'high',
    })
    
    # Scenario 2: Liquidity drain
    drain_amount = liquidity_pool_usd * 0.3
    scenarios.append({
        'name': 'Liquidity Pool Drain',
        'category': 'flash_loan',
        'description': 'Exploit AMM arbitrage or rounding errors to drain liquidity',
        'attack_vector': 'Flash loan → Execute many small trades → Accumulate rounding profits → Repay',
        'probability': 0.05,
        'severity': 'medium',
        'potential_loss_usd': round(drain_amount * 0.01, 2),  # 1% of 30%
        'potential_loss_percent': round(drain_amount * 0.01 / market_cap * 100, 4) if market_cap > 0 else 0,
        'mitigation_effectiveness': 80,  # Most AMMs fixed this
        'recovery_time_days': 1,
        'required_capital': 0,
        'complexity': 'medium',
    })
    
    return scenarios


def _calculate_sandwich_attacks(
    daily_volume_usd: float,
    liquidity_pool_usd: float,
    slippage_tolerance: float,
) -> List[Dict]:
    """Model sandwich attack (front-running) scenarios."""
    scenarios = []
    
    # Average trade size estimation
    avg_trade_size = daily_volume_usd / 100  # Assume 100 trades/day
    
    # Sandwich profit per trade = slippage captured
    profit_per_trade = avg_trade_size * (slippage_tolerance / 100) * 0.5  # 50% capture rate
    daily_sandwich_profit = profit_per_trade * 20  # ~20 sandwichable trades
    annual_loss = daily_sandwich_profit * 365
    
    scenarios.append({
        'name': 'DEX Sandwich Attack',
        'category': 'sandwich',
        'description': 'Front-run and back-run large swaps to extract value from slippage',
        'attack_vector': 'Monitor mempool → Front-run victim trade → Back-run to capture profit',
        'probability': 0.95,  # Very common on DEXs
        'severity': 'medium',
        'potential_loss_usd': round(annual_loss, 2),
        'potential_loss_percent': round(annual_loss / (daily_volume_usd * 365) * 100, 2) if daily_volume_usd > 0 else 0,
        'mitigation_effectiveness': 30,  # Hard to prevent
        'recovery_time_days': 0,  # Ongoing, no recovery needed
        'required_capital': avg_trade_size * 2,
        'complexity': 'medium',
        'daily_extraction': round(daily_sandwich_profit, 2),
    })
    
    # JIT (Just-In-Time) Liquidity Attack
    jit_profit = daily_volume_usd * 0.001  # 0.1% of volume
    scenarios.append({
        'name': 'JIT Liquidity Attack',
        'category': 'sandwich',
        'description': 'Add liquidity just before large trade, remove after, capturing fees',
        'attack_vector': 'Monitor pending trades → Add concentrated liquidity → Capture fees → Remove liquidity',
        'probability': 0.7,
        'severity': 'low',
        'potential_loss_usd': round(jit_profit * 365, 2),
        'potential_loss_percent': round(jit_profit / daily_volume_usd * 100, 3) if daily_volume_usd > 0 else 0,
        'mitigation_effectiveness': 20,
        'recovery_time_days': 0,
        'required_capital': liquidity_pool_usd * 0.1,
        'complexity': 'high',
    })
    
    return scenarios


def _calculate_mev_extraction(
    daily_volume_usd: float,
    staking_tvl_usd: float,
) -> List[Dict]:
    """Model MEV extraction scenarios."""
    scenarios = []
    
    # Solana-specific: validator MEV
    # Estimate 0.1-0.3% of volume extracted as MEV
    mev_rate = 0.002  # 0.2%
    daily_mev = daily_volume_usd * mev_rate
    annual_mev = daily_mev * 365
    
    scenarios.append({
        'name': 'Validator MEV Extraction',
        'category': 'mev',
        'description': 'Validators reorder transactions to extract maximum value',
        'attack_vector': 'Validator receives transactions → Reorders for profit → Includes own transactions',
        'probability': 0.99,  # Constant on most chains
        'severity': 'medium',
        'potential_loss_usd': round(annual_mev, 2),
        'potential_loss_percent': round(annual_mev / (daily_volume_usd * 365) * 100, 3) if daily_volume_usd > 0 else 0,
        'mitigation_effectiveness': 10,  # Protocol-level issue
        'recovery_time_days': 0,
        'required_capital': 0,  # Validators need existing stake
        'complexity': 'low',
        'daily_extraction': round(daily_mev, 2),
    })
    
    # Liquidation MEV
    liquidation_mev = staking_tvl_usd * 0.001  # 0.1% of TVL at risk
    scenarios.append({
        'name': 'Liquidation MEV',
        'category': 'mev',
        'description': 'Searchers compete to liquidate underwater positions',
        'attack_vector': 'Monitor positions → Trigger liquidation → Capture liquidation bonus',
        'probability': 0.5,
        'severity': 'low',
        'potential_loss_usd': round(liquidation_mev, 2),
        'potential_loss_percent': round(liquidation_mev / staking_tvl_usd * 100, 3) if staking_tvl_usd > 0 else 0,
        'mitigation_effectiveness': 50,
        'recovery_time_days': 0,
        'required_capital': 10000,  # Gas + liquidation capital
        'complexity': 'medium',
    })
    
    return scenarios


def _calculate_rug_pull_risk(
    team_token_percentage: float,
    vesting_remaining_months: int,
    liquidity_pool_usd: float,
    market_cap: float,
    has_timelock: bool,
    has_multisig: bool,
) -> List[Dict]:
    """Model rug pull risk scenarios."""
    scenarios = []
    
    # Risk factors
    team_risk = min(1, team_token_percentage / 30)  # 30%+ team = max risk
    vesting_risk = max(0, 1 - vesting_remaining_months / 48)  # 4 years vesting = low risk
    
    # Timelock/multisig reduce risk
    security_factor = 1.0
    if has_timelock:
        security_factor *= 0.5
    if has_multisig:
        security_factor *= 0.6
    
    overall_rug_risk = team_risk * (1 - vesting_risk * 0.5) * security_factor
    
    # Scenario: Coordinated team dump
    dump_amount = market_cap * (team_token_percentage / 100)
    price_impact = min(0.9, dump_amount / (liquidity_pool_usd * 2))  # Max 90% crash
    actual_loss = dump_amount * (1 - price_impact * 0.5)  # Slippage reduces extracted value
    
    scenarios.append({
        'name': 'Coordinated Team Dump',
        'category': 'rug_pull',
        'description': 'Team sells all unlocked tokens simultaneously',
        'attack_vector': 'Team coordinates → Sells through multiple channels → Drains liquidity',
        'probability': round(overall_rug_risk * 0.1, 3),  # Base 10% chance, modified by risk
        'severity': 'critical',
        'potential_loss_usd': round(actual_loss, 2),
        'potential_loss_percent': round(price_impact * 100, 1),
        'mitigation_effectiveness': round((1 - overall_rug_risk) * 100, 1),
        'recovery_time_days': 180,  # 6 months minimum
        'required_capital': 0,  # Team already has tokens
        'complexity': 'low',
        'team_token_at_risk': round(dump_amount, 2),
        'vesting_protection': vesting_remaining_months > 0,
    })
    
    # Scenario: Liquidity removal (if team controls LP)
    lp_removal_loss = liquidity_pool_usd * 0.5  # Assume 50% team-controlled
    scenarios.append({
        'name': 'Liquidity Pool Removal',
        'category': 'rug_pull',
        'description': 'Team removes liquidity, making token untradeable',
        'attack_vector': 'Team removes LP tokens → Token becomes illiquid → Price crashes',
        'probability': round(overall_rug_risk * 0.05, 3),
        'severity': 'critical',
        'potential_loss_usd': round(lp_removal_loss, 2),
        'potential_loss_percent': round(lp_removal_loss / market_cap * 100, 1) if market_cap > 0 else 0,
        'mitigation_effectiveness': 70 if has_timelock else 30,
        'recovery_time_days': 365,
        'required_capital': 0,
        'complexity': 'low',
    })
    
    return scenarios


def _calculate_oracle_manipulation(
    oracle_type: str,
    liquidity_pool_usd: float,
    staking_tvl_usd: float,
) -> List[Dict]:
    """Model oracle manipulation scenarios."""
    scenarios = []
    
    # Oracle vulnerability scores
    oracle_security = {
        'chainlink': 95,
        'pyth': 90,
        'twap': 70,
        'centralized': 30,
    }.get(oracle_type.lower(), 50)
    
    vulnerability = (100 - oracle_security) / 100
    
    # Scenario: Price feed manipulation
    max_exploit = min(staking_tvl_usd, liquidity_pool_usd) * vulnerability
    
    scenarios.append({
        'name': 'Oracle Price Manipulation',
        'category': 'oracle',
        'description': f'Exploit {oracle_type} oracle to report incorrect prices',
        'attack_vector': 'Manipulate price source → Oracle reports wrong price → Exploit dependent protocols',
        'probability': round(vulnerability * 0.2, 3),
        'severity': 'critical' if oracle_security < 50 else 'high' if oracle_security < 80 else 'low',
        'potential_loss_usd': round(max_exploit, 2),
        'potential_loss_percent': round(max_exploit / staking_tvl_usd * 100, 1) if staking_tvl_usd > 0 else 0,
        'mitigation_effectiveness': oracle_security,
        'recovery_time_days': 3,
        'required_capital': liquidity_pool_usd * 0.5 if oracle_type.lower() == 'twap' else 0,
        'complexity': 'high',
        'oracle_type': oracle_type,
    })
    
    return scenarios


def _calculate_governance_attacks(
    governance_voting_power_top_10: float,
    has_timelock: bool,
    timelock_delay_hours: int,
    market_cap: float,
) -> List[Dict]:
    """Model governance attack scenarios."""
    scenarios = []
    
    # Voting concentration risk
    concentration_risk = governance_voting_power_top_10 / 100
    
    # Cost to acquire 51% voting power
    voting_cost = market_cap * (0.51 - concentration_risk / 2)  # Discount if concentrated
    
    # Timelock protection
    timelock_protection = min(1, timelock_delay_hours / 72)  # 72h = good protection
    
    scenarios.append({
        'name': '51% Governance Attack',
        'category': 'governance',
        'description': 'Acquire majority voting power to pass malicious proposals',
        'attack_vector': 'Accumulate/borrow voting tokens → Submit malicious proposal → Vote to pass',
        'probability': round(0.1 * concentration_risk * (1 - timelock_protection), 3),
        'severity': 'critical',
        'potential_loss_usd': round(market_cap * 0.3, 2),  # Could drain 30% of value
        'potential_loss_percent': 30,
        'mitigation_effectiveness': round((1 - concentration_risk) * timelock_protection * 100, 1),
        'recovery_time_days': 30,
        'required_capital': round(voting_cost, 2),
        'complexity': 'high',
        'voting_power_needed': 51,
        'timelock_delay': timelock_delay_hours,
    })
    
    # Flash loan governance attack
    if not has_timelock:
        scenarios.append({
            'name': 'Flash Loan Governance Attack',
            'category': 'governance',
            'description': 'Borrow voting tokens via flash loan to pass instant proposals',
            'attack_vector': 'Flash borrow tokens → Vote on proposal → Execute immediately → Repay',
            'probability': 0.3 if not has_timelock else 0.01,
            'severity': 'critical',
            'potential_loss_usd': round(market_cap * 0.5, 2),
            'potential_loss_percent': 50,
            'mitigation_effectiveness': 10 if not has_timelock else 90,
            'recovery_time_days': 60,
            'required_capital': 0,
            'complexity': 'high',
        })
    
    return scenarios


def _calculate_severity_score(scenarios: List[Dict]) -> float:
    """Calculate average severity score from scenarios."""
    severity_values = {'low': 25, 'medium': 50, 'high': 75, 'critical': 100}
    if not scenarios:
        return 0
    
    total = sum(severity_values.get(s.get('severity', 'low'), 25) for s in scenarios)
    return total / len(scenarios)


def _calculate_vulnerability_score(
    liquidity_ratio: float,
    oracle_type: str,
    has_timelock: bool,
    has_multisig: bool,
    governance_concentration: float,
    team_tokens: float,
) -> float:
    """Calculate overall vulnerability score (0-100)."""
    score = 50  # Base score
    
    # Liquidity ratio (lower = more vulnerable)
    if liquidity_ratio < 0.02:
        score += 20
    elif liquidity_ratio < 0.05:
        score += 10
    elif liquidity_ratio > 0.1:
        score -= 10
    
    # Oracle type
    oracle_scores = {'chainlink': -15, 'pyth': -12, 'twap': 0, 'centralized': 20}
    score += oracle_scores.get(oracle_type.lower(), 5)
    
    # Security features
    if has_timelock:
        score -= 10
    if has_multisig:
        score -= 10
    
    # Governance concentration
    score += governance_concentration * 0.2  # Max +20 for 100% concentration
    
    # Team tokens
    if team_tokens > 30:
        score += 15
    elif team_tokens > 20:
        score += 8
    
    return max(0, min(100, score))


def _group_by_category(scenarios: List[Dict]) -> Dict[str, List[Dict]]:
    """Group scenarios by category."""
    grouped = {}
    for scenario in scenarios:
        category = scenario.get('category', 'other')
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(scenario)
    return grouped


def _generate_attack_recommendations(
    vulnerability_score: float,
    attack_scenarios: List[Dict],
    has_timelock: bool,
    has_multisig: bool,
    oracle_type: str,
) -> List[str]:
    """Generate security recommendations based on analysis."""
    recommendations = []
    
    # Critical vulnerabilities
    critical_scenarios = [s for s in attack_scenarios if s.get('severity') == 'critical']
    if critical_scenarios:
        recommendations.append(f"🚨 {len(critical_scenarios)} critical vulnerabilities identified - prioritize immediate fixes")
    
    # Timelock
    if not has_timelock:
        recommendations.append("⏰ Implement timelock (48-72h) for governance actions to prevent flash loan attacks")
    
    # Multisig
    if not has_multisig:
        recommendations.append("🔐 Deploy multisig (3/5 or 4/7) for admin functions and treasury")
    
    # Oracle
    if oracle_type.lower() in ['centralized', 'twap']:
        recommendations.append("🔮 Upgrade to Chainlink/Pyth oracles for manipulation resistance")
    
    # General
    if vulnerability_score >= 50:
        recommendations.append("🛡️ Consider bug bounty program to incentivize responsible disclosure")
        recommendations.append("📊 Implement real-time monitoring for unusual trading patterns")
    
    if vulnerability_score >= 70:
        recommendations.append("⚠️ High vulnerability score - consider security audit before mainnet")
        recommendations.append("🔒 Implement circuit breakers for extreme price movements")
    
    # MEV protection
    recommendations.append("⚡ Consider integrating MEV protection (e.g., Flashbots, Jito on Solana)")
    
    return recommendations

