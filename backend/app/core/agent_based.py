"""
Agent-Based simulation engine.
Simulates individual user behaviors to model realistic market dynamics.
"""

import numpy as np
from typing import Callable, Optional, List, Dict
from dataclasses import dataclass
from enum import Enum
from app.models import (
    SimulationParameters,
    AgentBasedResult,
    AgentResult,
    MarketDynamics,
    SystemMetrics,
)
from app.config import config
from app.core.modules.rewards import PLATFORM_FEE_RATE


class AgentType(Enum):
    CREATOR = "creator"
    CONSUMER = "consumer"
    WHALE = "whale"
    BOT = "bot"


@dataclass
class Agent:
    """Individual agent in the simulation"""
    id: str
    agent_type: AgentType
    tokens_held: float = 0.0
    tokens_staked: float = 0.0
    tokens_earned: float = 0.0
    tokens_spent: float = 0.0
    activity_level: float = 1.0  # 0-2 scale
    is_flagged: bool = False
    
    # Behavior parameters
    sell_threshold: float = 0.3  # Sells when holdings exceed this % of earnings
    stake_probability: float = 0.2
    post_frequency: float = 1.0  # Posts per day
    
    def monthly_activity(self) -> float:
        """Calculate monthly activity score"""
        return self.post_frequency * 30 * self.activity_level


def create_agent_population(
    count: int,
    params: SimulationParameters,
    rng: np.random.Generator
) -> List[Agent]:
    """
    Create a diverse population of agents with realistic distributions.
    """
    agents = []
    
    # Distribution of agent types (based on typical platform demographics)
    type_distribution = {
        AgentType.CREATOR: 0.10,    # 10% are active creators
        AgentType.CONSUMER: 0.80,   # 80% are consumers/lurkers
        AgentType.WHALE: 0.02,      # 2% are whales (high activity/holdings)
        AgentType.BOT: 0.08,        # 8% are bots (to be detected)
    }
    
    for i in range(count):
        # Determine agent type
        rand = rng.random()
        cumulative = 0
        agent_type = AgentType.CONSUMER
        for atype, prob in type_distribution.items():
            cumulative += prob
            if rand < cumulative:
                agent_type = atype
                break
        
        # Create agent with type-specific behavior
        if agent_type == AgentType.CREATOR:
            activity = rng.uniform(0.5, 2.0)
            post_freq = rng.uniform(1, 5)
            stake_prob = rng.uniform(0.3, 0.6)
            sell_threshold = rng.uniform(0.4, 0.8)
        elif agent_type == AgentType.CONSUMER:
            activity = rng.uniform(0.1, 1.0)
            post_freq = rng.uniform(0, 0.5)
            stake_prob = rng.uniform(0.1, 0.3)
            sell_threshold = rng.uniform(0.2, 0.5)
        elif agent_type == AgentType.WHALE:
            activity = rng.uniform(1.0, 2.0)
            post_freq = rng.uniform(0.5, 3)
            stake_prob = rng.uniform(0.5, 0.9)
            sell_threshold = rng.uniform(0.6, 0.95)
        else:  # BOT
            activity = rng.uniform(1.5, 2.0)  # Bots are highly active
            post_freq = rng.uniform(10, 20)   # Excessive posting
            stake_prob = 0.0  # Bots don't stake
            sell_threshold = 0.1  # Bots sell quickly
        
        agent = Agent(
            id=f"agent_{i:05d}",
            agent_type=agent_type,
            activity_level=activity,
            post_frequency=post_freq,
            stake_probability=stake_prob,
            sell_threshold=sell_threshold,
        )
        agents.append(agent)
    
    return agents


def detect_bots(agents: List[Agent], rng: np.random.Generator) -> int:
    """
    Detect and flag bot agents based on behavior patterns.
    Returns count of flagged bots.
    """
    flagged_count = 0
    
    for agent in agents:
        # Detection criteria
        is_excessive_poster = agent.post_frequency > 12
        is_no_staker = agent.stake_probability < 0.05
        is_quick_seller = agent.sell_threshold < 0.15
        
        # Detection probability based on suspicious behavior
        suspicion_score = 0
        if is_excessive_poster:
            suspicion_score += 0.4
        if is_no_staker and agent.agent_type != AgentType.CONSUMER:
            suspicion_score += 0.2
        if is_quick_seller:
            suspicion_score += 0.3
        if agent.agent_type == AgentType.BOT:
            suspicion_score += 0.5  # Actual bots have higher base suspicion
        
        # Flag with probability based on suspicion score (max 90% detection)
        if rng.random() < min(suspicion_score, 0.9):
            agent.is_flagged = True
            flagged_count += 1
    
    return flagged_count


def simulate_month(
    agents: List[Agent],
    params: SimulationParameters,
    monthly_emission: float,
    rng: np.random.Generator
) -> Dict:
    """
    Simulate one month of agent activity.
    """
    # Calculate total activity points
    total_activity = sum(a.monthly_activity() for a in agents if not a.is_flagged)
    
    if total_activity == 0:
        total_activity = 1  # Prevent division by zero
    
    # Distribute rewards based on activity share
    total_distributed = 0
    total_staked = 0
    total_sold = 0
    total_held = 0
    
    for agent in agents:
        if agent.is_flagged:
            continue  # Flagged agents get no rewards
        
        # Calculate reward share
        activity_share = agent.monthly_activity() / total_activity
        reward = monthly_emission * activity_share
        
        # Apply max daily reward cap (converted to monthly)
        max_monthly_reward = (params.max_daily_reward_usd / params.token_price) * 30
        reward = min(reward, max_monthly_reward)
        
        agent.tokens_earned += reward
        agent.tokens_held += reward
        total_distributed += reward
        
        # Staking behavior
        if rng.random() < agent.stake_probability:
            stake_amount = agent.tokens_held * rng.uniform(0.1, 0.3)
            agent.tokens_staked += stake_amount
            agent.tokens_held -= stake_amount
            total_staked += stake_amount
        
        # Selling behavior
        earnings_ratio = agent.tokens_held / max(agent.tokens_earned, 1)
        if earnings_ratio > agent.sell_threshold:
            sell_amount = agent.tokens_held * rng.uniform(0.2, 0.5)
            agent.tokens_held -= sell_amount
            agent.tokens_spent += sell_amount
            total_sold += sell_amount
        
        total_held += agent.tokens_held
    
    return {
        'distributed': total_distributed,
        'staked': total_staked,
        'sold': total_sold,
        'held': total_held,
    }


