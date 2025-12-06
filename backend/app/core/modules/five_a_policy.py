"""
5A Policy Gamification Module - December 2025

Implements the 5A Policy evaluation system that assesses users on 5 pillars:
1. Identity (Authenticity/Authority) - KYC, profile completeness, verification
2. Accuracy (Honesty) - Content quality, factual accuracy, report accuracy  
3. Agility - Response time, engagement speed, adaptability
4. Activity - Daily actions, posting frequency, platform engagement
5. Approved (Liability) - Reputation score, community standing, trust level

Each pillar is rated 0-100% and the weighted average creates a LINEAR multiplier
affecting rewards, fees, staking APY, governance power, and content visibility.

LINEAR FORMULA (Updated December 2025):
    average_stars = weighted_average(identity, accuracy, agility, activity, approved)
    multiplier = (average_stars / 100) * 2.0
    
    Result:
    - 0% average = 0x multiplier (earn nothing)
    - 50% average = 1x multiplier (neutral baseline)
    - 100% average = 2x multiplier (earn double)

All users START at 50% on all stars (neutral position).
Stars change dynamically based on user behavior.
- Below 50% = earning penalty (down to 0x at 0%)
- Above 50% = earning bonus (up to 2x at 100%)
"""

import math
import random
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass

from app.models import SimulationParameters
from app.models.results import (
    FiveAResult,
    FiveAStarDistribution,
    FiveAUserProfile,
    FiveAModuleImpact,
)


# =============================================================================
# CONSTANTS
# =============================================================================

# Star names and display names
STAR_NAMES = ['identity', 'accuracy', 'agility', 'activity', 'approved']
STAR_DISPLAY_NAMES = {
    'identity': 'Identity (Authority)',
    'accuracy': 'Accuracy (Honesty)',
    'agility': 'Agility',
    'activity': 'Activity',
    'approved': 'Approved (Liability)',
}

# Tier thresholds (percentages)
TIER_BRONZE_MAX = 30
TIER_SILVER_MAX = 60
TIER_GOLD_MAX = 90
# Diamond is 91-100

# Multiplier tiers (based on linear 0-2x scale)
# 0% = 0x, 50% = 1x (neutral), 100% = 2x
MULTIPLIER_PENALIZED_MAX = 0.8  # Below 40% stars
MULTIPLIER_NEUTRAL_MIN = 0.8   # 40% stars
MULTIPLIER_NEUTRAL_MAX = 1.2   # 60% stars
MULTIPLIER_BOOSTED_MAX = 1.6   # 80% stars
# Elite is 1.6+ (80%+ stars)

# =============================================================================
# USER SEGMENTS (Based on 90-9-1 Rule - Dec 2025)
# =============================================================================
# Research shows real social media user distribution follows:
# - 90% Lurkers: Consume content only, rarely interact
# - 9% Contributors: Occasional likes, comments, shares  
# - 1% Creators: Active content producers
#
# We use a modified 4-segment model for crypto/social apps:

USER_SEGMENTS = {
    'inactive': {
        'name': 'Inactive/Ghost',
        'description': 'Signed up but never returned - ZERO earnings',
        'percent': 0.20,  # 20% of users are inactive ghosts
        'identity_mean': 5,    # Minimal profile
        'accuracy_mean': 0,    # No content
        'agility_mean': 0,     # Never responds
        'activity_mean': 0,    # Zero activity
        'approved_mean': 10,   # Minimal standing
        'std_dev': 5,
        'expected_multiplier': 0.03,  # ~1.5% avg = essentially ZERO
    },
    'lurkers': {
        'name': 'Lurkers',
        'description': 'View only, minimal interaction',
        'percent': 0.40,  # 40% of users
        'identity_mean': 20,   # Low KYC completion
        'accuracy_mean': 30,   # Rarely rate content
        'agility_mean': 15,    # Slow response (inactive)
        'activity_mean': 10,   # Very low activity
        'approved_mean': 40,   # Basic standing
        'std_dev': 15,
        'expected_multiplier': 0.23,  # ~11.5% avg stars
    },
    'casual': {
        'name': 'Casual Users',
        'description': 'Weekly activity, some engagement',
        'percent': 0.25,  # 25% of users
        'identity_mean': 50,   # Partial verification
        'accuracy_mean': 55,   # Basic content quality
        'agility_mean': 45,    # Moderate response
        'activity_mean': 40,   # Weekly active
        'approved_mean': 60,   # Good standing
        'std_dev': 15,
        'expected_multiplier': 0.95,  # ~47.5% avg stars
    },
    'active': {
        'name': 'Active Users',
        'description': 'Daily activity, regular posting',
        'percent': 0.12,  # 12% of users
        'identity_mean': 70,   # Most KYC complete
        'accuracy_mean': 65,   # Good content quality
        'agility_mean': 70,    # Fast responder
        'activity_mean': 75,   # Daily active
        'approved_mean': 70,   # Strong standing
        'std_dev': 12,
        'expected_multiplier': 1.40,  # ~70% avg stars
    },
    'power_users': {
        'name': 'Power Users',
        'description': 'High creators, verified, engaged',
        'percent': 0.03,  # 3% of users (top creators)
        'identity_mean': 90,   # Fully verified
        'accuracy_mean': 80,   # High quality content
        'agility_mean': 85,    # Very responsive
        'activity_mean': 95,   # Always active
        'approved_mean': 85,   # Excellent standing
        'std_dev': 8,
        'expected_multiplier': 1.74,  # ~87% avg stars
    },
}

# Segment display order
SEGMENT_ORDER = ['inactive', 'lurkers', 'casual', 'active', 'power_users']

# =============================================================================
# SEGMENT EVOLUTION (Dynamic 5A - Dec 2025)
# =============================================================================
# Monthly transition probabilities for realistic user lifecycle.
# Users can improve (gamification incentives) or decay (disengagement).
# Platform maturity increases improvement rates over time.

SEGMENT_TRANSITIONS = {
    # From segment -> probability of moving to each segment per month
    # Rows must sum to 1.0
    'inactive': {
        'inactive': 0.70,     # 70% stay inactive
        'lurkers': 0.05,      # 5% re-engage as lurkers
        'casual': 0.00,       # Can't jump directly to casual
        'active': 0.00,       # Can't jump to active
        'power_users': 0.00,  # Can't jump to power
        'churned': 0.25,      # 25% churn completely (leave platform)
    },
    'lurkers': {
        'inactive': 0.02,     # 2% become inactive
        'lurkers': 0.85,      # 85% stay lurkers
        'casual': 0.08,       # 8% improve to casual
        'active': 0.00,       # Can't skip levels
        'power_users': 0.00,
        'churned': 0.05,      # 5% churn
    },
    'casual': {
        'inactive': 0.00,     # Can't drop to inactive directly
        'lurkers': 0.05,      # 5% decay to lurkers
        'casual': 0.80,       # 80% stay casual
        'active': 0.12,       # 12% improve to active
        'power_users': 0.00,  # Can't skip levels
        'churned': 0.03,      # 3% churn
    },
    'active': {
        'inactive': 0.00,
        'lurkers': 0.00,      # Can't drop 2 levels
        'casual': 0.08,       # 8% decay to casual
        'active': 0.85,       # 85% stay active
        'power_users': 0.05,  # 5% become power users
        'churned': 0.02,      # 2% churn (low - they're engaged)
    },
    'power_users': {
        'inactive': 0.00,
        'lurkers': 0.00,
        'casual': 0.00,       # Can't drop 2 levels
        'active': 0.05,       # 5% decay to active
        'power_users': 0.93,  # 93% stay power users (very sticky)
        'churned': 0.02,      # 2% churn
    },
}

