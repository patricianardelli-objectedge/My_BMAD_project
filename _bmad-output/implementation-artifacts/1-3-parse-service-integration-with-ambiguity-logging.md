# Story 1.3: Parse Service Integration with Ambiguity Logging

**Epic:** Discovery and Preference Capture  
**Status:** done  
**Created:** 2026-06-23  

---

## Story Summary

As a product team, I want free-text user input parsed into structured preferences with ambiguity logging, so that the pilot can improve matching quality over time.

**Dependencies:** Story 1.2 (Conversational Agent Modal) - Story 1.2 calls `/api/agent/parse`, which is implemented and logged in this story.

**References:** FR3, FR14, Additional Requirements 1-2, NFR5

**Source Documents:**
- PRD sections 7, 11
- Architecture sections 2-3, 9
- docs/api-specs.yaml
- _bmad-output/implementation-artifacts/nlu/parser.py

---

## Acceptance Criteria

### AC1: Structured Preference Object Response
**Given** the frontend submits free-text gift intent  
**When** `/api/agent/parse` receives the request  
**Then** the API returns a structured preference object aligned to the OpenAPI contract  
**And** the parser output is versioned and test-covered.

**Task Breakdown:**
- [ ] POST `/api/agent/parse` endpoint accepts JSON payload: `{ text: string, turn?: number, session_id?: string, context?: object }`
- [ ] Endpoint returns normalized response: `{ recipient, age_range, genres, avoid, surprise_level, raw, confidence, ambiguities }`
- [ ] Response schema matches OpenAPI 3.0.3 contract in docs/api-specs.yaml
- [ ] Parser version tracked in response metadata (e.g., parser_version: "1.0")
- [ ] Response includes confidence score (0.0–1.0) for parse quality
- [ ] Empty/null fields handled gracefully (no errors, just empty arrays or null values)
- [ ] Response time < 500ms (p95) for typical input
- [ ] Endpoint is public (no JWT auth required) per design requirements
- [ ] OpenAPI schema documents all request/response fields with examples
- [ ] Parser is versioned in code (comments or constants) for audit trail

### AC2: Ambiguity Detection and Logging
**Given** user input is ambiguous or partially parsed  
**When** parser confidence or rule coverage is insufficient  
**Then** the event is logged with reason codes for human review  
**And** the UX receives a safe clarification prompt instead of silent failure.

**Task Breakdown:**
- [ ] Parser detects ambiguity: age values outside expected ranges, missing required fields, conflicting inputs
- [ ] Ambiguity event structure: `{ event_type: 'ambiguity', reason_code: 'AGE_OUT_OF_RANGE', confidence: 0.42, raw_input: '...', parsed: {...}, timestamp: ISO8601 }`
- [ ] Reason codes defined: `MISSING_RECIPIENT`, `AMBIGUOUS_AGE`, `GENRE_UNRECOGNIZED`, `CONFLICTING_MOOD`, `PARTIAL_PARSE`, `LOW_CONFIDENCE`
- [ ] Ambiguities array included in API response: `{ ..., ambiguities: [ { reason: 'AGE_OUT_OF_RANGE', value: '150', suggestion: 'Did you mean 50 or 60+?' } ] }`
- [ ] Logged events stored in database or log file with session_id correlation for pilot review
- [ ] Logging includes: timestamp, session_id, user_input, parsed_output, reason_codes, parser_version
- [ ] Frontend receives ambiguities and displays clarification: "I'm not sure about the age — did you mean 50s or 60+?"
- [ ] Parser does not block on ambiguity; continues with best-match parse and flags in response
- [ ] Ambiguity events queryable by session_id and reason_code for pilot analysis
- [ ] Logging preserves privacy: no raw email/phone data, session_id opaque

### AC3: Error Handling and Safe Defaults
**Given** the parser encounters invalid or unparseable input  
**When** parsing fails or returns empty fields  
**Then** the API returns safe defaults and logs the error event  
**And** the frontend applies defaults without breaking downstream flows.

