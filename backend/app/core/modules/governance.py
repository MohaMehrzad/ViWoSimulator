"""
Governance Module - veVCoin Voting Power, Quorum, and Participation.

=== VECOIN GOVERNANCE SYSTEM (November 2025) ===

Vote-Escrowed VCoin (veVCoin) Governance Model:
- Lock VCoin for 1-208 weeks to receive veVCoin
- Voting power scales with lock duration (1x-4x boost)
- Based on proven ve-token model (veCRV, veBAL)

Governance Architecture:
1. veVCoin Token
   - Non-transferable vote-escrow token
   - Decays linearly to 0 at lock expiry
   - Re-lockable to maintain voting power

2. Proposal System
   - Quorum: 5% of total veVCoin supply
   - Threshold: Minimum 1000 veVCoin to create proposal
   - Voting period: 7 days
   - Timelock: 48-hour execution delay

3. Governance Tiers:
   - Community: 1-1000 veVCoin - Can vote
   - Delegate: 1000-10000 veVCoin - Can create proposals
   - Council: 10000+ veVCoin - Fast-track proposals

4. Voting Mechanisms:
   - Single choice voting
   - Weighted voting
   - Quadratic voting (for specific categories)
   - Snapshot-based voting weight

5. Integration:
   - Solana Realms integration
   - Off-chain snapshot voting
   - On-chain execution via Squads multisig
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import math
from app.models import SimulationParameters


class GovernanceTier(Enum):
    """Governance participation tiers"""
    COMMUNITY = "community"      # Basic voting rights
    DELEGATE = "delegate"        # Can create proposals
    COUNCIL = "council"          # Fast-track proposals


class ProposalCategory(Enum):
    """Types of governance proposals"""
    PARAMETER_CHANGE = "parameter_change"     # Fee adjustments, rates
    TREASURY_ALLOCATION = "treasury_allocation"  # Spending proposals
    PROTOCOL_UPGRADE = "protocol_upgrade"     # Smart contract upgrades
    EMISSIONS_CHANGE = "emissions_change"     # Reward rate changes
    PARTNERSHIP = "partnership"               # Strategic partnerships
    COMMUNITY_GRANT = "community_grant"       # Grant allocations


@dataclass
class GovernanceConfig:
    """Governance system configuration"""
    # Quorum requirements (% of total veVCoin)
    quorum_parameter_change: float = 0.05     # 5%
    quorum_treasury_allocation: float = 0.10  # 10%
    quorum_protocol_upgrade: float = 0.15     # 15%
    quorum_emissions_change: float = 0.12     # 12%
    quorum_partnership: float = 0.08          # 8%
    quorum_community_grant: float = 0.05      # 5%
    
    # Voting thresholds
    min_vevcoin_to_vote: float = 1.0
    min_vevcoin_to_propose: float = 1000.0
    min_vevcoin_fast_track: float = 10000.0
    
    # Timing
    voting_period_days: int = 7
    timelock_delay_hours: int = 48
    
    # Lock parameters
    min_lock_weeks: int = 1
    max_lock_weeks: int = 208  # 4 years
    max_boost: float = 4.0    # 4x boost at max lock


# Default governance configuration
DEFAULT_GOVERNANCE_CONFIG = GovernanceConfig()


def calculate_voting_power(
    vcoin_amount: float,
    lock_weeks: int,
    config: GovernanceConfig = DEFAULT_GOVERNANCE_CONFIG
) -> Dict[str, float]:
    """
    Calculate veVCoin voting power based on lock duration.
    
    The voting power boost scales linearly from 1x (1 week) to 4x (208 weeks).
    
    Formula:
    boost = 1 + (max_boost - 1) * (lock_weeks - min_lock) / (max_lock - min_lock)
    veVCoin = VCoin * boost
    
    Args:
        vcoin_amount: Amount of VCoin to lock
        lock_weeks: Duration of lock in weeks (1-208)
        config: Governance configuration
    
    Returns:
        Dict with veVCoin amount, boost multiplier, and lock details
    """
    # Clamp lock weeks to valid range
    lock_weeks = max(config.min_lock_weeks, min(config.max_lock_weeks, lock_weeks))
    
    # Calculate boost (linear scaling)
    lock_range = config.max_lock_weeks - config.min_lock_weeks
    boost = 1.0 + (config.max_boost - 1.0) * (lock_weeks - config.min_lock_weeks) / lock_range
    
    # Calculate veVCoin
    vevcoin_amount = vcoin_amount * boost
    
    # Calculate decay (veVCoin decays linearly to 0 over lock period)
    weeks_until_decay = lock_weeks
    decay_per_week = vevcoin_amount / lock_weeks
    
    # Determine governance tier
    if vevcoin_amount >= config.min_vevcoin_fast_track:
        tier = GovernanceTier.COUNCIL
    elif vevcoin_amount >= config.min_vevcoin_to_propose:
        tier = GovernanceTier.DELEGATE
    else:
        tier = GovernanceTier.COMMUNITY
    
    return {
        'vcoin_locked': vcoin_amount,
        'lock_weeks': lock_weeks,
        'lock_months': round(lock_weeks / 4.33, 1),
        'lock_years': round(lock_weeks / 52, 2),
        'boost_multiplier': round(boost, 2),
        'vevcoin_amount': round(vevcoin_amount, 2),
        'decay_per_week': round(decay_per_week, 4),
        'governance_tier': tier.value,
        'can_vote': vevcoin_amount >= config.min_vevcoin_to_vote,
        'can_propose': vevcoin_amount >= config.min_vevcoin_to_propose,
        'can_fast_track': vevcoin_amount >= config.min_vevcoin_fast_track,
    }


def check_quorum(
    category: ProposalCategory,
    votes_for: float,
    votes_against: float,
    total_vevcoin_supply: float,
    config: GovernanceConfig = DEFAULT_GOVERNANCE_CONFIG
) -> Dict[str, any]:
    """
    Check if a proposal meets quorum and passes.
    
    Args:
        category: Type of proposal
        votes_for: veVCoin votes in favor
        votes_against: veVCoin votes against
        total_vevcoin_supply: Total veVCoin supply
        config: Governance configuration
    
    Returns:
        Dict with quorum status and vote results
    """
    # Get quorum requirement for category
    quorum_map = {
        ProposalCategory.PARAMETER_CHANGE: config.quorum_parameter_change,
        ProposalCategory.TREASURY_ALLOCATION: config.quorum_treasury_allocation,
        ProposalCategory.PROTOCOL_UPGRADE: config.quorum_protocol_upgrade,
        ProposalCategory.EMISSIONS_CHANGE: config.quorum_emissions_change,
        ProposalCategory.PARTNERSHIP: config.quorum_partnership,
        ProposalCategory.COMMUNITY_GRANT: config.quorum_community_grant,
    }
    
    quorum_required_percent = quorum_map.get(category, 0.10)
    quorum_required_vevcoin = total_vevcoin_supply * quorum_required_percent
    
    total_votes = votes_for + votes_against
    participation_rate = total_votes / total_vevcoin_supply if total_vevcoin_supply > 0 else 0
    
    quorum_met = total_votes >= quorum_required_vevcoin
    majority_for = votes_for > votes_against if total_votes > 0 else False
    
    # Simple majority required
    passes = quorum_met and majority_for
    
    return {
        'category': category.value,
        'quorum_required_percent': round(quorum_required_percent * 100, 1),
        'quorum_required_vevcoin': round(quorum_required_vevcoin, 2),
        'total_votes': round(total_votes, 2),
        'votes_for': round(votes_for, 2),
        'votes_against': round(votes_against, 2),
        'votes_for_percent': round(votes_for / total_votes * 100, 1) if total_votes > 0 else 0,
        'participation_rate': round(participation_rate * 100, 1),
        'quorum_met': quorum_met,
        'majority_for': majority_for,
        'passes': passes,
        'voting_period_days': config.voting_period_days,
        'timelock_hours': config.timelock_delay_hours,
    }


def estimate_governance_participation(
    total_staked: float,
    stakers_count: int,
    platform_maturity: str,
    token_price: float,
    config: GovernanceConfig = DEFAULT_GOVERNANCE_CONFIG,
    # NEW: User-configurable parameters (passed from params)
    user_participation_rate: float = None,
    user_delegation_rate: float = None,
    user_avg_lock_weeks: int = None,
    user_proposals_per_month: int = None,
) -> Dict[str, any]:
    """
    Estimate governance participation based on staking and user-configured rates.
    
    Updated Nov 2025: Now uses user-configurable rates instead of hardcoded values
    to allow governance score to respond to parameter changes.
    
    Args:
        total_staked: Total VCoin staked
        stakers_count: Number of stakers
        platform_maturity: Platform maturity level
        token_price: Current token price
        config: Governance configuration
        user_participation_rate: User-configured voting participation rate
        user_delegation_rate: User-configured delegation rate
        user_avg_lock_weeks: User-configured average lock weeks
        user_proposals_per_month: User-configured proposals per month
    
    Returns:
        Dict with governance participation metrics
    """
    # Default participation rates by maturity (used as fallback)
    default_voting_rates = {
        'launch': 0.05,       # 5% of stakers vote
        'growing': 0.15,      # 15% of stakers vote
        'established': 0.30,  # 30% of stakers vote
    }
    
    # Default lock duration by maturity (in weeks)
    default_lock_weeks = {
        'launch': 12,         # 3 months avg
        'growing': 26,        # 6 months avg
        'established': 52,    # 1 year avg
    }
    
    # Use user-configured values if provided, otherwise fall back to maturity-based defaults
    participation_rate = user_participation_rate if user_participation_rate is not None else default_voting_rates.get(platform_maturity, 0.15)
    lock_weeks = user_avg_lock_weeks if user_avg_lock_weeks is not None else default_lock_weeks.get(platform_maturity, 26)
    delegation_rate = user_delegation_rate if user_delegation_rate is not None else 0.20
    
    # Calculate veVCoin supply
    avg_stake = total_staked / stakers_count if stakers_count > 0 else 0
    avg_voting_power = calculate_voting_power(avg_stake, lock_weeks, config)
    avg_vevcoin = avg_voting_power['vevcoin_amount']
    
    total_vevcoin_supply = stakers_count * avg_vevcoin
    
    # Active governance participants (direct voters)
    active_voters = int(stakers_count * participation_rate)
    active_voting_power = active_voters * avg_vevcoin
    
    # Delegators: users who delegate their votes instead of voting directly
    non_voters = stakers_count - active_voters
    delegators = int(non_voters * delegation_rate)
    delegated_voting_power = delegators * avg_vevcoin
    
    # Total effective participation = direct voters + delegators
    total_participants = active_voters + delegators
    effective_participation_rate = total_participants / stakers_count if stakers_count > 0 else 0
    
    # Distribution across tiers
    tier_distribution = {
        'community': int(stakers_count * 0.85),    # 85% community
        'delegate': int(stakers_count * 0.12),     # 12% delegates
        'council': int(stakers_count * 0.03),      # 3% council
    }
    
    # Proposal creation capacity
    eligible_proposers = tier_distribution['delegate'] + tier_distribution['council']
    
    # Use user-configured proposals per month if provided
    default_proposals = {
        'launch': 2,
        'growing': 5,
        'established': 10,
    }
    expected_monthly_proposals = user_proposals_per_month if user_proposals_per_month is not None else default_proposals.get(platform_maturity, 5)
    
    # Voting power concentration (Gini-like metric)
    # Higher delegation = better distribution
    base_concentration = {
        'launch': 0.65,
        'growing': 0.55,
        'established': 0.45,
    }
    # Delegation improves decentralization
    concentration = base_concentration.get(platform_maturity, 0.55) * (1 - delegation_rate * 0.3)
    
    return {
        # veVCoin metrics
        'total_vevcoin_supply': round(total_vevcoin_supply, 2),
        'total_vevcoin_supply_usd': round(total_vevcoin_supply * token_price, 2),
        'avg_vevcoin_per_staker': round(avg_vevcoin, 2),
        'avg_lock_weeks': lock_weeks,
        'avg_boost': round(avg_voting_power['boost_multiplier'], 2),
        
        # Direct Participation
        'active_voters': active_voters,
        'active_voting_power': round(active_voting_power, 2),
        'voting_participation_rate': round(participation_rate * 100, 1),
        
        # Delegation (NEW)
        'delegators': delegators,
        'delegated_voting_power': round(delegated_voting_power, 2),
        'delegation_rate': round(delegation_rate * 100, 1),
        
        # Effective participation (voters + delegators)
        'total_participants': total_participants,
        'effective_participation_rate': round(effective_participation_rate * 100, 1),
        
        # Tier distribution
        'tier_distribution': tier_distribution,
        'eligible_proposers': eligible_proposers,
        
        # Proposal activity
        'expected_monthly_proposals': expected_monthly_proposals,
        
        # Health metrics
        'voting_power_concentration': round(concentration * 100, 1),
        'decentralization_score': round((1 - concentration) * 100, 1),
        
        # Thresholds
        'min_vevcoin_to_vote': config.min_vevcoin_to_vote,
        'min_vevcoin_to_propose': config.min_vevcoin_to_propose,
        'min_vevcoin_fast_track': config.min_vevcoin_fast_track,
    }


def calculate_governance_revenue(
    proposals_count: int,
    total_staked: float,
    stakers_count: int,
    token_price: float,
    params: 'SimulationParameters' = None
) -> Dict[str, float]:
    """
    Calculate potential governance-related revenue.
    
    Revenue sources:
    1. Proposal creation fees
    2. Governance NFTs (voting badges)
    3. Premium governance features
    
    Args:
        proposals_count: Number of proposals per month
        total_staked: Total staked VCoin
        stakers_count: Number of stakers
        token_price: Current token price
        params: Optional simulation parameters for configurable fees
    
    Returns:
        Dict with governance revenue breakdown
    """
    # Get configurable fees from params or use defaults
    proposal_fee_vcoin = getattr(params, 'governance_proposal_fee', 100) if params else 100
    badge_price_vcoin = getattr(params, 'governance_badge_price', 50) if params else 50
    premium_fee_vcoin = getattr(params, 'governance_premium_fee', 100) if params else 100
    
    # Proposal creation fee revenue
    proposal_revenue_vcoin = proposals_count * proposal_fee_vcoin
    proposal_revenue_usd = proposal_revenue_vcoin * token_price
    
    # Governance badge NFTs (one-time purchase)
    # Estimate 2% of stakers buy badges per month
    badge_buyers = int(stakers_count * 0.02)
    badge_revenue_vcoin = badge_buyers * badge_price_vcoin
    badge_revenue_usd = badge_revenue_vcoin * token_price
    
    # Premium governance features (delegate dashboard, analytics)
    # 5% of delegates subscribe
    delegates = int(stakers_count * 0.12)
    premium_subscribers = int(delegates * 0.05)
    premium_revenue_vcoin = premium_subscribers * premium_fee_vcoin
    premium_revenue_usd = premium_revenue_vcoin * token_price
    
    total_revenue_vcoin = proposal_revenue_vcoin + badge_revenue_vcoin + premium_revenue_vcoin
    total_revenue_usd = proposal_revenue_usd + badge_revenue_usd + premium_revenue_usd
    
    return {
        'proposal_fee_vcoin': proposal_fee_vcoin,
        'badge_price_vcoin': badge_price_vcoin,
        'premium_fee_vcoin': premium_fee_vcoin,
        'proposal_revenue_vcoin': round(proposal_revenue_vcoin, 2),
        'proposal_revenue_usd': round(proposal_revenue_usd, 2),
        'badge_revenue_vcoin': round(badge_revenue_vcoin, 2),
        'badge_revenue_usd': round(badge_revenue_usd, 2),
        'premium_revenue_vcoin': round(premium_revenue_vcoin, 2),
        'premium_revenue_usd': round(premium_revenue_usd, 2),
        'total_revenue_vcoin': round(total_revenue_vcoin, 2),
        'total_revenue_usd': round(total_revenue_usd, 2),
    }


def calculate_governance(
    params: SimulationParameters,
    stakers_count: int,
    total_staked: float,
    circulating_supply: float = 100_000_000
) -> Dict:
    """
    Calculate complete governance metrics for veVCoin system.
    
    Args:
        params: Simulation parameters
        stakers_count: Number of stakers
        total_staked: Total staked VCoin
        circulating_supply: Current circulating supply
    
    Returns:
        Dict with all governance metrics
    """
    # Check if module is enabled
    if not getattr(params, 'enable_governance', True):
        return {
            'enabled': False,
            'revenue': 0,
            'costs': 0,
            'profit': 0,
            'total_vevcoin_supply': 0,
            'total_vevcoin_supply_usd': 0,
            'active_voters': 0,
            'voting_participation_rate': 0,
            'governance_health_score': 0,
            'expected_monthly_proposals': 0,
        }
    
    token_price = params.token_price
    platform_maturity = params.platform_maturity.value
    
    # Get user-configured governance parameters
    user_participation_rate = getattr(params, 'governance_participation_rate', None)
    user_delegation_rate = getattr(params, 'governance_delegation_rate', None)
    user_avg_lock_weeks = getattr(params, 'governance_avg_lock_weeks', None)
    user_proposals_per_month = getattr(params, 'governance_proposals_per_month', None)
    
    # Get participation estimates with user-configured parameters
    participation = estimate_governance_participation(
        total_staked,
        stakers_count,
        platform_maturity,
        token_price,
        user_participation_rate=user_participation_rate,
        user_delegation_rate=user_delegation_rate,
        user_avg_lock_weeks=user_avg_lock_weeks,
        user_proposals_per_month=user_proposals_per_month,
    )
    
    total_vevcoin = participation['total_vevcoin_supply']
    
    # Example quorum check for parameter change proposal
    # Simulate a vote with typical participation
    votes_for = total_vevcoin * participation['voting_participation_rate'] / 100 * 0.65  # 65% for
    votes_against = total_vevcoin * participation['voting_participation_rate'] / 100 * 0.35  # 35% against
    
    quorum_check = check_quorum(
        ProposalCategory.PARAMETER_CHANGE,
        votes_for,
        votes_against,
        total_vevcoin
    )
    
    # Calculate governance revenue
    revenue = calculate_governance_revenue(
        participation['expected_monthly_proposals'],
        total_staked,
        stakers_count,
        token_price,
        params
    )
    
    # veVCoin as percentage of circulating supply
    vevcoin_of_circulating = (total_vevcoin / circulating_supply * 100) if circulating_supply > 0 else 0
    
    # Governance health score (0-100) - now includes effective participation
    health_factors = [
        min(100, participation['effective_participation_rate'] * 2),  # Max at 50%+ effective participation
        participation['decentralization_score'],
        min(100, stakers_count / 100),  # Max at 10000 stakers
        min(100, participation['expected_monthly_proposals'] * 10),  # Max at 10 proposals
        min(100, participation['delegation_rate'] * 2),  # Delegation bonus - 50% = 100
    ]
    governance_health_score = sum(health_factors) / len(health_factors)
    
    return {
        'revenue': round(revenue['total_revenue_usd'], 2),
        'costs': 0,  # Governance has minimal costs (on-chain)
        'profit': round(revenue['total_revenue_usd'], 2),
        
        # veVCoin metrics
        'total_vevcoin_supply': round(total_vevcoin, 2),
        'total_vevcoin_supply_usd': round(total_vevcoin * token_price, 2),
        'vevcoin_of_circulating_percent': round(vevcoin_of_circulating, 2),
        'avg_vevcoin_per_staker': round(participation['avg_vevcoin_per_staker'], 2),
        'avg_lock_weeks': participation['avg_lock_weeks'],
        'avg_boost_multiplier': participation['avg_boost'],
        
        # Direct Participation
        'active_voters': participation['active_voters'],
        'active_voting_power': round(participation['active_voting_power'], 2),
        'voting_participation_rate': participation['voting_participation_rate'],
        
        # Delegation (NEW)
        'delegators': participation['delegators'],
        'delegated_voting_power': round(participation['delegated_voting_power'], 2),
        'delegation_rate': participation['delegation_rate'],
        
        # Effective Participation (voters + delegators)
        'total_participants': participation['total_participants'],
        'effective_participation_rate': participation['effective_participation_rate'],
        
        # Tier distribution
        'tier_distribution': participation['tier_distribution'],
        'eligible_proposers': participation['eligible_proposers'],
        
        # Proposal activity
        'expected_monthly_proposals': participation['expected_monthly_proposals'],
        
        # Example quorum check
        'quorum_example': quorum_check,
        
        # Revenue breakdown
        'revenue_breakdown': revenue,
        
        # Health metrics
        'voting_power_concentration': participation['voting_power_concentration'],
        'decentralization_score': participation['decentralization_score'],
        'governance_health_score': round(governance_health_score, 1),
        
        # Configuration
        'config': {
            'min_vevcoin_to_vote': DEFAULT_GOVERNANCE_CONFIG.min_vevcoin_to_vote,
            'min_vevcoin_to_propose': DEFAULT_GOVERNANCE_CONFIG.min_vevcoin_to_propose,
            'min_vevcoin_fast_track': DEFAULT_GOVERNANCE_CONFIG.min_vevcoin_fast_track,
            'max_lock_weeks': DEFAULT_GOVERNANCE_CONFIG.max_lock_weeks,
            'max_boost': DEFAULT_GOVERNANCE_CONFIG.max_boost,
            'voting_period_days': DEFAULT_GOVERNANCE_CONFIG.voting_period_days,
            'timelock_hours': DEFAULT_GOVERNANCE_CONFIG.timelock_delay_hours,
        },
        
        # Integration status
        'platform': 'solana_realms',
        'snapshot_voting': True,
        'on_chain_execution': True,
    }