# Retention multipliers per segment (affects base retention rate)
SEGMENT_RETENTION_MULTIPLIERS = {
    'inactive': 0.3,      # 70% higher churn than baseline
    'lurkers': 0.7,       # 30% higher churn
    'casual': 1.0,        # Baseline retention
    'active': 1.3,        # 30% better retention
    'power_users': 1.8,   # 80% better retention
}


def evolve_user_segments(
    current_counts: Dict[str, int],
    month: int,
    platform_maturity: float = 0.0,
    new_users: int = 0,
) -> Dict[str, any]:
    """
    Evolve user segment distribution for one month using transition matrix.
    
    Args:
        current_counts: Current user counts per segment {'inactive': n, 'lurkers': n, ...}
        month: Current month (1-60), used for maturity calculation
        platform_maturity: 0.0 to 1.0, increases improvement rates
        new_users: New users joining this month (distributed by initial probabilities)
    
    Returns:
        Dict with:
        - 'counts': New segment counts
        - 'churned': Users who churned this month
        - 'improved': Users who moved up a segment
        - 'decayed': Users who moved down a segment
    """
    new_counts = {seg: 0 for seg in SEGMENT_ORDER}
    churned = 0
    improved = 0
    decayed = 0
    
    # Apply transitions for existing users
    for from_segment in SEGMENT_ORDER:
        count = current_counts.get(from_segment, 0)
        if count == 0:
            continue
        
        transitions = SEGMENT_TRANSITIONS[from_segment]
        
        # Apply maturity boost to improvement rates (up to +50% at full maturity)
        maturity_boost = 1.0 + (platform_maturity * 0.5)
        
        for to_segment, base_prob in transitions.items():
            if to_segment == 'churned':
                # Churned users leave the platform
                churned_count = int(count * base_prob)
                churned += churned_count
            else:
                # Adjust probability based on maturity
                prob = base_prob
                from_idx = SEGMENT_ORDER.index(from_segment)
                to_idx = SEGMENT_ORDER.index(to_segment) if to_segment in SEGMENT_ORDER else from_idx
                
                if to_idx > from_idx:
                    # Improvement: boost by maturity
                    prob = min(base_prob * maturity_boost, 0.30)  # Cap at 30%
                    users_moved = int(count * prob)
                    improved += users_moved
                elif to_idx < from_idx:
                    # Decay: reduce slightly by maturity (engaged platforms decay less)
                    prob = max(base_prob * (1.0 - platform_maturity * 0.3), base_prob * 0.5)
                    users_moved = int(count * prob)
                    decayed += users_moved
                else:
                    # Stay in same segment
                    users_moved = int(count * prob)
                
                new_counts[to_segment] += users_moved
    
    # Distribute new users according to initial segment distribution
    # New users start mostly as inactive/lurkers (realistic)
    if new_users > 0:
        new_user_distribution = {
            'inactive': 0.25,     # 25% of new signups become ghosts
            'lurkers': 0.45,      # 45% become lurkers
            'casual': 0.20,       # 20% engage casually
            'active': 0.08,       # 8% are immediately active
            'power_users': 0.02,  # 2% are power users from day 1
        }
        
        for segment, percent in new_user_distribution.items():
            new_counts[segment] += int(new_users * percent)
    
    return {
        'counts': new_counts,
        'churned': churned,
        'improved': improved,
        'decayed': decayed,
        'total_active': sum(new_counts.values()),
    }


def calculate_segment_retention_multiplier(segment_counts: Dict[str, int]) -> float:
    """
    Calculate weighted retention multiplier based on segment distribution.
    
    Returns a multiplier (0.3 to 1.8) to apply to base retention rate.
    """
    total = sum(segment_counts.values())
    if total == 0:
        return 1.0
    
    weighted_sum = 0.0
    for segment, count in segment_counts.items():
        multiplier = SEGMENT_RETENTION_MULTIPLIERS.get(segment, 1.0)
        weighted_sum += count * multiplier
    
    return weighted_sum / total


def calculate_platform_maturity(month: int, max_months: int = 60) -> float:
    """
    Calculate platform maturity factor (0.0 to 1.0) based on month.
    
    Maturity increases improvement rates and decreases decay rates.
    Follows S-curve: slow start, rapid middle growth, plateau.
    """
    # S-curve using logistic function
    # Reaches ~0.5 at month 24, ~0.9 at month 48
    x = (month - max_months / 2) / (max_months / 6)
    maturity = 1.0 / (1.0 + math.exp(-x))
    return min(1.0, max(0.0, maturity))


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def get_tier_from_percentage(pct: float) -> str:
    """Map a percentage (0-100) to a tier name."""
    if pct <= TIER_BRONZE_MAX:
        return 'bronze'
    elif pct <= TIER_SILVER_MAX:
        return 'silver'
    elif pct <= TIER_GOLD_MAX:
        return 'gold'
    else:
        return 'diamond'


def get_multiplier_tier(multiplier: float) -> str:
    """
    Map a multiplier to a tier name based on linear 0-2x scale.
    
    - penalized: 0x - 0.8x (0% - 40% stars)
    - neutral: 0.8x - 1.2x (40% - 60% stars)
    - boosted: 1.2x - 1.6x (60% - 80% stars)
    - elite: 1.6x - 2.0x (80% - 100% stars)
    """
    if multiplier < MULTIPLIER_PENALIZED_MAX:
        return 'penalized'
    elif multiplier < MULTIPLIER_NEUTRAL_MAX:
        return 'neutral'
    elif multiplier < MULTIPLIER_BOOSTED_MAX:
        return 'boosted'
    else:
        return 'elite'


def generate_truncated_normal(
    mean: float,
    std_dev: float,
    min_val: float,
    max_val: float,
    count: int,
    seed: Optional[int] = None
) -> List[float]:
    """
    Generate a list of values from a truncated normal distribution.
    
    Uses rejection sampling to ensure all values fall within [min_val, max_val].
    """
    if seed is not None:
        random.seed(seed)
    
    values = []
    attempts = 0
    max_attempts = count * 10
    
    while len(values) < count and attempts < max_attempts:
        # Generate from normal distribution
        val = random.gauss(mean, std_dev)
        
        # Reject if outside bounds
        if min_val <= val <= max_val:
            values.append(val)
        
        attempts += 1
    
    # If we couldn't generate enough, fill with clamped values
    while len(values) < count:
        val = clamp(random.gauss(mean, std_dev), min_val, max_val)
        values.append(val)
    
    return values


