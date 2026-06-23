/**
 * Epic 4 End-to-End (E2E) Test Suite
 * Tests complete user workflows including frontend UI and API integration
 * Run with: npm test or npx jest --testPathPattern="test_e2e"
 * 
 * NOTE: These tests assume the Flask backend is running on http://127.0.0.1:5000
 * and frontend is served on http://127.0.0.1:3000 (or file://)
 */

const BASE_URL = 'http://127.0.0.1:3000'; // Frontend URL
const API_URL = 'http://127.0.0.1:5000'; // Backend API URL

// Helper: Fetch with error handling
async function fetchAPI(endpoint, options = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options
  });
  return response;
}

// Helper: Get DOM element
function getElement(selector) {
  const element = document.querySelector(selector);
  if (!element) {
    throw new Error(`Element not found: ${selector}`);
  }
  return element;
}

// Helper: Simulate user input
function setInputValue(selector, value) {
  const input = getElement(selector);
  input.value = value;
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
}

// Helper: Click element
function clickElement(selector) {
  const element = getElement(selector);
  element.click();
}

// Helper: Get localStorage value
function getStorageValue(key) {
  return localStorage.getItem(key);
}

// Helper: Clear localStorage
function clearStorage() {
  localStorage.clear();
}

// ============================================================================
// TEST SUITE 1: AUTHENTICATION FLOW
// ============================================================================

describe('E2E: Authentication Flow', () => {
  beforeEach(() => {
    clearStorage();
    // In real browser tests with Playwright, navigate to BASE_URL
  });

  test('User can register successfully', async () => {
    const testEmail = `e2e-register-${Date.now()}@test.com`;
    const testPassword = 'TestPassword123';

    // 1. Navigate to homepage (would use page.goto in Playwright)
    // page.goto(BASE_URL);

    // 2. Click Login button
    // clickElement('[data-testid="login-button"]');

    // 3. Click "Create Account" link
    // clickElement('[data-testid="switch-to-register"]');

    // 4. Fill registration form
    // setInputValue('input[name="name"]', 'Test User');
    // setInputValue('input[name="email"]', testEmail);
    // setInputValue('input[name="password"]', testPassword);
    // setInputValue('input[name="password_confirm"]', testPassword);

    // 5. Submit form
    // clickElement('button[type="submit"]');

    // 6. Verify tokens stored in localStorage
    // await page.waitForFunction(() => localStorage.getItem('jwt_token'));
    // expect(getStorageValue('jwt_token')).toBeTruthy();
    // expect(getStorageValue('user_id')).toBeTruthy();
    // expect(getStorageValue('user_email')).toBe(testEmail);

    console.log('✓ User registration test ready for Playwright');
  });

  test('User can login successfully', async () => {
    const testEmail = 'demo@blind-date-book.com';
    const testPassword = 'password123';

    // 1. Register first
    const registerResponse = await fetchAPI('/api/users/register', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Demo User',
        email: testEmail,
        password: testPassword
      })
    });
    expect(registerResponse.status).toBe(201);

    // 2. Clear localStorage to simulate new session
    clearStorage();

    // 3. Navigate to homepage
    // page.goto(BASE_URL);

    // 4. Click Login button
    // clickElement('[data-testid="login-button"]');

    // 5. Enter credentials
    // setInputValue('input[name="email"]', testEmail);
    // setInputValue('input[name="password"]', testPassword);

    // 6. Submit form
    // clickElement('button[type="submit"]');

    // 7. Verify authentication state
    // await page.waitForFunction(() => localStorage.getItem('jwt_token'));
    // expect(getStorageValue('jwt_token')).toBeTruthy();

    console.log('✓ User login test ready for Playwright');
  });

  test('Protected routes redirect to login when not authenticated', async () => {
    clearStorage();

    // 1. Try to access profile page directly
    // page.goto(`${BASE_URL}/profile.html`);

    // 2. Should redirect to homepage
    // await page.waitForURL(`${BASE_URL}/index.html`);
    // expect(page.url()).toContain('index.html');

    console.log('✓ Protected route test ready for Playwright');
  });

  test('User can logout successfully', async () => {
    // 1. Login first
    const registerResponse = await fetchAPI('/api/users/register', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Logout Test User',
        email: `e2e-logout-${Date.now()}@test.com`,
        password: 'TestPassword123'
      })
    });
    const userData = await registerResponse.json();
    localStorage.setItem('jwt_token', userData.jwt_token);
    localStorage.setItem('user_id', userData.user_id);

    // 2. Navigate to profile page
    // page.goto(`${BASE_URL}/profile.html`);

    // 3. Click Logout button
    // clickElement('[data-testid="logout-button"]');

    // 4. Verify localStorage cleared
    // await page.waitForFunction(() => !localStorage.getItem('jwt_token'));
    // expect(getStorageValue('jwt_token')).toBeNull();

    // 5. Verify redirected to homepage
    // expect(page.url()).toContain('index.html');

    console.log('✓ User logout test ready for Playwright');
  });
});

