# Story 2.1: Rule-Based Decision Engine with Candidate Scoring

**Epic:** AI Match and Cart Conversion  
**Status:** done  
**Created:** 2026-06-23  

---

## Story Summary

As a shopper, I want the system to choose a best-match book using my preferences and safety constraints, so that the surprise feels relevant and appropriate.

**Dependencies:** Story 1.1-1.4 (Discovery & Preference Capture) – Supplies structured preferences to this endpoint.

**References:** FR4, Additional Requirements 1, 7, 9, NFR9

**Source Documents:**
- PRD sections 8.2, 9
- Architecture sections 2-3, 6, 7, 8
- docs/api-specs.yaml

---

## Acceptance Criteria

### AC1: Decision Engine with Candidate Scoring
**Given** structured preferences and optional exclusion history  
**When** `/api/ai/decide` is invoked  
**Then** the engine ranks candidates and returns a selected book with rationale metadata  
**And** respects age appropriateness and avoid lists.

**Task Breakdown:**
- [ ] POST `/api/ai/decide` endpoint accepts preferences (recipient_type, age_range, genres, avoid, surprise_level)
- [ ] Engine returns single best-fit book: `{ book_id, title, author, cover_url, price, score }`
- [ ] Score calculated from 4 weighted rules: genre_match (40%), mood_match (30%), age_safety (20%), duplicate_penalty (10%)
- [ ] All candidates ranked; top candidate returned with runner-up candidates in array
- [ ] Score range: 0.0–1.0 with justification: `{ genre_match: 0.6, mood_match: 0.3, age_safety: 0.1, delivered_penalty: 0.0 }`
- [ ] Age appropriateness enforced: returns null or error if no suitable books for age_range
- [ ] Avoid list respected: books matching avoid keywords excluded from candidates
- [ ] Response time < 500ms (p95)

### AC2: Duplicate Prevention & Delivery History
**Given** a shopper with prior delivery history  
**When** decision engine is called  
**Then** previously delivered books are penalized in scoring  
**And** same book is never returned twice consecutively.

**Task Breakdown:**
- [ ] API accepts optional `exclude_books` array: `[book_id_1, book_id_2, ...]`
- [ ] Delivered books scored with delivered_penalty: -0.15 (reduces score, but not blocked)
- [ ] If top candidate is in exclude_books, auto-select next best candidate
- [ ] Query PostgreSQL `deliveries` table (future: when user profiles exist) for historical books
- [ ] Log duplicate prevention decision in reasoning metadata
- [ ] For pilot, exclude_books can be empty (first-time users have no history)

### AC3: Scoring Algorithm & Reasoning
**Given** a decision result  
**When** decision logs are reviewed  
**Then** reason fields show which rules influenced ranking  
**And** metadata can be persisted on order records.

**Task Breakdown:**
- [ ] Reason metadata structure: `{ genre_match: 0.6, mood_match: 0.3, age_safety: 0.1, delivered_penalty: 0.0, total_score: 1.0 }`
- [ ] Scoring formula: `total_score = (genre_match * 0.4) + (mood_match * 0.3) + (age_safety * 0.2) - (delivered_penalty * 0.1)`
- [ ] Genre matching: Jaccard similarity between user genres and book genres
- [ ] Mood matching: Keyword matching on book description and mood metadata
- [ ] Age safety: Boolean check (book_min_age <= user_age <= book_max_age); penalty if outside range
- [ ] Candidate pool: Top 10 books by score returned; frontend displays top 1 or top 3
- [ ] Reason logged: `{ "selected_for": "high_genre_match_and_age_appropriate", "genre_match_reason": "user_likes_mystery_book_is_mystery_thriller", "candidates_considered": 10, "runner_up_score": 0.82 }`

### AC4: Book Catalog Data Model
**Given** a decision engine implementation  
**When** books are scored  
**Then** the system has access to book metadata for matching  
**And** metadata structure supports all scoring rules.

