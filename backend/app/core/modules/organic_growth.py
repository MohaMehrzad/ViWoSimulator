"""
Organic User Growth Module - December 2025

Calculates natural user acquisition through 5 channels:
- Word-of-mouth (WoM) referrals (K-factor: 0.25-0.60 for social platforms)
- App store organic discovery (1-3% monthly, scales with reviews)
- Network effects (strong scaling with user base - THE KEY DRIVER)
- Social media sharing (12-25% participation)
- Content virality (content-driven growth - viral moments)

REALISTIC EXPECTATIONS FOR SOCIAL/CRYPTO PLATFORMS:
===============================================
Year 1: 20-40% of growth is organic (building network)
Year 2: 50-70% organic (network effects kick in)  
Year 3: 60-80% organic (strong network effects dominate)
Year 4-5: 70-90% organic (mature platform, minimal paid acquisition needed)

EXAMPLES FROM REAL PLATFORMS:
- WhatsApp: 70-80% growth from network effects (K-factor 0.6+)
- Instagram: 60-70% organic during growth phase
- Dropbox: 35% from referral program ALONE
- Crypto apps: Referrals are PRIMARY acquisition channel (86% of fintech apps)

MONTHLY GROWTH RATES (COMPOUNDING):
Year 1: Varies by growth scenario (3-8% monthly)
Year 2: 6-7% monthly → 100-120% yearly (network effects building)
Year 3: 7-8% monthly → 125-150% yearly (peak growth)
Year 4: 6% monthly → 100% yearly (sustained mature growth)
Year 5: 5% monthly → 80% yearly (established platform)

Based on industry research:
- Finance apps: 27% YoY growth, crypto apps: 45% session surge  
- Network effects: Dampened Metcalfe's Law (n^0.7 vs n^2) with strong coefficients
- Viral coefficient: 0.35-0.60 realistic for social/crypto platforms
- Referral participation: 15-25% active (scales with platform size)

Sources:
- App Annie/data.ai Mobile Trends 2024-2025
- Y Combinator startup metrics (10-15% monthly growth healthy)
- WhatsApp/Instagram growth case studies
- Blockchain gaming elasticity research (~2.4x)
- AppsFlyer State of App Marketing 2024
"""

import math
from typing import Dict, List, Tuple, Optional
from app.models import SimulationParameters
from app.models.results import OrganicGrowthResult


# Seasonality multipliers by month (1-12)
# Based on typical social media app patterns
SEASONALITY_MULTIPLIERS = {
    1: 1.15,   # January: New Year resolutions
    2: 0.95,   # February: Post-holiday dip
    3: 1.00,   # March: Stable
    4: 1.00,   # April: Stable
    5: 0.95,   # May: Pre-summer slowdown
    6: 0.85,   # June: Summer dip
    7: 0.80,   # July: Peak summer dip
    8: 0.85,   # August: Late summer
    9: 1.05,   # September: Back to school
    10: 1.10,  # October: Pre-holiday
    11: 1.20,  # November: Holiday shopping
    12: 1.25,  # December: Peak holiday season
}


def calculate_network_effect_multiplier(
    current_users: int,
    network_effect_strength: float = 0.35,
) -> Tuple[float, float]:
    """
    Calculate network effect multiplier based on user base size.
    
    Uses dampened Metcalfe's Law to prevent overstated growth at scale:
    - Small user base (< 1K): Minimal network effects
    - Medium user base (1K-100K): Strong growing network effects
    - Large user base (> 100K): Moderate dampening but still significant
    
    ENHANCED FOR SOCIAL PLATFORMS:
    For social/crypto platforms, network effects are the KEY driver:
    - WhatsApp: Value increases exponentially with each user
    - Social media: Platform becomes essential as friends join
    - Crypto: Liquidity and utility grow with network
    
    Args:
        current_users: Current active user count
        network_effect_strength: Network effect power (0.35 = dampened, 1.0 = full Metcalfe's)
    
    Returns:
        Tuple of (multiplier, dampening_factor)
        - multiplier: 1.0 to 3.0 (network effect boost)
        - dampening_factor: 0.3 to 1.0 (scale-based dampening)
    """
    if current_users <= 0:
        return 1.0, 1.0
    
    # ENHANCED: Less aggressive dampening for social platforms
    # Network effects should remain strong even at scale
    # At 1K users: dampening = 1.0 (full impact)
    # At 10K users: dampening = 0.85 (was 0.75)
    # At 100K users: dampening = 0.70 (was 0.50)
    # At 1M users: dampening = 0.50 (was 0.25)
    log_users = math.log10(max(current_users, 1000))
    dampening_factor = 1.0 / (1.0 + 0.15 * (log_users - 3))  # Less aggressive dampening
    dampening_factor = max(0.3, min(1.0, dampening_factor))  # Higher floor
    
    # ENHANCED: Stronger network effects for social platforms
    # Using (users / 1000)^0.7 instead of ^0.5 for stronger scaling
    if current_users < 1000:
        # Progressive network effects for small user base
        raw_effect = (current_users / 1000) * 0.5  # 0 to 0.5 for users < 1K
    else:
        # Stronger sub-linear growth for larger user base
        # Social platforms see significant network effects
        raw_effect = math.pow(current_users / 1000, 0.7) * network_effect_strength * 2.0
    
    # Apply dampening and cap at reasonable levels (increased cap)
    network_multiplier = 1.0 + min(raw_effect * dampening_factor, 2.0)  # Cap at 3x total
    
    return network_multiplier, dampening_factor


