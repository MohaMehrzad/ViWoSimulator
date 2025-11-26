"""
Messaging Module calculations.

Updated for Issue #9: Linear cost scaling
Activity rates updated with documented sources.
"""

from app.config import config
from app.models import SimulationParameters, ModuleResult


def calculate_messaging(params: SimulationParameters, users: int) -> ModuleResult:
    """
    Calculate Messaging module revenue, costs, and profit.
    
    Issue #9: Now uses linear cost scaling.
    Activity rates reduced to realistic levels based on 2024 data.
    """
    if not params.enable_messaging:
        return ModuleResult(
            revenue=0,
            costs=0,
            profit=0,
            margin=0,
            breakdown={
                'total_messages': 0,
                'regular_messages': 0,
                'encrypted_messages': 0,
                'group_chats_created': 0,
                'files_transferred': 0,
                'call_users': 0,
                'total_call_minutes': 0,
                'storage_subscribers': 0,
                'premium_users': 0,
                'dm_revenue': 0,
                'group_chat_revenue': 0,
                'file_transfer_revenue': 0,
                'call_revenue': 0,
                'storage_revenue': 0,
                'premium_revenue': 0,
            }
        )
    
    # Message volume (reduced from 100 to 50 per user)
    messages_per_user = config.ACTIVITY_RATES.get('MESSAGES_PER_USER', 50)
    total_messages = users * messages_per_user
    
    # Message type distribution
    regular_rate = config.ACTIVITY_RATES.get('REGULAR_MESSAGES', 0.85)
    encrypted_rate = config.ACTIVITY_RATES.get('ENCRYPTED_MESSAGES', 0.15)
    regular_messages = round(total_messages * regular_rate)
    encrypted_messages = round(total_messages * encrypted_rate)
    
    # Encrypted DM revenue
    dm_revenue = encrypted_messages * params.encrypted_dm_fee
    
    # Group chat creation (20% of users, reduced from 30%)
    group_chat_rate = config.ACTIVITY_RATES.get('GROUP_CHAT_USERS', 0.20)
    group_chats_created = round(users * group_chat_rate)
    group_chat_revenue = group_chats_created * params.group_chat_fee
    
    # File transfers (3 per user, reduced from 5)
    files_per_user = config.ACTIVITY_RATES.get('FILES_PER_USER', 3)
    files_transferred = users * files_per_user
    file_transfer_revenue = files_transferred * params.file_transfer_fee
    
    # Voice/video calls (5% of users, reduced from 10%)
    call_rate = config.ACTIVITY_RATES.get('CALL_USERS', 0.05)
    call_users = round(users * call_rate)
    
    # Average call duration (15 min, reduced from 30)
    avg_call_minutes = config.ACTIVITY_RATES.get('AVG_CALL_MINUTES', 15)
    total_call_minutes = call_users * avg_call_minutes
    call_revenue = total_call_minutes * params.voice_call_fee
    
    # Storage subscriptions (10% of users, reduced from 20%)
    storage_rate = config.ACTIVITY_RATES.get('STORAGE_SUBSCRIBERS', 0.10)
    storage_subscribers = round(users * storage_rate)
    storage_revenue = storage_subscribers * params.message_storage_fee
    
    # Premium messaging features (8% of users, reduced from 15%)
    premium_rate = config.ACTIVITY_RATES.get('MESSAGING_PREMIUM_USERS', 0.08)
    premium_users = round(users * premium_rate)
    premium_revenue = premium_users * params.messaging_premium_fee
    
    # Total revenue
    revenue = (
        dm_revenue + group_chat_revenue + file_transfer_revenue +
        call_revenue + storage_revenue + premium_revenue
    )
    
    # Issue #9: Linear cost scaling
    costs = config.get_linear_cost('MESSAGING', users)
    
    # Profit
    profit = revenue - costs
    margin = (profit / revenue * 100) if revenue > 0 else 0
    
    return ModuleResult(
        revenue=round(revenue, 2),
        costs=round(costs, 2),
        profit=round(profit, 2),
        margin=round(margin, 1),
        breakdown={
            'total_messages': total_messages,
            'regular_messages': regular_messages,
            'encrypted_messages': encrypted_messages,
            'group_chats_created': group_chats_created,
            'files_transferred': files_transferred,
            'call_users': call_users,
            'total_call_minutes': total_call_minutes,
            'storage_subscribers': storage_subscribers,
            'premium_users': premium_users,
            'dm_revenue': round(dm_revenue, 2),
            'group_chat_revenue': round(group_chat_revenue, 2),
            'file_transfer_revenue': round(file_transfer_revenue, 2),
            'call_revenue': round(call_revenue, 2),
            'storage_revenue': round(storage_revenue, 2),
            'premium_revenue': round(premium_revenue, 2),
        }
    )