# =============================================================================
# CORE CALCULATION FUNCTIONS
# =============================================================================

@dataclass
class UserStarProfile:
    """A single user's 5A star ratings."""
    identity: float
    accuracy: float
    agility: float
    activity: float
    approved: float
    compound_multiplier: float = 1.0
    
    def get_average(self, weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate weighted average of all stars."""
        if weights is None:
            return (self.identity + self.accuracy + self.agility + 
                    self.activity + self.approved) / 5
        
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 50.0
        
        return (
            self.identity * weights.get('identity', 0.2) +
            self.accuracy * weights.get('accuracy', 0.2) +
            self.agility * weights.get('agility', 0.2) +
            self.activity * weights.get('activity', 0.2) +
            self.approved * weights.get('approved', 0.2)
        ) / total_weight


def calculate_linear_multiplier(
    stars: UserStarProfile,
    weights: Dict[str, float],
    min_multiplier: float = 0.0,
    max_multiplier: float = 2.0,
) -> float:
    """
    Calculate LINEAR multiplier from 5A star ratings.
    
    Simple linear formula (December 2025 update):
        average_stars = weighted_average(all 5 stars)
        multiplier = (average_stars / 100) * 2.0
    
    Results:
        - 0% average stars = 0x multiplier (earn nothing)
        - 50% average stars = 1x multiplier (neutral baseline)
        - 100% average stars = 2x multiplier (earn double)
    
    All users start at 50% on all stars (neutral position).
    Stars change dynamically based on user behavior.
    """
    star_values = {
        'identity': stars.identity,
        'accuracy': stars.accuracy,
        'agility': stars.agility,
        'activity': stars.activity,
        'approved': stars.approved,
    }
    
    # Calculate weighted average of all stars
    total_weight = sum(weights.values())
    if total_weight == 0:
        total_weight = 1.0
    
    weighted_sum = sum(
        star_pct * weights.get(star_name, 0.2)
        for star_name, star_pct in star_values.items()
    )
    average_stars = weighted_sum / total_weight
    
    # Simple linear formula: 0% = 0x, 50% = 1x, 100% = 2x
    multiplier = (average_stars / 100.0) * 2.0
    
    # Clamp to min/max bounds (0x to 2x)
    multiplier = clamp(multiplier, min_multiplier, max_multiplier)
    
    return multiplier


# Alias for backwards compatibility
def calculate_compound_multiplier(
    stars: UserStarProfile,
    weights: Dict[str, float],
    compound_base: float = 1.0,
    compound_exponent: float = 1.5,
    min_multiplier: float = 0.0,
    max_multiplier: float = 2.0,
) -> float:
    """
    Backwards-compatible wrapper that now uses linear formula.
    compound_base and compound_exponent are ignored in the new formula.
    """
    return calculate_linear_multiplier(stars, weights, min_multiplier, max_multiplier)


def generate_star_distribution(
    users: int,
    star_config: dict,
    seed: Optional[int] = None
) -> Tuple[List[float], FiveAStarDistribution]:
    """
    Generate star percentage distribution for a single star across all users.
    
    Args:
        users: Number of users
        star_config: Configuration dict with avg_percentage, std_deviation, etc.
        seed: Random seed for reproducibility
    
    Returns:
        Tuple of (list of user percentages, FiveAStarDistribution summary)
    """
    avg_pct = star_config.get('avg_percentage', 50.0)
    std_dev = star_config.get('std_deviation', 20.0)
    min_pct = star_config.get('min_percentage', 5.0)
    max_pct = star_config.get('max_percentage', 100.0)
    weight = star_config.get('weight', 0.2)
    star_name = star_config.get('star_name', 'unknown')
    
    # Generate distribution
    percentages = generate_truncated_normal(
        mean=avg_pct,
        std_dev=std_dev,
        min_val=min_pct,
        max_val=max_pct,
        count=users,
        seed=seed
    )
    
    # Calculate tier counts
    bronze_count = sum(1 for p in percentages if p <= TIER_BRONZE_MAX)
    silver_count = sum(1 for p in percentages if TIER_BRONZE_MAX < p <= TIER_SILVER_MAX)
    gold_count = sum(1 for p in percentages if TIER_SILVER_MAX < p <= TIER_GOLD_MAX)
    diamond_count = sum(1 for p in percentages if p > TIER_GOLD_MAX)
    
    # Calculate statistics
    actual_avg = sum(percentages) / len(percentages) if percentages else 0
    sorted_pcts = sorted(percentages)
    median = sorted_pcts[len(sorted_pcts) // 2] if sorted_pcts else 0
    actual_min = min(percentages) if percentages else 0
    actual_max = max(percentages) if percentages else 0
    
    # Calculate standard deviation
    if len(percentages) > 1:
        variance = sum((p - actual_avg) ** 2 for p in percentages) / len(percentages)
        actual_std = math.sqrt(variance)
    else:
        actual_std = 0
    
    distribution = FiveAStarDistribution(
        star_name=star_name,
        display_name=STAR_DISPLAY_NAMES.get(star_name, star_name.title()),
        avg_percentage=round(actual_avg, 2),
        min_percentage=round(actual_min, 2),
        max_percentage=round(actual_max, 2),
        std_deviation=round(actual_std, 2),
        median_percentage=round(median, 2),
        bronze_count=bronze_count,
        silver_count=silver_count,
        gold_count=gold_count,
        diamond_count=diamond_count,
        tier_counts={
            'bronze': bronze_count,
            'silver': silver_count,
            'gold': gold_count,
            'diamond': diamond_count,
        },
        bronze_percent=round(bronze_count / users * 100, 1) if users > 0 else 0,
        silver_percent=round(silver_count / users * 100, 1) if users > 0 else 0,
        gold_percent=round(gold_count / users * 100, 1) if users > 0 else 0,
        diamond_percent=round(diamond_count / users * 100, 1) if users > 0 else 0,
        weight=weight,
    )
    
    return percentages, distribution


def generate_segment_users(
    count: int,
    segment_config: dict,
    weights: Dict[str, float],
    min_multiplier: float,
    max_multiplier: float,
    seed: Optional[int] = None
) -> List[UserStarProfile]:
    """
    Generate user profiles for a specific segment.
    
    Args:
        count: Number of users in this segment
        segment_config: Segment configuration with star means and std_dev
        weights: Star weights for multiplier calculation
        min_multiplier: Minimum allowed multiplier
        max_multiplier: Maximum allowed multiplier
        seed: Random seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)
    
    profiles = []
    std_dev = segment_config['std_dev']
    
    for i in range(count):
        # Generate each star from segment-specific distribution
        # Min is 0.0 so users can truly earn ZERO if all stars are 0%
        identity = clamp(
            random.gauss(segment_config['identity_mean'], std_dev),
            0.0, 100.0
        )
        accuracy = clamp(
            random.gauss(segment_config['accuracy_mean'], std_dev),
            0.0, 100.0
        )
        agility = clamp(
            random.gauss(segment_config['agility_mean'], std_dev),
            0.0, 100.0
        )
        activity = clamp(
            random.gauss(segment_config['activity_mean'], std_dev),
            0.0, 100.0
        )
        approved = clamp(
            random.gauss(segment_config['approved_mean'], std_dev),
            0.0, 100.0
        )
        
        profile = UserStarProfile(
            identity=identity,
            accuracy=accuracy,
            agility=agility,
            activity=activity,
            approved=approved,
        )
        
        # Calculate linear multiplier
        profile.compound_multiplier = calculate_linear_multiplier(
            profile, weights, min_multiplier, max_multiplier
        )
        
        profiles.append(profile)
    
    return profiles


