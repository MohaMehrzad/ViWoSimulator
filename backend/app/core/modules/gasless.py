"""
Gasless Module - Sponsored transaction cost modeling for user onboarding.

=== GASLESS ONBOARDING (2025 Standards) ===

Problem Solved:
New users shouldn't need SOL to start using the platform.
This is critical for 2025 Web3 UX - users expect Web2-like experience.

Sponsored Transaction Tiers:
| Tier              | Free Transactions | Per Month |
|-------------------|-------------------|-----------|
| New User          | First 10          | Once      |
| Verified User     | 50                | Monthly   |
| Premium User      | Unlimited         | Monthly   |

Technical Approach (Solana):
- Versioned transactions with fee payer abstraction
- Platform wallet pays fees, user signs
- Convert VCoin to SOL for fees using Jupiter swap
- Priority fee subsidy for first-time users

Cost Model:
- Base transaction cost: ~$0.00025 per tx
- Priority fee (optional): ~$0.0001 additional
- 100K users × 10 sponsored tx = $250/month base cost
- Paid by platform marketing budget

User Experience Flow:
1. User creates account (no wallet needed initially)
2. Platform creates embedded wallet for user
3. First 10 actions are gasless (sponsored)
4. After 10 actions, prompt to add SOL or earn VCoin
5. VCoin rewards auto-convert to cover future fees
"""

from dataclasses import dataclass
from typing import Dict, Optional, NamedTuple
from enum import Enum


class UserTier(str, Enum):
    """User tiers for gasless transaction allocation"""
    NEW_USER = "new_user"
    VERIFIED = "verified"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class GaslessTierConfig:
    """Configuration for gasless transactions per user tier"""
    name: str
    free_transactions_per_month: int  # -1 = unlimited
    priority_fee_included: bool
    description: str


# Default gasless tier configurations
GASLESS_TIERS: Dict[UserTier, GaslessTierConfig] = {
    UserTier.NEW_USER: GaslessTierConfig(
        name="New User",
        free_transactions_per_month=10,  # First 10 only (one-time)
        priority_fee_included=False,
        description="First 10 transactions sponsored for new users",
    ),
    UserTier.VERIFIED: GaslessTierConfig(
        name="Verified User",
        free_transactions_per_month=50,
        priority_fee_included=False,
        description="50 free transactions per month for verified users",
    ),
    UserTier.PREMIUM: GaslessTierConfig(
        name="Premium User",
        free_transactions_per_month=-1,  # Unlimited
        priority_fee_included=True,
        description="Unlimited sponsored transactions with priority fees",
    ),
    UserTier.ENTERPRISE: GaslessTierConfig(
        name="Enterprise",
        free_transactions_per_month=-1,  # Unlimited
        priority_fee_included=True,
        description="Unlimited sponsored transactions for business accounts",
    ),
}


# Cost constants (November 2025 Solana mainnet)
SOLANA_BASE_FEE_USD = 0.00025  # ~5000 lamports at SOL=$200
SOLANA_PRIORITY_FEE_USD = 0.0001  # Optional priority fee
SOLANA_ACCOUNT_RENT_USD = 0.10  # Rent-exempt minimum for new accounts


class SponsorshipCostBreakdown(NamedTuple):
    """Breakdown of sponsorship costs"""
    base_fee_cost: float
    priority_fee_cost: float
    account_creation_cost: float
    total_cost: float


@dataclass
class GaslessResult:
    """Result of gasless module calculations"""
    # User tier distribution
    total_users: int
    new_users: int
    verified_users: int
    premium_users: int
    enterprise_users: int
    
    # Transaction estimates
    total_sponsored_transactions: int
    avg_transactions_per_user: float
    
    # Cost breakdown
    base_fee_cost_usd: float
    priority_fee_cost_usd: float
    account_creation_cost_usd: float
    total_sponsorship_cost_usd: float
    
    # Per-tier costs
    new_user_cost_usd: float
    verified_user_cost_usd: float
    premium_user_cost_usd: float
    enterprise_user_cost_usd: float
    
    # Cost per user metrics
    avg_cost_per_user_usd: float
    cost_per_transaction_usd: float
    
    # Budget metrics
    monthly_sponsorship_budget_usd: float
    budget_utilization: float
    
    # VCoin equivalent (for internal accounting)
    sponsorship_cost_vcoin: float
    
    # Breakdown
    breakdown: Dict


