from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import os
import json
import uuid
from datetime import datetime, timedelta
import logging
import sys
import time

HERE = Path(__file__).parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT / 'ai'))
sys.path.insert(0, str(PARENT / 'checkout'))
sys.path.insert(0, str(PARENT / 'user'))

app = Flask(__name__, static_folder=str(HERE / 'static'))

# In-memory storage for MVP (persistence layer)
# In production, these would be in a database
IN_MEMORY_USERS = {}  # {user_id: {email, password_hash, name, created_at, ...}}
IN_MEMORY_PREFERENCES = {}  # {user_id: {preferred_genres, mood_keywords, ...}}
IN_MEMORY_AVOID_LIST = {}  # {user_id: [book_ids]}
IN_MEMORY_SUBSCRIPTIONS = {}  # {subscription_id: {status, cadence, next_billing_date, ...}}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(HERE / 'parse_events.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# import parser and decision engine
from parser import parse_input, PARSER_VERSION
from decision_engine import parse_input as decision_parse_input, PARSER_VERSION as DECISION_VERSION
from checkout_service import parse_checkout_request, CHECKOUT_VERSION, create_pix_qr_code
from webhook_handler import verify_stripe_signature, process_webhook_event, WEBHOOK_VERSION
from user_service import (
    parse_register_request, parse_login_request, parse_preferences_request, parse_avoid_list_request,
    generate_jwt_token, verify_jwt_token, USER_VERSION
)
from order_history_service import (
    parse_order_for_history, get_unified_exclude_list, get_books_from_delivered_orders,
    apply_order_filters, paginate_orders, ORDER_HISTORY_VERSION
)
from subscription_lifecycle_service import (
    pause_subscription, resume_subscription, cancel_subscription, get_subscription_status_ui,
    SUBSCRIPTION_LIFECYCLE_VERSION
)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

def log_parse_event(session_id, text, parsed, ambiguities, confidence):
    """Log parse event for pilot analysis."""
    event = {
        'event_id': str(uuid.uuid4()),
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'session_id': session_id,
        'parser_version': PARSER_VERSION,
        'raw_input': text,
        'parsed_output': {
            'recipient': parsed.get('recipient'),
            'age_range': parsed.get('age_range'),
            'genres': parsed.get('genres'),
            'avoid': parsed.get('avoid'),
            'surprise_level': parsed.get('surprise_level'),
            'mood': parsed.get('mood')
        },
        'confidence': confidence,
        'ambiguities': ambiguities,
        'event_type': 'ambiguity' if ambiguities else 'parse_success'
    }
    
    logger.info(json.dumps(event))
    return event

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/parse', methods=['POST'])
def api_parse():
    try:
        data = request.get_json(force=True)
        text = data.get('text', '')
        result = parse_input(text)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Parse error: {str(e)}")
        return jsonify({'error': 'Parse failed', 'recipient': 'self', 'genres': [], 'avoid': []}), 200