**Task Breakdown:**
- [ ] Book catalog table/mock data: `{ book_id, title, author, isbn, genres, mood_keywords, min_age, max_age, avoid_keywords, cover_url, price, published_year }`
- [ ] Sample data seeded: At least 20 books across multiple genres (mystery, romance, sci-fi, fantasy, memoir)
- [ ] Age ranges support: teen, 20s, 30s, 40s, 50s, 60+
- [ ] Genres include: mystery, romance, sci-fi, fantasy, memoir, horror, thriller, children, history, politics, self_help
- [ ] Avoid keywords: violence, explicit, heavy themes, sad endings, politics (configurable per book)
- [ ] Each book has min/max age and 1-3 primary genres
- [ ] Book mock data stored in JSON file or in-memory dict for pilot

### AC5: Error Handling & Safe Defaults
**Given** the decision engine receives invalid or edge-case input  
**When** no suitable books are found  
**Then** the API returns safe recommendation or error with fallback.

**Task Breakdown:**
- [ ] Invalid preferences: Return error 400 with helpful message
- [ ] No books match age range: Return error 400 "No books suitable for this age" or recommend popular book for age
- [ ] Empty genres: Return recommendation based on age + surprise_level only
- [ ] All candidates excluded: Return next best non-excluded candidate or error
- [ ] API timeout (>2s): Log error event, return safe default (popular book in age range)
- [ ] Response always includes `confidence` field (0.0–1.0) to indicate recommendation quality
- [ ] Low confidence (<0.5): Include note: "This is a best guess; feel free to explore other options"

---

## Implementation Context

### Backend File Structure

**Decision Engine Implementation:**  
Create new file: `_bmad-output/implementation-artifacts/ai/decision_engine.py`

**FastAPI Endpoint:**  
Update or create: `_bmad-output/implementation-artifacts/nlu/app.py` (or split into separate FastAPI app)

**Book Catalog Data:**  
`_bmad-output/implementation-artifacts/ai/book_catalog.json` – Mock books for pilot

**Database Schema (Future):**  
PostgreSQL tables for books, deliveries, user_preferences

### Book Catalog Mock Data

**Sample structure (20 books):**
```json
{
  "books": [
    {
      "book_id": "uuid-1",
      "title": "Midsummer Manor Mystery",
      "author": "Jane Author",
      "isbn": "978-0123456789",
      "genres": ["mystery", "cozy"],
      "mood_keywords": ["cozy", "charming", "relaxing"],
      "min_age": "20s",
      "max_age": "60+",
      "avoid_keywords": [],
      "cover_url": "https://example.com/book1.jpg",
      "price": 14.99,
      "description": "A charming mystery set in a Victorian manor..."
    },
    ...
  ]
}
```

### Scoring Algorithm Pseudocode

```python
def score_candidate(book, preferences, exclude_books):
    # Genre matching (Jaccard similarity)
    user_genres = set(preferences.get('genres', []))
    book_genres = set(book.get('genres', []))
    genre_match = len(user_genres & book_genres) / max(len(user_genres | book_genres), 1)
    
    # Mood matching (keyword match on description)
    mood_keywords = preferences.get('mood', '').split()
    description = book.get('description', '').lower()
    mood_match = sum(1 for kw in mood_keywords if kw.lower() in description) / max(len(mood_keywords), 1)
    
    # Age safety (boolean + penalty if outside range)
    user_age_range = preferences.get('age_range')  # teen, 20s, 30s, ...
    book_age_min = book.get('min_age')
    book_age_max = book.get('max_age')
    age_safety = 1.0 if age_in_range(user_age_range, book_age_min, book_age_max) else 0.3
    
    # Duplicate penalty
    delivered_penalty = 0.15 if book['book_id'] in exclude_books else 0.0
    
    # Weighted score
    total_score = (genre_match * 0.4) + (mood_match * 0.3) + (age_safety * 0.2) - (delivered_penalty * 0.1)
    
    # Avoid check: set score to 0 if book has avoided keywords
    avoid_keywords = preferences.get('avoid', [])
    if any(kw.lower() in description.lower() for kw in avoid_keywords):
        total_score = 0.0
    
    return max(0.0, min(1.0, total_score))  # Clamp to 0.0–1.0
```

