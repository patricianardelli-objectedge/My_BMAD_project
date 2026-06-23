# Story 4.1: User Profile, Preferences & Avoid-List Management

**Epic:** User Profile & Preferences  
**Status:** ready-for-dev  
**Created:** 2026-06-23  

---

## Story Summary

As a subscriber, I want to create and manage my profile with persistent preferences and an avoid-list, so that the AI can learn my tastes and never recommend books I've already read or disliked.

**Dependencies:** Story 1.2-1.4 (Preference Capture), Story 2.1-2.3 (Decision Engine) – Supplies user preferences and recommendations.

**References:** FR1, FR2, FR3, NFR1, NFR4

**Source Documents:**
- PRD sections 3, 4, 5
- Architecture section 3, 6
- docs/api-specs.yaml

---

## Acceptance Criteria

### AC1: User Registration & Profile Creation
**Given** a new visitor to Blind Date Book  
**When** they start the preference modal or checkout flow  
**Then** they can create an account or continue as guest  
**And** account stores email, password, created_at timestamp.

**Task Breakdown:**
- [ ] New endpoint: POST `/api/users/register` accepts email, password (hashed), name
- [ ] Validation: Email format, password min 8 chars, no duplicates
- [ ] Hash password using bcrypt or argon2
- [ ] Create `users` table: user_id (UUID), email (unique), password_hash, name, created_at, updated_at
- [ ] Return jwt_token for session (expires 30 days)
- [ ] Login endpoint: POST `/api/users/login` accepts email, password → returns jwt_token
- [ ] Guest checkout: No account required (anonymous user_id generated)
- [ ] On order creation: Link to existing user if logged in, or create guest order if not

### AC2: Persistent User Preferences
**Given** a logged-in user completes the preference modal  
**When** preferences are submitted  
**Then** preferences are saved to user profile  
**And** persisted for future sessions.

**Task Breakdown:**
- [ ] Create `user_preferences` table: user_id, preferred_genres (array), mood_keywords (array), age_range (min, max), surprise_level, recipient_type (self/gift), created_at, updated_at
- [ ] POST `/api/users/{user_id}/preferences` accepts preferences object
- [ ] Store: preferred_genres (ARRAY), mood_keywords (ARRAY), age_range (JSON), surprise_level (VARCHAR)
- [ ] GET `/api/users/{user_id}/preferences` returns stored preferences
- [ ] On login: Pre-fill preference modal with stored preferences
- [ ] Update endpoint: PATCH `/api/users/{user_id}/preferences` to modify existing preferences
- [ ] Version tracking: Log preference changes with timestamp for A/B testing

### AC3: Avoid-List (Books Already Read / Disliked)
**Given** a user has received recommendations or purchased books  
**When** they mark a book as "already read" or "dislike"  
**Then** the book is added to their avoid-list  
**And** future recommendations never include that book.

**Task Breakdown:**
- [ ] Create `user_avoid_list` table: user_id, book_id, reason (read/dislike/gift-giver-bought), created_at
- [ ] POST `/api/users/{user_id}/avoid-list` accepts book_id, reason
- [ ] GET `/api/users/{user_id}/avoid-list` returns array of avoided book_ids
- [ ] DELETE `/api/users/{user_id}/avoid-list/{book_id}` removes book from avoid-list
- [ ] Decision engine (Story 2.1) calls: `exclude_books = get_user_avoid_list(user_id)` before scoring
- [ ] UI: "Add to avoid-list" button on recommendation card, history items
- [ ] UI: Display avoid-list on profile settings page
- [ ] After order completion: Automatically add delivered books to avoid-list (optional, for future)

### AC4: User Profile Settings Page
**Given** a logged-in user visits their profile  
**When** they view settings  
**Then** they see preferences, avoid-list, order history, subscription status  
**And** can edit preferences and manage avoid-list.

**Task Breakdown:**
- [ ] New page/route: `/profile` (requires authentication)
- [ ] Display sections:
  - [ ] Account info: Email, name, joined date, account status
  - [ ] Preferences: Genres, mood, age range, surprise level (edit button)
  - [ ] Avoid-list: Table of avoided books with reason, remove buttons
  - [ ] Subscription status: Current cadence, next billing date, manage link
  - [ ] Order history: Last 10 orders (link to Order History page – Story 4.2)
- [ ] Edit preferences modal: Same as Story 1.2, but pre-filled
- [ ] Avoid-list management: Add/remove books
- [ ] Logout button