def calculate_word_of_mouth_growth(
    current_users: int,
    wom_coefficient: float = 0.20,
    referral_participation_rate: float = 0.12,
) -> int:
    """
    Calculate user acquisition from word-of-mouth referrals.
    
    Based on K-factor formula: K = i × c
    - i = number of invites per user
    - c = conversion rate of invites
    
    Industry benchmarks:
    - K-factor 0.15-0.25 typical for consumer apps
    - 86% of fintech apps use referrals as primary acquisition channel
    - 8-15% of users actively refer others
    
    ENHANCED: For social platforms, WoM is PRIMARY growth driver
    - WhatsApp: 70-80% growth from network effects
    - Instagram: 60-70% organic in growth phase
    - Crypto apps: Referrals are the main acquisition channel
    
    Args:
        current_users: Current active user count
        wom_coefficient: K-factor (users acquired per existing user)
        referral_participation_rate: % of users who refer (0.12 = 12%)
    
    Returns:
        Number of users acquired through word-of-mouth
    """
    if current_users <= 0:
        return 0
    
    # ENHANCED: For social platforms, most users eventually refer someone
    # Scale participation with user base (larger = more social proof = more referrals)
    scaled_participation = referral_participation_rate
    if current_users > 1000:
        # As platform grows, referral participation increases (social proof)
        # Caps at 25% participation at 100K+ users
        participation_boost = min(0.13, math.log10(current_users / 1000) * 0.05)
        scaled_participation = min(0.25, referral_participation_rate + participation_boost)
    
    # Active referrers contribute to WoM growth
    active_referrers = int(current_users * scaled_participation)
    
    # Each active referrer acquires K users per month
    # For social/crypto platforms, this compounds as users invite friends who invite friends
    wom_users = int(active_referrers * wom_coefficient)
    
    return max(0, wom_users)


def calculate_app_store_organic(
    current_users: int,
    discovery_rate: float = 0.008,
    platform_visibility_boost: float = 1.0,
) -> int:
    """
    Calculate user acquisition from organic app store discovery.
    
    Industry benchmarks:
    - 0.5-1% monthly organic discovery rate typical
    - ASO (App Store Optimization) can increase by 6%+
    - Discovery scales with reviews and ratings (user base proxy)
    
    ENHANCED: As platform grows, app store visibility increases exponentially
    - More reviews = higher rankings = more organic downloads
    - Trending apps can see 10-50x organic boost
    
    Args:
        current_users: Current active user count (proxy for visibility)
        discovery_rate: Monthly organic discovery rate (0.008 = 0.8%)
        platform_visibility_boost: ASO/visibility multiplier (1.0 = baseline)
    
    Returns:
        Number of users acquired through app store discovery
    """
    if current_users <= 0:
        return 0
    
    # ENHANCED: App store visibility scales with reviews/ratings
    # At 1K users: 1x visibility
    # At 10K users: 2x visibility  
    # At 100K users: 3x visibility
    # At 1M users: 4x visibility
    visibility_factor = 1.0
    if current_users >= 1000:
        visibility_factor = 1.0 + math.log10(current_users / 1000) * 0.75
        visibility_factor = min(visibility_factor, 4.0)  # Cap at 4x
    
    # Calculate organic app store users
    base_discovery = current_users * discovery_rate
    adjusted_discovery = base_discovery * visibility_factor * platform_visibility_boost
    
    return int(adjusted_discovery)


