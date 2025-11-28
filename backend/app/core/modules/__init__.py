# Module calculations

from .identity import calculate_identity
from .content import calculate_content
from .advertising import calculate_advertising
from .exchange import calculate_exchange
from .rewards import calculate_rewards
from .recapture import calculate_recapture
from .liquidity import calculate_liquidity
from .staking import calculate_staking
from .governance import calculate_governance
from .vchain import calculate_vchain
from .marketplace import calculate_marketplace
from .business_hub import calculate_business_hub
from .cross_platform import calculate_cross_platform

# Pre-Launch Modules (Nov 2025)
from .referral import calculate_referral, ReferralResult
from .points import calculate_points, PointsResult
from .gasless import calculate_gasless, GaslessResult

__all__ = [
    'calculate_identity',
    'calculate_content',
    'calculate_advertising',
    'calculate_exchange',
    'calculate_rewards',
    'calculate_recapture',
    'calculate_liquidity',
    'calculate_staking',
    'calculate_governance',
    'calculate_vchain',
    'calculate_marketplace',
    'calculate_business_hub',
    'calculate_cross_platform',
    # Pre-Launch Modules
    'calculate_referral',
    'calculate_points',
    'calculate_gasless',
    'ReferralResult',
    'PointsResult',
    'GaslessResult',
]
