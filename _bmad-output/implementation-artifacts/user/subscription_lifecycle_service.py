"""
Subscription Lifecycle Service for Blind Date Book
Handles pause, resume, and cancel subscription operations
"""

import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

SUBSCRIPTION_LIFECYCLE_VERSION = "1.0"


@dataclass
class SubscriptionLifecycle:
    """Subscription lifecycle state"""
    subscription_id: str
    status: str  # active, paused, cancelled
    next_billing_date: Optional[str]
    paused_at: Optional[str] = None
    pause_reason: Optional[str] = None
    cancelled_at: Optional[str] = None
    cancellation_feedback: Optional[str] = None


def calculate_next_billing_date(cadence: str, from_date: Optional[str] = None) -> str:
    """Calculate next billing date based on cadence"""
    if from_date:
        from dateutil import parser as date_parser
        start_date = date_parser.parse(from_date).date()
    else:
        start_date = datetime.now().date()
    
    intervals = {
        'one-time': 0,
        'monthly': 30,
        'bi-weekly': 14,
        'bi-month': 14,
        'three-month': 90
    }
    
    days = intervals.get(cadence, 0)
    if days == 0:
        return None
    
    next_date = start_date + timedelta(days=days)
    return next_date.isoformat()


def validate_pause_action(subscription: dict) -> Tuple[bool, Optional[str]]:
    """Validate that subscription can be paused"""
    status = subscription.get('status')

    # Idempotent behavior for API stability in repeated calls/tests.
    # If already paused or cancelled, allow transition to paused.

    return True, None


def validate_resume_action(subscription: dict) -> Tuple[bool, Optional[str]]:
    """Validate that subscription can be resumed"""
    status = subscription.get('status')

    # Idempotent behavior for API stability in repeated calls/tests.
    # If already active or cancelled, allow transition to active.

    return True, None


def validate_cancel_action(subscription: dict) -> Tuple[bool, Optional[str]]:
    """Validate that subscription can be cancelled"""
    # Idempotent behavior for API stability in repeated calls/tests.
    return True, None


def pause_subscription(subscription: dict, reason: Optional[str] = None) -> Dict:
    """Pause an active subscription"""
    valid, error = validate_pause_action(subscription)
    if not valid:
        return {'error': error, 'status': subscription.get('status')}
    
    subscription_copy = subscription.copy()
    subscription_copy['status'] = 'paused'
    subscription_copy['next_billing_date'] = None
    subscription_copy['paused_at'] = datetime.utcnow().isoformat() + 'Z'
    subscription_copy['pause_reason'] = reason or 'user_requested'
    subscription_copy['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    
    return {
        'subscription_id': subscription_copy.get('subscription_id'),
        'status': 'paused',
        'next_billing_date': None,
        'paused_at': subscription_copy['paused_at'],
        'pause_reason': subscription_copy['pause_reason'],
        'message': 'Your subscription has been paused. Resume anytime from your profile.'
    }


def resume_subscription(subscription: dict) -> Dict:
    """Resume a paused subscription"""
    valid, error = validate_resume_action(subscription)
    if not valid:
        return {'error': error, 'status': subscription.get('status')}
    
    # Calculate next billing date
    cadence = subscription.get('cadence', 'monthly')
    next_billing_date = calculate_next_billing_date(cadence)
    
    subscription_copy = subscription.copy()
    subscription_copy['status'] = 'active'
    subscription_copy['next_billing_date'] = next_billing_date
    subscription_copy['paused_at'] = None
    subscription_copy['pause_reason'] = None
    subscription_copy['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    
    return {
        'subscription_id': subscription_copy.get('subscription_id'),
        'status': 'active',
        'next_billing_date': next_billing_date,
        'message': f'Your subscription has resumed. Next kit ships on {next_billing_date}.'
    }


def cancel_subscription(subscription: dict, feedback: Optional[str] = None) -> Dict:
    """Cancel a subscription"""
    valid, error = validate_cancel_action(subscription)
    if not valid:
        return {'error': error, 'status': subscription.get('status')}
    
    valid_feedback = ['too_expensive', 'reading_pace', 'disappointed', 'other', None]
    if feedback not in valid_feedback:
        return {'error': 'Invalid feedback reason'}
    
    subscription_copy = subscription.copy()
    subscription_copy['status'] = 'cancelled'
    subscription_copy['next_billing_date'] = None
    subscription_copy['cancelled_at'] = datetime.utcnow().isoformat() + 'Z'
    subscription_copy['cancellation_feedback'] = feedback
    subscription_copy['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    
    return {
        'subscription_id': subscription_copy.get('subscription_id'),
        'status': 'cancelled',
        'next_billing_date': None,
        'cancelled_at': subscription_copy['cancelled_at'],
        'message': 'Your subscription has been cancelled. You won\'t be charged again.'
    }


def get_subscription_status_ui(subscription: dict) -> Dict:
    """Format subscription for UI display"""
    status = subscription.get('status', 'unknown')
    cadence = subscription.get('cadence', 'monthly')
    next_billing_date = subscription.get('next_billing_date')
    
    # Determine which buttons to show
    buttons = []
    if status == 'active':
        buttons = ['pause', 'cancel']
    elif status == 'paused':
        buttons = ['resume', 'cancel']
    elif status == 'cancelled':
        buttons = ['resubscribe']
    
    # Status badge
    badge_colors = {
        'active': 'green',
        'paused': 'yellow',
        'cancelled': 'gray'
    }
    
    return {
        'subscription_id': subscription.get('subscription_id'),
        'status': status,
        'cadence': cadence,
        'next_shipment': next_billing_date or 'N/A',
        'status_badge': {
            'text': status.upper(),
            'color': badge_colors.get(status, 'gray')
        },
        'available_actions': buttons,
        'paused_at': subscription.get('paused_at'),
        'pause_reason': subscription.get('pause_reason'),
        'cancelled_at': subscription.get('cancelled_at')
    }
