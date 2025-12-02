"""
Game Theory Analysis Module

2025 Industry Compliance: Models rational actor behavior,
Nash equilibria, and strategic decision-making in tokenomics.

Key Features:
1. Staking vs Selling Nash Equilibrium
2. Rational Actor Behavior Modeling
3. Prisoner's Dilemma for Governance
4. Optimal Strategy Analysis
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class Strategy:
    """Represents a player strategy"""
    name: str
    expected_return: float
    risk_level: float
    probability: float  # Probability of choosing this strategy


@dataclass 
class NashEquilibrium:
    """Nash equilibrium result"""
    strategy_profile: Dict[str, str]  # player -> strategy
    is_stable: bool
    deviation_incentive: float  # % gain from deviating
    description: str


def analyze_staking_vs_selling(
    staking_apy: float,
    expected_price_change: float,  # Annual expected price change %
    price_volatility: float,  # Standard deviation of price
    lock_period_months: int,
    early_unstake_penalty: float,  # % penalty
    sell_slippage: float = 0.5,  # % slippage when selling
    time_horizon_months: int = 12,
) -> Dict:
    """
    Analyze the Nash equilibrium between staking and selling.
    
    This models a 2-player game where each player can:
    - STAKE: Lock tokens for APY rewards
    - SELL: Exit position immediately
    - HOLD: Keep tokens without staking
    
    Returns equilibrium analysis and optimal strategy.
    """
    # Calculate expected returns for each strategy
    
    # STAKE strategy
    # Monthly compounding of staking rewards
    monthly_apy = (1 + staking_apy / 100) ** (1/12) - 1
    stake_return = (1 + monthly_apy) ** time_horizon_months - 1
    
    # Factor in price change
    price_multiplier = 1 + expected_price_change / 100
    stake_total_return = (1 + stake_return) * price_multiplier - 1
    
    # Risk: locked capital + price volatility
    stake_risk = (lock_period_months / 12) * price_volatility / 100 + early_unstake_penalty / 100
    
    # SELL strategy
    # Immediate exit, capture current value minus slippage
    sell_return = -sell_slippage / 100  # Just lose slippage
    sell_risk = 0  # No further risk after selling
    
    # HOLD strategy
    # Keep tokens, no staking rewards, exposed to price change
    hold_return = expected_price_change / 100
    hold_risk = price_volatility / 100
    
    # Calculate risk-adjusted returns (Sharpe-like ratio)
    def risk_adjusted_return(ret: float, risk: float) -> float:
        if risk <= 0:
            return ret * 100  # If no risk, just return the raw return
        return ret / risk
    
    stake_rar = risk_adjusted_return(stake_total_return, stake_risk)
    sell_rar = risk_adjusted_return(sell_return, max(0.01, sell_risk))
    hold_rar = risk_adjusted_return(hold_return, max(0.01, hold_risk))
    
    # Determine dominant strategy
    strategies = {
        'stake': {'return': stake_total_return * 100, 'risk': stake_risk * 100, 'rar': stake_rar},
        'sell': {'return': sell_return * 100, 'risk': sell_risk * 100, 'rar': sell_rar},
        'hold': {'return': hold_return * 100, 'risk': hold_risk * 100, 'rar': hold_rar},
    }
    
    # Find Nash equilibrium
    # In this simplified model, we assume:
    # - If staking return > hold return, rational actors stake
    # - If price expected to drop significantly, rational actors sell
    
    best_strategy = max(strategies.keys(), key=lambda s: strategies[s]['rar'])
    
    # Calculate equilibrium ratios
    # Based on expected returns, estimate % of actors choosing each strategy
    total_rar = abs(stake_rar) + abs(sell_rar) + abs(hold_rar)
    if total_rar > 0:
        stake_prob = max(0, stake_rar) / total_rar if stake_rar > 0 else 0
        sell_prob = max(0, sell_rar) / total_rar if sell_rar > 0 else 0
        hold_prob = max(0, hold_rar) / total_rar if hold_rar > 0 else 0
        
        # Normalize
        total_prob = stake_prob + sell_prob + hold_prob
        if total_prob > 0:
            stake_prob /= total_prob
            sell_prob /= total_prob
            hold_prob /= total_prob
    else:
        stake_prob = hold_prob = sell_prob = 1/3
    
    # Equilibrium stability
    # If one strategy dominates (>60%), equilibrium is unstable
    max_prob = max(stake_prob, sell_prob, hold_prob)
    is_stable = max_prob < 0.6
    
    # Deviation incentive: how much better is best vs second-best?
    sorted_strategies = sorted(strategies.items(), key=lambda x: x[1]['rar'], reverse=True)
    if len(sorted_strategies) >= 2:
        deviation_incentive = sorted_strategies[0][1]['rar'] - sorted_strategies[1][1]['rar']
    else:
        deviation_incentive = 0
    
    # Generate interpretation
    if best_strategy == 'stake':
        interpretation = f"Staking is the dominant strategy with {stake_total_return*100:.1f}% expected return"
        recommendation = "Lock tokens for staking rewards - APY compensates for lock-up risk"
    elif best_strategy == 'sell':
        interpretation = f"Selling is optimal due to negative expected returns or high risk"
        recommendation = "Consider reducing position - fundamentals don't support holding"
    else:
        interpretation = f"Holding without staking is optimal - rewards don't justify lock-up"
        recommendation = "Keep liquid position to maintain flexibility"
    
    return {
        'strategies': strategies,
        'equilibrium': {
            'stake_probability': round(stake_prob * 100, 1),
            'sell_probability': round(sell_prob * 100, 1),
            'hold_probability': round(hold_prob * 100, 1),
            'dominant_strategy': best_strategy,
            'is_stable': is_stable,
            'deviation_incentive': round(deviation_incentive, 2),
        },
        'analysis': {
            'best_strategy': best_strategy,
            'interpretation': interpretation,
            'recommendation': recommendation,
            'staking_breakeven_price_drop': round(_calculate_staking_breakeven(staking_apy, time_horizon_months), 1),
        },
        'parameters': {
            'staking_apy': staking_apy,
            'expected_price_change': expected_price_change,
            'price_volatility': price_volatility,
            'lock_period_months': lock_period_months,
            'time_horizon_months': time_horizon_months,
        },
    }


def _calculate_staking_breakeven(apy: float, months: int) -> float:
    """Calculate how much price can drop before staking becomes unprofitable."""
    # Staking return over period
    staking_return = (1 + apy / 100) ** (months / 12) - 1
    # Price can drop by staking_return before breakeven
    return staking_return * 100


def analyze_governance_game(
    voting_power_distribution: List[float],  # % held by each major holder
    proposal_value_usd: float,  # Value at stake in proposal
    quorum_threshold: float = 0.10,  # 10% quorum
    passing_threshold: float = 0.50,  # 50% to pass
) -> Dict:
    """
    Analyze game theory dynamics of governance voting.
    
    Models:
    - Voting participation incentives
    - Coalition formation
    - Voter apathy problem
    """
    num_holders = len(voting_power_distribution)
    total_power = sum(voting_power_distribution)
    
    # Normalize to percentages
    voting_power = [v / total_power * 100 if total_power > 0 else 0 for v in voting_power_distribution]
    
    # Calculate pivot probability for each holder
    # A holder is pivotal if their vote changes the outcome
    pivot_probabilities = []
    for i, power in enumerate(voting_power):
        # Simplified: pivotal if power > remaining gap to threshold
        others_power = sum(voting_power) - power
        # Probability of being pivotal ≈ power / (50 - others_expected)
        pivot_prob = min(1, power / (100 - passing_threshold * 100)) if power > 0 else 0
        pivot_probabilities.append(round(pivot_prob * 100, 2))
    
    # Voting cost-benefit analysis
    # Cost: time, gas, attention
    voting_cost_usd = 5  # Estimated cost to vote
    
    # Expected benefit = pivot_probability * value_at_stake
    expected_benefits = []
    for pivot_prob in pivot_probabilities:
        benefit = (pivot_prob / 100) * proposal_value_usd
        expected_benefits.append(round(benefit, 2))
    
    # Rational participation: only vote if benefit > cost
    rational_participants = sum(1 for b in expected_benefits if b > voting_cost_usd)
    
    # Check if quorum is achievable
    participating_power = sum(p for p, b in zip(voting_power, expected_benefits) if b > voting_cost_usd)
    quorum_achievable = participating_power >= quorum_threshold * 100
    
    # Coalition analysis
    # Find minimum winning coalition
    sorted_holders = sorted(enumerate(voting_power), key=lambda x: x[1], reverse=True)
    coalition_power = 0
    coalition_members = []
    for idx, power in sorted_holders:
        coalition_power += power
        coalition_members.append(idx)
        if coalition_power >= passing_threshold * 100:
            break
    
    min_coalition_size = len(coalition_members)
    min_coalition_power = coalition_power
    
    # Voter apathy risk
    # If expected benefit < cost for most voters, apathy is high
    apathetic_ratio = 1 - (rational_participants / num_holders) if num_holders > 0 else 1
    
    if apathetic_ratio > 0.7:
        apathy_risk = "Critical"
        apathy_interpretation = "Most holders have no rational incentive to vote"
    elif apathetic_ratio > 0.5:
        apathy_risk = "High"
        apathy_interpretation = "Majority may abstain from voting"
    elif apathetic_ratio > 0.3:
        apathy_risk = "Moderate"
        apathy_interpretation = "Some voter apathy expected"
    else:
        apathy_risk = "Low"
        apathy_interpretation = "Most holders have incentive to participate"
    
    return {
        'holder_analysis': [
            {
                'holder_id': i,
                'voting_power': round(p, 2),
                'pivot_probability': pivot_probabilities[i],
                'expected_benefit_usd': expected_benefits[i],
                'rational_to_vote': expected_benefits[i] > voting_cost_usd,
            }
            for i, p in enumerate(voting_power)
        ],
        'participation': {
            'rational_participants': rational_participants,
            'total_holders': num_holders,
            'participation_rate': round(rational_participants / num_holders * 100, 1) if num_holders > 0 else 0,
            'participating_power': round(participating_power, 1),
            'quorum_achievable': quorum_achievable,
        },
        'coalition': {
            'min_coalition_size': min_coalition_size,
            'min_coalition_power': round(min_coalition_power, 1),
            'coalition_members': coalition_members,
        },
        'apathy': {
            'apathetic_ratio': round(apathetic_ratio * 100, 1),
            'risk_level': apathy_risk,
            'interpretation': apathy_interpretation,
        },
        'thresholds': {
            'quorum': quorum_threshold * 100,
            'passing': passing_threshold * 100,
            'voting_cost_usd': voting_cost_usd,
        },
    }


def analyze_coordination_game(
    num_participants: int,
    cooperation_benefit: float,  # Benefit if all cooperate
    defection_benefit: float,  # Benefit from defecting
    punishment_rounds: int = 3,  # Rounds of punishment for defection
) -> Dict:
    """
    Analyze coordination games and prisoner's dilemmas in token ecosystems.
    
    Models:
    - Staking coordination (if everyone stakes, price goes up)
    - Sell coordination (if everyone sells, price crashes)
    - Tit-for-tat dynamics
    """
    # Payoff matrix for 2-player game
    # C = Cooperate (stake/hold), D = Defect (sell)
    # Payoffs: (Player 1, Player 2)
    
    # If both cooperate: both get cooperation benefit
    cc_payoff = cooperation_benefit
    
    # If one defects: defector gets more, cooperator loses
    cd_payoff_defector = defection_benefit
    cd_payoff_cooperator = -defection_benefit * 0.5  # Cooperator hurt by defection
    
    # If both defect: both lose (tragedy of commons)
    dd_payoff = -defection_benefit * 0.3  # Both lose, but less than single cooperator
    
    payoff_matrix = {
        'cooperate_cooperate': (cc_payoff, cc_payoff),
        'cooperate_defect': (cd_payoff_cooperator, cd_payoff_defector),
        'defect_cooperate': (cd_payoff_defector, cd_payoff_cooperator),
        'defect_defect': (dd_payoff, dd_payoff),
    }
    
    # Nash equilibrium analysis
    # Check if defect-defect is Nash (neither can improve by changing)
    # From DD: if switch to C, get cd_payoff_cooperator (worse if < dd_payoff)
    defect_is_nash = cd_payoff_cooperator < dd_payoff
    
    # Check if cooperate-cooperate is Nash
    # From CC: if switch to D, get cd_payoff_defector (better if > cc_payoff)
    cooperate_is_nash = cd_payoff_defector <= cc_payoff
    
    # Determine game type
    if defection_benefit > cooperation_benefit and cd_payoff_cooperator < dd_payoff:
        game_type = "Prisoner's Dilemma"
        game_description = "Rational actors defect even though cooperation is better for all"
        equilibrium = "Defect-Defect (suboptimal)"
    elif cooperation_benefit > defection_benefit:
        game_type = "Coordination Game"
        game_description = "Multiple equilibria exist - outcome depends on expectations"
        equilibrium = "Cooperate-Cooperate or Defect-Defect"
    else:
        game_type = "Mixed Strategy Game"
        game_description = "No pure strategy equilibrium - players randomize"
        equilibrium = "Mixed strategies"
    
    # Tit-for-tat analysis (repeated game)
    # In repeated games, cooperation can be sustained if:
    # present value of future cooperation > one-time defection benefit
    
    discount_rate = 0.9  # How much future payoffs are valued
    future_cooperation_value = cc_payoff * discount_rate / (1 - discount_rate) if discount_rate < 1 else float('inf')
    future_punishment_cost = abs(dd_payoff) * punishment_rounds
    
    cooperation_sustainable = future_cooperation_value > defection_benefit - future_punishment_cost
    
    # Calculate cooperation probability in mixed equilibrium
    # For prisoner's dilemma: p = (T-R)/(T-S) where T=defect payoff, R=coop, S=sucker
    T = cd_payoff_defector
    R = cc_payoff
    S = cd_payoff_cooperator
    P = dd_payoff
    
    if T != S and T > R and P > S:  # Classic PD conditions
        # Mixed equilibrium probability of cooperation
        coop_prob = (P - S) / (T - R + P - S) if (T - R + P - S) != 0 else 0.5
    else:
        coop_prob = 0.5
    
    return {
        'payoff_matrix': {
            'CC': payoff_matrix['cooperate_cooperate'],
            'CD': payoff_matrix['cooperate_defect'],
            'DC': payoff_matrix['defect_cooperate'],
            'DD': payoff_matrix['defect_defect'],
        },
        'game_analysis': {
            'game_type': game_type,
            'description': game_description,
            'equilibrium': equilibrium,
            'defect_is_dominant': cd_payoff_defector > cc_payoff,
            'social_optimum': 'Cooperate-Cooperate' if cc_payoff > 0 else 'Defect-Defect',
        },
        'repeated_game': {
            'cooperation_sustainable': cooperation_sustainable,
            'future_cooperation_value': round(future_cooperation_value, 2) if future_cooperation_value != float('inf') else 'Infinite',
            'punishment_cost': round(future_punishment_cost, 2),
            'tit_for_tat_effective': cooperation_sustainable,
        },
        'mixed_equilibrium': {
            'cooperation_probability': round(coop_prob * 100, 1),
            'expected_payoff': round(coop_prob * cc_payoff + (1 - coop_prob) * dd_payoff, 2),
        },
        'recommendations': _generate_coordination_recommendations(
            game_type=game_type,
            cooperation_sustainable=cooperation_sustainable,
            coop_prob=coop_prob,
        ),
    }


def _generate_coordination_recommendations(
    game_type: str,
    cooperation_sustainable: bool,
    coop_prob: float,
) -> List[str]:
    """Generate recommendations for coordination games."""
    recs = []
    
    if game_type == "Prisoner's Dilemma":
        recs.append("⚠️ Classic PD structure - individual incentives oppose collective good")
        recs.append("🔒 Consider lock-ups or vesting to change payoff structure")
        recs.append("👥 Build community/reputation systems to enable tit-for-tat")
    
    if cooperation_sustainable:
        recs.append("✅ Long-term cooperation is sustainable through repeated interactions")
        recs.append("📊 Transparent tracking of holder behavior can reinforce cooperation")
    else:
        recs.append("🚨 Cooperation is not self-sustaining - need mechanism design")
        recs.append("💰 Consider increasing staking rewards to shift payoff matrix")
    
    if coop_prob < 0.5:
        recs.append("📉 Low cooperation probability - expect selling pressure")
    else:
        recs.append("📈 Higher cooperation probability - community alignment is strong")
    
    return recs


def calculate_full_game_theory_analysis(
    staking_apy: float,
    expected_price_change: float,
    price_volatility: float,
    lock_period_months: int,
    early_unstake_penalty: float,
    voting_power_distribution: List[float],
    proposal_value_usd: float,
) -> Dict:
    """
    Complete game theory analysis combining all models.
    """
    # Staking equilibrium
    staking_analysis = analyze_staking_vs_selling(
        staking_apy=staking_apy,
        expected_price_change=expected_price_change,
        price_volatility=price_volatility,
        lock_period_months=lock_period_months,
        early_unstake_penalty=early_unstake_penalty,
    )
    
    # Governance game
    governance_analysis = analyze_governance_game(
        voting_power_distribution=voting_power_distribution,
        proposal_value_usd=proposal_value_usd,
    )
    
    # Coordination game
    # Model cooperation benefit as staking return, defection as selling
    coordination_analysis = analyze_coordination_game(
        num_participants=len(voting_power_distribution),
        cooperation_benefit=staking_apy,  # % benefit from everyone staking
        defection_benefit=10,  # % benefit from selling while others stake
    )
    
    # Overall assessment
    overall_health = _calculate_game_theory_health(
        staking_analysis=staking_analysis,
        governance_analysis=governance_analysis,
        coordination_analysis=coordination_analysis,
    )
    
    return {
        'staking_equilibrium': staking_analysis,
        'governance_game': governance_analysis,
        'coordination_game': coordination_analysis,
        'overall': {
            'health_score': overall_health,
            'primary_risk': _identify_primary_risk(
                staking_analysis, governance_analysis, coordination_analysis
            ),
        },
    }


def _calculate_game_theory_health(
    staking_analysis: Dict,
    governance_analysis: Dict,
    coordination_analysis: Dict,
) -> float:
    """Calculate overall game theory health score (0-100)."""
    score = 50  # Base score
    
    # Staking equilibrium bonus
    if staking_analysis['equilibrium']['dominant_strategy'] == 'stake':
        score += 15
    elif staking_analysis['equilibrium']['dominant_strategy'] == 'sell':
        score -= 20
    
    if staking_analysis['equilibrium']['is_stable']:
        score += 10
    
    # Governance health
    if governance_analysis['participation']['quorum_achievable']:
        score += 10
    
    if governance_analysis['apathy']['risk_level'] in ['Low', 'Moderate']:
        score += 5
    elif governance_analysis['apathy']['risk_level'] == 'Critical':
        score -= 15
    
    # Coordination health
    if coordination_analysis['repeated_game']['cooperation_sustainable']:
        score += 10
    
    if coordination_analysis['mixed_equilibrium']['cooperation_probability'] > 50:
        score += 5
    
    return max(0, min(100, score))


def _identify_primary_risk(
    staking_analysis: Dict,
    governance_analysis: Dict,
    coordination_analysis: Dict,
) -> str:
    """Identify the primary game-theoretic risk."""
    risks = []
    
    if staking_analysis['equilibrium']['dominant_strategy'] == 'sell':
        risks.append(("Sell pressure", 3))
    
    if not governance_analysis['participation']['quorum_achievable']:
        risks.append(("Governance gridlock", 2))
    
    if governance_analysis['apathy']['risk_level'] == 'Critical':
        risks.append(("Voter apathy", 2))
    
    if not coordination_analysis['repeated_game']['cooperation_sustainable']:
        risks.append(("Coordination failure", 2))
    
    if not risks:
        return "None - game dynamics are healthy"
    
    return max(risks, key=lambda x: x[1])[0]

