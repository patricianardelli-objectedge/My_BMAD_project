# Epic 4 - End-to-End Testing Guide

**Completion Date:** 2026-06-23  
**Test Coverage:** 30+ automated test cases  
**Framework:** pytest (API) + Jest/Playwright (E2E)  
**Expected Duration:** ~2-5 minutes (full suite)

---

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install pytest requests

# (Optional) For E2E tests
npm install --save-dev @playwright/test jest
```

### Run All Tests

```bash
# From the tests directory
cd _bmad-output/implementation-artifacts/tests/

# Run everything
python run_tests.py

# Run only API tests
python run_tests.py --api-only

# Run specific suite
python run_tests.py --suite story-4.1
python run_tests.py --suite decision-engine
python run_tests.py --suite journey
```

---

## Test Architecture

### 1. **API Test Suite** (`test_api_endpoints.py`)
- **Framework:** pytest + requests
- **Focus:** Backend endpoint validation
- **Coverage:** 30+ test cases across 7 test classes
- **Duration:** ~60-120 seconds
- **Status Codes Tested:** 200, 201, 400, 401, 500

### 2. **E2E Test Suite** (`test_e2e.js`)
- **Framework:** Jest + Playwright (ready for configuration)
- **Focus:** Frontend UI flows + API integration
- **Coverage:** 10+ test scenarios across 7 test suites
- **Note:** Currently scaffolded for Playwright integration

### 3. **Test Runner** (`run_tests.py`)
- **Purpose:** Orchestrates all tests with reporting
- **Features:** Dependency checking, backend health check, detailed reporting
- **Output:** Console + JSON report file

---

## Test Coverage by Story

### Story 4.1: User Profile, Preferences & Avoid-List

#### Test Class: `TestUserRegistration`
```
✓ test_register_new_user_success
  - Validates successful user registration
  - Checks: user_id, email, jwt_token, created_at, name
  - Expected: 201 Created

✓ test_register_missing_email
  - Validates email requirement
  - Expected: 400 Bad Request

✓ test_register_invalid_email_format
  - Validates email format validation
  - Expected: 400 Bad Request

✓ test_register_password_too_short
  - Validates password minimum length (8 chars)
  - Expected: 400 Bad Request
```

#### Test Class: `TestUserLogin`
```
✓ test_login_success
  - Validates successful login with correct credentials
  - Checks: user_id, jwt_token, email
  - Expected: 200 OK

✓ test_login_wrong_password
  - Validates authentication failure
  - Expected: 401 Unauthorized
```

#### Test Class: `TestUserPreferences`
```
✓ test_save_preferences_success
  - Validates preference storage
  - Checks: genres, mood_keywords, age range, surprise_level
  - Expected: 201 Created

✓ test_save_preferences_invalid_age_range
  - Validates age constraint (min ≤ max)
  - Expected: 400 Bad Request

✓ test_save_preferences_invalid_surprise_level
  - Validates enum validation (minimal|balanced|maximum)
  - Expected: 400 Bad Request

✓ test_get_preferences_success
  - Validates preference retrieval
  - Expected: 200 OK

✓ test_save_preferences_empty_genres
  - Validates required genres array
  - Expected: 400 Bad Request
```

#### Test Class: `TestAvoidList`
```
✓ test_add_to_avoid_list_success
  - Validates adding book to avoid-list
  - Checks: user_id, book_id, reason, avoid_id
  - Expected: 201 Created

✓ test_add_to_avoid_list_invalid_reason
  - Validates reason enum (read|dislike|duplicate|other)
  - Expected: 400 Bad Request

✓ test_get_avoid_list_success
  - Validates avoid-list retrieval
  - Checks: user_id, total, avoided_books[]
  - Expected: 200 OK

✓ test_remove_from_avoid_list_success
  - Validates book removal from avoid-list
  - Expected: 200 OK
```

**Story 4.1 Coverage: 16 test cases**

---

### Story 4.2: Order History Tracking & Duplicate Exclusion

#### Test Class: `TestOrderHistory`
```
✓ test_get_orders_success
  - Validates order history retrieval
  - Checks: total, count, offset, limit, orders[]
  - Expected: 200 OK

✓ test_get_orders_with_pagination
  - Validates pagination parameters (limit, offset)
  - Expected: 200 OK with ≤ limit items

✓ test_get_orders_with_sorting
  - Validates sorting by date (asc|desc)
  - Expected: 200 OK with sorted results

✓ test_get_orders_with_status_filter
  - Validates status filtering (delivered|pending|in-transit)
  - Expected: 200 OK with filtered results