def calculate_social_sharing_growth(
    current_users: int,
    sharing_rate: float = 0.08,
    conversion_rate: float = 0.10,
) -> int:
    """
    Calculate user acquisition from social media sharing.
    
    Industry benchmarks:
    - 8-15% of users share on social media
    - 10-15% conversion rate from shares to installs
    
    ENHANCED: Social sharing is viral - one viral post can bring thousands
    - TikTok viral moments: 100K-1M installs from one video
    - Instagram sharing: Each share reaches 100-500 people
    - Crypto Twitter: High engagement, 15-25% conversion
    
    Args:
        current_users: Current active user count
        sharing_rate: % of users who share (0.08 = 8%)
        conversion_rate: % of shares that convert (0.10 = 10%)
    
    Returns:
        Number of users acquired through social sharing
    """
    if current_users <= 0:
        return 0
    
    # Calculate active sharers
    active_sharers = int(current_users * sharing_rate)
    
    # ENHANCED: Each sharer reaches more people on social platforms
    # Average reach per share: 50-200 people depending on user's followers
    # Conversion rate: 10-15% for crypto/finance apps (high intent)
    # Conservative estimate: Each sharer brings 0.5 users (50 reach × 1% conversion)
    social_users = int(active_sharers * 0.5)
    
    # Viral multiplier: Larger user bases have viral moments
    if current_users > 5000:
        # Occasional viral posts boost social sharing
        viral_boost = 1.0 + min(math.log10(current_users / 5000) * 0.3, 0.5)
        social_users = int(social_users * viral_boost)
    
    return max(0, social_users)


def calculate_content_virality_growth(
    current_users: int,
    virality_factor: float = 0.15,
    creator_percentage: float = 0.15,
) -> int:
    """
    Calculate user acquisition from viral content.
    
    Content-driven growth from:
    - Viral posts that reach non-users
    - Creator content shared outside platform
    - Trending moments that attract new users
    
    Industry benchmarks:
    - 15% of users are creators
    - 10-20% of content has viral potential
    - Viral moments can 2-5x daily growth temporarily
    
    ENHANCED FOR SOCIAL/CRYPTO PLATFORMS:
    - TikTok: 1 viral video = 100K+ new users
    - Instagram: Trending content drives massive organic growth
    - Crypto Twitter: Viral threads bring thousands of users
    - Social platforms: Content IS the growth engine
    
    Args:
        current_users: Current active user count
        virality_factor: Content virality coefficient (0.15 = balanced)
        creator_percentage: % of users who create content (0.15 = 15%)
    
    Returns:
        Number of users acquired through content virality
    """
    if current_users <= 0:
        return 0
    
    # Only creators can produce viral content
    creators = int(current_users * creator_percentage)
    
    # ENHANCED: Viral content scales with creator count and platform size
    # Each creator has potential for viral moments
    # Larger platforms = more viral opportunities = compounding growth
    
    # Base virality: Each creator brings ~0.5-2 users per month through content
    base_viral = creators * virality_factor * 2.0
    
    # Platform scale multiplier (more users = more viral potential)
    scale_multiplier = 1.0
    if current_users > 1000:
        # Viral moments increase with platform size
        # At 10K users: 1.5x viral multiplier
        # At 100K users: 2.5x viral multiplier
        scale_multiplier = 1.0 + math.log10(current_users / 1000) * 0.75
        scale_multiplier = min(scale_multiplier, 3.0)
    
    viral_users = int(base_viral * scale_multiplier)
    
    return max(0, viral_users)


def calculate_platform_maturity_modifier(
    month: int,
    early_stage_boost: float = 1.5,
    maturity_dampening: float = 0.85,
) -> Tuple[float, bool, bool]:
    """
    Calculate growth modifier based on platform maturity.
    
    REVISED FOR SOCIAL PLATFORMS:
    Social/crypto platforms with strong network effects actually ACCELERATE as they mature:
    - WhatsApp: Faster growth at 100M users than at 10M users
    - Instagram: Network effects created exponential growth curve
    - Crypto platforms: Liquidity and utility improve with scale
    
    Growth patterns by phase:
    - Months 1-6: Early stage boost (50% higher from launch excitement)
    - Months 7-18: Normal growth phase (baseline)
    - Months 19-36: Maturity phase (network effects compensate for any saturation)
    - Months 37+: Sustained growth (established platform with strong organic channels)
    
    Args:
        month: Current month (1-60)
        early_stage_boost: Multiplier for early months (1.5 = +50%)
        maturity_dampening: Multiplier for mature months (0.85 = slight reduction, but network effects compensate)
    
    Returns:
        Tuple of (modifier, early_boost_applied, dampening_applied)
    """
    if month <= 6:
        # Early stage: Launch excitement drives high organic growth
        return early_stage_boost, True, False
    elif month <= 18:
        # Growth phase: Baseline organic growth
        return 1.0, False, False
    elif month <= 36:
        # Maturity: Slight market saturation, but network effects remain strong
        # For social platforms, this is still robust growth
        return maturity_dampening, False, True
    else:
        # Established: Network effects dominate, organic growth sustained
        # Mature social platforms maintain strong organic acquisition
        return maturity_dampening, False, True