def calculate_gasless(
    users: int,
    token_price: float = 0.03,
    new_user_rate: float = 0.30,  # 30% are new users this month
    verified_rate: float = 0.40,  # 40% are verified
    premium_rate: float = 0.05,   # 5% are premium
    enterprise_rate: float = 0.01,  # 1% are enterprise
    avg_transactions_per_active_user: float = 25.0,
    monthly_budget_usd: float = 5000.0,
) -> GaslessResult:
    """
    Calculate gasless onboarding costs.
    
    Models the cost of sponsoring transactions for different user tiers
    to provide a seamless onboarding experience.
    
    Args:
        users: Total user count
        token_price: VCoin price in USD
        new_user_rate: % of users who are new this month
        verified_rate: % of users who are verified
        premium_rate: % of users who are premium
        enterprise_rate: % of users who are enterprise
        avg_transactions_per_active_user: Average monthly transactions
        monthly_budget_usd: Budget for sponsorship
    
    Returns:
        GaslessResult with all metrics
    """
    # Calculate user segments
    # Note: Categories overlap (premium users are also verified)
    new_users = int(users * new_user_rate)
    
    # Non-new users split into verified, premium, enterprise
    existing_users = users - new_users
    verified_users = int(existing_users * verified_rate)
    premium_users = int(existing_users * premium_rate)
    enterprise_users = int(existing_users * enterprise_rate)
    
    # Users paying their own fees (remainder)
    self_pay_users = existing_users - verified_users - premium_users - enterprise_users
    
    # Calculate sponsored transactions per tier
    tier_transactions = {}
    tier_costs = {}
    
    # New users: First 10 transactions only
    new_user_tier = GASLESS_TIERS[UserTier.NEW_USER]
    new_user_tx = new_users * min(new_user_tier.free_transactions_per_month, 10)
    new_user_cost = new_user_tx * SOLANA_BASE_FEE_USD
    # Add account creation cost for new users
    new_user_cost += new_users * SOLANA_ACCOUNT_RENT_USD
    tier_transactions[UserTier.NEW_USER.value] = new_user_tx
    tier_costs[UserTier.NEW_USER.value] = new_user_cost
    
    # Verified users: 50 transactions per month
    verified_tier = GASLESS_TIERS[UserTier.VERIFIED]
    verified_tx = verified_users * min(verified_tier.free_transactions_per_month, avg_transactions_per_active_user)
    verified_cost = verified_tx * SOLANA_BASE_FEE_USD
    tier_transactions[UserTier.VERIFIED.value] = int(verified_tx)
    tier_costs[UserTier.VERIFIED.value] = verified_cost
    
    # Premium users: Unlimited (use average)
    premium_tier = GASLESS_TIERS[UserTier.PREMIUM]
    premium_tx = premium_users * avg_transactions_per_active_user * 1.5  # Premium users more active
    premium_cost = premium_tx * (SOLANA_BASE_FEE_USD + SOLANA_PRIORITY_FEE_USD)  # Includes priority
    tier_transactions[UserTier.PREMIUM.value] = int(premium_tx)
    tier_costs[UserTier.PREMIUM.value] = premium_cost
    
    # Enterprise users: Unlimited with priority
    enterprise_tier = GASLESS_TIERS[UserTier.ENTERPRISE]
    enterprise_tx = enterprise_users * avg_transactions_per_active_user * 3.0  # Very active
    enterprise_cost = enterprise_tx * (SOLANA_BASE_FEE_USD + SOLANA_PRIORITY_FEE_USD)
    tier_transactions[UserTier.ENTERPRISE.value] = int(enterprise_tx)
    tier_costs[UserTier.ENTERPRISE.value] = enterprise_cost
    
    # Total calculations
    total_sponsored_tx = sum(tier_transactions.values())
    
    # Cost breakdown
    base_fee_cost = total_sponsored_tx * SOLANA_BASE_FEE_USD
    priority_fee_cost = (tier_transactions[UserTier.PREMIUM.value] + tier_transactions[UserTier.ENTERPRISE.value]) * SOLANA_PRIORITY_FEE_USD
    account_creation_cost = new_users * SOLANA_ACCOUNT_RENT_USD
    total_cost = base_fee_cost + priority_fee_cost + account_creation_cost
    
    # Per-user metrics
    avg_cost_per_user = total_cost / users if users > 0 else 0
    cost_per_tx = total_cost / total_sponsored_tx if total_sponsored_tx > 0 else 0
    avg_tx_per_user = total_sponsored_tx / users if users > 0 else 0
    
    # Budget utilization
    budget_utilization = total_cost / monthly_budget_usd if monthly_budget_usd > 0 else 0
    
    # VCoin equivalent
    sponsorship_vcoin = total_cost / token_price if token_price > 0 else 0
    
    return GaslessResult(
        total_users=users,
        new_users=new_users,
        verified_users=verified_users,
        premium_users=premium_users,
        enterprise_users=enterprise_users,
        total_sponsored_transactions=total_sponsored_tx,
        avg_transactions_per_user=round(avg_tx_per_user, 2),
        base_fee_cost_usd=round(base_fee_cost, 2),
        priority_fee_cost_usd=round(priority_fee_cost, 2),
        account_creation_cost_usd=round(account_creation_cost, 2),
        total_sponsorship_cost_usd=round(total_cost, 2),
        new_user_cost_usd=round(tier_costs[UserTier.NEW_USER.value], 2),
        verified_user_cost_usd=round(tier_costs[UserTier.VERIFIED.value], 2),
        premium_user_cost_usd=round(tier_costs[UserTier.PREMIUM.value], 2),
        enterprise_user_cost_usd=round(tier_costs[UserTier.ENTERPRISE.value], 2),
        avg_cost_per_user_usd=round(avg_cost_per_user, 4),
        cost_per_transaction_usd=round(cost_per_tx, 6),
        monthly_sponsorship_budget_usd=monthly_budget_usd,
        budget_utilization=round(budget_utilization, 4),
        sponsorship_cost_vcoin=round(sponsorship_vcoin, 2),
        breakdown={
            'tiers': {
                tier.value: {
                    'name': config.name,
                    'free_tx_per_month': config.free_transactions_per_month,
                    'priority_included': config.priority_fee_included,
                    'users': tier_transactions.get(tier.value, 0) // max(1, 
                        new_users if tier == UserTier.NEW_USER else
                        verified_users if tier == UserTier.VERIFIED else
                        premium_users if tier == UserTier.PREMIUM else
                        enterprise_users
                    ) if tier.value in tier_transactions else 0,
                    'cost_usd': round(tier_costs.get(tier.value, 0), 2),
                }
                for tier, config in GASLESS_TIERS.items()
            },
            'cost_constants': {
                'base_fee_usd': SOLANA_BASE_FEE_USD,
                'priority_fee_usd': SOLANA_PRIORITY_FEE_USD,
                'account_rent_usd': SOLANA_ACCOUNT_RENT_USD,
            },
            'user_experience': {
                'step_1': 'User creates account (no wallet needed)',
                'step_2': 'Platform creates embedded wallet',
                'step_3': 'First 10 actions are gasless',
                'step_4': 'After 10 actions, earn VCoin or add SOL',
                'step_5': 'VCoin rewards auto-convert for fees',
            },
            'self_pay_users': max(0, self_pay_users),
            'sponsorship_coverage': round((users - max(0, self_pay_users)) / users * 100, 1) if users > 0 else 0,
        }
    )