@app.route('/api/agent/parse', methods=['POST'])
def api_agent_parse():
    try:
        import time
        start_time = time.time()
        
        data = request.get_json(force=True)
        text = data.get('text', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        turn_number = data.get('turn', 0)
        
        # Parse input
        result = parse_input(text)
        
        # Log parse event
        log_parse_event(
            session_id=session_id,
            text=text,
            parsed=result,
            ambiguities=result.get('ambiguities', []),
            confidence=result.get('confidence', 0.0)
        )
        
        # Build normalized response
        parsed = {
            'recipient_type': result.get('recipient') or 'self',
            'recipient_age_range': result.get('age_range'),
            'genres': result.get('genres', []),
            'avoid': result.get('avoid', []),
            'surprise_level': result.get('surprise_level') or 'balanced',
            'mood': result.get('mood'),
            'raw_input': result.get('raw', text)
        }
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return jsonify({
            'parsed': parsed,
            'recipient': result.get('recipient') or 'self',
            'age_range': result.get('age_range'),
            'genres': result.get('genres', []),
            'avoid': result.get('avoid', []),
            'surprise_level': result.get('surprise_level') or 'balanced',
            'raw': result.get('raw', text),
            'confidence': result.get('confidence', 0.0),
            'parser_version': PARSER_VERSION,
            'ambiguities': result.get('ambiguities', []),
            'response_time_ms': response_time_ms,
            'parsed_at': datetime.utcnow().isoformat() + 'Z',
            'follow_up_question': None,
            'suggestions': []
        })
    except Exception as e:
        logger.error(f"Agent parse error: {str(e)}")
        # Return safe defaults on error
        return jsonify({
            'parsed': {
                'recipient_type': 'self',
                'genres': [],
                'avoid': [],
                'surprise_level': 'balanced'
            },
            'recipient': 'self',
            'genres': [],
            'avoid': [],
            'surprise_level': 'balanced',
            'confidence': 0.0,
            'parser_version': PARSER_VERSION,
            'ambiguities': [{
                'reason': 'PARSE_ERROR',
                'value': '',
                'suggestion': 'Sorry, I had trouble understanding that. Could you try again?'
            }]
        }), 200

@app.route('/api/ai/decide', methods=['POST'])
def api_ai_decide():
    """Decision engine endpoint - selects best-fit book based on preferences (Story 4.2 Integration)"""
    try:
        start_time = time.time()
        
        data = request.get_json(force=True)
        preferences = data.get('preferences', {})
        exclude_books = list(data.get('exclude_books', []))  # Manually passed exclusions
        user_id = data.get('user_id')  # Optional: if provided, auto-fetch user's exclude-list
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Validate preferences
        if not preferences.get('recipient_age_range'):
            return jsonify({
                'error': 'recipient_age_range required',
                'confidence': 0.0,
                'parser_version': DECISION_VERSION
            }), 400
        
        # Story 4.2 Integration: Auto-fetch user's exclude-list (delivered + avoid-list)
        if user_id:
            # Get actual user avoid-list from in-memory storage
            user_avoid_list = IN_MEMORY_AVOID_LIST.get(user_id, [])
            
            # Mock delivered books (in production, would query from database)
            # Keep this aligned with /api/users/<user_id>/excluded-books mock behavior.
            mock_delivered_books = ['book-001', 'book-002', 'book-003']
            
            # Merge with unified exclude-list (deduplication happens in get_unified_exclude_list)
            unified_exclude = get_unified_exclude_list(user_avoid_list, mock_delivered_books)
            exclude_books.extend(unified_exclude)
            exclude_books = list(set(exclude_books))  # Remove any duplicates
            
            logger.info(f"User {user_id} excluded books: {exclude_books}")
        
        # Call decision engine with exclude-list
        decision = decision_parse_input(preferences, exclude_books, session_id)
        
        if not decision or 'error' in decision:
            return jsonify(decision or {
                'error': 'No suitable books found',
                'confidence': 0.0,
                'parser_version': DECISION_VERSION
            }), 400
        
        # Add response time
        response_time_ms = int((time.time() - start_time) * 1000)
        decision['response_time_ms'] = response_time_ms
        
        # Log decision event (Story 4.2: include exclude-list info)
        event = {
            'event_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'session_id': session_id,
            'user_id': user_id,
            'event_type': 'decision_success',
            'book_id': decision.get('book_id'),
            'score': decision.get('score'),
            'confidence': decision.get('confidence'),
            'excluded_books_count': len(exclude_books),
            'excluded_books': exclude_books[:10] if exclude_books else [],  # Log first 10
            'preferences': preferences,
            'response_time_ms': response_time_ms
        }
        logger.info(json.dumps(event))
        
        return jsonify(decision), 200
        
    except Exception as e:
        logger.error(f"Decision engine error: {str(e)}")
        return jsonify({
            'error': 'Decision failed',
            'confidence': 0.0,
            'parser_version': DECISION_VERSION,
            'event_type': 'decision_error'
        }), 500

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    """Checkout endpoint - Process payment and create order (Story 3.1)"""
    try:
        start_time = time.time()
        
        data = request.get_json(force=True)
        
        # Validate checkout request
        order_data, error = parse_checkout_request(data)
        
        if error or not order_data:
            return jsonify({
                'error': error or 'Checkout validation failed',
                'parser_version': CHECKOUT_VERSION
            }), 400
        
        # For MVP: Mock payment processing
        # In production: Call Stripe API with stripe_token
        payment_method = data.get('payment_method', 'card')
        
        if payment_method == 'pix':
            # Generate PIX QR code
            pix_data = create_pix_qr_code(order_data['order_id'], order_data['total_amount'])
            
            order_data['status'] = 'awaiting_pix_confirmation'
            order_data['payment_details'].update(pix_data)
            
            response = {
                'order_id': order_data['order_id'],
                'status': 'awaiting_pix_confirmation',
                'payment_method': 'pix',
                'pix_qr_code': pix_data['pix_qr_code'],
                'pix_copy_paste': pix_data['pix_copy_paste'],
                'pix_request_id': pix_data['pix_request_id'],
                'expires_at': pix_data['expires_at'],
                'total_amount': order_data['total_amount'],
                'currency': order_data['currency'],
                'created_at': order_data['created_at']
            }
        else:
            # Card payment (mock for MVP)
            # In production: stripe.PaymentIntent.create(amount, currency, customer, ...) 
            order_data['status'] = 'paid'
            order_data['payment_details']['payment_intent_id'] = f"pi_{order_data['order_id'][:12]}"
            order_data['payment_details']['last_four_digits'] = "4242"  # Mock
            
            response = {
                'order_id': order_data['order_id'],
                'status': 'paid',
                'total_amount': order_data['total_amount'],
                'currency': order_data['currency'],
                'payment_method': 'card',
                'last_four_digits': '4242',
                'subscription': {
                    'cadence': order_data['subscription_data']['cadence'],
                    'next_billing_date': order_data['subscription_data']['start_date'],
                    'stripe_subscription_id': order_data['subscription_data']['stripe_subscription_id']
                },
                'shipping_address': {
                    'name': order_data['shipping_address'].get('name'),
                    'city': order_data['shipping_address'].get('city')
                },
                'receipt_url': f"https://example.com/receipts/{order_data['order_id']}",
                'next_shipment_date': (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z',
                'created_at': order_data['created_at'],
                'parser_version': CHECKOUT_VERSION
            }
        
        response_time_ms = int((time.time() - start_time) * 1000)
        response['response_time_ms'] = response_time_ms
        
        # Log checkout event
        event = {
            'event_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': 'checkout_success',
            'order_id': order_data['order_id'],
            'payment_method': payment_method,
            'total_amount': order_data['total_amount'],
            'response_time_ms': response_time_ms
        }
        logger.info(json.dumps(event))
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        return jsonify({
            'error': 'Checkout failed',
            'parser_version': CHECKOUT_VERSION,
            'event_type': 'checkout_error'
        }), 500

@app.route('/api/webhooks/stripe', methods=['POST'])
def handle_stripe_webhook():
    """Stripe webhook handler (Story 3.3)"""
    try:
        # Get raw body and signature
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        # Get webhook secret from environment
        webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_test_secret')
        
        # Verify signature
        is_valid, error = verify_stripe_signature(payload, sig_header, webhook_secret)
        
        if not is_valid:
            logger.warning(f"Invalid webhook signature: {error}")
            return jsonify({'error': error}), 400
        
        # Parse event
        event = json.loads(payload)
        event_id = str(uuid.uuid4())
        stripe_event_id = event.get('id')
        
        # Log webhook received
        webhook_log = {
            'event_id': event_id,
            'stripe_event_id': stripe_event_id,
            'event_type': event.get('type'),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'status': 'received'
        }
        logger.info(f"Webhook received: {json.dumps(webhook_log)}")
        
        # Process event
        result = process_webhook_event(event)
        
        webhook_log['status'] = result.get('status', 'unknown')
        webhook_log['action'] = result.get('action')
        
        if result.get('error'):
            webhook_log['error'] = result['error']
        
        logger.info(f"Webhook processed: {json.dumps(webhook_log)}")
        
        # Return 200 OK immediately (async processing)
        return jsonify({'status': 'received', 'id': event_id}), 200
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        return jsonify({'error': 'Invalid JSON'}), 400
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return jsonify({'error': 'Processing error'}), 500

# ============ Story 4.1: User Registration & Authentication ============
@app.route('/api/users/register', methods=['POST'])
def register_user():
    """User registration endpoint (Story 4.1)"""
    try:
        data = request.get_json(force=True)
        
        # Parse and validate registration
        user_data, error = parse_register_request(data)
        
        if error or not user_data:
            return jsonify({'error': error or 'Registration failed', 'parser_version': USER_VERSION}), 400
        
        # Store user in in-memory storage
        IN_MEMORY_USERS[user_data['user_id']] = user_data
        
        token = generate_jwt_token(user_data['user_id'], user_data['email'])
        
        response = {
            'user_id': user_data['user_id'],
            'email': user_data['email'],
            'name': user_data['name'],
            'jwt_token': token,
            'created_at': user_data['created_at'],
            'parser_version': USER_VERSION
        }
        
        logger.info(f"User registered: {user_data['email']}")
        return jsonify(response), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed', 'parser_version': USER_VERSION}), 500

@app.route('/api/users/login', methods=['POST'])
def login_user():
    """User login endpoint (Story 4.1)"""
    try:
        data = request.get_json(force=True)
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required', 'parser_version': USER_VERSION}), 400
        
        # Log what's in IN_MEMORY_USERS
        logger.info(f"Login attempt for {email}. Users in storage: {[u['email'] for u in IN_MEMORY_USERS.values()]}")
        
        # Look up user in in-memory storage by email
        user_record = None
        for user_id, user_data in IN_MEMORY_USERS.items():
            if user_data['email'] == email:
                user_record = user_data
                break
        
        # Parse and validate login
        token, error = parse_login_request(data, user_record)
        
        if error or not token:
            return jsonify({'error': error or 'Login failed', 'parser_version': USER_VERSION}), 401
        
        response = {
            'user_id': user_record['user_id'],
            'email': user_record['email'],
            'name': user_record['name'],
            'jwt_token': token,
            'parser_version': USER_VERSION
        }
        
        logger.info(f"User logged in: {email}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed', 'parser_version': USER_VERSION}), 500

# ============ Story 4.1: User Preferences ============
@app.route('/api/users/<user_id>/preferences', methods=['POST'])
def save_user_preferences(user_id):
    """Save user preferences endpoint (Story 4.1)"""
    try:
        data = request.get_json(force=True)
        
        # Parse preferences
        prefs, error = parse_preferences_request(data)
        
        if error or not prefs:
            return jsonify({'error': error or 'Invalid preferences', 'parser_version': USER_VERSION}), 400
        
        prefs['user_id'] = user_id
        
        # Store in in-memory storage
        IN_MEMORY_PREFERENCES[user_id] = prefs
        
        response = {
            'user_id': user_id,
            'preferences': prefs,
            'message': 'Preferences saved successfully',
            'parser_version': USER_VERSION
        }
        
        logger.info(f"Preferences saved for user {user_id}")
        return jsonify(response), 201
        
    except Exception as e:
        logger.error(f"Preference save error: {str(e)}")
        return jsonify({'error': 'Failed to save preferences', 'parser_version': USER_VERSION}), 500

@app.route('/api/users/<user_id>/preferences', methods=['GET'])
def get_user_preferences(user_id):
    """Get user preferences endpoint (Story 4.1)"""
    try:
        # Retrieve from in-memory storage
        if user_id in IN_MEMORY_PREFERENCES:
            prefs = IN_MEMORY_PREFERENCES[user_id]
            return jsonify(prefs), 200
        
        # User hasn't set preferences yet - return error
        return jsonify({'error': 'No preferences found for this user', 'parser_version': USER_VERSION}), 404
        
    except Exception as e:
        logger.error(f"Preference fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch preferences', 'parser_version': USER_VERSION}), 500

# ============ Story 4.1: Avoid-List Management ============
@app.route('/api/users/<user_id>/avoid-list', methods=['POST'])
def add_to_avoid_list(user_id):
    """Add book to avoid-list endpoint (Story 4.1)"""
    try:
        data = request.get_json(force=True)
        
        # Parse avoid-list entry
        entry, error = parse_avoid_list_request(data)
        
        if error or not entry:
            return jsonify({'error': error or 'Invalid entry', 'parser_version': USER_VERSION}), 400
        
        entry['user_id'] = user_id
        
        # Store in in-memory avoid-list
        if user_id not in IN_MEMORY_AVOID_LIST:
            IN_MEMORY_AVOID_LIST[user_id] = []
        
        IN_MEMORY_AVOID_LIST[user_id].append(entry['book_id'])
        
        response = {
            'user_id': user_id,
            'avoid_id': entry['avoid_id'],
            'book_id': entry['book_id'],
            'reason': entry['reason'],
            'message': f'Book {entry["book_id"]} added to avoid-list',
            'parser_version': USER_VERSION
        }
        
        logger.info(f"Book {entry['book_id']} added to avoid-list for user {user_id}")
        return jsonify(response), 201
        
    except Exception as e:
        logger.error(f"Avoid-list add error: {str(e)}")
        return jsonify({'error': 'Failed to add to avoid-list', 'parser_version': USER_VERSION}), 500

@app.route('/api/users/<user_id>/avoid-list', methods=['GET'])
def get_avoid_list(user_id):
    """Get user avoid-list endpoint (Story 4.1)"""
    try:
        # Retrieve from in-memory storage
        avoided_books = IN_MEMORY_AVOID_LIST.get(user_id, [])
        
        response = {
            'user_id': user_id,
            'total': len(avoided_books),
            'avoided_books': [{'book_id': book_id, 'reason': 'user-marked'} for book_id in avoided_books]
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Avoid-list fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch avoid-list', 'parser_version': USER_VERSION}), 500

@app.route('/api/users/<user_id>/avoid-list/<book_id>', methods=['DELETE'])
def remove_from_avoid_list(user_id, book_id):
    """Remove book from avoid-list endpoint (Story 4.1)"""
    try:
        # Remove from in-memory storage
        if user_id in IN_MEMORY_AVOID_LIST and book_id in IN_MEMORY_AVOID_LIST[user_id]:
            IN_MEMORY_AVOID_LIST[user_id].remove(book_id)
        
        response = {
            'user_id': user_id,
            'book_id': book_id,
            'message': f'Book {book_id} removed from avoid-list',
            'parser_version': USER_VERSION
        }
        
        logger.info(f"Book {book_id} removed from avoid-list for user {user_id}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Avoid-list remove error: {str(e)}")
        return jsonify({'error': 'Failed to remove from avoid-list', 'parser_version': USER_VERSION}), 500

# ============ Story 4.2: Order History ============
@app.route('/api/users/<user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """Get user order history endpoint (Story 4.2)"""
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 10)), 100)
        offset = int(request.args.get('offset', 0))
        
        # Mock: In production, retrieve from database
        mock_orders = [
            {
                'order_id': 'order-001',
                'created_at': '2026-06-15T10:00:00Z',
                'delivery_date': '2026-06-20',
                'delivery_status': 'delivered',
                'items': ['Midsummer Manor Mystery', 'Cozy Autumn Reads'],
                'total_amount': 49.98
            },
            {
                'order_id': 'order-002',
                'created_at': '2026-06-08T14:30:00Z',
                'delivery_date': '2026-06-13',
                'delivery_status': 'delivered',
                'items': ['Epic Adventure Tales'],
                'total_amount': 24.99
            }
        ]
        
        # Apply filtering/sorting/pagination (mock)
        paginated = paginate_orders(mock_orders, limit, offset)
        paginated['parser_version'] = ORDER_HISTORY_VERSION
        
        return jsonify(paginated), 200
        
    except Exception as e:
        logger.error(f"Order history fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch order history', 'parser_version': ORDER_HISTORY_VERSION}), 500

@app.route('/api/users/<user_id>/excluded-books', methods=['GET'])
def get_excluded_books(user_id):
    """Get unified exclude-list (avoid-list + delivered) endpoint (Story 4.2)"""
    try:
        # Mock: In production, merge from database
        mock_avoid_list = ['book-005', 'book-010']
        mock_delivered_books = ['book-001', 'book-002', 'book-003']
        
        excluded_list = get_unified_exclude_list(mock_avoid_list, mock_delivered_books)
        
        response = {
            'user_id': user_id,
            'total': len(excluded_list),
            'excluded_ids': excluded_list,
            'breakdown': {
                'delivered': len(mock_delivered_books),
                'user_marked': len(mock_avoid_list),
                'system': 0
            },
            'parser_version': ORDER_HISTORY_VERSION
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Excluded books fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch excluded books', 'parser_version': ORDER_HISTORY_VERSION}), 500

# ============ Story 4.3: Subscription Lifecycle ============
@app.route('/api/subscriptions/<subscription_id>', methods=['GET'])
def get_subscription_status(subscription_id):
    """Get subscription status endpoint (Story 4.3)"""
    try:
        # Get from in-memory storage or create default
        if subscription_id not in IN_MEMORY_SUBSCRIPTIONS:
            IN_MEMORY_SUBSCRIPTIONS[subscription_id] = {
                'subscription_id': subscription_id,
                'status': 'active',
                'cadence': 'monthly',
                'next_billing_date': '2026-07-23',
                'stripe_subscription_id': 'sub_test_123',
                'created_at': '2026-06-23T10:00:00Z'
            }
        
        ui_status = get_subscription_status_ui(IN_MEMORY_SUBSCRIPTIONS[subscription_id])
        ui_status['parser_version'] = SUBSCRIPTION_LIFECYCLE_VERSION
        
        return jsonify(ui_status), 200
        
    except Exception as e:
        logger.error(f"Subscription status fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch subscription status', 'parser_version': SUBSCRIPTION_LIFECYCLE_VERSION}), 500

@app.route('/api/subscriptions/<subscription_id>', methods=['PATCH'])
def update_subscription(subscription_id):
    """Update subscription (pause/resume/cancel) endpoint (Story 4.3)"""
    try:
        data = request.get_json(force=True)
        action = data.get('action', '')
        
        if action not in ['pause', 'resume', 'cancel']:
            return jsonify({'error': 'Invalid action', 'parser_version': SUBSCRIPTION_LIFECYCLE_VERSION}), 400
        
        # Get current subscription from in-memory storage or create default
        if subscription_id not in IN_MEMORY_SUBSCRIPTIONS:
            IN_MEMORY_SUBSCRIPTIONS[subscription_id] = {
                'subscription_id': subscription_id,
                'status': 'active',
                'cadence': 'monthly',
                'next_billing_date': '2026-07-23'
            }
        
        subscription = IN_MEMORY_SUBSCRIPTIONS[subscription_id]
        
        # Process action
        if action == 'pause':
            reason = data.get('reason', 'user_requested')
            result = pause_subscription(subscription, reason)
        elif action == 'resume':
            result = resume_subscription(subscription)
        elif action == 'cancel':
            feedback = data.get('feedback_reason')
            result = cancel_subscription(subscription, feedback)
        
        if 'error' in result:
            return jsonify({'error': result['error'], 'parser_version': SUBSCRIPTION_LIFECYCLE_VERSION}), 400
        
        # Update in-memory storage with new state
        IN_MEMORY_SUBSCRIPTIONS[subscription_id] = {**subscription, **result}
        
        result['parser_version'] = SUBSCRIPTION_LIFECYCLE_VERSION
        
        logger.info(f"Subscription {subscription_id} {action}ed")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Subscription update error: {str(e)}")
        return jsonify({'error': 'Failed to update subscription', 'parser_version': SUBSCRIPTION_LIFECYCLE_VERSION}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=False)