def run_agent_based_simulation(
    params: SimulationParameters,
    agent_count: int = 1000,
    duration_months: int = 12,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    seed: Optional[int] = None
) -> AgentBasedResult:
    """
    Run agent-based simulation.
    
    Args:
        params: Simulation parameters
        agent_count: Number of agents to simulate
        duration_months: Simulation duration in months
        progress_callback: Optional callback for progress updates
        seed: Random seed for reproducibility
    
    Returns:
        AgentBasedResult with agent behaviors and market dynamics
    """
    rng = np.random.default_rng(seed)
    
    # Create agent population
    agents = create_agent_population(agent_count, params, rng)
    
    # Detect bots
    flagged_bots = detect_bots(agents, rng)
    
    # Calculate allocation percentage (dynamic or static)
    use_dynamic = getattr(params, 'enable_dynamic_allocation', False)
    
    if use_dynamic and agent_count > 0:
        from app.core.modules.rewards import calculate_dynamic_allocation
        dynamic_result = calculate_dynamic_allocation(
            current_users=agent_count,
            token_price=params.token_price,
            initial_users=getattr(params, 'initial_users_for_allocation', 1000),
            target_users=getattr(params, 'target_users_for_max_allocation', 1_000_000),
            max_per_user_monthly_usd=getattr(params, 'max_per_user_monthly_usd', 50.0),
            min_per_user_monthly_usd=getattr(params, 'min_per_user_monthly_usd', 0.10),
            monthly_emission=config.MONTHLY_EMISSION,
        )
        allocation_percent = dynamic_result.allocation_percent
    else:
        allocation_percent = params.reward_allocation_percent
    
    # Calculate monthly emission (gross - before platform fee)
    gross_monthly_emission = config.MONTHLY_EMISSION * allocation_percent
    
    # Calculate platform fee (5% of gross)
    monthly_platform_fee = gross_monthly_emission * PLATFORM_FEE_RATE
    
    # Net monthly emission (95% - what agents receive)
    net_monthly_emission = gross_monthly_emission - monthly_platform_fee
    
    # Run simulation for each month
    total_distributed = 0
    total_staked = 0
    total_sold = 0
    total_platform_fee = 0
    
    for month in range(duration_months):
        # Distribute only net emission to agents
        month_results = simulate_month(agents, params, net_monthly_emission, rng)
        total_distributed += month_results['distributed']
        total_staked += month_results['staked']
        total_sold += month_results['sold']
        total_platform_fee += monthly_platform_fee
        
        if progress_callback:
            progress_callback(month + 1, duration_months)
    
    # Calculate agent breakdown
    agent_breakdown = {
        'creator': sum(1 for a in agents if a.agent_type == AgentType.CREATOR and not a.is_flagged),
        'consumer': sum(1 for a in agents if a.agent_type == AgentType.CONSUMER and not a.is_flagged),
        'whale': sum(1 for a in agents if a.agent_type == AgentType.WHALE and not a.is_flagged),
        'bot': sum(1 for a in agents if a.agent_type == AgentType.BOT),
    }
    
    # Calculate market dynamics
    buy_pressure = (total_staked / max(total_distributed, 1)) * 100
    sell_pressure = (total_sold / max(total_distributed, 1)) * 100
    net_pressure = buy_pressure - sell_pressure
    price_impact = net_pressure * 0.1  # Simplified price impact model
    
    market_dynamics = MarketDynamics(
        buy_pressure=round(buy_pressure, 1),
        sell_pressure=round(sell_pressure, 1),
        price_impact=round(price_impact, 2),
    )
    
    # Calculate system metrics
    total_recaptured = total_staked + (total_distributed * params.burn_rate)
    net_circulation = total_distributed - total_recaptured
    platform_fee_usd = total_platform_fee * params.token_price
    
    system_metrics = SystemMetrics(
        total_rewards_distributed=round(total_distributed, 2),
        total_recaptured=round(total_recaptured, 2),
        net_circulation=round(net_circulation, 2),
        platform_fee_collected=round(total_platform_fee, 2),
        platform_fee_usd=round(platform_fee_usd, 2),
    )
    
    # Get top agents by earnings
    active_agents = [a for a in agents if not a.is_flagged]
    top_agents_data = sorted(active_agents, key=lambda a: a.tokens_earned, reverse=True)[:10]
    
    top_agents = [
        AgentResult(
            id=a.id,
            type=a.agent_type.value,
            rewards_earned=round(a.tokens_earned, 2),
            tokens_spent=round(a.tokens_spent, 2),
            tokens_staked=round(a.tokens_staked, 2),
            activity=round(a.activity_level, 2),
            flagged=a.is_flagged,
        )
        for a in top_agents_data
    ]
    
    return AgentBasedResult(
        total_agents=agent_count,
        agent_breakdown=agent_breakdown,
        market_dynamics=market_dynamics,
        system_metrics=system_metrics,
        top_agents=top_agents,
        flagged_bots=flagged_bots,
    )