**Task Breakdown:**
- [ ] Error scenarios handled: empty string, null input, malformed JSON, timeout (>2s)
- [ ] Safe defaults applied: `{ recipient: 'self', age_range: null, genres: [], avoid: [], surprise_level: 'balanced', confidence: 0.0 }`
- [ ] Error logged with structure: `{ event_type: 'parse_error', reason_code: 'TIMEOUT_EXCEEDED', error_message: '...', raw_input: '...', timestamp: ISO8601 }`
- [ ] API returns HTTP 200 with error event in response (not 400/500) to prevent frontend crashes
- [ ] Frontend handles safe defaults: checks for null/empty fields, applies UI defaults (e.g., genres → [])
- [ ] Parser timeout set to 2 seconds (no blocking calls)
- [ ] Parsing errors logged for alerting: high error rate (>20% of requests) triggers manual review
- [ ] Error recovery: frontend can retry same input without session state corruption

### AC4: Version Control and Audit Trail
**Given** parsing rules are updated over the pilot  
**When** a new parser version is deployed  
**Then** all events include parser version for traceability  
**And** pilot team can segment results by parser version for tuning.

**Task Breakdown:**
- [ ] Parser version constant in code: `PARSER_VERSION = "1.0"`
- [ ] Version included in every API response: `{ ..., parser_version: "1.0" }`
- [ ] Version included in every logged event
- [ ] Changelog maintained: `PARSER_CHANGELOG.md` with rule changes, date, and reason
- [ ] Ambiguity events can be queried by parser_version to track rule effectiveness
- [ ] Backward compatibility note: document if response schema changes break frontend compatibility
- [ ] Migration guide for frontend if API contract changes

---

## Implementation Context

### Backend File Structure

**Parser Implementation (existing):**  
`_bmad-output/implementation-artifacts/nlu/parser.py` – Rule-based NLU parser

**Backend Endpoints:**  
`api/api_server.py` or similar – FastAPI app with `/api/agent/parse` route

**Database Schema:**  
PostgreSQL table `parse_events` or equivalent:
```sql
CREATE TABLE parse_events (
  id SERIAL PRIMARY KEY,
  session_id UUID,
  user_id UUID,
  raw_input TEXT,
  parsed_output JSONB,
  ambiguities JSONB,
  reason_codes TEXT[],
  confidence FLOAT,
  parser_version VARCHAR(10),
  event_type VARCHAR(50), -- 'parse_success' | 'parse_error' | 'ambiguity'
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_parse_events_session ON parse_events(session_id);
CREATE INDEX idx_parse_events_reason_code ON parse_events USING GIN(reason_codes);
```

**OpenAPI Specification Update:**  
`docs/api-specs.yaml` – Add/update POST `/api/agent/parse` endpoint schema

### Parser Integration Points

**Frontend → Backend (Already Implemented in Story 1.2):**
```javascript
POST /api/agent/parse
{
  "text": "Gift for my 8-year-old niece who loves fantasy",
  "turn": 1,
  "session_id": "uuid-string",
  "context": {
    "selected_trail": "adventure",
    "recipient_type_from_ui": "sibling"
  }
}
```

**Backend Response (to be implemented):**
```json
{
  "recipient": "sibling",
  "age_range": "teen",
  "genres": ["fantasy"],
  "avoid": [],
  "surprise_level": "balanced",
  "raw": "Gift for my 8-year-old niece who loves fantasy",
  "confidence": 0.89,
  "parser_version": "1.0",
  "ambiguities": [
    {
      "reason": "AGE_OUT_OF_RANGE",
      "value": "8",
      "suggestion": "Did you mean 'tween' (8-12) or 'teen' (13-19)?"
    }
  ],
  "parsed_at": "2026-06-23T10:42:11Z"
}
```

### Rule-Based Parser Logic Reference