def generate_user_profiles(
    users: int,
    params: SimulationParameters,
    seed: Optional[int] = 42
) -> Tuple[List[UserStarProfile], Dict[str, FiveAStarDistribution], Dict[str, dict]]:
    """
    Generate 5A star profiles for all users using segment-based distribution.
    
    Based on the 90-9-1 rule for social media, users are distributed into 4 segments:
    - Lurkers (60%): View only, minimal interaction
    - Casual (25%): Weekly activity, some engagement
    - Active (12%): Daily activity, regular posting
    - Power Users (3%): High creators, verified, engaged
    
    Returns:
        Tuple of (list of user profiles, dict of star distributions, segment breakdown)
    """
    five_a = params.five_a
    if five_a is None:
        return [], {}, {}
    
    # Build weights dict
    weights = {
        'identity': five_a.identity_star.weight,
        'accuracy': five_a.accuracy_star.weight,
        'agility': five_a.agility_star.weight,
        'activity': five_a.activity_star.weight,
        'approved': five_a.approved_star.weight,
    }
    
    profiles = []
    segment_breakdown = {}
    
    # Check if we should use segment-based distribution
    use_segments = getattr(five_a, 'use_segments', True)
    
    if use_segments and users > 0:
        # Get segment percentages from params or use defaults
        # Inactive users (20%) are ghost accounts that earn ZERO VCoin
        segment_percentages = {
            'inactive': getattr(five_a, 'segment_inactive_percent', 0.20),
            'lurkers': getattr(five_a, 'segment_lurkers_percent', 0.40),
            'casual': getattr(five_a, 'segment_casual_percent', 0.25),
            'active': getattr(five_a, 'segment_active_percent', 0.12),
            'power_users': getattr(five_a, 'segment_power_percent', 0.03),
        }
        
        # Calculate user counts per segment
        segment_counts = {}
        remaining = users
        for i, segment_name in enumerate(SEGMENT_ORDER):
            if i == len(SEGMENT_ORDER) - 1:
                # Last segment gets all remaining to avoid rounding issues
                segment_counts[segment_name] = remaining
            else:
                count = int(users * segment_percentages[segment_name])
                segment_counts[segment_name] = count
                remaining -= count
        
        # Generate users for each segment
        for i, segment_name in enumerate(SEGMENT_ORDER):
            segment_config = USER_SEGMENTS[segment_name]
            count = segment_counts[segment_name]
            
            if count > 0:
                segment_seed = (seed + i * 1000) if seed else None
                segment_profiles = generate_segment_users(
                    count,
                    segment_config,
                    weights,
                    five_a.min_multiplier,
                    five_a.max_multiplier,
                    segment_seed
                )
                profiles.extend(segment_profiles)
                
                # Calculate segment statistics
                if segment_profiles:
                    segment_mults = [p.compound_multiplier for p in segment_profiles]
                    segment_breakdown[segment_name] = {
                        'name': segment_config['name'],
                        'description': segment_config['description'],
                        'count': count,
                        'percent': count / users * 100,
                        'avg_multiplier': sum(segment_mults) / len(segment_mults),
                        'min_multiplier': min(segment_mults),
                        'max_multiplier': max(segment_mults),
                    }
    else:
        # Fallback to uniform distribution (legacy behavior)
        star_configs = {
            'identity': {
                'star_name': 'identity',
                'avg_percentage': five_a.identity_star.avg_percentage,
                'std_deviation': five_a.identity_star.std_deviation,
                'min_percentage': five_a.identity_star.min_percentage,
                'max_percentage': five_a.identity_star.max_percentage,
                'weight': five_a.identity_star.weight,
            },
            'accuracy': {
                'star_name': 'accuracy',
                'avg_percentage': five_a.accuracy_star.avg_percentage,
                'std_deviation': five_a.accuracy_star.std_deviation,
                'min_percentage': five_a.accuracy_star.min_percentage,
                'max_percentage': five_a.accuracy_star.max_percentage,
                'weight': five_a.accuracy_star.weight,
            },
            'agility': {
                'star_name': 'agility',
                'avg_percentage': five_a.agility_star.avg_percentage,
                'std_deviation': five_a.agility_star.std_deviation,
                'min_percentage': five_a.agility_star.min_percentage,
                'max_percentage': five_a.agility_star.max_percentage,
                'weight': five_a.agility_star.weight,
            },
            'activity': {
                'star_name': 'activity',
                'avg_percentage': five_a.activity_star.avg_percentage,
                'std_deviation': five_a.activity_star.std_deviation,
                'min_percentage': five_a.activity_star.min_percentage,
                'max_percentage': five_a.activity_star.max_percentage,
                'weight': five_a.activity_star.weight,
            },
            'approved': {
                'star_name': 'approved',
                'avg_percentage': five_a.approved_star.avg_percentage,
                'std_deviation': five_a.approved_star.std_deviation,
                'min_percentage': five_a.approved_star.min_percentage,
                'max_percentage': five_a.approved_star.max_percentage,
                'weight': five_a.approved_star.weight,
            },
        }
        
        # Generate distributions for each star
        star_percentages = {}
        for i, (star_name, config) in enumerate(star_configs.items()):
            star_seed = seed + i if seed else None
            percentages, _ = generate_star_distribution(users, config, star_seed)
            star_percentages[star_name] = percentages
        
        # Create user profiles
        for i in range(users):
            profile = UserStarProfile(
                identity=star_percentages['identity'][i],
                accuracy=star_percentages['accuracy'][i],
                agility=star_percentages['agility'][i],
                activity=star_percentages['activity'][i],
                approved=star_percentages['approved'][i],
            )
            profile.compound_multiplier = calculate_linear_multiplier(
                profile, weights, five_a.min_multiplier, five_a.max_multiplier
            )
            profiles.append(profile)
    
    # Shuffle profiles to mix segments (more realistic)
    if seed is not None:
        random.seed(seed)
    random.shuffle(profiles)
    
    # Build star distributions from all profiles
    star_distributions = {}
    for star_name in STAR_NAMES:
        percentages = [getattr(p, star_name) for p in profiles]
        
        if percentages:
            avg_pct = sum(percentages) / len(percentages)
            sorted_pcts = sorted(percentages)
            median = sorted_pcts[len(sorted_pcts) // 2]
            variance = sum((p - avg_pct) ** 2 for p in percentages) / len(percentages)
            std = math.sqrt(variance)
            
            bronze_count = sum(1 for p in percentages if p <= TIER_BRONZE_MAX)
            silver_count = sum(1 for p in percentages if TIER_BRONZE_MAX < p <= TIER_SILVER_MAX)
            gold_count = sum(1 for p in percentages if TIER_SILVER_MAX < p <= TIER_GOLD_MAX)
            diamond_count = sum(1 for p in percentages if p > TIER_GOLD_MAX)
            
            star_distributions[star_name] = FiveAStarDistribution(
                star_name=star_name,
                display_name=STAR_DISPLAY_NAMES.get(star_name, star_name.title()),
                avg_percentage=round(avg_pct, 2),
                min_percentage=round(min(percentages), 2),
                max_percentage=round(max(percentages), 2),
                std_deviation=round(std, 2),
                median_percentage=round(median, 2),
                bronze_count=bronze_count,
                silver_count=silver_count,
                gold_count=gold_count,
                diamond_count=diamond_count,
                weight=weights.get(star_name, 0.2),
                tier_counts={
                    'bronze': bronze_count,
                    'silver': silver_count,
                    'gold': gold_count,
                    'diamond': diamond_count,
                }
            )
    
    return profiles, star_distributions, segment_breakdown


def create_typical_user_profile(
    profiles: List[UserStarProfile],
    tier: str,
    weights: Dict[str, float],
) -> Optional[FiveAUserProfile]:
    """
    Create a representative user profile for a given tier.
    """
    # Filter profiles by tier based on average percentage
    tier_thresholds = {
        'bronze': (0, TIER_BRONZE_MAX),
        'silver': (TIER_BRONZE_MAX, TIER_SILVER_MAX),
        'gold': (TIER_SILVER_MAX, TIER_GOLD_MAX),
        'diamond': (TIER_GOLD_MAX, 100),
    }
    
    if tier not in tier_thresholds:
        return None
    
    min_avg, max_avg = tier_thresholds[tier]
    tier_profiles = [
        p for p in profiles 
        if min_avg < p.get_average(weights) <= max_avg
    ]
    
    if not tier_profiles:
        return None
    
    # Calculate average for this tier
    avg_identity = sum(p.identity for p in tier_profiles) / len(tier_profiles)
    avg_accuracy = sum(p.accuracy for p in tier_profiles) / len(tier_profiles)
    avg_agility = sum(p.agility for p in tier_profiles) / len(tier_profiles)
    avg_activity = sum(p.activity for p in tier_profiles) / len(tier_profiles)
    avg_approved = sum(p.approved for p in tier_profiles) / len(tier_profiles)
    avg_multiplier = sum(p.compound_multiplier for p in tier_profiles) / len(tier_profiles)
    
    total_users = len(profiles)
    
    return FiveAUserProfile(
        tier=tier,
        identity_pct=round(avg_identity, 1),
        accuracy_pct=round(avg_accuracy, 1),
        agility_pct=round(avg_agility, 1),
        activity_pct=round(avg_activity, 1),
        approved_pct=round(avg_approved, 1),
        compound_multiplier=round(avg_multiplier, 3),
        user_count=len(tier_profiles),
        percent_of_users=round(len(tier_profiles) / total_users * 100, 1) if total_users > 0 else 0,
    )


# =============================================================================
# MAIN CALCULATION FUNCTION
# =============================================================================

def calculate_five_a(
    params: SimulationParameters,
    users: int,
    base_reward_pool: float = 0,
    base_fee_revenue: float = 0,
    staking_apy: float = 0.10,
    total_staked: float = 0,
    governance_power: float = 0,
) -> FiveAResult:
    """
    Calculate 5A Policy results for the simulation.
    
    Args:
        params: Simulation parameters with five_a configuration
        users: Number of active users
        base_reward_pool: Base reward pool in VCoin (before 5A adjustments)
        base_fee_revenue: Base fee revenue in USD (before 5A adjustments)
        staking_apy: Base staking APY (e.g., 0.10 for 10%)
        total_staked: Total VCoin staked
        governance_power: Total governance voting power
    
    Returns:
        FiveAResult with complete analysis
    """
    five_a = params.five_a
    
    # Check if 5A is enabled
    if five_a is None or not five_a.enable_five_a or users <= 0:
        return FiveAResult(
            enabled=False,
            total_users=users,
        )
    
    # Generate user profiles with segment-based distribution
    profiles, star_distributions, segment_breakdown = generate_user_profiles(users, params)
    
    if not profiles:
        return FiveAResult(
            enabled=True,
            total_users=users,
        )
    
    # Build weights dict
    weights = {
        'identity': five_a.identity_star.weight,
        'accuracy': five_a.accuracy_star.weight,
        'agility': five_a.agility_star.weight,
        'activity': five_a.activity_star.weight,
        'approved': five_a.approved_star.weight,
    }
    
    # Extract multipliers
    multipliers = [p.compound_multiplier for p in profiles]
    sorted_multipliers = sorted(multipliers)
    
    # Calculate multiplier statistics
    avg_multiplier = sum(multipliers) / len(multipliers)
    median_multiplier = sorted_multipliers[len(sorted_multipliers) // 2]
    min_mult = min(multipliers)
    max_mult = max(multipliers)
    
    # Standard deviation
    variance = sum((m - avg_multiplier) ** 2 for m in multipliers) / len(multipliers)
    std_multiplier = math.sqrt(variance)
    
    # Multiplier tier counts
    penalized_count = sum(1 for m in multipliers if m < MULTIPLIER_PENALIZED_MAX)
    neutral_count = sum(1 for m in multipliers if MULTIPLIER_PENALIZED_MAX <= m < MULTIPLIER_NEUTRAL_MAX)
    boosted_count = sum(1 for m in multipliers if MULTIPLIER_NEUTRAL_MAX <= m < MULTIPLIER_BOOSTED_MAX)
    elite_count = sum(1 for m in multipliers if m >= MULTIPLIER_BOOSTED_MAX)
    
    # Percentile calculations
    p10_idx = max(0, int(len(sorted_multipliers) * 0.10) - 1)
    p25_idx = max(0, int(len(sorted_multipliers) * 0.25) - 1)
    p75_idx = min(len(sorted_multipliers) - 1, int(len(sorted_multipliers) * 0.75))
    p90_idx = min(len(sorted_multipliers) - 1, int(len(sorted_multipliers) * 0.90))
    
    bottom_10_mult = sorted_multipliers[p10_idx]
    bottom_25_mult = sorted_multipliers[p25_idx]
    top_25_mult = sorted_multipliers[p75_idx]
    top_10_mult = sorted_multipliers[p90_idx]
    
    # Population star averages
    pop_avg_identity = sum(p.identity for p in profiles) / len(profiles)
    pop_avg_accuracy = sum(p.accuracy for p in profiles) / len(profiles)
    pop_avg_agility = sum(p.agility for p in profiles) / len(profiles)
    pop_avg_activity = sum(p.activity for p in profiles) / len(profiles)
    pop_avg_approved = sum(p.approved for p in profiles) / len(profiles)
    
    # Weighted overall average
    pop_avg_overall = (
        pop_avg_identity * weights['identity'] +
        pop_avg_accuracy * weights['accuracy'] +
        pop_avg_agility * weights['agility'] +
        pop_avg_activity * weights['activity'] +
        pop_avg_approved * weights['approved']
    ) / sum(weights.values())
    
    # Create typical user profiles
    typical_bronze = create_typical_user_profile(profiles, 'bronze', weights)
    typical_silver = create_typical_user_profile(profiles, 'silver', weights)
    typical_gold = create_typical_user_profile(profiles, 'gold', weights)
    typical_diamond = create_typical_user_profile(profiles, 'diamond', weights)
    
    # Calculate economic impact on rewards
    reward_impact_weight = five_a.reward_impact_weight
    
    # Each user gets base_reward * multiplier
    # We need to normalize so total rewards stay the same
    total_multiplier_weight = sum(multipliers)
    normalization_factor = len(multipliers) / total_multiplier_weight if total_multiplier_weight > 0 else 1.0
    
    reward_boost_total = 0.0
    reward_reduction_total = 0.0
    
    base_per_user = base_reward_pool / users if users > 0 else 0
    
    for mult in multipliers:
        adjusted_mult = 1.0 + (mult - 1.0) * reward_impact_weight
        normalized_mult = adjusted_mult * normalization_factor
        
        if normalized_mult > 1.0:
            reward_boost_total += base_per_user * (normalized_mult - 1.0)
        else:
            reward_reduction_total += base_per_user * (1.0 - normalized_mult)
    
    net_reward_adjustment = reward_boost_total - reward_reduction_total
    reward_redistribution_pct = (reward_boost_total / base_reward_pool * 100) if base_reward_pool > 0 else 0
    
    # Calculate fee discount impact
    fee_discount_max = five_a.fee_discount_max
    
    # Users with multiplier > 1.0 get fee discounts proportional to their boost
    fee_discount_total = 0.0
    for mult in multipliers:
        if mult > 1.0:
            # Discount scales from 0% at 1.0x to max_discount at max_multiplier
            discount_factor = min(1.0, (mult - 1.0) / (five_a.max_multiplier - 1.0))
            user_fee_share = base_fee_revenue / users if users > 0 else 0
            fee_discount_total += user_fee_share * discount_factor * fee_discount_max
    
    adjusted_fee_revenue = base_fee_revenue - fee_discount_total
    fee_discount_pct = (fee_discount_total / base_fee_revenue * 100) if base_fee_revenue > 0 else 0
    
    # Calculate staking APY boost
    staking_apy_bonus_max = five_a.staking_apy_bonus_max
    staking_boosts = []
    for mult in multipliers:
        if mult > 1.0:
            boost_factor = min(1.0, (mult - 1.0) / (five_a.max_multiplier - 1.0))
            staking_boosts.append(staking_apy * boost_factor * staking_apy_bonus_max)
        else:
            staking_boosts.append(0.0)
    
    staking_apy_boost_avg = sum(staking_boosts) / len(staking_boosts) if staking_boosts else 0
    staking_apy_boost_max_actual = max(staking_boosts) if staking_boosts else 0
    
    # Calculate governance power boost
    governance_bonus_max = five_a.governance_power_bonus_max
    gov_boosts = []
    for mult in multipliers:
        if mult > 1.0:
            boost_factor = min(1.0, (mult - 1.0) / (five_a.max_multiplier - 1.0))
            gov_boosts.append(boost_factor * governance_bonus_max)
        else:
            gov_boosts.append(0.0)
    
    governance_power_boost_avg = sum(gov_boosts) / len(gov_boosts) if gov_boosts else 0
    governance_power_boost_max_actual = max(gov_boosts) if gov_boosts else 0
    
    # Calculate content visibility boost
    visibility_bonus_max = five_a.content_visibility_bonus_max
    visibility_boosts = []
    for mult in multipliers:
        if mult > 1.0:
            boost_factor = min(1.0, (mult - 1.0) / (five_a.max_multiplier - 1.0))
            visibility_boosts.append(boost_factor * visibility_bonus_max)
        else:
            visibility_boosts.append(0.0)
    
    content_visibility_boost_avg = sum(visibility_boosts) / len(visibility_boosts) if visibility_boosts else 0
    content_visibility_boost_max_actual = max(visibility_boosts) if visibility_boosts else 0
    
    # Calculate exchange fee discount
    exchange_discounts = []
    for mult in multipliers:
        if mult > 1.0:
            boost_factor = min(1.0, (mult - 1.0) / (five_a.max_multiplier - 1.0))
            exchange_discounts.append(boost_factor * fee_discount_max)
        else:
            exchange_discounts.append(0.0)
    
    exchange_fee_discount_avg = sum(exchange_discounts) / len(exchange_discounts) if exchange_discounts else 0
    exchange_fee_discount_max_actual = max(exchange_discounts) if exchange_discounts else 0
    
    # Create module impact details
    module_impacts = [
        FiveAModuleImpact(
            module_name="Rewards",
            base_value=base_reward_pool,
            adjusted_value=base_reward_pool,  # Total stays same, distribution changes
            boost_amount=reward_boost_total,
            boost_percent=reward_redistribution_pct,
            description=f"Redistributes {reward_redistribution_pct:.1f}% of rewards from low to high performers"
        ),
        FiveAModuleImpact(
            module_name="Fees",
            base_value=base_fee_revenue,
            adjusted_value=adjusted_fee_revenue,
            boost_amount=-fee_discount_total,
            boost_percent=-fee_discount_pct,
            description=f"High performers receive up to {fee_discount_max*100:.0f}% fee discount"
        ),
        FiveAModuleImpact(
            module_name="Staking",
            base_value=staking_apy * 100,
            adjusted_value=(staking_apy + staking_apy_boost_avg) * 100,
            boost_amount=staking_apy_boost_avg * 100,
            boost_percent=(staking_apy_boost_avg / staking_apy * 100) if staking_apy > 0 else 0,
            description=f"Top performers earn up to +{staking_apy_bonus_max*100:.0f}% bonus APY"
        ),
        FiveAModuleImpact(
            module_name="Governance",
            base_value=governance_power,
            adjusted_value=governance_power * (1 + governance_power_boost_avg),
            boost_amount=governance_power * governance_power_boost_avg,
            boost_percent=governance_power_boost_avg * 100,
            description=f"Voting power boosted up to {governance_bonus_max*100:.0f}% for high performers"
        ),
        FiveAModuleImpact(
            module_name="Content",
            base_value=100,  # Baseline visibility
            adjusted_value=100 * (1 + content_visibility_boost_avg),
            boost_amount=100 * content_visibility_boost_avg,
            boost_percent=content_visibility_boost_avg * 100,
            description=f"Content visibility boosted up to {visibility_bonus_max*100:.0f}% for creators"
        ),
    ]
    
    # Calculate Gini coefficient for fairness
    # Sort multipliers and calculate Lorenz curve
    sorted_mults = sorted(multipliers)
    n = len(sorted_mults)
    cumulative = 0
    area_under = 0
    total = sum(sorted_mults)
    
    for i, m in enumerate(sorted_mults):
        cumulative += m
        area_under += cumulative
    
    area_under = area_under / (n * total) if total > 0 else 0.5
    gini = 1 - 2 * (1 - area_under)
    gini = clamp(gini, 0, 1)
    
    # Fairness score (inverted Gini, 0-100)
    fairness_score = (1 - gini) * 100
    
    # Engagement incentive score based on multiplier spread
    # Higher spread = more incentive, but too high = discouraging
    spread = top_10_mult / bottom_10_mult if bottom_10_mult > 0 else 10
    engagement_score = clamp(50 + (spread - 3) * 10, 0, 100)  # Optimal spread around 3x
    
    # User category counts
    users_with_boost = sum(1 for m in multipliers if m > 1.0)
    users_with_penalty = sum(1 for m in multipliers if m < 1.0)
    users_neutral = users - users_with_boost - users_with_penalty
    
    # ==========================================================================
    # 60-MONTH EVOLUTION PROJECTION
    # ==========================================================================
    # Project how segments and metrics evolve over 5 years using transition matrix
    
    # Get initial segment counts - ensure we have valid counts
    def get_segment_count(seg_name: str, default_pct: float) -> int:
        seg_data = segment_breakdown.get(seg_name, {})
        if isinstance(seg_data, dict) and 'count' in seg_data:
            return seg_data['count']
        return int(users * default_pct)
    
    initial_counts = {
        'inactive': get_segment_count('inactive', 0.20),
        'lurkers': get_segment_count('lurkers', 0.40),
        'casual': get_segment_count('casual', 0.25),
        'active': get_segment_count('active', 0.12),
        'power_users': get_segment_count('power_users', 0.03),
    }
    
    # Ensure we have at least 100 users for meaningful evolution
    if sum(initial_counts.values()) < 100:
        initial_counts = {
            'inactive': int(users * 0.20),
            'lurkers': int(users * 0.40),
            'casual': int(users * 0.25),
            'active': int(users * 0.12),
            'power_users': int(users * 0.03),
        }
    
    # Project 60-month evolution
    projected_counts = initial_counts.copy()
    total_churned = 0
    total_improved = 0
    total_decayed = 0
    monthly_new_users = max(10, int(users * 0.02))  # At least 10 new users/month
    
    for month in range(1, 61):
        platform_maturity = calculate_platform_maturity(month, 60)
        evolution = evolve_user_segments(
            current_counts=projected_counts,
            month=month,
            platform_maturity=platform_maturity,
            new_users=monthly_new_users,
        )
        projected_counts = evolution['counts']
        total_churned += evolution['churned']
        total_improved += evolution['improved']
        total_decayed += evolution['decayed']
    
    # Calculate Month 60 metrics
    total_users_m60 = sum(projected_counts.values())
    if total_users_m60 > 0:
        month60_active_pct = (
            (projected_counts.get('active', 0) + projected_counts.get('power_users', 0)) 
            / total_users_m60 * 100
        )
        # Estimate Month 60 avg multiplier based on segment distribution
        segment_mults = {
            'inactive': 0.03, 'lurkers': 0.23, 'casual': 0.98, 
            'active': 1.41, 'power_users': 1.74
        }
        month60_avg_mult = sum(
            (projected_counts.get(seg, 0) / total_users_m60) * mult 
            for seg, mult in segment_mults.items()
        )
    else:
        month60_active_pct = 35.0
        month60_avg_mult = 0.95
    
    # Calculate Month 1 baseline
    month1_active_pct = (
        segment_breakdown.get('active', {}).get('percent', 12.0) +
        segment_breakdown.get('power_users', {}).get('percent', 3.0)
    )
    
    # Calculate cumulative impacts over 60 months
    # Growth compounds: each month's boost contributes to next month's base
    avg_monthly_growth_boost = (month60_avg_mult - avg_multiplier) / 60 * 0.05  # 5% per 1x
    cumulative_growth = (1 + avg_monthly_growth_boost) ** 60 - 1
    
    avg_monthly_retention_boost = (month60_avg_mult - avg_multiplier) / 60 * 0.10  # 10% per 1x
    cumulative_retention = (1 + avg_monthly_retention_boost) ** 60 - 1
    
    # Price impact compounds over time
    avg_monthly_price_impact = 0.001  # 0.1% per month average
    cumulative_price = (1 + avg_monthly_price_impact) ** 60 - 1
    
    # Monthly rates
    avg_improvement_rate = (total_improved / 60 / users * 100) if users > 0 else 0
    avg_decay_rate = (total_decayed / 60 / users * 100) if users > 0 else 0
    
    return FiveAResult(
        enabled=True,
        
        # Star distributions
        identity_star=star_distributions.get('identity', FiveAStarDistribution(star_name='identity')),
        accuracy_star=star_distributions.get('accuracy', FiveAStarDistribution(star_name='accuracy')),
        agility_star=star_distributions.get('agility', FiveAStarDistribution(star_name='agility')),
        activity_star=star_distributions.get('activity', FiveAStarDistribution(star_name='activity')),
        approved_star=star_distributions.get('approved', FiveAStarDistribution(star_name='approved')),
        
        # Population averages
        population_avg_identity=round(pop_avg_identity, 1),
        population_avg_accuracy=round(pop_avg_accuracy, 1),
        population_avg_agility=round(pop_avg_agility, 1),
        population_avg_activity=round(pop_avg_activity, 1),
        population_avg_approved=round(pop_avg_approved, 1),
        population_avg_overall=round(pop_avg_overall, 1),
        
        # Multiplier metrics
        avg_compound_multiplier=round(avg_multiplier, 3),
        median_compound_multiplier=round(median_multiplier, 3),
        min_compound_multiplier=round(min_mult, 3),
        max_compound_multiplier=round(max_mult, 3),
        std_compound_multiplier=round(std_multiplier, 3),
        
        # Multiplier tier distribution
        multiplier_tier_counts={
            'penalized': penalized_count,
            'neutral': neutral_count,
            'boosted': boosted_count,
            'elite': elite_count,
        },
        penalized_users_count=penalized_count,
        neutral_users_count=neutral_count,
        boosted_users_count=boosted_count,
        elite_users_count=elite_count,
        
        # Percentiles
        top_10_percent_multiplier=round(top_10_mult, 3),
        top_25_percent_multiplier=round(top_25_mult, 3),
        bottom_10_percent_multiplier=round(bottom_10_mult, 3),
        bottom_25_percent_multiplier=round(bottom_25_mult, 3),
        
        # Typical profiles
        typical_bronze_user=typical_bronze,
        typical_silver_user=typical_silver,
        typical_gold_user=typical_gold,
        typical_diamond_user=typical_diamond,
        
        # Economic impact - rewards
        base_reward_pool_vcoin=round(base_reward_pool, 2),
        adjusted_reward_pool_vcoin=round(base_reward_pool, 2),
        reward_boost_total_vcoin=round(reward_boost_total, 2),
        reward_reduction_total_vcoin=round(reward_reduction_total, 2),
        net_reward_adjustment_vcoin=round(net_reward_adjustment, 2),
        reward_redistribution_percent=round(reward_redistribution_pct, 2),
        
        # Economic impact - fees
        base_fee_revenue_usd=round(base_fee_revenue, 2),
        adjusted_fee_revenue_usd=round(adjusted_fee_revenue, 2),
        fee_discount_total_usd=round(fee_discount_total, 2),
        fee_discount_percent=round(fee_discount_pct, 2),
        
        # Module boosts
        staking_apy_boost_avg=round(staking_apy_boost_avg * 100, 2),
        staking_apy_boost_max=round(staking_apy_boost_max_actual * 100, 2),
        governance_power_boost_avg=round(governance_power_boost_avg * 100, 2),
        governance_power_boost_max=round(governance_power_boost_max_actual * 100, 2),
        content_visibility_boost_avg=round(content_visibility_boost_avg * 100, 2),
        content_visibility_boost_max=round(content_visibility_boost_max_actual * 100, 2),
        exchange_fee_discount_avg=round(exchange_fee_discount_avg * 100, 2),
        exchange_fee_discount_max=round(exchange_fee_discount_max_actual * 100, 2),
        
        # Module impacts
        module_impacts=module_impacts,
        
        # Fairness metrics
        gini_coefficient=round(gini, 4),
        fairness_score=round(fairness_score, 1),
        engagement_incentive_score=round(engagement_score, 1),
        
        # User counts
        total_users=users,
        users_with_boost=users_with_boost,
        users_with_penalty=users_with_penalty,
        users_neutral=users_neutral,
        
        # Platform-wide impact multipliers
        # These affect user growth, retention, revenue, and token price
        retention_boost=round((avg_multiplier - 1.0) * 0.1, 4),  # +10% retention boost per 1x multiplier above baseline
        growth_boost=round((avg_multiplier - 1.0) * 0.05, 4),  # +5% growth boost per 1x multiplier above baseline
        revenue_boost=round(content_visibility_boost_avg * 0.1, 4),  # Revenue boost from content visibility
        token_price_impact=round((engagement_score / 100 - 0.5) * 0.02, 4),  # Price impact from engagement incentive
        
        # Segment-based distribution (90-9-1 rule)
        use_segments=getattr(five_a, 'use_segments', True),
        segment_breakdown=segment_breakdown,
        
        # Segment counts and statistics
        # INACTIVE: Ghost users who earn ZERO VCoin
        inactive_count=segment_breakdown.get('inactive', {}).get('count', 0),
        inactive_percent=segment_breakdown.get('inactive', {}).get('percent', 20.0),
        inactive_avg_multiplier=round(segment_breakdown.get('inactive', {}).get('avg_multiplier', 0.03), 3),
        
        lurkers_count=segment_breakdown.get('lurkers', {}).get('count', 0),
        lurkers_percent=segment_breakdown.get('lurkers', {}).get('percent', 40.0),
        lurkers_avg_multiplier=round(segment_breakdown.get('lurkers', {}).get('avg_multiplier', 0.23), 3),
        
        casual_count=segment_breakdown.get('casual', {}).get('count', 0),
        casual_percent=segment_breakdown.get('casual', {}).get('percent', 25.0),
        casual_avg_multiplier=round(segment_breakdown.get('casual', {}).get('avg_multiplier', 0.95), 3),
        
        active_count=segment_breakdown.get('active', {}).get('count', 0),
        active_percent=segment_breakdown.get('active', {}).get('percent', 12.0),
        active_avg_multiplier=round(segment_breakdown.get('active', {}).get('avg_multiplier', 1.40), 3),
        
        power_users_count=segment_breakdown.get('power_users', {}).get('count', 0),
        power_users_percent=segment_breakdown.get('power_users', {}).get('percent', 3.0),
        power_users_avg_multiplier=round(segment_breakdown.get('power_users', {}).get('avg_multiplier', 1.74), 3),
        
        # ZERO EARNERS: Users with multiplier < 0.1 effectively earn nothing
        # Multiplier 0.1x means 5% stars average = essentially 0 VCoin
        zero_earners_count=sum(1 for m in multipliers if m < 0.1),
        zero_earners_percent=round((sum(1 for m in multipliers if m < 0.1) / len(multipliers) * 100) if multipliers else 0, 1),
        
        # 60-MONTH EVOLUTION TRACKING
        # These show projected changes over 5 years
        segment_evolution_history=[],  # Populated during monthly progression
        total_churned_users=total_churned,
        total_improved_users=total_improved,
        total_decayed_users=total_decayed,
        avg_improvement_rate=round(avg_improvement_rate, 2),
        avg_decay_rate=round(avg_decay_rate, 2),
        
        # Cumulative impact over 60 months
        cumulative_retention_boost=round(cumulative_retention, 4),
        cumulative_growth_boost=round(cumulative_growth, 4),
        cumulative_price_impact=round(cumulative_price * 100, 2),  # As percentage
        
        # Month 1 vs Month 60 comparison
        month1_avg_multiplier=round(avg_multiplier, 2),
        month60_avg_multiplier=round(month60_avg_mult, 2),
        month1_active_percent=round(month1_active_pct, 1),
        month60_active_percent=round(month60_active_pct, 1),
    )


def get_user_multiplier_adjustment(
    five_a_result: FiveAResult,
    percentile: str = 'avg'
) -> float:
    """
    Get a multiplier for adjusting module calculations based on 5A.
    
    Args:
        five_a_result: The calculated 5A result
        percentile: 'avg', 'top_10', 'top_25', 'bottom_10', 'bottom_25', 'median'
    
    Returns:
        Multiplier to apply to module calculations
    """
    if not five_a_result.enabled:
        return 1.0
    
    if percentile == 'avg':
        return five_a_result.avg_compound_multiplier
    elif percentile == 'median':
        return five_a_result.median_compound_multiplier
    elif percentile == 'top_10':
        return five_a_result.top_10_percent_multiplier
    elif percentile == 'top_25':
        return five_a_result.top_25_percent_multiplier
    elif percentile == 'bottom_10':
        return five_a_result.bottom_10_percent_multiplier
    elif percentile == 'bottom_25':
        return five_a_result.bottom_25_percent_multiplier
    else:
        return 1.0

