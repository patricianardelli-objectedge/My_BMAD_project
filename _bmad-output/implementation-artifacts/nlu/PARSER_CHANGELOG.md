# Parser Changelog

All notable changes to the NLU parser are documented here.

## [1.0] - 2026-06-23

### Added
- **Ambiguity Detection**: Added detection for 9 ambiguity types (MISSING_RECIPIENT, AMBIGUOUS_AGE, AGE_OUT_OF_RANGE, GENRE_UNRECOGNIZED, CONFLICTING_MOOD, PARTIAL_PARSE, LOW_CONFIDENCE, EMPTY_INPUT, PARSE_ERROR)
- **Confidence Scoring**: Introduced confidence score (0.0–1.0) based on number of fields successfully parsed
- **Enhanced Age Ranges**: Updated age range mapping from old schema (under-12, under-18, etc.) to new normalized ranges (teen, 20s, 30s, 40s, 50s, 60+)
- **Logging Support**: Added parse event logging with session_id, parser_version, ambiguities, and confidence metadata
- **Response Enrichment**: Enhanced API response with parser_version, ambiguities array, confidence, and response_time_ms
- **Event Tracking**: Implemented parse_events table schema for PostgreSQL audit trail and pilot analysis

### Changed
- **parse_input() return structure**: Now returns dict with confidence, ambiguities, parser_version fields in addition to preference fields
- **API response format**: `/api/agent/parse` now returns ambiguities array and confidence score for frontend clarification prompts
- **Age mapping values**: Old 'under-12' → 'teen', '18-24' → '20s', '25-34' → '30s', etc.
- **Error handling**: Parser no longer throws errors on edge cases; returns safe defaults and logs event_type='parse_error'

### Breaking Changes
- API response schema changed; frontend must handle new fields (confidence, ambiguities, parser_version)
- Age range values are no longer compatible with old schema; migration guide: see MIGRATION.md
- parse_input() return structure changed; any code calling parser directly must be updated

### Deprecations
- follow_up_question and suggestions fields in API response are deprecated; use ambiguities array instead

### Performance
- Parse latency unchanged (p95 < 500ms) despite added ambiguity detection logic
- Logging overhead < 50ms per parse event

### Bug Fixes
- Fixed genre detection when text contains negative context (e.g., "no politics" now correctly added to avoid list)
- Fixed age parsing for edge cases (e.g., "aged 8 years old" now correctly parsed as age 8)

### Testing
- Added 20+ unit tests for ambiguity detection and confidence scoring
- Added 10+ integration tests for API endpoint response schema
- Added 5+ tests for privacy-preserving logging (no raw PII stored)

---

## Migration Guide: 0.x → 1.0

### If updating frontend calling /api/agent/parse:

**Old response:**
```json
{
  "parsed": {
    "recipient_type": "gift",
    "recipient_age_range": "under-12",
    "genres": ["adventure"],
    "avoid": [],
    "surprise_level": "light_hint"
  }
}
```

**New response:**
```json
{
  "parsed": { ... },
  "confidence": 0.89,
  "parser_version": "1.0",
  "ambiguities": [
    {
      "reason": "AGE_OUT_OF_RANGE",
      "value": "8",
      "suggestion": "Did you mean 'tween' (8-12) or 'teen' (13-19)?"
    }
  ]
}
```

**Frontend changes:**
1. Check `confidence` score; if < 0.6, consider asking user for clarification
2. Display ambiguities: if `ambiguities.length > 0`, show first ambiguity's `suggestion` to user
3. Update age range expectations: `under-12` → `teen`, `18-24` → `20s`, etc.

### If updating database queries:

**Create parse_events table:**
```bash
psql -f 001_create_parse_events_table.sql
```

### If using parser.py directly:

**Old usage:**
```python
result = parse_input("Gift for my 8-year-old son")
# result['age_range'] == 'under-12'
```

**New usage:**
```python
result = parse_input("Gift for my 8-year-old son")
# result['age_range'] == 'teen'
# result['confidence'] == 0.92
# result['ambiguities'] == [{reason: 'AGE_OUT_OF_RANGE', ...}]
# result['parser_version'] == "1.0"
```

---

## Upcoming Enhancements (v1.1+)

- Machine learning ranking for top genres (currently deterministic)
- Multi-language support (Spanish, Portuguese for Brazil market)
- Dynamic rule updates without server restart
- Real-time parser metrics dashboard for pilot team
- A/B testing framework for rule variants