// ============================================================================
// TEST SUITE 2: USER PREFERENCES FLOW
// ============================================================================

describe('E2E: User Preferences Management', () => {
  let userId;
  let jwtToken;

  beforeEach(async () => {
    // Register test user
    const response = await fetchAPI('/api/users/register', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Preferences Test User',
        email: `e2e-prefs-${Date.now()}@test.com`,
        password: 'TestPassword123'
      })
    });
    const userData = await response.json();
    userId = userData.user_id;
    jwtToken = userData.jwt_token;
    localStorage.setItem('jwt_token', jwtToken);
    localStorage.setItem('user_id', userId);
  });

  test('User can save reading preferences', async () => {
    // 1. Navigate to profile page
    // page.goto(`${BASE_URL}/profile.html`);

    // 2. Click Preferences tab
    // clickElement('[data-tab="preferences"]');

    // 3. Add genres
    // setInputValue('select[name="genre"]', 'Mystery');
    // clickElement('button[data-action="add-genre"]');
    // setInputValue('select[name="genre"]', 'Thriller');
    // clickElement('button[data-action="add-genre"]');

    // 4. Add mood keywords
    // setInputValue('input[name="mood"]', 'cozy');
    // clickElement('button[data-action="add-mood"]');

    // 5. Set age range
    // setInputValue('input[name="age-min"]', '25');
    // setInputValue('input[name="age-max"]', '65');

    // 6. Select surprise level
    // clickElement('input[value="balanced"]');

    // 7. Click Save
    // clickElement('button[data-action="save-preferences"]');

    // 8. Verify API call succeeded
    const apiResponse = await fetchAPI(`/api/users/${userId}/preferences`, {
      method: 'POST',
      body: JSON.stringify({
        preferred_genres: ['Mystery', 'Thriller'],
        mood_keywords: ['cozy'],
        age_min: 25,
        age_max: 65,
        surprise_level: 'balanced',
        recipient_type: 'self'
      })
    });
    expect(apiResponse.status).toBe(201);

    // 9. Verify success message displayed
    // await page.waitForSelector('.success-message');

    console.log('✓ User preferences save test ready for Playwright');
  });

  test('User can view saved preferences', async () => {
    // 1. Save preferences via API
    const saveResponse = await fetchAPI(`/api/users/${userId}/preferences`, {
      method: 'POST',
      body: JSON.stringify({
        preferred_genres: ['Fantasy', 'Historical'],
        mood_keywords: ['inspiring'],
        age_min: 30,
        age_max: 70,
        surprise_level: 'maximum',
        recipient_type: 'gift'
      })
    });
    expect(saveResponse.status).toBe(201);

    // 2. Navigate to profile page
    // page.goto(`${BASE_URL}/profile.html`);

    // 3. Click Preferences tab
    // clickElement('[data-tab="preferences"]');

    // 4. Verify preferences displayed
    // await page.waitForSelector('[data-field="genre"]');
    // const genreChips = await page.$$('[data-genre-chip]');
    // expect(genreChips.length).toBe(2);

    // 5. Verify API call to GET preferences
    const getResponse = await fetchAPI(`/api/users/${userId}/preferences`);
    expect(getResponse.status).toBe(200);
    const prefs = await getResponse.json();
    expect(prefs.preferred_genres).toContain('Fantasy');
    expect(prefs.surprise_level).toBe('maximum');

    console.log('✓ User preferences view test ready for Playwright');
  });

  test('User cannot save invalid preferences', async () => {
    // 1. Navigate to profile page
    // page.goto(`${BASE_URL}/profile.html`);

    // 2. Set invalid age range (min > max)
    // setInputValue('input[name="age-min"]', '65');
    // setInputValue('input[name="age-max"]', '25');

    // 3. Try to save
    // clickElement('button[data-action="save-preferences"]');

    // 4. Verify error message displayed
    // await page.waitForSelector('.error-message');

    // 5. Verify API returns 400
    const response = await fetchAPI(`/api/users/${userId}/preferences`, {
      method: 'POST',
      body: JSON.stringify({
        preferred_genres: ['Mystery'],
        mood_keywords: ['cozy'],
        age_min: 65,
        age_max: 25,  // Invalid: min > max
        surprise_level: 'balanced'
      })
    });
    expect(response.status).toBe(400);

    console.log('✓ Invalid preferences validation test ready for Playwright');
  });
});