**From nlu/parser.py:**
```python
def parse_input(text):
    """
    Rule-based parser for gift preference extraction.
    Returns: { recipient, age_range, genres, avoid, surprise_level, raw }
    """
    # recipient types: parent, sibling, friend, partner, colleague, self, other
    # age_range: teen, 20s, 30s, 40s, 50s, 60+
    # genres: horror, romance, sci-fi, mystery, fantasy, memoir, etc.
    # avoid: violence, explicit, heavy themes, etc.
    # surprise_level: safe, balanced, wildcard
```

**Key Parsing Rules to Log:**
- Age extraction: Map numeric ages to ranges (0-12 → teen, 13-19 → teen, 20-29 → 20s, etc.)
- Genre recognition: Match keywords against known genres (mystery, romance, sci-fi, etc.)
- Recipient inference: Extract relationships (parent, sibling, friend from text context)
- Conflict detection: If input says "safe" and "wildcard", log ambiguity
- Missing fields: Track which preferred fields are absent (confidence score adjustment)

### Ambiguity Reason Codes

| Reason Code | Trigger | Example | Suggested Prompt |
|-------------|---------|---------|-------------------|
| `MISSING_RECIPIENT` | No recipient type detected | "Gift for someone" | "Who is this for? E.g., parent, sibling, friend?" |
| `AMBIGUOUS_AGE` | Multiple age values or range overlap | "They're 8 or 13" | "Are they 8 or 13? Let me know the exact age range." |
| `AGE_OUT_OF_RANGE` | Age outside typical bounds | "150 years old" | "Did you mean 50 or 60+?" |
| `GENRE_UNRECOGNIZED` | Genre keyword not in known list | "They like stuff" | "Can you name a specific genre or book they love?" |
| `CONFLICTING_MOOD` | Contradictory mood/surprise signals | "Safe wildcard" | "Should this be a safe pick or an adventurous one?" |
| `PARTIAL_PARSE` | Multiple fields unparseable | "Just a book gift" | "Tell me a bit more about who this is for and what they like." |
| `LOW_CONFIDENCE` | Parser confidence < 0.6 | Unclear input | "I'm not quite sure — could you say that again?" |

### Logging Event Structure

```python
{
  "event_id": "uuid",
  "timestamp": "2026-06-23T10:42:11Z",
  "session_id": "user-session-uuid",
  "user_id": "user-uuid or null if new user",
  "event_type": "parse_success | parse_error | ambiguity",
  "parser_version": "1.0",
  "turn_number": 1,
  "raw_input": "Gift for my 8-year-old niece who loves fantasy",
  "parsed_output": {
    "recipient": "sibling",
    "age_range": "teen",
    "genres": ["fantasy"],
    "avoid": [],
    "surprise_level": "balanced"
  },
  "confidence": 0.89,
  "reason_codes": ["AGE_OUT_OF_RANGE"],
  "ambiguities": [
    {
      "reason": "AGE_OUT_OF_RANGE",
      "value": "8",
      "suggestion": "Did you mean 'tween' (8-12) or 'teen' (13-19)?"
    }
  ],
  "response_time_ms": 145
}
```

---

## Testing Requirements

### Unit Tests (Python - parser.py)

- [ ] `test_parse_input_recipient_types()` – Extracts parent, sibling, friend, partner, colleague, self, other
- [ ] `test_parse_input_age_ranges()` – Maps ages 0-12→teen, 13-19→teen, 20-29→20s, 30-39→30s, 40-49→40s, 50-59→50s, 60+→60+
- [ ] `test_parse_input_genres()` – Recognizes horror, romance, sci-fi, mystery, fantasy, memoir, etc.
- [ ] `test_parse_input_avoid_list()` – Extracts violence, explicit, heavy themes, sad endings, etc.
- [ ] `test_parse_input_surprise_level()` – Identifies safe, balanced, wildcard signals
- [ ] `test_parse_input_ambiguity_detection()` – Flags AGE_OUT_OF_RANGE, GENRE_UNRECOGNIZED, CONFLICTING_MOOD
- [ ] `test_parse_input_confidence_scoring()` – Returns 1.0 for fully parsed, 0.6 for partial, 0.0 for empty
- [ ] `test_parse_input_safe_defaults()` – Returns valid structure even on malformed input
- [ ] `test_parse_input_empty_string()` – Returns safe defaults (recipient='self', genres=[], avoid=[])
- [ ] `test_parse_input_versioning()` – Response includes parser_version field

