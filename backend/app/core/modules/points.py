"""
Points Module - Pre-launch points system with TGE token conversion.

=== PRE-LAUNCH POINTS SYSTEM (2025 Standards) ===

Philosophy:
- Build community before TGE
- Reward early adopters fairly
- Prevent gaming with anti-sybil measures
- Transparent conversion formula

Points Pool:
- 10,000,000 VCoin (1% of total supply)
- Distributed proportionally at TGE
- Formula: user_tokens = (user_points / total_points) × 10,000,000

Point Earning Activities:
| Activity                    | Points | Max/Day    |
|-----------------------------|--------|------------|
| Waitlist Signup             | 100    | Once       |
| Social Follow (per platform)| 25     | Once each  |
| Daily Check-in              | 5      | 5          |
| Invite Friend (joins)       | 50     | Unlimited  |
| Invite Friend (verifies)    | 100    | Unlimited  |
| Complete Tasks              | 10-50  | Varies     |
| Beta Testing                | 500    | Once       |

Anti-Gaming:
- Points are non-transferable
- Suspicious accounts flagged (same IP, bot patterns)
- Final allocation reviewed pre-TGE
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, NamedTuple
from enum import Enum


class PointActivity(str, Enum):
    """Point-earning activities"""
    WAITLIST_SIGNUP = "waitlist_signup"
    SOCIAL_FOLLOW_TWITTER = "social_follow_twitter"
    SOCIAL_FOLLOW_DISCORD = "social_follow_discord"
    SOCIAL_FOLLOW_TELEGRAM = "social_follow_telegram"
    DAILY_CHECKIN = "daily_checkin"
    INVITE_JOIN = "invite_join"
    INVITE_VERIFY = "invite_verify"
    COMPLETE_TASK = "complete_task"
    BETA_TESTING = "beta_testing"


@dataclass
class PointActivityConfig:
    """Configuration for a point-earning activity"""
    name: str
    points: int
    max_per_day: Optional[int]  # None = once only, -1 = unlimited
    description: str


# Default activity configurations
POINT_ACTIVITIES: Dict[PointActivity, PointActivityConfig] = {
    PointActivity.WAITLIST_SIGNUP: PointActivityConfig(
        name="Waitlist Signup",
        points=100,
        max_per_day=None,  # Once only
        description="Join the waitlist for early access",
    ),
    PointActivity.SOCIAL_FOLLOW_TWITTER: PointActivityConfig(
        name="Follow on Twitter/X",
        points=25,
        max_per_day=None,
        description="Follow official Twitter account",
    ),
    PointActivity.SOCIAL_FOLLOW_DISCORD: PointActivityConfig(
        name="Join Discord",
        points=25,
        max_per_day=None,
        description="Join official Discord server",
    ),
    PointActivity.SOCIAL_FOLLOW_TELEGRAM: PointActivityConfig(
        name="Join Telegram",
        points=25,
        max_per_day=None,
        description="Join official Telegram group",
    ),
    PointActivity.DAILY_CHECKIN: PointActivityConfig(
        name="Daily Check-in",
        points=5,
        max_per_day=1,
        description="Check in daily on the platform",
    ),
    PointActivity.INVITE_JOIN: PointActivityConfig(
        name="Invite Friend (Joins Waitlist)",
        points=50,
        max_per_day=-1,  # Unlimited
        description="Friend joins waitlist via your link",
    ),
    PointActivity.INVITE_VERIFY: PointActivityConfig(
        name="Invite Friend (Verifies Email)",
        points=100,
        max_per_day=-1,
        description="Friend verifies their email",
    ),
    PointActivity.COMPLETE_TASK: PointActivityConfig(
        name="Complete Task",
        points=25,  # Average of 10-50
        max_per_day=5,
        description="Complete platform tasks/quests",
    ),
    PointActivity.BETA_TESTING: PointActivityConfig(
        name="Beta Testing",
        points=500,
        max_per_day=None,
        description="Participate in beta testing program",
    ),
}


# Points pool configuration
POINTS_POOL_TOKENS = 10_000_000  # 1% of 1B supply
POINTS_POOL_PERCENT = 0.01  # 1%


@dataclass
class PointsUserSegment:
    """User segment for points distribution modeling"""
    name: str
    percent_of_waitlist: float
    avg_points: int
    description: str


# User segment distribution for modeling
POINTS_USER_SEGMENTS = [
    PointsUserSegment(
        name="Casual",
        percent_of_waitlist=0.50,
        avg_points=150,  # Signup + 1-2 socials
        description="Basic signup, minimal engagement",
    ),
    PointsUserSegment(
        name="Active",
        percent_of_waitlist=0.30,
        avg_points=500,  # All socials + some check-ins + 1-2 invites
        description="Follows socials, occasional check-ins",
    ),
    PointsUserSegment(
        name="Power User",
        percent_of_waitlist=0.15,
        avg_points=2000,  # All activities + multiple invites
        description="Daily active, invites friends, completes tasks",
    ),
    PointsUserSegment(
        name="Ambassador",
        percent_of_waitlist=0.05,
        avg_points=10000,  # Heavy inviter + all activities
        description="Top referrers, beta testers, community leaders",
    ),
]


@dataclass
class PointsResult:
    """Result of points module calculations"""
    # Pool configuration
    points_pool_tokens: int
    points_pool_percent: float
    
    # Participation metrics
    waitlist_users: int
    participating_users: int
    participation_rate: float
    
    # Points distribution
    total_points_distributed: int
    avg_points_per_user: float
    median_points_estimate: float
    
    # Token conversion
    tokens_per_point: float
    avg_tokens_per_user: float
    
    # Segment breakdown
    users_by_segment: Dict[str, int]
    points_by_segment: Dict[str, int]
    tokens_by_segment: Dict[str, float]
    
    # Anti-gaming metrics
    suspected_sybil_users: int
    sybil_rejection_rate: float
    points_rejected: int
    
    # Activity breakdown
    points_by_activity: Dict[str, int]
    
    # Top earner estimates
    top_1_percent_tokens: float
    top_10_percent_tokens: float
    bottom_50_percent_tokens: float
    
    # Breakdown
    breakdown: Dict


def calculate_points(
    waitlist_users: int,
    participation_rate: float = 0.80,
    sybil_rate: float = 0.05,
    points_pool_tokens: int = POINTS_POOL_TOKENS,
) -> PointsResult:
    """
    Calculate pre-launch points system metrics.
    
    Models the distribution of points among waitlist users and
    calculates expected token allocation at TGE.
    
    Args:
        waitlist_users: Number of users on waitlist
        participation_rate: % of waitlist that earns points
        sybil_rate: % of suspicious accounts to reject
        points_pool_tokens: Token pool for points conversion
    
    Returns:
        PointsResult with all metrics
    """
    # Calculate participating users
    participating_users = int(waitlist_users * participation_rate)
    
    # Apply sybil rejection
    suspected_sybil = int(waitlist_users * sybil_rate)
    eligible_users = max(1, participating_users - suspected_sybil)
    
    # Calculate points by segment
    users_by_segment = {}
    points_by_segment = {}
    total_points = 0
    
    for segment in POINTS_USER_SEGMENTS:
        segment_users = int(eligible_users * segment.percent_of_waitlist)
        segment_points = segment_users * segment.avg_points
        
        users_by_segment[segment.name] = segment_users
        points_by_segment[segment.name] = segment_points
        total_points += segment_points
    
    # Ensure minimum points to prevent division by zero
    total_points = max(1, total_points)
    
    # Calculate token conversion rate
    tokens_per_point = points_pool_tokens / total_points
    
    # Calculate tokens by segment
    tokens_by_segment = {
        name: points * tokens_per_point
        for name, points in points_by_segment.items()
    }
    
    # Average metrics
    avg_points = total_points / eligible_users if eligible_users > 0 else 0
    avg_tokens = points_pool_tokens / eligible_users if eligible_users > 0 else 0
    
    # Median estimate (closer to Casual segment)
    median_points = POINTS_USER_SEGMENTS[0].avg_points * 1.5  # Between Casual and Active
    
    # Points by activity estimate (proportional model)
    activity_weights = {
        'waitlist_signup': 0.15,      # Everyone does this
        'social_follows': 0.20,       # Most do at least 1
        'daily_checkins': 0.25,       # Engaged users
        'invites': 0.30,              # Power users drive this
        'tasks_beta': 0.10,           # Small group
    }
    
    points_by_activity = {
        activity: int(total_points * weight)
        for activity, weight in activity_weights.items()
    }
    
    # Top earner estimates
    # Power law distribution - top users earn disproportionately
    ambassador_total_tokens = tokens_by_segment.get("Ambassador", 0)
    ambassador_users = users_by_segment.get("Ambassador", 1)
    top_1_tokens = ambassador_total_tokens / ambassador_users if ambassador_users > 0 else 0
    
    power_total = tokens_by_segment.get("Power User", 0)
    power_users = users_by_segment.get("Power User", 1)
    top_10_tokens = power_total / power_users if power_users > 0 else 0
    
    casual_total = tokens_by_segment.get("Casual", 0)
    casual_users = users_by_segment.get("Casual", 1)
    bottom_50_tokens = casual_total / casual_users if casual_users > 0 else 0
    
    # Points rejected from sybil
    avg_sybil_points = 500  # Assume sybils try to look like Active users
    points_rejected = suspected_sybil * avg_sybil_points
    
    return PointsResult(
        points_pool_tokens=points_pool_tokens,
        points_pool_percent=POINTS_POOL_PERCENT,
        waitlist_users=waitlist_users,
        participating_users=eligible_users,
        participation_rate=participation_rate,
        total_points_distributed=total_points,
        avg_points_per_user=round(avg_points, 2),
        median_points_estimate=median_points,
        tokens_per_point=round(tokens_per_point, 6),
        avg_tokens_per_user=round(avg_tokens, 2),
        users_by_segment=users_by_segment,
        points_by_segment=points_by_segment,
        tokens_by_segment={k: round(v, 2) for k, v in tokens_by_segment.items()},
        suspected_sybil_users=suspected_sybil,
        sybil_rejection_rate=sybil_rate,
        points_rejected=points_rejected,
        points_by_activity=points_by_activity,
        top_1_percent_tokens=round(top_1_tokens, 2),
        top_10_percent_tokens=round(top_10_tokens, 2),
        bottom_50_percent_tokens=round(bottom_50_tokens, 2),
        breakdown={
            'activities': {
                activity.value: {
                    'name': config.name,
                    'points': config.points,
                    'max_per_day': config.max_per_day,
                }
                for activity, config in POINT_ACTIVITIES.items()
            },
            'segments': {
                segment.name: {
                    'percent': segment.percent_of_waitlist,
                    'avg_points': segment.avg_points,
                    'description': segment.description,
                }
                for segment in POINTS_USER_SEGMENTS
            },
            'conversion_example': {
                'user_points': 5000,
                'total_points': total_points,
                'tokens_received': round(5000 * tokens_per_point, 2),
            },
        }
    )

