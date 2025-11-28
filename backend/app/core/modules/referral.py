"""
Referral Module - Tiered referral program with qualification criteria.

=== REFERRAL PROGRAM (2025 Standards) ===

Design Philosophy:
- Rewards genuine user acquisition, not spam
- Rewards tied to referee ACTIVITY, not just signup
- Integrates with viral_coefficient from growth scenarios

Referral Tiers:
| Tier       | Referrals | Bonus/Ref | Max Monthly |
|------------|-----------|-----------|-------------|
| Starter    | 1-10      | 50 VCoin  | 500 VCoin   |
| Builder    | 11-50     | 75 VCoin  | 3,000 VCoin |
| Ambassador | 51-200    | 100 VCoin | 10,000 VCoin|
| Partner    | 200+      | Negotiated| Custom      |

Qualification Criteria:
- Referee must complete 7-day active period
- Referee must verify identity (at least email)
- Referee must make at least 5 posts
- No self-referrals (device/IP tracking)

Integration:
- viral_coefficient (0.3-0.8) models referral effectiveness
- Conservative: 0.3 (each user brings 0.3 new users)
- Base: 0.5 (moderate virality)
- Bullish: 0.8 (strong word-of-mouth)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, NamedTuple
from enum import Enum
from app.models import SimulationParameters


class ReferralTier(str, Enum):
    """Referral tier levels"""
    STARTER = "starter"
    BUILDER = "builder"
    AMBASSADOR = "ambassador"
    PARTNER = "partner"


@dataclass
class ReferralTierConfig:
    """Configuration for a referral tier"""
    name: str
    min_referrals: int
    max_referrals: int
    bonus_per_referral_vcoin: float
    max_monthly_bonus_vcoin: float
    
    def get_bonus_for_count(self, referral_count: int) -> float:
        """Calculate bonus for a given referral count within this tier"""
        if referral_count < self.min_referrals:
            return 0
        
        # Count referrals within this tier's range
        tier_referrals = min(referral_count, self.max_referrals) - self.min_referrals + 1
        if self.min_referrals == 1:
            tier_referrals = min(referral_count, self.max_referrals)
        else:
            tier_referrals = max(0, min(referral_count, self.max_referrals) - self.min_referrals + 1)
        
        raw_bonus = tier_referrals * self.bonus_per_referral_vcoin
        return min(raw_bonus, self.max_monthly_bonus_vcoin)


# Default referral tier configurations
REFERRAL_TIERS: Dict[ReferralTier, ReferralTierConfig] = {
    ReferralTier.STARTER: ReferralTierConfig(
        name="Starter",
        min_referrals=1,
        max_referrals=10,
        bonus_per_referral_vcoin=50.0,
        max_monthly_bonus_vcoin=500.0,
    ),
    ReferralTier.BUILDER: ReferralTierConfig(
        name="Builder",
        min_referrals=11,
        max_referrals=50,
        bonus_per_referral_vcoin=75.0,
        max_monthly_bonus_vcoin=3000.0,
    ),
    ReferralTier.AMBASSADOR: ReferralTierConfig(
        name="Ambassador",
        min_referrals=51,
        max_referrals=200,
        bonus_per_referral_vcoin=100.0,
        max_monthly_bonus_vcoin=10000.0,
    ),
    ReferralTier.PARTNER: ReferralTierConfig(
        name="Partner",
        min_referrals=201,
        max_referrals=999999,  # Unlimited
        bonus_per_referral_vcoin=150.0,  # Negotiated, use high default
        max_monthly_bonus_vcoin=50000.0,  # Custom cap
    ),
}


class ReferralQualificationCriteria(NamedTuple):
    """Criteria for a referral to be considered "active" and qualify for bonus"""
    active_days_required: int = 7  # Days referee must be active
    min_posts_required: int = 5  # Minimum posts by referee
    email_verification_required: bool = True
    device_fingerprint_check: bool = True  # Anti-sybil


# Default qualification criteria
DEFAULT_QUALIFICATION = ReferralQualificationCriteria()


@dataclass
class ReferralResult:
    """Result of referral module calculations"""
    # User segments
    total_users: int
    users_with_referrals: int  # Users who have referred at least 1 person
    total_referrals: int  # Total referee count
    qualified_referrals: int  # Referees meeting qualification criteria
    
    # Tier distribution
    referrers_by_tier: Dict[str, int]
    referrals_by_tier: Dict[str, int]
    
    # Token economics
    bonus_distributed_vcoin: float
    bonus_distributed_usd: float
    avg_bonus_per_referrer_vcoin: float
    
    # Viral metrics
    viral_coefficient: float
    effective_referral_rate: float  # % of users who actively refer
    qualification_rate: float  # % of referrals that qualify
    
    # Cost to platform (this is a COST, not revenue)
    monthly_referral_cost_vcoin: float
    monthly_referral_cost_usd: float
    
    # Anti-sybil metrics
    suspected_sybil_referrals: int
    sybil_rejection_rate: float
    
    # Breakdown
    breakdown: Dict


def get_tier_for_referral_count(count: int) -> ReferralTier:
    """Determine which tier a referrer belongs to based on their referral count"""
    if count >= 201:
        return ReferralTier.PARTNER
    elif count >= 51:
        return ReferralTier.AMBASSADOR
    elif count >= 11:
        return ReferralTier.BUILDER
    elif count >= 1:
        return ReferralTier.STARTER
    else:
        return ReferralTier.STARTER  # Default


def calculate_referrer_bonus(
    referral_count: int,
    qualification_rate: float = 0.70,
) -> float:
    """
    Calculate total bonus for a referrer based on their referral count.
    
    Args:
        referral_count: Number of referrals made
        qualification_rate: % of referrals that meet qualification criteria
    
    Returns:
        Total bonus in VCoin
    """
    # Apply qualification rate
    qualified_referrals = int(referral_count * qualification_rate)
    
    if qualified_referrals <= 0:
        return 0.0
    
    # Calculate tiered bonuses
    total_bonus = 0.0
    remaining = qualified_referrals
    
    # Starter tier (1-10)
    if remaining > 0:
        starter_count = min(remaining, 10)
        total_bonus += starter_count * REFERRAL_TIERS[ReferralTier.STARTER].bonus_per_referral_vcoin
        remaining -= starter_count
    
    # Builder tier (11-50)
    if remaining > 0:
        builder_count = min(remaining, 40)  # 50 - 10 = 40
        total_bonus += builder_count * REFERRAL_TIERS[ReferralTier.BUILDER].bonus_per_referral_vcoin
        remaining -= builder_count
    
    # Ambassador tier (51-200)
    if remaining > 0:
        ambassador_count = min(remaining, 150)  # 200 - 50 = 150
        total_bonus += ambassador_count * REFERRAL_TIERS[ReferralTier.AMBASSADOR].bonus_per_referral_vcoin
        remaining -= ambassador_count
    
    # Partner tier (201+)
    if remaining > 0:
        total_bonus += remaining * REFERRAL_TIERS[ReferralTier.PARTNER].bonus_per_referral_vcoin
    
    return total_bonus


def calculate_referral(
    params: SimulationParameters,
    users: int,
    viral_coefficient: float = 0.5,
    monthly_budget_usd: float = 1000.0,  # Default monthly budget cap
) -> ReferralResult:
    """
    Calculate referral program metrics.
    
    The referral program creates a COST to the platform (bonus distribution),
    but drives user growth through viral mechanics.
    
    IMPORTANT: Costs are capped at monthly_budget_usd to prevent runaway costs
    in early months when revenue is low.
    
    Args:
        params: Simulation parameters
        users: Total user count
        viral_coefficient: Expected viral coefficient (0.3-0.8)
        monthly_budget_usd: Maximum monthly spend on referral bonuses
    
    Returns:
        ReferralResult with all metrics
    """
    # Get referral parameters if available
    referral_params = getattr(params, 'referral', None)
    
    # Override defaults with params if provided
    if referral_params:
        qualification_rate = getattr(referral_params, 'qualification_rate', 0.70)
        active_referrer_rate = getattr(referral_params, 'active_referrer_rate', 0.15)
        sybil_rejection_rate = getattr(referral_params, 'sybil_rejection_rate', 0.05)
        monthly_budget_usd = getattr(referral_params, 'monthly_budget_usd', monthly_budget_usd)
    else:
        qualification_rate = 0.70  # 70% of referrals meet criteria
        active_referrer_rate = 0.15  # 15% of users actively refer
        sybil_rejection_rate = 0.05  # 5% flagged as sybil
    
    # Calculate user segments
    users_with_referrals = int(users * active_referrer_rate)
    
    # Total referrals generated (based on viral coefficient)
    # viral_coefficient = referrals_per_active_user
    total_referrals = int(users * viral_coefficient)
    
    # Apply qualification rate
    qualified_referrals = int(total_referrals * qualification_rate)
    
    # Apply sybil rejection
    suspected_sybil = int(total_referrals * sybil_rejection_rate)
    qualified_referrals = max(0, qualified_referrals - suspected_sybil)
    
    # Distribution of referrers across tiers (power law distribution)
    # Most users are Starter, few are Partners
    tier_distribution = {
        ReferralTier.STARTER: 0.75,     # 75% have 1-10 referrals
        ReferralTier.BUILDER: 0.18,     # 18% have 11-50 referrals
        ReferralTier.AMBASSADOR: 0.06,  # 6% have 51-200 referrals
        ReferralTier.PARTNER: 0.01,     # 1% have 200+ referrals
    }
    
    referrers_by_tier = {}
    referrals_by_tier = {}
    total_bonus_vcoin = 0.0
    
    for tier, pct in tier_distribution.items():
        tier_config = REFERRAL_TIERS[tier]
        tier_referrers = int(users_with_referrals * pct)
        referrers_by_tier[tier.value] = tier_referrers
        
        # Average referrals for this tier
        avg_referrals = (tier_config.min_referrals + min(tier_config.max_referrals, 200)) / 2
        tier_referrals_count = int(tier_referrers * avg_referrals * qualification_rate)
        referrals_by_tier[tier.value] = tier_referrals_count
        
        # Calculate bonus for this tier
        tier_bonus = tier_referrers * calculate_referrer_bonus(
            int(avg_referrals),
            qualification_rate
        )
        total_bonus_vcoin += tier_bonus
    
    # Calculate USD value
    token_price = getattr(params, 'token_price', 0.03)
    uncapped_bonus_usd = total_bonus_vcoin * token_price
    
    # Apply monthly budget cap - critical for early months
    # This prevents referral costs from exceeding platform's ability to pay
    if uncapped_bonus_usd > monthly_budget_usd:
        # Scale down bonuses proportionally
        scale_factor = monthly_budget_usd / uncapped_bonus_usd
        total_bonus_usd = monthly_budget_usd
        total_bonus_vcoin = total_bonus_vcoin * scale_factor
    else:
        total_bonus_usd = uncapped_bonus_usd
    
    # Average bonus per referrer
    avg_bonus = total_bonus_vcoin / users_with_referrals if users_with_referrals > 0 else 0
    
    # Effective referral rate
    effective_rate = qualified_referrals / users if users > 0 else 0
    
    return ReferralResult(
        total_users=users,
        users_with_referrals=users_with_referrals,
        total_referrals=total_referrals,
        qualified_referrals=qualified_referrals,
        referrers_by_tier=referrers_by_tier,
        referrals_by_tier=referrals_by_tier,
        bonus_distributed_vcoin=round(total_bonus_vcoin, 2),
        bonus_distributed_usd=round(total_bonus_usd, 2),
        avg_bonus_per_referrer_vcoin=round(avg_bonus, 2),
        viral_coefficient=viral_coefficient,
        effective_referral_rate=round(effective_rate, 4),
        qualification_rate=qualification_rate,
        monthly_referral_cost_vcoin=round(total_bonus_vcoin, 2),
        monthly_referral_cost_usd=round(total_bonus_usd, 2),
        suspected_sybil_referrals=suspected_sybil,
        sybil_rejection_rate=sybil_rejection_rate,
        breakdown={
            'tier_configs': {
                tier.value: {
                    'name': config.name,
                    'bonus_per_referral': config.bonus_per_referral_vcoin,
                    'max_monthly': config.max_monthly_bonus_vcoin,
                }
                for tier, config in REFERRAL_TIERS.items()
            },
            'qualification_criteria': {
                'active_days_required': DEFAULT_QUALIFICATION.active_days_required,
                'min_posts_required': DEFAULT_QUALIFICATION.min_posts_required,
                'email_verification': DEFAULT_QUALIFICATION.email_verification_required,
                'device_fingerprint': DEFAULT_QUALIFICATION.device_fingerprint_check,
            },
            'cost_breakdown': {
                'starter_cost_vcoin': referrers_by_tier.get('starter', 0) * 250,  # avg 5 refs * 50
                'builder_cost_vcoin': referrers_by_tier.get('builder', 0) * 1875,  # avg 25 refs * 75
                'ambassador_cost_vcoin': referrers_by_tier.get('ambassador', 0) * 7500,  # avg 100 refs * 75
                'partner_cost_vcoin': referrers_by_tier.get('partner', 0) * 30000,  # avg 200 refs * 150
            },
        }
    )

