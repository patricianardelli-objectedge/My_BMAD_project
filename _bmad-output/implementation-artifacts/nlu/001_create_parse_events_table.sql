"""
PostgreSQL migration for parse_events table.
Run with: alembic upgrade head
"""

CREATE TABLE IF NOT EXISTS parse_events (
  id BIGSERIAL PRIMARY KEY,
  event_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL,
  user_id UUID,
  raw_input TEXT NOT NULL,
  parsed_output JSONB NOT NULL,
  ambiguities JSONB,
  reason_codes TEXT[],
  confidence FLOAT NOT NULL,
  parser_version VARCHAR(10) NOT NULL,
  event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('parse_success', 'parse_error', 'ambiguity')),
  response_time_ms INTEGER,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_parse_events_session_id ON parse_events(session_id);
CREATE INDEX idx_parse_events_user_id ON parse_events(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_parse_events_reason_codes ON parse_events USING GIN(reason_codes);
CREATE INDEX idx_parse_events_parser_version ON parse_events(parser_version);
CREATE INDEX idx_parse_events_event_type ON parse_events(event_type);
CREATE INDEX idx_parse_events_timestamp ON parse_events(timestamp DESC);
CREATE INDEX idx_parse_events_confidence ON parse_events(confidence);
