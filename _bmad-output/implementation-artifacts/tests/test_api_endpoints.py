"""
Epic 4 API Test Suite - Comprehensive endpoint validation
Tests all user profile, preferences, order history, and subscription endpoints
"""

import pytest
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Tuple

# Test Configuration
BASE_URL = 'http://127.0.0.1:5000'
TEST_USER_EMAIL = 'test.user@blind-date-book.com'
TEST_USER_PASSWORD = 'SecurePassword123'
TEST_USER_NAME = 'Test User'

# Test Data
VALID_PREFERENCES = {
    'preferred_genres': ['Mystery', 'Thriller'],
    'mood_keywords': ['cozy', 'suspenseful'],
    'age_min': 25,
    'age_max': 65,
    'surprise_level': 'balanced',
    'recipient_type': 'self'
}

INVALID_PREFERENCES_AGE_REVERSED = {
    'preferred_genres': ['Mystery'],
    'mood_keywords': ['cozy'],
    'age_min': 65,
    'age_max': 25,  # Invalid: min > max
    'surprise_level': 'balanced'
}

AVOID_LIST_ENTRY = {
    'book_id': 'book-123',
    'reason': 'read'
}

# ============================================================================
# STORY 4.1: USER PROFILE, PREFERENCES & AVOID-LIST MANAGEMENT
# ============================================================================