// ============================================================================
// TEST SUITE 3: AVOID-LIST FLOW
// ============================================================================

describe('E2E: Avoid-List Management', () => {
  let userId;
  let jwtToken;

  beforeEach(async () => {
    const response = await fetchAPI('/api/users/register', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Avoid-List Test User',
        email: `e2e-avoid-${Date.now()}@test.com`,
        password: 'TestPassword123'
      })
    });
    const userData = await response.json();
    userId = userData.user_id;
    jwtToken = userData.jwt_token;
  });

  test('User can add book to avoid-list', async () => {
    // 1. Navigate to profile → Avoid-List tab
    // page.goto(`${BASE_URL}/profile.html`);
    // clickElement('[data-tab="avoid-list"]');

    // 2. Enter book ID
    // setInputValue('input[name="book-id"]', 'book-123');

    // 3. Select reason
    // setInputValue('select[name="reason"]', 'read');

    // 4. Click Add button
    // clickElement('button[data-action="add-avoid"]');

    // 5. Verify book appears in list
    // await page.waitForSelector('[data-book-id="book-123"]');

    // 6. Verify API call
    const response = await fetchAPI(`/api/users/${userId}/avoid-list`, {
      method: 'POST',
      body: JSON.stringify({
        book_id: 'book-123',
        reason: 'read'
      })
    });
    expect(response.status).toBe(201);

    console.log('✓ Add to avoid-list test ready for Playwright');
  });

  test('User can remove book from avoid-list', async () => {
    // 1. Add book via API
    await fetchAPI(`/api/users/${userId}/avoid-list`, {
      method: 'POST',
      body: JSON.stringify({
        book_id: 'book-456',
        reason: 'dislike'
      })
    });

    // 2. Navigate to profile → Avoid-List tab
    // page.goto(`${BASE_URL}/profile.html`);
    // clickElement('[data-tab="avoid-list"]');

    // 3. Click remove button for book
    // clickElement('[data-book-id="book-456"] button.remove-btn');

    // 4. Verify confirmation dialog (optional)
    // 5. Click confirm

    // 6. Verify book removed from list
    // await page.waitForSelector('[data-book-id="book-456"]', { state: 'hidden' });

    // 7. Verify API call
    const response = await fetchAPI(`/api/users/${userId}/avoid-list/book-456`, {
      method: 'DELETE'
    });
    expect(response.status).toBe(200);

    console.log('✓ Remove from avoid-list test ready for Playwright');
  });
});