### AC5: Authentication & Session Management
**Given** user is logged in or guest  
**When** making API requests  
**Then** requests include auth token and API validates  
**And** token expires after 30 days or on logout.

**Task Breakdown:**
- [ ] JWT token generation on login/register: exp=30 days, sub=user_id
- [ ] All protected endpoints require Authorization header: `Authorization: Bearer {token}`
- [ ] Middleware validates token: signature, expiry, user_id
- [ ] Guest requests: Use anonymous user_id, no token required for some endpoints
- [ ] Login endpoint: POST `/api/users/login` → returns jwt_token
- [ ] Logout endpoint: POST `/api/users/logout` (invalidates token server-side if needed)
- [ ] Token refresh: POST `/api/users/token/refresh` → returns new token (optional)
- [ ] Error responses: 401 (unauthorized), 403 (forbidden), 419 (token expired)

---

## Implementation Context

### Database Schema

**users table:**
```sql
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  account_type VARCHAR(20) DEFAULT 'standard',  -- standard, premium, guest
  status VARCHAR(20) DEFAULT 'active',  -- active, suspended, deleted
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);

CREATE TABLE user_preferences (
  preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(user_id),
  preferred_genres TEXT[],  -- {mystery, romance, sci-fi, ...}
  mood_keywords TEXT[],  -- {cozy, adventurous, thrilling, ...}
  age_range JSONB,  -- {min: 18, max: 65}
  surprise_level VARCHAR(20),  -- minimal, balanced, maximum
  recipient_type VARCHAR(20),  -- self, gift
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);

CREATE TABLE user_avoid_list (
  avoid_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(user_id),
  book_id VARCHAR(255) NOT NULL,
  reason VARCHAR(50),  -- read, dislike, already-gifted
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_avoid_list_user_id ON user_avoid_list(user_id);
CREATE INDEX idx_user_avoid_list_book_id ON user_avoid_list(book_id);
```

### API Endpoints

**Authentication:**
- POST `/api/users/register` – Create account
- POST `/api/users/login` – Login, return JWT
- POST `/api/users/logout` – Logout (optional)

**Profile:**
- GET `/api/users/{user_id}` – Get user profile
- PATCH `/api/users/{user_id}` – Update name, email

**Preferences:**
- POST `/api/users/{user_id}/preferences` – Save preferences
- GET `/api/users/{user_id}/preferences` – Get preferences
- PATCH `/api/users/{user_id}/preferences` – Update preferences

**Avoid-List:**
- POST `/api/users/{user_id}/avoid-list` – Add book to avoid-list
- GET `/api/users/{user_id}/avoid-list` – Get avoid-list
- DELETE `/api/users/{user_id}/avoid-list/{book_id}` – Remove from avoid-list

### JWT Token Example

```json
{
  "sub": "user-uuid-123",
  "email": "jane@example.com",
  "iat": 1687448400,
  "exp": 1690040400
}
```

---

## Testing Requirements

### Unit Tests (Python - user_service.py)

- [ ] `test_register_user_success()` – Valid email/password → user created, token returned
- [ ] `test_register_user_duplicate_email()` – Duplicate email → 400 error
- [ ] `test_register_user_weak_password()` – Password < 8 chars → 400 error
- [ ] `test_login_success()` – Valid credentials → token returned
- [ ] `test_login_invalid_password()` – Wrong password → 401 error
- [ ] `test_password_hashed()` – Password never stored plaintext
- [ ] `test_save_preferences()` – Preferences stored correctly
- [ ] `test_get_preferences()` – Retrieve stored preferences
- [ ] `test_add_to_avoid_list()` – Book added, can retrieve
- [ ] `test_remove_from_avoid_list()` – Book removed from list

### Integration Tests

- [ ] `test_register_and_login_flow()` – Register → login → get preferences
- [ ] `test_preferences_persist_across_sessions()` – Set preferences → logout → login → preferences still there
- [ ] `test_avoid_list_affects_decision_engine()` – Add book to avoid-list → decision engine excludes it
- [ ] `test_jwt_token_expiry()` – Token expires after 30 days
- [ ] `test_invalid_token_rejected()` – Tampered token → 401 error
- [ ] `test_guest_checkout_creates_anonymous_order()` – No account → guest order created

### UI Tests

- [ ] `/profile` page loads (authenticated)
- [ ] Profile displays user info, preferences, avoid-list
- [ ] Edit preferences modal opens and saves
- [ ] Add to avoid-list button works
- [ ] Remove from avoid-list button works
- [ ] Logout clears session