### API Response Example

**Request:**
```json
{
  "preferences": {
    "recipient_type": "sibling",
    "recipient_age_range": "20s",
    "genres": ["mystery", "thriller"],
    "avoid": ["violence"],
    "surprise_level": "balanced",
    "mood": "cozy"
  },
  "exclude_books": ["book-id-123"],
  "session_id": "user-session-uuid"
}
```

**Response (200 OK):**
```json
{
  "book_id": "uuid-1",
  "title": "Midsummer Manor Mystery",
  "author": "Jane Author",
  "cover_url": "https://example.com/book1.jpg",
  "price": 14.99,
  "score": 0.84,
  "confidence": 0.92,
  "reason": {
    "genre_match": 0.8,
    "mood_match": 0.75,
    "age_safety": 1.0,
    "delivered_penalty": 0.0,
    "selected_for": "strong_genre_and_mood_match_age_appropriate",
    "candidates_considered": 10,
    "runner_up_title": "Tea & Alibis",
    "runner_up_score": 0.78
  },
  "candidates": [
    { "book_id": "uuid-1", "title": "Midsummer Manor Mystery", "score": 0.84 },
    { "book_id": "uuid-2", "title": "Tea & Alibis", "score": 0.78 },
    { "book_id": "uuid-3", "title": "Secrets of the Seaside", "score": 0.72 }
  ]
}
```

---

## Testing Requirements

### Unit Tests (Python - decision_engine.py)

- [ ] `test_genre_matching_jaccard()` – Correctly calculates Jaccard similarity
- [ ] `test_mood_matching_keyword()` – Matches mood keywords in book description
- [ ] `test_age_safety_check()` – Boolean check for age range appropriateness
- [ ] `test_avoid_keywords_excluded()` – Books with avoid keywords scored 0.0
- [ ] `test_duplicate_penalty_applied()` – Delivered books penalized -0.15
- [ ] `test_score_clamped_0_to_1()` – Score always between 0.0 and 1.0
- [ ] `test_ranking_top_10_candidates()` – Top 10 candidates returned in order
- [ ] `test_confidence_score_calculated()` – Confidence correlates with top candidate score gap

### Integration Tests (FastAPI - /api/ai/decide)

- [ ] `test_endpoint_post_valid_preferences()` – Returns 200 with valid response
- [ ] `test_endpoint_response_schema()` – Response matches OpenAPI contract
- [ ] `test_endpoint_age_appropriateness()` – Book recommended matches age_range
- [ ] `test_endpoint_avoid_list_respected()` – No books with avoid keywords returned
- [ ] `test_endpoint_exclude_books_honored()` – Previously delivered books not selected
- [ ] `test_endpoint_empty_genres_handled()` – Recommendation based on age + mood
- [ ] `test_endpoint_response_time()` – p95 latency < 500ms
- [ ] `test_endpoint_jwt_protected()` – Request without JWT returns 401

### Scoring Accuracy Tests

- [ ] Manual test: 3-4 preference profiles → verify scoring logic matches expected order
- [ ] Edge case: User with all mystery books delivered, new request for mystery → next best mystery selected
- [ ] Edge case: User requests avoid=[violence], book marked as violent → score 0.0
- [ ] Edge case: No books match age_range → error or safe default

### Performance Tests

- [ ] Scoring 100 books < 100ms
- [ ] Full endpoint (validate, score, rank, return) < 500ms (p95)
- [ ] Memory: Load all books once, cache in-memory (no reload per request)

---

## Developer Implementation Checklist

### Decision Engine Module (decision_engine.py)

- [ ] Create `Book` dataclass: book_id, title, author, genres, mood_keywords, min_age, max_age, avoid_keywords, cover_url, price
- [ ] Create `Preference` dataclass: recipient_type, age_range, genres, avoid, surprise_level, mood
- [ ] Implement `score_candidate(book, preferences, exclude_books) -> float`
- [ ] Implement `rank_candidates(books, preferences, exclude_books, limit=10) -> List[Tuple[Book, float]]`
- [ ] Implement `select_best_fit(books, preferences, exclude_books) -> Tuple[Book, Dict[reason]]`
- [ ] Add type hints for all functions
- [ ] Add docstrings with examples