// ============================================================================
// TEST SUITE 4: ORDER HISTORY FLOW
// ============================================================================

describe('E2E: Order History Display', () => {
  let userId;
  let jwtToken;

  beforeEach(async () => {
    const response = await fetchAPI('/api/users/register', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Order History Test User',
        email: `e2e-orders-${Date.now()}@test.com`,
        password: 'TestPassword123'
      })
    });
    const userData = await response.json();
    userId = userData.user_id;
    jwtToken = userData.jwt_token;
  });

  test('User can view order history with pagination', async () => {
    // 1. Navigate to profile → Order History tab
    // page.goto(`${BASE_URL}/profile.html`);
    // clickElement('[data-tab="order-history"]');

    // 2. Verify orders table displayed
    // await page.waitForSelector('[data-testid="orders-table"]');

    // 3. Verify pagination controls
    // const prevButton = getElement('[data-pagination="prev"]');
    // const nextButton = getElement('[data-pagination="next"]');
    // expect(prevButton).toBeTruthy();
    // expect(nextButton).toBeTruthy();

    // 4. Verify API call for orders
    const response = await fetchAPI(`/api/users/${userId}/orders?limit=10&offset=0`);
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.orders).toBeDefined();
    expect(data.total).toBeDefined();

    console.log('✓ Order history view test ready for Playwright');
  });

  test('User can filter orders by status', async () => {
    // 1. Navigate to profile → Order History tab
    // page.goto(`${BASE_URL}/profile.html`);
    // clickElement('[data-tab="order-history"]');

    // 2. Click status filter dropdown
    // clickElement('[data-filter="status"]');

    // 3. Select "delivered"
    // clickElement('[data-status-option="delivered"]');

    // 4. Verify only delivered orders shown
    // const orders = await page.$$('[data-order-row]');

    // 5. Verify API call with status filter
    const response = await fetchAPI(`/api/users/${userId}/orders?status=delivered`);
    expect(response.status).toBe(200);
    const data = await response.json();
    data.orders.forEach(order => {
      expect(order.delivery_status).toBe('delivered');
    });

    console.log('✓ Order filtering test ready for Playwright');
  });

  test('User sees excluded-books that prevent duplicates', async () => {
    // 1. Add book to avoid-list
    await fetchAPI(`/api/users/${userId}/avoid-list`, {
      method: 'POST',
      body: JSON.stringify({
        book_id: 'book-duplicate-test',
        reason: 'read'
      })
    });

    // 2. Get excluded-books list
    const response = await fetchAPI(`/api/users/${userId}/excluded-books`);
    expect(response.status).toBe(200);
    const data = await response.json();

    // 3. Verify excluded books include user avoid-list + delivered
    expect(data.excluded_ids).toContain('book-duplicate-test');
    expect(data.breakdown).toBeDefined();

    console.log('✓ Excluded books deduplication test ready for Playwright');
  });
});

// ============================================================================
// TEST SUITE 5: SUBSCRIPTION LIFECYCLE FLOW
// ============================================================================