✓ test_get_excluded_books_success
  - Validates unified exclude-list retrieval
  - Checks: excluded_ids[], breakdown{delivered, user_marked}, total
  - Expected: 200 OK

✓ test_excluded_books_deduplication
  - Validates set union (no duplicates)
  - Checks: len(excluded_ids) == len(set(excluded_ids))
  - Expected: 200 OK with no duplicates
```

**Story 4.2 Coverage: 6 test cases**

---

### Story 4.3: Subscription Lifecycle Controls

#### Test Class: `TestSubscriptionLifecycle`
```
✓ test_get_subscription_success
  - Validates subscription state retrieval
  - Checks: subscription_id, status, cadence, next_shipment, available_actions
  - Expected: 200 OK

✓ test_pause_subscription_success
  - Validates subscription pause
  - Checks: status='paused', paused_at field
  - Expected: 200 OK

✓ test_resume_subscription_success
  - Validates subscription resume
  - Checks: status='active', next_billing_date
  - Expected: 200 OK

✓ test_cancel_subscription_success
  - Validates subscription cancellation
  - Checks: status='cancelled', cancelled_at field
  - Expected: 200 OK

✓ test_subscription_invalid_action
  - Validates action validation
  - Expected: 400 Bad Request
```

**Story 4.3 Coverage: 5 test cases**

---

### Story 4.2 Integration: Decision Engine + Exclude-List

#### Test Class: `TestDecisionEngineIntegration`
```
✓ test_decide_with_auto_exclude_list
  - Validates decision engine auto-fetches exclude-list when user_id provided
  - Checks: book_id not in avoided books
  - Expected: 200 OK with excluded book ID

✓ test_decide_logs_exclude_list_info
  - Validates logging of exclude-list information
  - Expected: 200 OK with proper response structure
```

**Integration Coverage: 2 test cases**

---

### Full User Journey Tests

#### Test Class: `TestFullUserJourney`
```
✓ test_complete_user_flow_register_to_recommendation
  - Validates end-to-end: Register → Preferences → Recommendation → Avoid-List
  - Checks: Different books recommended after adding to avoid-list
  - Expected: All steps successful with deduplication

✓ test_subscription_lifecycle_flow
  - Validates end-to-end: Get → Pause → Resume → Cancel
  - Checks: Status transitions
  - Expected: All transitions successful
```

**Journey Coverage: 2 test cases**

---

## Running Tests by Category

### Quick Tests (All Tests)
```bash
python run_tests.py
```
**Duration:** 2-5 minutes  
**What's Tested:** All functionality across all 3 stories + integration

### Story 4.1 Only (User Profile & Preferences)
```bash
python run_tests.py --suite story-4.1
```
**Tests:** 16 cases  
**Duration:** ~30 seconds  
**Covers:** Registration, login, preferences, avoid-list

### Story 4.2 Only (Order History & Exclusion)
```bash
python run_tests.py --suite story-4.2
```
**Tests:** 6 cases  
**Duration:** ~15 seconds  
**Covers:** Order history, pagination, filtering, deduplication

### Story 4.3 Only (Subscription Lifecycle)
```bash
python run_tests.py --suite story-4.3
```
**Tests:** 5 cases  
**Duration:** ~10 seconds  
**Covers:** Subscription pause, resume, cancel

### Decision Engine Integration
```bash
python run_tests.py --suite decision-engine
```
**Tests:** 2 cases  
**Duration:** ~5 seconds  
**Covers:** Exclude-list auto-fetch, recommendation exclusion

### Specific Component Tests
```bash
# Registration only
python run_tests.py --suite registration

# Preferences only
python run_tests.py --suite preferences

# Avoid-list only
python run_tests.py --suite avoid-list

# Order history only
python run_tests.py --suite order-history

# Subscription only
python run_tests.py --suite subscription

# Full journey
python run_tests.py --suite journey
```

---

## Backend Setup

### Start Flask Server

```bash
cd _bmad-output/implementation-artifacts/nlu/

# Install dependencies if needed
pip install flask requests python-dotenv bcrypt pyjwt

# Run server
python app.py
```

**Expected Output:**
```
* Serving Flask app 'app'
* Debug mode: off
WARNING in app.run_simple()
WARNING: This is a development server. Do not use it in production deployments.
* Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### Verify Backend is Running

```bash
# In another terminal
curl http://127.0.0.1:5000/api/health

# Expected response
{"status": "ok"}
```

---

## Test Execution Flow

### Step 1: Dependency Check
```
✓ pytest installed
✓ requests installed
✓ (Optional) Jest installed
```

