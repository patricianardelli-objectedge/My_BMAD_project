"""
Webhook Handler for Stripe Events
Processes payment confirmations, failures, and subscription updates
"""

import json
import hashlib
import hmac
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

WEBHOOK_VERSION = "1.0"


@dataclass
class WebhookEvent:
    """Webhook event data"""
    event_id: str
    stripe_event_id: str
    event_type: str
    resource_type: str
    resource_id: Optional[str]
    order_id: Optional[str]
    subscription_id: Optional[str]
    status: str  # received, processing, processed, failed
    payload: dict
    created_at: str
    processed_at: Optional[str] = None
    error_message: Optional[str] = None


def verify_stripe_signature(payload_bytes: bytes, sig_header: str, webhook_secret: str) -> Tuple[bool, Optional[str]]:
    """
    Verify Stripe webhook signature
    Args:
        payload_bytes: Raw request body bytes
        sig_header: Stripe-Signature header value
        webhook_secret: Webhook signing secret from Stripe dashboard
    Returns:
        (is_valid, error_message)
    """
    if not sig_header:
        return False, "Missing Stripe-Signature header"
    
    try:
        # Parse signature header: t=timestamp,v1=signature
        parts = {}
        for part in sig_header.split(','):
            key, value = part.split('=')
            parts[key] = value
        
        timestamp = parts.get('t')
        signature = parts.get('v1')
        
        if not timestamp or not signature:
            return False, "Invalid Stripe-Signature header format"
        
        # Create signed content: timestamp.payload
        signed_content = f"{timestamp}.{payload_bytes.decode('utf-8')}"
        
        # Compute expected signature
        expected_sig = hmac.new(
            webhook_secret.encode('utf-8'),
            signed_content.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (constant-time comparison)
        if not hmac.compare_digest(expected_sig, signature):
            return False, "Invalid signature"
        
        return True, None
        
    except Exception as e:
        return False, f"Signature verification error: {str(e)}"


def process_payment_intent_succeeded(event_data: dict) -> Dict:
    """
    Process payment_intent.succeeded webhook event
    Updates order status to paid
    """
    try:
        payload = event_data.get('data', {}).get('object', {})
        payment_intent_id = payload.get('id')
        amount = payload.get('amount', 0) / 100  # Convert cents to dollars
        metadata = payload.get('metadata', {})
        order_id = metadata.get('order_id')
        
        return {
            'status': 'processed',
            'event_type': 'payment_intent.succeeded',
            'order_id': order_id,
            'payment_intent_id': payment_intent_id,
            'amount': amount,
            'action': 'update_order_status_to_paid',
            'error': None
        }
    except Exception as e:
        return {
            'status': 'failed',
            'event_type': 'payment_intent.succeeded',
            'error': f"Processing error: {str(e)}"
        }


def process_charge_failed(event_data: dict) -> Dict:
    """
    Process charge.failed webhook event
    Updates order status to failed and notifies customer
    """
    try:
        payload = event_data.get('data', {}).get('object', {})
        charge_id = payload.get('id')
        amount = payload.get('amount', 0) / 100
        metadata = payload.get('metadata', {})
        order_id = metadata.get('order_id')
        failure_code = payload.get('failure_code')
        failure_message = payload.get('failure_message')
        
        # Map Stripe failure codes to user-friendly messages
        failure_messages = {
            'card_declined': 'Your card was declined. Please try another card.',
            'expired_card': 'Your card has expired. Please update your card.',
            'insufficient_funds': 'Insufficient funds. Please check your account.',
            'lost_card': 'Your card was reported lost. Please contact your bank.',
            'stolen_card': 'Your card was reported stolen. Please contact your bank.',
            'generic_decline': 'Payment declined. Please try another card.'
        }
        
        user_message = failure_messages.get(failure_code, failure_message or 'Payment failed')
        
        return {
            'status': 'processed',
            'event_type': 'charge.failed',
            'order_id': order_id,
            'charge_id': charge_id,
            'amount': amount,
            'failure_code': failure_code,
            'failure_message': failure_message,
            'user_message': user_message,
            'action': 'update_order_status_to_failed_and_email_customer',
            'error': None
        }
    except Exception as e:
        return {
            'status': 'failed',
            'event_type': 'charge.failed',
            'error': f"Processing error: {str(e)}"
        }


def process_customer_subscription_updated(event_data: dict) -> Dict:
    """
    Process customer.subscription.updated webhook event
    Updates subscription metadata and status
    """
    try:
        payload = event_data.get('data', {}).get('object', {})
        subscription_id = payload.get('id')
        status = payload.get('status')  # active, past_due, canceled, etc.
        current_period_end = payload.get('current_period_end')
        metadata = payload.get('metadata', {})
        
        return {
            'status': 'processed',
            'event_type': 'customer.subscription.updated',
            'subscription_id': subscription_id,
            'stripe_status': status,
            'current_period_end': current_period_end,
            'action': 'update_subscription_metadata',
            'error': None
        }
    except Exception as e:
        return {
            'status': 'failed',
            'event_type': 'customer.subscription.updated',
            'error': f"Processing error: {str(e)}"
        }


def process_customer_subscription_deleted(event_data: dict) -> Dict:
    """
    Process customer.subscription.deleted webhook event
    Cancels subscription
    """
    try:
        payload = event_data.get('data', {}).get('object', {})
        subscription_id = payload.get('id')
        metadata = payload.get('metadata', {})
        
        return {
            'status': 'processed',
            'event_type': 'customer.subscription.deleted',
            'subscription_id': subscription_id,
            'action': 'update_subscription_status_to_cancelled',
            'error': None
        }
    except Exception as e:
        return {
            'status': 'failed',
            'event_type': 'customer.subscription.deleted',
            'error': f"Processing error: {str(e)}"
        }


def process_webhook_event(event: dict) -> Dict:
    """
    Route webhook event to appropriate handler
    """
    event_type = event.get('type')
    
    if event_type == 'payment_intent.succeeded':
        return process_payment_intent_succeeded(event)
    elif event_type == 'charge.failed':
        return process_charge_failed(event)
    elif event_type == 'customer.subscription.updated':
        return process_customer_subscription_updated(event)
    elif event_type == 'customer.subscription.deleted':
        return process_customer_subscription_deleted(event)
    else:
        # Unhandled event type (log but don't fail)
        return {
            'status': 'received',
            'event_type': event_type,
            'action': 'log_unhandled_event_type',
            'error': None
        }