### FastAPI Endpoint (app.py or new decision_api.py)

- [ ] Create POST `/api/ai/decide` endpoint
- [ ] Accept request: `{ preferences, exclude_books, session_id, allow_explicit }`
- [ ] Validate preferences schema
- [ ] Load book catalog from JSON
- [ ] Call decision engine
- [ ] Return formatted response with reason metadata
- [ ] Handle errors: invalid input, no matching books, timeout
- [ ] Add response time tracking
- [ ] Add request/response logging
- [ ] Protect with JWT auth (or public for pilot MVP)

### Book Catalog (book_catalog.json)

- [ ] Create JSON file with at least 20 books
- [ ] Diversity: Multiple genres, age ranges, price points
- [ ] Test coverage: 
  - [ ] 3+ mystery books (for mystery preference tests)
  - [ ] 3+ romance books
  - [ ] 3+ sci-fi books
  - [ ] 2+ children's books
  - [ ] 2+ memoir books
  - [ ] Books marked with avoid_keywords (violence, explicit)
- [ ] Each book has: book_id, title, author, genres, mood_keywords, min_age, max_age, description, cover_url, price

### Configuration

- [ ] Scoring weights configurable: `GENRE_WEIGHT=0.4, MOOD_WEIGHT=0.3, AGE_WEIGHT=0.2, PENALTY_WEIGHT=0.1`
- [ ] Duplicate penalty amount configurable: `DELIVERED_PENALTY=0.15`
- [ ] Candidate pool size configurable: `MAX_CANDIDATES=10`
- [ ] Response time timeout configurable: `DECISION_TIMEOUT_MS=2000`

### Logging & Monitoring

- [ ] Log every decision: book_id, score, reason, confidence, preferences
- [ ] Log errors: invalid preferences, no matching books, timeout
- [ ] Metrics: average score, average confidence, error rate by reason
- [ ] Decision events table (future): session_id, decision_id, book_id, score, reason_json, timestamp

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Decision accuracy | >= 85% | Manual review of 50 decisions vs. expected best fit |
| Confidence calibration | >= 90% | High confidence decisions (>0.8) match manual expectation |
| Recommendation diversity | >= 70% | Across 100 users, top book recommended to <= 30 |
| Response latency p95 | < 500ms | Query 1000 requests, measure p95 |
| Avoid list compliance | 100% | No recommended books have avoid keywords |
| Age safety compliance | 100% | All recommendations within user age range |
| Duplicate prevention | 100% | Previously delivered books never auto-selected without penalty |

---

## Deployment and Handoff

**Story Status Transitions:**
- [ ] Implement: Status remains `ready-for-dev`
- [ ] Submit for review: Update story artifact to `Status: review`
- [ ] Code review complete, ready to merge: Update to `Status: done`
- [ ] Update sprint-status.yaml: Move story from backlog → review → done

**File Updates After Implementation:**
- Create `_bmad-output/implementation-artifacts/ai/decision_engine.py` with scoring logic
- Create `_bmad-output/implementation-artifacts/ai/book_catalog.json` with 20+ test books
- Update `_bmad-output/implementation-artifacts/nlu/app.py` with `/api/ai/decide` endpoint
- Update `docs/api-specs.yaml` with /api/ai/decide endpoint documentation
- Commit changes with message: `Story 2.1: Rule-based decision engine with candidate scoring`

**Next Story:** Story 2.2 (Recommendation Summary Card & One-Click Add-to-Cart)

---

## References

- **PRD:** _bmad-output/implementation-artifacts/prd-blind-date-book.md sections 8.2, 9
- **Architecture:** _bmad-output/implementation-artifacts/architecture/architecture.md
- **API Spec:** docs/api-specs.yaml
- **Story Context:** _bmad-output/planning-artifacts/epics.md (Epic 2 Story 2.1)