class TestUserRegistration:
    """Test Story 4.1 - User Registration endpoint"""
    
    def test_register_new_user_success(self):
        """POST /api/users/register - Valid registration"""
        response = requests.post(
            f'{BASE_URL}/api/users/register',
            json={
                'name': TEST_USER_NAME,
                'email': TEST_USER_EMAIL,
                'password': TEST_USER_PASSWORD
            }
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert 'user_id' in data
        assert 'email' in data
        assert data['email'] == TEST_USER_EMAIL
        assert 'jwt_token' in data
        assert 'created_at' in data
        assert data['name'] == TEST_USER_NAME
        
        # Store for later tests
        pytest.user_id = data['user_id']
        pytest.jwt_token = data['jwt_token']
    
    def test_register_missing_email(self):
        """POST /api/users/register - Missing email field"""
        response = requests.post(
            f'{BASE_URL}/api/users/register',
            json={'name': 'Test', 'password': TEST_USER_PASSWORD}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_register_invalid_email_format(self):
        """POST /api/users/register - Invalid email format"""
        response = requests.post(
            f'{BASE_URL}/api/users/register',
            json={
                'name': 'Test',
                'email': 'not-an-email',
                'password': TEST_USER_PASSWORD
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_register_password_too_short(self):
        """POST /api/users/register - Password less than 8 characters"""
        response = requests.post(
            f'{BASE_URL}/api/users/register',
            json={
                'name': 'Test',
                'email': f'short-pwd-{datetime.now().timestamp()}@test.com',
                'password': 'short'
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data


class TestUserLogin:
    """Test Story 4.1 - User Login endpoint"""
    
    def test_login_success(self):
        """POST /api/users/login - Valid credentials"""
        # First register a user
        register_response = requests.post(
            f'{BASE_URL}/api/users/register',
            json={
                'name': 'Login Test User',
                'email': f'login-test-{datetime.now().timestamp()}@test.com',
                'password': TEST_USER_PASSWORD
            }
        )
        assert register_response.status_code == 201
        registered_email = register_response.json()['email']
        
        # Now login with those credentials
        response = requests.post(
            f'{BASE_URL}/api/users/login',
            json={'email': registered_email, 'password': TEST_USER_PASSWORD}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'user_id' in data
        assert 'jwt_token' in data
        assert data['email'] == registered_email
        
        pytest.login_token = data['jwt_token']
    
    def test_login_wrong_password(self):
        """POST /api/users/login - Wrong password"""
        response = requests.post(
            f'{BASE_URL}/api/users/login',
            json={
                'email': 'demo@blind-date-book.com',
                'password': 'WrongPassword123'
            }
        )
        
        assert response.status_code == 401


class TestUserPreferences:
    """Test Story 4.1 - User Preferences endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure user_id and jwt_token are available"""
        if not hasattr(pytest, 'user_id'):
            # Register a test user
            response = requests.post(
                f'{BASE_URL}/api/users/register',
                json={
                    'name': 'Preferences Test',
                    'email': f'pref-test-{datetime.now().timestamp()}@test.com',
                    'password': TEST_USER_PASSWORD
                }
            )
            pytest.user_id = response.json()['user_id']
            pytest.jwt_token = response.json()['jwt_token']
    
    def test_save_preferences_success(self):
        """POST /api/users/{user_id}/preferences - Valid preferences"""
        response = requests.post(
            f'{BASE_URL}/api/users/{pytest.user_id}/preferences',
            json=VALID_PREFERENCES
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data['user_id'] == pytest.user_id
        assert data['preferences']['preferred_genres'] == VALID_PREFERENCES['preferred_genres']
        assert data['preferences']['mood_keywords'] == VALID_PREFERENCES['mood_keywords']
        assert data['preferences']['age_min'] == VALID_PREFERENCES['age_min']
        assert data['preferences']['age_max'] == VALID_PREFERENCES['age_max']
        assert data['preferences']['surprise_level'] == 'balanced'
    
    def test_save_preferences_invalid_age_range(self):
        """POST /api/users/{user_id}/preferences - Age min > max"""
        response = requests.post(
            f'{BASE_URL}/api/users/{pytest.user_id}/preferences',
            json=INVALID_PREFERENCES_AGE_REVERSED
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_save_preferences_invalid_surprise_level(self):
        """POST /api/users/{user_id}/preferences - Invalid surprise level"""
        invalid_prefs = VALID_PREFERENCES.copy()
        invalid_prefs['surprise_level'] = 'extreme'  # Invalid enum
        
        response = requests.post(
            f'{BASE_URL}/api/users/{pytest.user_id}/preferences',
            json=invalid_prefs
        )
        
        assert response.status_code == 400
    
    def test_get_preferences_success(self):
        """GET /api/users/{user_id}/preferences - Retrieve saved preferences"""
        # First save preferences
        requests.post(
            f'{BASE_URL}/api/users/{pytest.user_id}/preferences',
            json=VALID_PREFERENCES
        )
        
        # Then retrieve
        response = requests.get(
            f'{BASE_URL}/api/users/{pytest.user_id}/preferences'
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['user_id'] == pytest.user_id
        assert data['preferred_genres'] == VALID_PREFERENCES['preferred_genres']
        assert data['mood_keywords'] == VALID_PREFERENCES['mood_keywords']
    
    def test_save_preferences_empty_genres(self):
        """POST /api/users/{user_id}/preferences - Empty genres array"""
        invalid_prefs = VALID_PREFERENCES.copy()
        invalid_prefs['preferred_genres'] = []
        
        response = requests.post(
            f'{BASE_URL}/api/users/{pytest.user_id}/preferences',
            json=invalid_prefs
        )
        
        # Should reject empty genres
        assert response.status_code == 400


class TestAvoidList:
    """Test Story 4.1 - Avoid-list endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure user_id is available"""
        if not hasattr(pytest, 'user_id'):
            response = requests.post(
                f'{BASE_URL}/api/users/register',
                json={
                    'name': 'AvoidList Test',
                    'email': f'avoid-test-{datetime.now().timestamp()}@test.com',
                    'password': TEST_USER_PASSWORD
                }
            )
            pytest.user_id = response.json()['user_id']
    
    def test_add_to_avoid_list_success(self):
        """POST /api/users/{user_id}/avoid-list - Add book"""
        response = requests.post(
            f'{BASE_URL}/api/users/{pytest.user_id}/avoid-list',
            json=AVOID_LIST_ENTRY
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data['user_id'] == pytest.user_id
        assert data['book_id'] == AVOID_LIST_ENTRY['book_id']
        assert data['reason'] == AVOID_LIST_ENTRY['reason']
        
        pytest.avoid_id = data.get('avoid_id')
    
    def test_add_to_avoid_list_invalid_reason(self):
        """POST /api/users/{user_id}/avoid-list - Invalid reason"""
        response = requests.post(
            f'{BASE_URL}/api/users/{pytest.user_id}/avoid-list',
            json={
                'book_id': 'book-456',
                'reason': 'invalid_reason'
            }
        )
        
        assert response.status_code == 400
    
    def test_get_avoid_list_success(self):
        """GET /api/users/{user_id}/avoid-list - Retrieve avoid-list"""
        # First add a book
        requests.post(
            f'{BASE_URL}/api/users/{pytest.user_id}/avoid-list',
            json=AVOID_LIST_ENTRY
        )
        
        # Then retrieve
        response = requests.get(
            f'{BASE_URL}/api/users/{pytest.user_id}/avoid-list'
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['user_id'] == pytest.user_id
        assert 'avoided_books' in data
        assert isinstance(data['avoided_books'], list)
        assert data['total'] >= 1
    
    def test_remove_from_avoid_list_success(self):
        """DELETE /api/users/{user_id}/avoid-list/{book_id} - Remove book"""
        # First add
        response = requests.post(
            f'{BASE_URL}/api/users/{pytest.user_id}/avoid-list',
            json=AVOID_LIST_ENTRY
        )
        
        # Then delete
        delete_response = requests.delete(
            f'{BASE_URL}/api/users/{pytest.user_id}/avoid-list/{AVOID_LIST_ENTRY["book_id"]}'
        )
        
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data['message'] is not None


# ============================================================================
# STORY 4.2: ORDER HISTORY TRACKING & DUPLICATE EXCLUSION
# ============================================================================

class TestOrderHistory:
    """Test Story 4.2 - Order History endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure user_id is available"""
        if not hasattr(pytest, 'user_id'):
            response = requests.post(
                f'{BASE_URL}/api/users/register',
                json={
                    'name': 'Order History Test',
                    'email': f'order-test-{datetime.now().timestamp()}@test.com',
                    'password': TEST_USER_PASSWORD
                }
            )
            pytest.user_id = response.json()['user_id']
    
    def test_get_orders_success(self):
        """GET /api/users/{user_id}/orders - Retrieve order history"""
        response = requests.get(
            f'{BASE_URL}/api/users/{pytest.user_id}/orders'
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'total' in data
        assert 'count' in data
        assert 'offset' in data
        assert 'limit' in data
        assert 'orders' in data
        assert isinstance(data['orders'], list)
    
    def test_get_orders_with_pagination(self):
        """GET /api/users/{user_id}/orders?limit=5&offset=0 - Pagination"""
        response = requests.get(
            f'{BASE_URL}/api/users/{pytest.user_id}/orders?limit=5&offset=0'
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['limit'] == 5
        assert data['offset'] == 0
        assert len(data['orders']) <= 5
    
    def test_get_orders_with_sorting(self):
        """GET /api/users/{user_id}/orders?sort=date&order=desc - Sorting"""
        response = requests.get(
            f'{BASE_URL}/api/users/{pytest.user_id}/orders?sort=date&order=desc'
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify orders are sorted by date descending
        if len(data['orders']) > 1:
            for i in range(len(data['orders']) - 1):
                current_date = datetime.fromisoformat(data['orders'][i]['created_at'].replace('Z', '+00:00'))
                next_date = datetime.fromisoformat(data['orders'][i+1]['created_at'].replace('Z', '+00:00'))
                assert current_date >= next_date, "Orders should be sorted descending by date"
    
    def test_get_orders_with_status_filter(self):
        """GET /api/users/{user_id}/orders?status=delivered - Filter by status"""
        response = requests.get(
            f'{BASE_URL}/api/users/{pytest.user_id}/orders?status=delivered'
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned orders should have 'delivered' status
        for order in data['orders']:
            assert order['delivery_status'] == 'delivered'
    
    def test_get_excluded_books_success(self):
        """GET /api/users/{user_id}/excluded-books - Retrieve unified exclude-list"""
        response = requests.get(
            f'{BASE_URL}/api/users/{pytest.user_id}/excluded-books'
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['user_id'] == pytest.user_id
        assert 'excluded_ids' in data
        assert isinstance(data['excluded_ids'], list)
        assert 'breakdown' in data
        assert 'total' in data
        
        # Verify breakdown contains expected categories
        breakdown = data['breakdown']
        assert 'delivered' in breakdown
        assert 'user_marked' in breakdown
    
    def test_excluded_books_deduplication(self):
        """Verify unified exclude-list removes duplicates (Story 4.2)"""
        # Add a book to avoid-list
        requests.post(
            f'{BASE_URL}/api/users/{pytest.user_id}/avoid-list',
            json={'book_id': 'book-duplicate-test', 'reason': 'read'}
        )
        
        # Get excluded books
        response = requests.get(
            f'{BASE_URL}/api/users/{pytest.user_id}/excluded-books'
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify no duplicates in excluded_ids
        excluded_ids = data['excluded_ids']
        assert len(excluded_ids) == len(set(excluded_ids)), "Exclude-list should have no duplicates"


# ============================================================================
# STORY 4.3: SUBSCRIPTION LIFECYCLE CONTROLS
# ============================================================================

class TestSubscriptionLifecycle:
    """Test Story 4.3 - Subscription endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a subscription for testing"""
        if not hasattr(pytest, 'subscription_id'):
            # Mock subscription ID for testing
            pytest.subscription_id = 'sub-test-123'
    
    def test_get_subscription_success(self):
        """GET /api/subscriptions/{subscription_id} - Retrieve subscription"""
        response = requests.get(
            f'{BASE_URL}/api/subscriptions/{pytest.subscription_id}'
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'subscription_id' in data
        assert 'status' in data
        assert data['status'] in ['active', 'paused', 'cancelled']
        assert 'cadence' in data
        assert data['cadence'] in ['monthly', 'bi-weekly', '3-month']
        assert 'next_shipment' in data
        assert 'available_actions' in data
        assert isinstance(data['available_actions'], list)
    
    def test_pause_subscription_success(self):
        """PATCH /api/subscriptions/{subscription_id} - Pause subscription"""
        response = requests.patch(
            f'{BASE_URL}/api/subscriptions/{pytest.subscription_id}',
            json={'action': 'pause', 'reason': 'reading_pace'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['subscription_id'] == pytest.subscription_id
        assert data['status'] == 'paused'
        assert 'paused_at' in data
    
    def test_resume_subscription_success(self):
        """PATCH /api/subscriptions/{subscription_id} - Resume subscription"""
        # First pause
        requests.patch(
            f'{BASE_URL}/api/subscriptions/{pytest.subscription_id}',
            json={'action': 'pause', 'reason': 'reading_pace'}
        )
        
        # Then resume
        response = requests.patch(
            f'{BASE_URL}/api/subscriptions/{pytest.subscription_id}',
            json={'action': 'resume'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'active'
        assert 'next_billing_date' in data
    
    def test_cancel_subscription_success(self):
        """PATCH /api/subscriptions/{subscription_id} - Cancel subscription"""
        response = requests.patch(
            f'{BASE_URL}/api/subscriptions/{pytest.subscription_id}',
            json={
                'action': 'cancel',
                'feedback_reason': 'too_expensive'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'cancelled'
        assert 'cancelled_at' in data
    
    def test_subscription_invalid_action(self):
        """PATCH /api/subscriptions/{subscription_id} - Invalid action"""
        response = requests.patch(
            f'{BASE_URL}/api/subscriptions/{pytest.subscription_id}',
            json={'action': 'invalid_action'}
        )
        
        assert response.status_code == 400


# ============================================================================
# STORY 4.2 INTEGRATION: DECISION ENGINE + EXCLUDE-LIST
# ============================================================================

class TestDecisionEngineIntegration:
    """Test Story 4.2 Integration - Decision engine with exclude-list"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create user and add to avoid-list"""
        if not hasattr(pytest, 'user_id'):
            response = requests.post(
                f'{BASE_URL}/api/users/register',
                json={
                    'name': 'Decision Engine Test',
                    'email': f'decision-test-{datetime.now().timestamp()}@test.com',
                    'password': TEST_USER_PASSWORD
                }
            )
            pytest.user_id = response.json()['user_id']
            
            # Add some books to avoid-list
            requests.post(
                f'{BASE_URL}/api/users/{pytest.user_id}/avoid-list',
                json={'book_id': 'book-001', 'reason': 'read'}
            )
            requests.post(
                f'{BASE_URL}/api/users/{pytest.user_id}/avoid-list',
                json={'book_id': 'book-002', 'reason': 'dislike'}
            )
    
    def test_decide_with_auto_exclude_list(self):
        """POST /api/ai/decide with user_id - Auto-fetch exclude-list"""
        response = requests.post(
            f'{BASE_URL}/api/ai/decide',
            json={
                'preferences': {
                    'recipient_age_range': '25-45',
                    'genres': ['Mystery', 'Thriller'],
                    'mood': 'cozy'
                },
                'user_id': pytest.user_id,
                'session_id': f'test-session-{datetime.now().timestamp()}'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'book_id' in data
        assert 'confidence' in data
        assert 'score' in data
        
        # Verify excluded books were considered (should not be in recommendation)
        recommended_book_id = data.get('book_id')
        assert recommended_book_id not in ['book-001', 'book-002'], \
            f"Recommendation should not include avoided books, got: {recommended_book_id}"
    
    def test_decide_logs_exclude_list_info(self):
        """Verify decision engine logs exclude-list information"""
        response = requests.post(
            f'{BASE_URL}/api/ai/decide',
            json={
                'preferences': {
                    'recipient_age_range': '25-45',
                    'genres': ['Mystery'],
                    'mood': 'cozy'
                },
                'user_id': pytest.user_id,
                'session_id': f'test-session-{datetime.now().timestamp()}'
            }
        )
        
        assert response.status_code == 200
        # Response should include excluded books count info
        data = response.json()
        # Check if logging included exclude_list count (in practice, check server logs)
        assert 'book_id' in data


# ============================================================================
# INTEGRATION TESTS - FULL USER JOURNEY
# ============================================================================

class TestFullUserJourney:
    """End-to-end user journey tests"""
    
    def test_complete_user_flow_register_to_recommendation(self):
        """Full flow: Register → Set Preferences → Get Recommendation → Add to Avoid"""
        test_email = f'e2e-flow-{datetime.now().timestamp()}@test.com'
        
        # Step 1: Register
        register_response = requests.post(
            f'{BASE_URL}/api/users/register',
            json={
                'name': 'E2E Test User',
                'email': test_email,
                'password': TEST_USER_PASSWORD
            }
        )
        assert register_response.status_code == 201
        user_id = register_response.json()['user_id']
        
        # Step 2: Set Preferences
        prefs_response = requests.post(
            f'{BASE_URL}/api/users/{user_id}/preferences',
            json=VALID_PREFERENCES
        )
        assert prefs_response.status_code == 201
        
        # Step 3: Get Recommendation with auto-exclude
        decision_response = requests.post(
            f'{BASE_URL}/api/ai/decide',
            json={
                'preferences': {
                    'recipient_age_range': f'{VALID_PREFERENCES["age_min"]}-{VALID_PREFERENCES["age_max"]}',
                    'genres': VALID_PREFERENCES['preferred_genres'],
                    'mood': VALID_PREFERENCES['mood_keywords'][0]
                },
                'user_id': user_id
            }
        )
        assert decision_response.status_code == 200
        recommendation = decision_response.json()
        recommended_book_id = recommendation['book_id']
        
        # Step 4: Add recommended book to avoid-list
        avoid_response = requests.post(
            f'{BASE_URL}/api/users/{user_id}/avoid-list',
            json={
                'book_id': recommended_book_id,
                'reason': 'read'
            }
        )
        assert avoid_response.status_code == 201
        
        # Step 5: Get another recommendation (should exclude the first one)
        second_decision_response = requests.post(
            f'{BASE_URL}/api/ai/decide',
            json={
                'preferences': {
                    'recipient_age_range': f'{VALID_PREFERENCES["age_min"]}-{VALID_PREFERENCES["age_max"]}',
                    'genres': VALID_PREFERENCES['preferred_genres'],
                    'mood': VALID_PREFERENCES['mood_keywords'][0]
                },
                'user_id': user_id
            }
        )
        assert second_decision_response.status_code == 200
        second_recommendation = second_decision_response.json()
        
        # Verify second recommendation is different
        assert second_recommendation['book_id'] != recommended_book_id, \
            "Second recommendation should exclude the first book"
    
    def test_subscription_lifecycle_flow(self):
        """Full flow: Get Subscription → Pause → Resume → Cancel"""
        subscription_id = 'sub-lifecycle-test-123'
        
        # Get subscription
        get_response = requests.get(
            f'{BASE_URL}/api/subscriptions/{subscription_id}'
        )
        assert get_response.status_code == 200
        initial_status = get_response.json()['status']
        
        # Pause
        pause_response = requests.patch(
            f'{BASE_URL}/api/subscriptions/{subscription_id}',
            json={'action': 'pause', 'reason': 'too_busy'}
        )
        assert pause_response.status_code == 200
        assert pause_response.json()['status'] == 'paused'
        
        # Resume
        resume_response = requests.patch(
            f'{BASE_URL}/api/subscriptions/{subscription_id}',
            json={'action': 'resume'}
        )
        assert resume_response.status_code == 200
        assert resume_response.json()['status'] == 'active'
        
        # Cancel
        cancel_response = requests.patch(
            f'{BASE_URL}/api/subscriptions/{subscription_id}',
            json={'action': 'cancel', 'feedback_reason': 'disappointed'}
        )
        assert cancel_response.status_code == 200
        assert cancel_response.json()['status'] == 'cancelled'


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