### Integration Tests (FastAPI - /api/agent/parse)

- [ ] `test_endpoint_post_valid_input()` – Returns 200 with valid parsed structure
- [ ] `test_endpoint_response_schema()` – Response matches OpenAPI contract (recipient, age_range, genres, avoid, surprise_level, raw, confidence, parser_version, ambiguities)
- [ ] `test_endpoint_accepts_optional_fields()` – session_id, turn, context accepted without error
- [ ] `test_endpoint_ambiguity_response()` – Returns ambiguities array for unclear input
- [ ] `test_endpoint_error_handling()` – Empty input returns safe defaults, logs error event
- [ ] `test_endpoint_response_time()` – p95 latency < 500ms for typical requests
- [ ] `test_endpoint_public_no_auth()` – No JWT required, publicly callable
- [ ] `test_endpoint_cors_enabled()` – Frontend can call from different origin

### Logging Tests

- [ ] `test_parse_event_logged_on_success()` – Event written to parse_events table
- [ ] `test_parse_event_includes_metadata()` – session_id, user_id, timestamp, parser_version, confidence in log
- [ ] `test_ambiguity_event_logged_separately()` – Ambiguity reason_codes recorded
- [ ] `test_error_event_logged_on_parse_failure()` – event_type='parse_error', error_message recorded
- [ ] `test_parse_events_queryable_by_session()` – SELECT * FROM parse_events WHERE session_id = ? returns all events for session
- [ ] `test_parse_events_queryable_by_reason_code()` – SELECT * FROM parse_events WHERE reason_codes @> ? returns all AGE_OUT_OF_RANGE events
- [ ] `test_privacy_no_raw_pii()` – Logs do not include email, phone, or identifying personal data

### Frontend Integration Tests (JavaScript)

- [ ] `test_frontend_calls_parse_endpoint()` – Story 1.2 code calls /api/agent/parse with text payload
- [ ] `test_frontend_normalizes_response()` – Frontend maps recipient→recipient_type, age_range→recipient_age_range
- [ ] `test_frontend_displays_ambiguities()` – Clarification prompt shown for ambiguity events
- [ ] `test_frontend_applies_safe_defaults()` – If genres missing, defaults to []
- [ ] `test_frontend_handles_error_response()` – Parse error doesn't crash modal, shows retry prompt

### Performance & Load Tests

- [ ] `test_parse_latency_p50()` – p50 < 150ms
- [ ] `test_parse_latency_p95()` – p95 < 500ms
- [ ] `test_parse_latency_p99()` – p99 < 1000ms
- [ ] `test_parse_endpoint_throughput()` – Handles 100 req/s without degradation
- [ ] `test_logging_overhead()` – Parse response time not increased by >50ms due to logging

### Pilot Analytics

- [ ] Query parse accuracy by reason_code (e.g., AGE_OUT_OF_RANGE events per session)
- [ ] Query average confidence score by turn (expect trend: turn 1 low confidence → turn 6 high confidence)
- [ ] Query error rate by time of day / cohort for anomaly detection
- [ ] Segment results by parser_version to measure rule improvements

---

## Developer Implementation Checklist

### Backend Implementation

**Parser Module Updates (parser.py):**
- [ ] Add `PARSER_VERSION = "1.0"` constant
- [ ] Add ambiguity detection logic: `detect_ambiguities(parsed_dict, raw_input) -> list[ambiguity]`
- [ ] Add confidence scoring: `calculate_confidence(parsed_dict, raw_input) -> float`
- [ ] Update `parse_input()` to return: `{ recipient, age_range, genres, avoid, surprise_level, raw, confidence, ambiguities, parser_version }`
- [ ] Add logging calls: `log_parse_event(session_id, raw_input, parsed_output, ambiguities, confidence)`
- [ ] Test all rule combinations