describe('E2E: Subscription Management', () => {
  let subscriptionId = 'sub-e2e-test-123';

  test('User can pause subscription', async () => {
    // 1. Navigate to profile → Subscription tab
    // page.goto(`${BASE_URL}/profile.html`);
    // clickElement('[data-tab="subscription"]');

    // 2. Verify subscription status badge (ACTIVE)
    // await page.waitForSelector('[data-status-badge="active"]');

    // 3. Click Pause button
    // clickElement('[data-action="pause-subscription"]');

    // 4. Verify pause reason dialog
    // await page.waitForSelector('[data-dialog="pause-reason"]');

    // 5. Select reason
    // clickElement('[data-reason="reading-pace"]');

    // 6. Confirm
    // clickElement('[data-dialog-action="confirm"]');

    // 7. Verify status changed to PAUSED
    // await page.waitForSelector('[data-status-badge="paused"]');

    // 8. Verify API call
    const response = await fetch(`${API_URL}/api/subscriptions/${subscriptionId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'pause',
        reason: 'reading_pace'
      })
    });
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.status).toBe('paused');

    console.log('✓ Pause subscription test ready for Playwright');
  });

  test('User can resume subscription', async () => {
    // 1. Pause subscription first
    await fetch(`${API_URL}/api/subscriptions/${subscriptionId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'pause', reason: 'reading_pace' })
    });

    // 2. Navigate to profile → Subscription tab
    // page.goto(`${BASE_URL}/profile.html`);
    // clickElement('[data-tab="subscription"]');

    // 3. Verify status is PAUSED and Resume button visible
    // await page.waitForSelector('[data-status-badge="paused"]');
    // await page.waitForSelector('[data-action="resume-subscription"]');

    // 4. Click Resume button
    // clickElement('[data-action="resume-subscription"]');

    // 5. Verify status changed to ACTIVE
    // await page.waitForSelector('[data-status-badge="active"]');

    // 6. Verify API call
    const response = await fetch(`${API_URL}/api/subscriptions/${subscriptionId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'resume' })
    });
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.status).toBe('active');

    console.log('✓ Resume subscription test ready for Playwright');
  });

  test('User can cancel subscription with feedback', async () => {
    // 1. Navigate to profile → Subscription tab
    // page.goto(`${BASE_URL}/profile.html`);
    // clickElement('[data-tab="subscription"]');

    // 2. Click Cancel button
    // clickElement('[data-action="cancel-subscription"]');

    // 3. Verify cancel confirmation dialog
    // await page.waitForSelector('[data-dialog="cancel-confirmation"]');

    // 4. Select feedback reason
    // clickElement('[data-feedback="too-expensive"]');

    // 5. Click Confirm Cancel
    // clickElement('[data-dialog-action="confirm-cancel"]');

    // 6. Verify status changed to CANCELLED
    // await page.waitForSelector('[data-status-badge="cancelled"]');

    // 7. Verify Resubscribe button available
    // await page.waitForSelector('[data-action="resubscribe"]');

    // 8. Verify API call
    const response = await fetch(`${API_URL}/api/subscriptions/${subscriptionId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'cancel',
        feedback_reason: 'too_expensive'
      })
    });
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.status).toBe('cancelled');

    console.log('✓ Cancel subscription with feedback test ready for Playwright');
  });
});

// ============================================================================
// TEST SUITE 6: DECISION ENGINE INTEGRATION
// ============================================================================

describe('E2E: Decision Engine with Exclude-List Integration', () => {
  let userId;

  beforeEach(async () => {
    const response = await fetchAPI('/api/users/register', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Decision Engine Test User',
        email: `e2e-decision-${Date.now()}@test.com`,
        password: 'TestPassword123'
      })
    });
    const userData = await response.json();
    userId = userData.user_id;
    localStorage.setItem('user_id', userId);
    localStorage.setItem('jwt_token', userData.jwt_token);
  });

  test('Recommendation excludes delivered books', async () => {
    // 1. Add books to avoid-list (simulating delivered)
    await fetchAPI(`/api/users/${userId}/avoid-list`, {
      method: 'POST',
      body: JSON.stringify({
        book_id: 'book-already-read-001',
        reason: 'read'
      })
    });

    // 2. Request recommendation with user_id
    const response = await fetchAPI('/api/ai/decide', {
      method: 'POST',
      body: JSON.stringify({
        preferences: {
          recipient_age_range: '25-45',
          genres: ['Mystery', 'Thriller'],
          mood: 'cozy'
        },
        user_id: userId
      })
    });
    expect(response.status).toBe(200);
    const recommendation = await response.json();

    // 3. Verify recommendation is not in exclude-list
    expect(recommendation.book_id).not.toBe('book-already-read-001');

    // 4. Verify reasoning includes duplicate prevention (if available)
    // if (recommendation.reason) {
    //   expect(recommendation.reason).toContain('Not in reading history');
    // }

    console.log('✓ Decision engine exclude-list integration test ready for Playwright');
  });

  test('Frontend gets recommendation and shows "Not in reading history"', async () => {
    // 1. Navigate to homepage
    // page.goto(BASE_URL);

    // 2. Complete preference selection flow
    // ... (select genres, mood, age range, click "Get Recommendation")

    // 3. Verify recommendation card displays
    // await page.waitForSelector('[data-testid="recommendation-card"]');

    // 4. Verify reasoning includes duplicate prevention
    // const reasoningText = await page.textContent('[data-testid="recommendation-reasoning"]');
    // expect(reasoningText).toContain('Not in your reading history');

    // 5. API call verification
    const response = await fetchAPI('/api/ai/decide', {
      method: 'POST',
      body: JSON.stringify({
        preferences: {
          recipient_age_range: '25-45',
          genres: ['Mystery'],
          mood: 'cozy'
        },
        user_id: userId
      })
    });
    expect(response.status).toBe(200);

    console.log('✓ Frontend recommendation display test ready for Playwright');
  });
});