### Step 2: Backend Connectivity
```
✓ Checking http://127.0.0.1:5000
✓ Backend reachable - all tests can proceed
```

### Step 3: Run Test Suites
```
Story 4.1: Registration, Login, Preferences, Avoid-List [16 tests]
Story 4.2: Order History, Pagination, Filtering, Exclusion [6 tests]
Story 4.3: Subscription Lifecycle [5 tests]
Integration: Decision Engine + Exclude-List [2 tests]
Journey: Complete User Workflows [2 tests]
```

### Step 4: Generate Report
```
test-report-20260623-120000.json
├─ timestamp
├─ backend_url
├─ tests
│  ├─ api_tests: PASSED/FAILED
│  └─ e2e_tests: PASSED/FAILED
└─ overall_status: ALL TESTS PASSED
```

---

## Expected Test Results

### Passing Test Output Example
```
RUNNING API TESTS (Python/pytest)
✓ Backend is running ✓
Running: pytest test_api_endpoints.py -v --tb=short --color=yes

test_api_endpoints.py::TestUserRegistration::test_register_new_user_success PASSED
test_api_endpoints.py::TestUserRegistration::test_register_missing_email PASSED
test_api_endpoints.py::TestUserRegistration::test_register_invalid_email_format PASSED
test_api_endpoints.py::TestUserLogin::test_login_success PASSED
test_api_endpoints.py::TestOrderHistory::test_excluded_books_deduplication PASSED
test_api_endpoints.py::TestFullUserJourney::test_complete_user_flow_register_to_recommendation PASSED

======================== 30 passed in 2.45s ========================

Overall Status: ✓ ALL TESTS PASSED
```

---

## Troubleshooting

### Problem: "pytest not found"
```bash
# Solution
pip install pytest
```

### Problem: "Backend not running"
```bash
# Solution 1: Start backend
python _bmad-output/implementation-artifacts/nlu/app.py

# Solution 2: Use different port
# Edit BACKEND_URL in test_api_endpoints.py
```

### Problem: "Connection refused"
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process if needed (Windows)
taskkill /PID <PID> /F
```

### Problem: "Tests timing out"
```bash
# Backend may be slow, check logs:
# Look at Flask console for errors