**FastAPI Endpoint Implementation:**
- [ ] Create POST `/api/agent/parse` endpoint (or update if exists)
- [ ] Accept request: `{ text: str, turn?: int, session_id?: str, context?: dict }`
- [ ] Call `parser.parse_input(text)` and attach metadata
- [ ] Return OpenAPI-compliant response
- [ ] Add error handling: invalid input → safe defaults, log error event
- [ ] Add response time tracking
- [ ] Enable CORS (allow all origins for frontend)
- [ ] Add request validation (max text length, reject null input)

**Database/Logging Setup:**
- [ ] Create PostgreSQL table `parse_events` with schema above
- [ ] Add migration script: `alembic/versions/001_create_parse_events_table.py`
- [ ] Implement `ParseEventRepository` or ORM model for `parse_events` table
- [ ] Add logging function: `log_parse_event(event_dict) -> None`
- [ ] Set up indices for fast queries by session_id, reason_code, parser_version

**OpenAPI Schema Update:**
- [ ] Update `docs/api-specs.yaml` with `/api/agent/parse` endpoint definition
- [ ] Document request schema with examples
- [ ] Document response schema with all fields, types, examples
- [ ] Document possible reason_codes and ambiguities structure
- [ ] Include auth requirement: none (public endpoint)

### Monitoring & Alerts

- [ ] Add metric: `parse_requests_total` (counter by reason_code)
- [ ] Add metric: `parse_latency_ms` (histogram)
- [ ] Add metric: `parse_errors_total` (counter by error_code)
- [ ] Add metric: `parse_confidence_avg` (gauge)
- [ ] Alert: Error rate > 20% in last 5 minutes
- [ ] Alert: p95 latency > 1000ms
- [ ] Dashboard: Parse success rate, top ambiguity reason codes, confidence distribution

### Configuration

- [ ] Environment variable: `PARSER_VERSION` (for easy override)
- [ ] Config: Parse timeout = 2 seconds
- [ ] Config: Min confidence threshold = 0.6 (for confidence-based filtering)
- [ ] Config: Max input length = 500 chars

---

## Deployment and Handoff

**Story Status Transitions:**
- [ ] Implement: Status remains `ready-for-dev`
- [ ] Submit for review: Manually update story artifact to `Status: review`
- [ ] Code review complete, ready to merge: Manually update to `Status: done`
- [ ] Update sprint-status.yaml: Move story from backlog → review → done

**File Updates After Implementation:**
- Update `_bmad-output/implementation-artifacts/nlu/parser.py` with ambiguity detection, confidence scoring, versioning
- Update or create backend API endpoint file with `/api/agent/parse` implementation
- Create PostgreSQL migration file for `parse_events` table
- Update `docs/api-specs.yaml` with `/api/agent/parse` OpenAPI schema
- Create or update `PARSER_CHANGELOG.md` documenting rule changes
- Commit changes with message: `Story 1.3: Parse service integration with ambiguity logging for pilot`

**Next Story:** Story 1.4 (Agent Skip Flow and Default Matching Entry)

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Parse accuracy | >= 85% | Manual review of 100 random parse events |
| Ambiguity detection rate | Baseline established | Count of ambiguity events vs. total parses |
| Average confidence score | >= 0.75 | Mean confidence across all parse events |
| Parse latency p95 | < 500ms | Query parse_events.response_time_ms, p95 |
| Error rate | < 5% | Count of parse_errors / total_requests |
| Logging completeness | 100% | All events logged with required fields |
| Parser version tracking | 100% | All response/event records include parser_version |

---

## References

- **Parser Implementation:** _bmad-output/implementation-artifacts/nlu/parser.py
- **OpenAPI Specification:** docs/api-specs.yaml
- **Architecture:** _bmad-output/implementation-artifacts/architecture/architecture.md
- **Frontend Integration:** Story 1.2 implementation (index.html, submitAgent function)
- **PRD:** _bmad-output/implementation-artifacts/prd-blind-date-book.md sections 7, 11
