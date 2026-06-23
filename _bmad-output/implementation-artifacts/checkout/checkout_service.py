"""
Checkout Service for Blind Date Book
Handles payment processing, order creation, and subscription setup
"""

import json
import uuid
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

CHECKOUT_VERSION = "1.0"


@dataclass
class Order:
    """Order data model"""
    order_id: str
    status: str  # pending, paid, failed, shipped, delivered
    cart_items: list
    subscription_data: dict
    total_amount: float
    email: str


def validate_cart_items(cart_items: list) -> Tuple[bool, Optional[str]]:
    """Validate cart items"""
    if not cart_items:
        return False, "Cart is empty"
    
    for item in cart_items:
        if not item.get('book_id') or not item.get('price'):
            return False, "Invalid item in cart"
        
        if item['price'] <= 0:
            return False, "Invalid price"
    
    return True, None


def validate_address(address: dict) -> Tuple[bool, Optional[str]]:
    """Validate shipping/billing address"""
    required_fields = ['name', 'street', 'city', 'state', 'postal_code']
    
    for field in required_fields:
        if not address.get(field) or not str(address[field]).strip():
            return False, f"Missing required field: {field}"
    
    # Validate postal code format (basic)
    postal = str(address.get('postal_code', '')).strip()
    if len(postal) < 3 or len(postal) > 10:
        return False, "Invalid postal code format"
    
    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email format"""
    if not email or '@' not in email or '.' not in email.split('@')[-1]:
        return False, "Invalid email address"
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """Validate phone format"""
    if not phone or len(phone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '').replace('+', '')) < 10:
        return False, "Invalid phone number"
    return True, None


def calculate_order_total(cart_items: list, subscription: dict) -> float:
    """Calculate total order amount"""
    subtotal = sum(item['price'] * item.get('quantity', 1) for item in cart_items)
    
    # Kit fee (included in price model for this MVP)
    # Could be: subtotal + 10.00 for kit fee, but currently included in item price
    
    return round(subtotal, 2)


def get_next_billing_date(cadence: str, start_date_str: str) -> str:
    """Calculate next billing date based on cadence"""
    from dateutil import parser as date_parser
    
    try:
        start_date = date_parser.parse(start_date_str).date()
    except:
        start_date = datetime.now().date()
    
    intervals = {
        'one-time': 0,  # No recurring
        'monthly': 30,
        'bi-weekly': 14,
        'bi-month': 14,
        'three-month': 90
    }
    
    days = intervals.get(cadence, 0)
    next_date = start_date + timedelta(days=days)
    return next_date.isoformat()


def validate_checkout_request(request_data: dict) -> Tuple[bool, Optional[str]]:
    """Validate complete checkout request"""
    
    # Validate cart
    valid, error = validate_cart_items(request_data.get('cart_items', []))
    if not valid:
        return False, error
    
    # Validate shipping address
    shipping_addr = request_data.get('shipping_address', {})
    valid, error = validate_address(shipping_addr)
    if not valid:
        return False, error
    
    # Validate email
    email = request_data.get('email', '')
    valid, error = validate_email(email)
    if not valid:
        return False, error
    
    # Validate phone
    phone = request_data.get('phone', '')
    valid, error = validate_phone(phone)
    if not valid:
        return False, error
    
    # Validate payment method
    payment_method = request_data.get('payment_method', '')
    if payment_method not in ['card', 'pix']:
        return False, "Invalid payment method"
    
    # Validate subscription data
    subscription = request_data.get('subscription', {})
    cadence = subscription.get('cadence', 'one-time')
    if cadence not in ['one-time', 'monthly', 'bi-weekly', 'three-month']:
        return False, "Invalid subscription cadence"
    
    return True, None


def create_order_dict(request_data: dict) -> Dict:
    """Create order dict from checkout request"""
    order_id = str(uuid.uuid4())
    
    cart_items = request_data.get('cart_items', [])
    subscription = request_data.get('subscription', {})
    total_amount = calculate_order_total(cart_items, subscription)
    
    # Build subscription data
    subscription_data = {
        'cadence': subscription.get('cadence', 'one-time'),
        'start_date': subscription.get('start_date', datetime.now().date().isoformat()),
        'initial_price': subscription.get('initial_price', total_amount),
        'recurring_price': subscription.get('recurring_price'),
        'stripe_subscription_id': None,  # Set after Stripe charge
        'payment_status': 'pending'
    }
    
    order = {
        'order_id': order_id,
        'user_id': request_data.get('user_id'),
        'email': request_data.get('email'),
        'status': 'pending',
        'cart_items': cart_items,
        'subscription_data': subscription_data,
        'shipping_address': request_data.get('shipping_address', {}),
        'billing_address': request_data.get('billing_address'),
        'total_amount': total_amount,
        'currency': 'USD',
        'payment_method': request_data.get('payment_method'),
        'payment_details': {
            'payment_intent_id': None,
            'stripe_token': request_data.get('stripe_token'),
            'last_four_digits': None,
            'pix_qr_code': None,
            'pix_request_id': None
        },
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    return order


def create_pix_qr_code(order_id: str, amount: float) -> Dict:
    """Generate PIX QR code (mock for MVP)"""
    import random
    
    # In production, this would call Stripe's PIX API or Brazilian central bank API
    # For MVP, return mock data
    qr_code = f"00020126360014br.gov.bcb.brcode0136{order_id}0220{amount:.2f}"
    
    return {
        'pix_qr_code': qr_code,
        'pix_copy_paste': qr_code,
        'pix_request_id': f"pix-{order_id[:12]}",
        'expires_at': (datetime.utcnow() + timedelta(minutes=30)).isoformat() + 'Z'
    }


def parse_checkout_request(request_data: dict) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Main entry point for checkout
    Validates request and creates order dict
    Returns (order_dict, error_message)
    """
    # Validate request
    valid, error = validate_checkout_request(request_data)
    if not valid:
        return None, error
    
    # Create order
    try:
        order = create_order_dict(request_data)
        return order, None
    except Exception as e:
        return None, f"Order creation failed: {str(e)}"