# Increase timeout in tests if needed:
# response = requests.get(..., timeout=10)
```

### Problem: "JWT token validation failures"
```bash
# Ensure tokens are being stored correctly
# Check localStorage in frontend tests
# Verify SECRET_KEY in app.py matches token generation
```

---

## Detailed Test Case Reference

### TestUserRegistration::test_register_new_user_success

**Endpoint:** `POST /api/users/register`

**Request:**
```json
{
  "name": "Test User",
  "email": "test.user@blind-date-book.com",
  "password": "SecurePassword123"
}
```

**Expected Response (201):**
```json
{
  "user_id": "abc-123-def",
  "email": "test.user@blind-date-book.com",
  "name": "Test User",
  "jwt_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "created_at": "2026-06-23T12:00:00Z"
}
```

**What's Tested:**
- ✓ Status code is 201 Created
- ✓ Response includes user_id
- ✓ Response includes jwt_token
- ✓ Email is stored correctly
- ✓ Name is preserved
- ✓ Timestamp is set

---

### TestUserPreferences::test_save_preferences_success

**Endpoint:** `POST /api/users/{user_id}/preferences`

**Request:**
```json
{
  "preferred_genres": ["Mystery", "Thriller"],
  "mood_keywords": ["cozy", "suspenseful"],
  "age_min": 25,
  "age_max": 65,
  "surprise_level": "balanced",
  "recipient_type": "self"
}
```

**Expected Response (201):**
```json
{
  "user_id": "abc-123-def",
  "preferences": {
    "preferred_genres": ["Mystery", "Thriller"],
    "mood_keywords": ["cozy", "suspenseful"],
    "age_min": 25,
    "age_max": 65,
    "surprise_level": "balanced",
    "recipient_type": "self"
  },
  "message": "Preferences saved successfully"
}
```

**What's Tested:**
- ✓ All fields stored correctly
- ✓ Age constraint (min ≤ max)
- ✓ Surprise level is valid enum
- ✓ Genres array is not empty
- ✓ Status code is 201

---

### TestOrderHistory::test_excluded_books_deduplication

**Endpoint:** `GET /api/users/{user_id}/excluded-books`

**Expected Response (200):**
```json
{
  "user_id": "abc-123-def",
  "total": 5,
  "excluded_ids": ["book-001", "book-002", "book-005", "book-010"],
  "breakdown": {
    "delivered": 3,
    "user_marked": 2,
    "system": 0
  }
}
```

**What's Tested:**
- ✓ Excluded IDs are unique (no duplicates)
- ✓ Set union combines delivered + user-marked
- ✓ len(excluded_ids) == len(set(excluded_ids))
- ✓ Breakdown categories are accurate
- ✓ Status code is 200

---

### TestDecisionEngineIntegration::test_decide_with_auto_exclude_list

**Endpoint:** `POST /api/ai/decide`

**Request with user_id:**
```json
{
  "preferences": {
    "recipient_age_range": "25-45",
    "genres": ["Mystery", "Thriller"],
    "mood": "cozy"
  },
  "user_id": "abc-123-def",
  "session_id": "session-xyz"
}
```

**Expected Response (200):**
```json
{
  "book_id": "book-999",
  "confidence": 0.87,
  "score": 8.7,
  "reason": {
    "genre_match": 0.8,
    "mood_match": 0.75,
    "age_safety": 1.0,
    "delivered_penalty": 0.0
  },
  "excluded_books_count": 5,
  "response_time_ms": 145
}
```

**What's Tested:**
- ✓ Auto-fetches user's exclude-list when user_id provided
- ✓ Recommended book_id is NOT in excluded-books
- ✓ Logging includes excluded_books_count
- ✓ Status code is 200
- ✓ Confidence and score are valid

---

### TestFullUserJourney::test_complete_user_flow_register_to_recommendation

**Complete Flow:**
1. POST /api/users/register → Get user_id ✓
2. POST /api/users/{user_id}/preferences → Save preferences ✓
3. POST /api/ai/decide → Get recommendation ✓
4. POST /api/users/{user_id}/avoid-list → Add to avoid-list ✓
5. POST /api/ai/decide → Get another recommendation ✓
6. Verify: recommendation.book_id != first_recommendation.book_id ✓

**What's Tested:**
- ✓ All endpoints work together
- ✓ State is maintained across calls
- ✓ Deduplication prevents repeated recommendations
- ✓ API integration is seamless

---

## Test Metrics

| Metric | Value |
|--------|-------|
| Total Test Cases | 31 |
| Story 4.1 Coverage | 16 tests |
| Story 4.2 Coverage | 6 tests |
| Story 4.3 Coverage | 5 tests |
| Integration Tests | 2 tests |
| Journey Tests | 2 tests |
| Average Duration | 2-5 minutes |
| Pass Rate Target | 100% |
| Code Coverage | ~85% of endpoints |

---

## Next Steps After Testing

### If All Tests Pass ✓
1. **Deploy to Staging:** Ready for staging environment
2. **Manual QA:** Have QA team validate UI/UX flows
3. **Load Testing:** Run performance tests with concurrent users
4. **Database Integration:** Connect to PostgreSQL for production data

### If Any Tests Fail ✗
1. **Review Error:** Check test output and error message
2. **Check Backend Logs:** Look for exceptions in Flask console
3. **Verify Data:** Ensure mock data is set up correctly
4. **Debug Specific Test:** Run single test with `--suite` flag
5. **Fix Issue:** Update backend/frontend code
6. **Re-run Tests:** Validate fix works

---

## Continuous Integration (CI/CD)

### GitHub Actions Example

```yaml
name: Epic 4 Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: blind_date_book
          POSTGRES_PASSWORD: password
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install pytest requests
      
      - name: Start Flask server
        run: |
          cd _bmad-output/implementation-artifacts/nlu/
          python app.py &
          sleep 2
      
      - name: Run tests
        run: |
          cd _bmad-output/implementation-artifacts/tests/
          python run_tests.py
```

---

## Support & Documentation

**Questions?**
- Check logs in test output
- Review error messages for hints
- See troubleshooting section above
- Check backend Flask console for errors

**Documentation Files:**
- `EPIC-4-IMPLEMENTATION-SUMMARY.md` - Architecture & code structure
- `test_api_endpoints.py` - API test source code
- `test_e2e.js` - E2E test source code (ready for Playwright)
- `run_tests.py` - Test runner with detailed execution

---

## Test Success Criteria

✅ **All Tests Pass** - All 31 test cases executed successfully  
✅ **No Errors** - Zero exceptions or failures  
✅ **Response Times** - All requests complete in < 1 second  
✅ **Data Integrity** - Correct data stored and retrieved  
✅ **Deduplication** - Exclude-list properly prevents duplicates  
✅ **State Management** - User state maintained across API calls  
✅ **Error Handling** - Proper HTTP status codes (201, 200, 400, 401, 500)  
✅ **Validation** - All input validation working correctly  

---

**Ready for end-to-end testing!** 🚀