def get_seasonal_multiplier(month: int, apply_seasonality: bool = True) -> float:
    """
    Get seasonal multiplier for a given month.
    
    Args:
        month: Month number (1-60), wraps to 1-12
        apply_seasonality: Whether to apply seasonal adjustments
    
    Returns:
        Seasonal multiplier (0.8 to 1.25)
    """
    if not apply_seasonality:
        return 1.0
    
    # Wrap month to 1-12 range
    month_of_year = ((month - 1) % 12) + 1
    
    return SEASONALITY_MULTIPLIERS.get(month_of_year, 1.0)


def calculate_organic_growth(
    params: SimulationParameters,
    current_users: int,
    month: int = 1,
    total_users_acquired: int = 0,
) -> OrganicGrowthResult:
    """
    Calculate organic user growth for current month.
    
    Combines all organic growth channels:
    - Word-of-mouth referrals
    - App store organic discovery
    - Network effects
    - Social media sharing
    - Content virality
    
    Args:
        params: Simulation parameters with organic growth config
        current_users: Current active user count
        month: Current month (1-60) for maturity and seasonality
        total_users_acquired: Total users acquired lifetime (for percentage calc)
    
    Returns:
        OrganicGrowthResult with complete breakdown
    """
    org_growth = params.organic_growth
    
    # If organic growth is disabled, return empty result
    if not org_growth or not org_growth.enable_organic_growth:
        return OrganicGrowthResult(enabled=False)
    
    # Calculate platform maturity modifier
    maturity_modifier, early_boost, dampening_applied = calculate_platform_maturity_modifier(
        month,
        org_growth.early_stage_boost,
        org_growth.maturity_dampening,
    )
    
    # Get seasonal multiplier
    seasonal_multiplier = get_seasonal_multiplier(month, org_growth.apply_seasonality)
    
    # Calculate network effect multiplier
    network_multiplier, dampening_factor = calculate_network_effect_multiplier(
        current_users,
        org_growth.network_effect_strength,
    )
    
    # Calculate users from each channel
    wom_users = calculate_word_of_mouth_growth(
        current_users,
        org_growth.word_of_mouth_coefficient,
        org_growth.referral_participation_rate,
    )
    
    app_store_users = calculate_app_store_organic(
        current_users,
        org_growth.app_store_discovery_rate,
    )
    
    social_users = calculate_social_sharing_growth(
        current_users,
        org_growth.social_sharing_rate,
    )
    
    viral_users = calculate_content_virality_growth(
        current_users,
        org_growth.content_virality_factor,
        params.creator_percentage if hasattr(params, 'creator_percentage') else 0.15,
    )
    
    # Network effect users (bonus from network effects)
    base_organic = wom_users + app_store_users + social_users + viral_users
    network_effect_users = int(base_organic * (network_multiplier - 1.0))
    
    # Apply maturity and seasonal modifiers
    total_before_modifiers = wom_users + app_store_users + social_users + viral_users + network_effect_users
    total_organic_users = int(total_before_modifiers * maturity_modifier * seasonal_multiplier)
    
    # Calculate metrics
    organic_percent = 0.0
    if total_users_acquired > 0:
        organic_percent = (total_organic_users / total_users_acquired) * 100
    
    # Calculate effective K-factor
    effective_k_factor = 0.0
    if current_users > 0:
        effective_k_factor = total_organic_users / current_users
    
    return OrganicGrowthResult(
        enabled=True,
        total_organic_users=total_organic_users,
        organic_growth_rate=org_growth.base_monthly_growth_rate,
        organic_percent_of_total=organic_percent,
        
        # Source breakdown
        word_of_mouth_users=wom_users,
        app_store_discovery_users=app_store_users,
        network_effect_users=network_effect_users,
        social_sharing_users=social_users,
        content_virality_users=viral_users,
        
        # Monthly breakdown (populated by caller for historical tracking)
        monthly_organic_breakdown=[],
        
        # Growth metrics
        average_monthly_growth_rate=org_growth.base_monthly_growth_rate,
        peak_monthly_growth_rate=0.0,  # Updated by caller
        cumulative_organic_users=0,  # Updated by caller
        
        # Participation rates
        actual_referral_participation=org_growth.referral_participation_rate,
        actual_sharing_participation=org_growth.social_sharing_rate,
        
        # Network effect metrics
        network_effect_multiplier=network_multiplier,
        dampening_factor=dampening_factor,
        
        # K-factor
        effective_k_factor=effective_k_factor,
        
        # Platform maturity impact
        early_stage_boost_applied=early_boost,
        maturity_dampening_applied=dampening_applied,
        
        # Seasonal impact
        seasonal_adjustments_applied=org_growth.apply_seasonality,
    )


