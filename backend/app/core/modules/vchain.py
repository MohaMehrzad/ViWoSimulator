"""
VChain Module - Cross-Chain Network Revenue Calculations.

=== VCHAIN CROSS-CHAIN NETWORK (2027-2028) ===

A proprietary cross-chain network enabling seamless interaction
between all major blockchain networks through a unified interface.

Revenue Streams:
1. Cross-chain Transaction Fees (0.2%)
2. Bridge Fees (0.1%)
3. Gas Abstraction Markup (8%)
4. Enterprise API Subscriptions
5. Validator Revenue (from staking)

Launch Timeline: Month 24 (Year 2 after TGE)
"""

from typing import Dict
from app.models import SimulationParameters, VChainParameters


def calculate_vchain(
    params: SimulationParameters,
    current_month: int,
    users: int,
    token_price: float
) -> Dict:
    """
    Calculate VChain cross-chain network revenue.
    
    Args:
        params: Simulation parameters
        current_month: Current month in simulation
        users: Total active users
        token_price: Current token price
    
    Returns:
        Dict with VChain revenue metrics
    """
    # Check if VChain is enabled and launched
    vchain_params = params.vchain
    if not vchain_params or not vchain_params.enable_vchain:
        return {
            'enabled': False,
            'revenue': 0,
            'costs': 0,
            'profit': 0,
            'launch_month': vchain_params.vchain_launch_month if vchain_params else 24,
            'months_until_launch': (vchain_params.vchain_launch_month if vchain_params else 24) - current_month,
        }
    
    # Check if launched yet
    if current_month < vchain_params.vchain_launch_month:
        months_until = vchain_params.vchain_launch_month - current_month
        return {
            'enabled': True,
            'launched': False,
            'revenue': 0,
            'costs': 0,
            'profit': 0,
            'launch_month': vchain_params.vchain_launch_month,
            'months_until_launch': months_until,
        }
    
    # Calculate months since launch for growth curve
    months_active = current_month - vchain_params.vchain_launch_month + 1
    
    # Growth curve - volume ramps up over first 12 months
    growth_factor = min(1.0, months_active / 12)  # Full volume at 12 months
    
    # === REVENUE CALCULATIONS ===
    
    # 1. Cross-chain Transaction Fees
    monthly_tx_volume = vchain_params.vchain_monthly_tx_volume_usd * growth_factor
    tx_fee_revenue = monthly_tx_volume * vchain_params.vchain_tx_fee_percent
    
    # Apply min/max fee caps (estimate number of transactions)
    avg_tx_size = 500  # $500 average transaction
    estimated_txs = monthly_tx_volume / avg_tx_size
    
    # 2. Bridge Fees
    monthly_bridge_volume = vchain_params.vchain_monthly_bridge_volume_usd * growth_factor
    bridge_fee_revenue = monthly_bridge_volume * vchain_params.vchain_bridge_fee_percent
    
    # 3. Gas Abstraction Markup
    # Users pay gas in VCoin, platform covers actual gas and marks up
    estimated_gas_usage = estimated_txs * 0.10  # $0.10 avg gas per tx
    gas_markup_revenue = estimated_gas_usage * vchain_params.vchain_gas_markup_percent
    
    # 4. Enterprise API Revenue
    # Scale enterprise clients with months active
    active_enterprise_clients = int(vchain_params.vchain_enterprise_clients * growth_factor)
    enterprise_api_revenue = active_enterprise_clients * vchain_params.vchain_avg_enterprise_revenue
    
    # 5. Validator Revenue
    # Validators earn portion of tx fees + staking rewards
    validator_share = 0.30  # 30% of tx fees to validators
    validator_fee_pool = tx_fee_revenue * validator_share
    
    # Total validator staked (estimate based on users)
    validators_active = min(vchain_params.vchain_validator_count, int(users * 0.001))
    validators_active = max(10, validators_active)  # Minimum 10 validators
    
    # Calculate validator APY from fees
    total_validator_stake = validators_active * vchain_params.vchain_min_validator_stake
    total_validator_stake_usd = total_validator_stake * token_price
    
    # Add staking APY to validator earnings
    validator_staking_rewards_monthly = (
        total_validator_stake * vchain_params.vchain_validator_apy / 12
    )
    
    # === COST CALCULATIONS ===
    
    # Infrastructure costs
    infrastructure_monthly = 5000 * growth_factor  # $5K/month at full scale
    
    # Security (audits, bug bounty)
    security_monthly = 3000 * growth_factor
    
    # Bridge liquidity costs (opportunity cost)
    bridge_liquidity_cost = monthly_bridge_volume * 0.001  # 0.1% opportunity cost
    
    # Validator rewards (cost to protocol)
    validator_rewards_cost = validator_staking_rewards_monthly * token_price
    
    total_costs = (
        infrastructure_monthly +
        security_monthly +
        bridge_liquidity_cost +
        validator_rewards_cost
    )
    
    # === TOTALS ===
    
    total_revenue = (
        tx_fee_revenue +
        bridge_fee_revenue +
        gas_markup_revenue +
        enterprise_api_revenue
    )
    
    profit = total_revenue - total_costs
    margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        'enabled': True,
        'launched': True,
        'months_active': months_active,
        'growth_factor': round(growth_factor, 2),
        
        # Revenue
        'revenue': round(total_revenue, 2),
        'tx_fee_revenue': round(tx_fee_revenue, 2),
        'bridge_fee_revenue': round(bridge_fee_revenue, 2),
        'gas_markup_revenue': round(gas_markup_revenue, 2),
        'enterprise_api_revenue': round(enterprise_api_revenue, 2),
        
        # Volume metrics
        'monthly_tx_volume': round(monthly_tx_volume, 2),
        'monthly_bridge_volume': round(monthly_bridge_volume, 2),
        'estimated_transactions': int(estimated_txs),
        
        # Enterprise
        'active_enterprise_clients': active_enterprise_clients,
        
        # Validators
        'validators_active': validators_active,
        'total_validator_stake': round(total_validator_stake, 2),
        'total_validator_stake_usd': round(total_validator_stake_usd, 2),
        'validator_fee_pool_usd': round(validator_fee_pool, 2),
        'validator_monthly_earnings_vcoin': round(validator_staking_rewards_monthly, 2),
        
        # Costs
        'costs': round(total_costs, 2),
        'infrastructure_cost': round(infrastructure_monthly, 2),
        'security_cost': round(security_monthly, 2),
        'bridge_liquidity_cost': round(bridge_liquidity_cost, 2),
        'validator_rewards_cost': round(validator_rewards_cost, 2),
        
        # Profit
        'profit': round(profit, 2),
        'margin': round(margin, 1),
        
        # Configuration
        'launch_month': vchain_params.vchain_launch_month,
        'tx_fee_percent': vchain_params.vchain_tx_fee_percent * 100,
        'bridge_fee_percent': vchain_params.vchain_bridge_fee_percent * 100,
        'gas_markup_percent': vchain_params.vchain_gas_markup_percent * 100,
        'validator_apy': vchain_params.vchain_validator_apy * 100,
    }