### Performance Tests

- [ ] Preference retrieval < 100ms
- [ ] Avoid-list check < 50ms
- [ ] Decision engine with avoid-list < 2s (no extra latency)

---

## Developer Implementation Checklist

### Flask User Service (user_service.py)

- [ ] Create `User` dataclass
- [ ] Implement `register_user(email, password, name) -> User`
- [ ] Implement `login_user(email, password) -> jwt_token`
- [ ] Implement `hash_password(password) -> hash`
- [ ] Implement `verify_password(password, hash) -> bool`
- [ ] Implement `generate_jwt_token(user_id) -> token`
- [ ] Implement `verify_jwt_token(token) -> user_id`
- [ ] Implement `get_user_preferences(user_id) -> dict`
- [ ] Implement `save_user_preferences(user_id, prefs) -> bool`
- [ ] Implement `get_avoid_list(user_id) -> list[book_id]`
- [ ] Implement `add_to_avoid_list(user_id, book_id, reason) -> bool`
- [ ] Implement `remove_from_avoid_list(user_id, book_id) -> bool`

### Flask Authentication Endpoints

- [ ] POST `/api/users/register` route
- [ ] POST `/api/users/login` route
- [ ] GET `/api/users/{user_id}` route (authenticated)
- [ ] POST `/api/users/logout` route (optional)
- [ ] Auth middleware: Validate JWT on protected endpoints

### Flask Profile Endpoints

- [ ] POST `/api/users/{user_id}/preferences` route
- [ ] GET `/api/users/{user_id}/preferences` route
- [ ] PATCH `/api/users/{user_id}/preferences` route
- [ ] POST `/api/users/{user_id}/avoid-list` route
- [ ] GET `/api/users/{user_id}/avoid-list` route
- [ ] DELETE `/api/users/{user_id}/avoid-list/{book_id}` route

### Database Setup

- [ ] Create `users` table with indices
- [ ] Create `user_preferences` table
- [ ] Create `user_avoid_list` table
- [ ] Run migration script

### Frontend - Login/Register

- [ ] Add login modal to homepage
- [ ] Add register form (email, password, name)
- [ ] Add login form (email, password)
- [ ] Store JWT in localStorage/sessionStorage
- [ ] Logout button clears token
- [ ] Add Auth header to all API requests

### Frontend - Profile Page

- [ ] Create `/profile` route
- [ ] Display user info
- [ ] Display preferences (edit button)
- [ ] Display avoid-list (add/remove buttons)
- [ ] Display subscription status
- [ ] Display order history (link to Story 4.2)

### Environment Configuration

- [ ] JWT_SECRET from env
- [ ] TOKEN_EXPIRY_DAYS from env
- [ ] Bcrypt/Argon2 configuration

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Registration success rate | >= 98% | Successful registrations / attempts |
| Login success rate | >= 98% | Successful logins / attempts |
| Preference persistence | 100% | Preferences survive logout/login |
| Avoid-list accuracy | 100% | Avoided books never recommended |
| Profile page load time | < 500ms | Time to load profile page |
| Token validation latency | < 50ms | Auth middleware response |

---

## Deployment and Handoff

**Story Status Transitions:**
- [ ] Implement: Status remains `ready-for-dev`
- [ ] Submit for review: Update to `Status: review`
- [ ] Code review complete: Update to `Status: done`

**File Updates After Implementation:**
- Create `_bmad-output/implementation-artifacts/user/user_service.py`
- Update `_bmad-output/implementation-artifacts/nlu/app.py` with user endpoints
- Create `_bmad-output/implementation-artifacts/user/001_create_users_tables.sql`
- Create `frontend/profile.html` or profile route
- Update `frontend/index.html` with login/register modals
- Update `docs/api-specs.yaml` with user endpoints
- Commit: `Story 4.1: User profile, preferences & avoid-list management`

**Next Story:** Story 4.2 (Delivered History Tracking & Duplicate Exclusion)

---

## References

- **PRD:** _bmad-output/implementation-artifacts/prd-blind-date-book.md sections 3, 4, 5
- **Architecture:** _bmad-output/implementation-artifacts/architecture/architecture.md
- **JWT Docs:** https://jwt.io/
- **Bcrypt:** https://pypi.org/project/bcrypt/
- **Story Context:** _bmad-output/planning-artifacts/epics.md (Epic 4 Story 4.1)