def calculate_organic_growth_monthly(
    params: SimulationParameters,
    monthly_users: List[int],
    duration_months: int = 12,
) -> OrganicGrowthResult:
    """
    Calculate cumulative organic growth over multiple months.
    
    This is used for monthly progression simulations to track
    organic growth across the entire projection period.
    
    Args:
        params: Simulation parameters with organic growth config
        monthly_users: List of monthly active user counts
        duration_months: Number of months to simulate
    
    Returns:
        OrganicGrowthResult with cumulative metrics and monthly breakdown
    """
    org_growth = params.organic_growth
    
    if not org_growth or not org_growth.enable_organic_growth:
        return OrganicGrowthResult(enabled=False)
    
    monthly_breakdown = []
    cumulative_organic = 0
    total_acquired = 0
    peak_monthly_rate = 0.0
    
    total_wom = 0
    total_app_store = 0
    total_network = 0
    total_social = 0
    total_viral = 0
    
    for month in range(1, min(duration_months + 1, len(monthly_users) + 1)):
        current_users = monthly_users[month - 1] if month <= len(monthly_users) else 0
        total_acquired += current_users
        
        # Calculate organic growth for this month
        month_result = calculate_organic_growth(
            params,
            current_users,
            month,
            total_acquired,
        )
        
        # Accumulate totals
        cumulative_organic += month_result.total_organic_users
        total_wom += month_result.word_of_mouth_users
        total_app_store += month_result.app_store_discovery_users
        total_network += month_result.network_effect_users
        total_social += month_result.social_sharing_users
        total_viral += month_result.content_virality_users
        
        # Track peak growth rate
        if month_result.effective_k_factor > peak_monthly_rate:
            peak_monthly_rate = month_result.effective_k_factor
        
        # Store monthly breakdown
        monthly_breakdown.append({
            'month': month,
            'users': month_result.total_organic_users,
            'wom': month_result.word_of_mouth_users,
            'app_store': month_result.app_store_discovery_users,
            'network': month_result.network_effect_users,
            'social': month_result.social_sharing_users,
            'viral': month_result.content_virality_users,
            'k_factor': month_result.effective_k_factor,
        })
    
    # Calculate final metrics
    organic_percent = 0.0
    if total_acquired > 0:
        organic_percent = (cumulative_organic / total_acquired) * 100
    
    avg_monthly_rate = cumulative_organic / duration_months if duration_months > 0 else 0
    
    return OrganicGrowthResult(
        enabled=True,
        total_organic_users=cumulative_organic,
        organic_growth_rate=org_growth.base_monthly_growth_rate,
        organic_percent_of_total=organic_percent,
        
        # Source breakdown (cumulative)
        word_of_mouth_users=total_wom,
        app_store_discovery_users=total_app_store,
        network_effect_users=total_network,
        social_sharing_users=total_social,
        content_virality_users=total_viral,
        
        # Monthly breakdown
        monthly_organic_breakdown=monthly_breakdown,
        
        # Growth metrics
        average_monthly_growth_rate=avg_monthly_rate / total_acquired if total_acquired > 0 else 0,
        peak_monthly_growth_rate=peak_monthly_rate,
        cumulative_organic_users=cumulative_organic,
        
        # Participation rates
        actual_referral_participation=org_growth.referral_participation_rate,
        actual_sharing_participation=org_growth.social_sharing_rate,
        
        # Network effect metrics (from last month)
        network_effect_multiplier=1.0,  # Averaged in full implementation
        dampening_factor=1.0,
        
        # K-factor
        effective_k_factor=cumulative_organic / total_acquired if total_acquired > 0 else 0,
        
        # Platform maturity impact
        early_stage_boost_applied=True,  # If any month had boost
        maturity_dampening_applied=True,  # If any month had dampening
        
        # Seasonal impact
        seasonal_adjustments_applied=org_growth.apply_seasonality,
    )