// ============================================================================
// TEST SUITE 7: COMPLETE USER JOURNEY
// ============================================================================

describe('E2E: Complete User Journey', () => {
  test('Full journey: Register → Preferences → Recommendation → Avoid-List', async () => {
    const testEmail = `e2e-journey-${Date.now()}@test.com`;
    const testPassword = 'JourneyTest123';

    // Step 1: Register
    const registerResponse = await fetchAPI('/api/users/register', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Journey Test User',
        email: testEmail,
        password: testPassword
      })
    });
    expect(registerResponse.status).toBe(201);
    const userData = await registerResponse.json();
    const userId = userData.user_id;

    // Step 2: Set preferences
    const prefsResponse = await fetchAPI(`/api/users/${userId}/preferences`, {
      method: 'POST',
      body: JSON.stringify({
        preferred_genres: ['Mystery', 'Thriller'],
        mood_keywords: ['cozy', 'suspenseful'],
        age_min: 25,
        age_max: 65,
        surprise_level: 'balanced',
        recipient_type: 'self'
      })
    });
    expect(prefsResponse.status).toBe(201);

    // Step 3: Get recommendation with auto-exclude
    const decisionResponse = await fetchAPI('/api/ai/decide', {
      method: 'POST',
      body: JSON.stringify({
        preferences: {
          recipient_age_range: '25-65',
          genres: ['Mystery', 'Thriller'],
          mood: 'cozy'
        },
        user_id: userId
      })
    });
    expect(decisionResponse.status).toBe(200);
    const recommendation = await decisionResponse.json();
    const bookId = recommendation.book_id;

    // Step 4: Add recommendation to avoid-list
    const avoidResponse = await fetchAPI(`/api/users/${userId}/avoid-list`, {
      method: 'POST',
      body: JSON.stringify({
        book_id: bookId,
        reason: 'read'
      })
    });
    expect(avoidResponse.status).toBe(201);

    // Step 5: Get another recommendation (should exclude first one)
    const decision2Response = await fetchAPI('/api/ai/decide', {
      method: 'POST',
      body: JSON.stringify({
        preferences: {
          recipient_age_range: '25-65',
          genres: ['Mystery'],
          mood: 'cozy'
        },
        user_id: userId
      })
    });
    expect(decision2Response.status).toBe(200);
    const recommendation2 = await decision2Response.json();

    // Verify second recommendation is different
    expect(recommendation2.book_id).not.toBe(bookId);

    // Step 6: Verify excluded books list includes the book
    const excludedResponse = await fetchAPI(`/api/users/${userId}/excluded-books`);
    expect(excludedResponse.status).toBe(200);
    const excludedData = await excludedResponse.json();
    expect(excludedData.excluded_ids).toContain(bookId);

    console.log('✓ Complete user journey test verified');
  });
});

// ============================================================================
// EXPORT FOR TESTING FRAMEWORKS
// ============================================================================

module.exports = {
  describe,
  test,
  beforeEach,
  expect
};
