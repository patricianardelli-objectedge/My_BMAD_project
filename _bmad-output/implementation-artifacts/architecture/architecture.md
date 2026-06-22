# Blind Date Book — Architecture Decisions (summary)

Status: Pilot — prototype wiring and API contract exist. This document captures recommended production architecture and decisions derived from current artifacts: `docs/api-specs.yaml`, the rule-based NLU in `_bmad-output/implementation-artifacts/nlu/`, the Flask demo, and the static frontend prototype.

1. High-level overview
- Frontend: Static prototype (vanilla HTML/CSS/JS) → production: React + TypeScript (Vite) single-page app served from CDN or S3+CloudFront.
- Backend HTTP API: FastAPI (Python) serving OpenAPI spec (`docs/api-specs.yaml`) — routes: `/api/agent/parse`, `/api/ai/decide`, `/api/checkout`, webhooks.
- NLU: Rule-based parser (current `parser.py`) behind `/api/agent/parse` (wrap as a service). Replaceable with ML model later.
- Decisioning: `ai/decide` service — stateless API that scores candidates using business rules + optional ML ranker.
- Payments: Stripe for card, PIX provider integration for Brazil; tokenize cards client-side and send tokens to backend.
- Worker & scheduler: Redis + RQ or Celery for background tasks (subscription renewals, fulfillment, webhooks processing).
- Database: PostgreSQL (12+) with JSONB fields for flexible `preferences`, `ai_decision_reason`, and event logs.

2. Key components & responsibilities
- Static frontend (UX prototype → React app)
  - Renders agent modal and cart UI.
  - Calls `POST /api/agent/parse` and `POST /api/ai/decide`.
  - Handles client-side tokenization for payments (Stripe Elements) and submits `payment_method.token` to `/api/checkout`.

- API Server (FastAPI)
  - `POST /api/agent/parse` — call into NLU service (rule-based parser). Returns `PreferenceObject` per OpenAPI.
  - `POST /api/ai/decide` — requires authentication; returns selected book and `candidates` list.
  - `POST /api/checkout` — creates order, charges payment (or returns PIX QR), returns `order_id`.
  - Auth: JWT Bearer for protected endpoints. Public parse endpoint remains unauthenticated for UX flow.

- NLU Service
  - Wrap existing `parser.parse_input()` into a module callable by FastAPI. Keep rules and `nlu_rules.json` under version control.
  - Add lightweight metrics logging (counts, unknown tokens) and a small corpus for iterative rule improvement.

- Decision Engine
  - Business-rule layer + optional ML ranker. Inputs: `PreferenceObject`, `recipient_details`, `exclude_books`.
  - Outputs: scored `BookCandidate[]` and chosen `book_id` with `reason` object.
  - Store decisions (reason) in `orders.ai_decision_reason` for auditing.

- Database schema (recommended)
  - `books` — canonical catalog (id UUID, title, metadata JSONB, inventory int)
  - `orders` — (id, user_id nullable, cart JSONB, shipping JSONB, billing JSONB, total_cents int, status, ai_decision_reason JSONB, created_at)
  - `subscriptions` — (id, user_id, plan, interval, next_charge_at, status)
  - `users` — (id, email, hashed_password, profile JSONB)
  - Index JSONB fields used for search and analytics.

3. Data flow (user preference → book selection → checkout)
1. User submits free text in agent modal. Frontend POSTs `{text}` to `/api/agent/parse`.
2. API calls NLU service → returns structured `PreferenceObject` (per `docs/api-specs.yaml`).
3. Frontend may call `/api/ai/decide` with preferences to get a suggested book (requires auth for production flows).
4. User confirms and initiates checkout; frontend collects shipping/billing and obtains Stripe token.
5. Frontend POSTs `/api/checkout` with cart, addresses, and `payment_method` token.
6. Backend creates order, calls payment provider, persists order, returns `order_id` and payment status. For PIX, return QR payload.

4. Security & compliance
- PCI: Never send raw card data to backend. Use Stripe Elements to collect and tokenize card data client-side.
- Secrets: Store provider keys and JWT secrets in environment variables / secrets manager (AWS Secrets Manager / Azure Key Vault).
- Rate limiting & bot protection: Protect `/api/agent/parse` with per-IP throttling and optionally a CAPTCHA if abused.

5. Scalability & operations
- Start single FastAPI process behind Uvicorn+Gunicorn (workers) behind a load balancer. Use autoscaling for traffic.
- Use Redis for caching popular candidate lists and as broker for background tasks (Celery/RQ).
- Use worker pool for long-running tasks: order fulfillment, subscription billing, webhook processing.
- Observability: structured logs (JSON), metrics (Prometheus), and distributed tracing for ai/decide calls.

6. Deployment recommendations
- Containerize services using Docker, deploy to ECS/Fargate, Kubernetes, or a Platform-as-a-Service.
- Use managed Postgres (RDS / Azure Database / Cloud SQL) and managed Redis (Elasticache).
- CI: run tests, lint, and build frontend; publish Docker images to registry and deploy via CD pipeline.

7. Local dev & quick start (prototype)
1. Run NLU demo server (Flask prototype) for quick local testing:
```bash
cd _bmad-output/implementation-artifacts/nlu
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt  # if present, else: pip install flask
python app.py
# Server listens on http://127.0.0.1:5000 with endpoint POST /api/parse
```
2. Use the static prototype: open `design-artifacts/.../frontend/index.html` in a static host or local server. The included `openapi-client.js` expects same-origin API at `/api` unless configured.

8. Next actions (prioritized)
- Implement a FastAPI wrapper that imports `parser.parse_input` and exposes `/api/agent/parse` matching the OpenAPI contract.
- Implement a simple rule-based `ai/decide` service that queries `books` catalog and returns candidates.
- Add payments integration with Stripe using tokenized flows and webhook handlers.
- Implement background worker for subscription billing and order fulfillment.

9. References (in-repo)
- `docs/api-specs.yaml` — OpenAPI contract used by frontend client.
- `_bmad-output/implementation-artifacts/nlu/parser.py` — current rule-based NLU.
- `_bmad-output/implementation-artifacts/nlu/app.py` — Flask demo for quick testing.
- `design-artifacts/E-Development/.../frontend/index.html` — prototype frontend wired to `window.BlindDateApi`.

Decision notes
- Use PostgreSQL + JSONB to allow flexible storage of `preferences` and decision reasons without schema churn.
- FastAPI recommended for automatic OpenAPI generation and type-safety in production.
- Keep the NLU ruleset under test coverage and version control; move to a model when corpus and metrics justify it.

Document created automatically from repository artifacts on 2026-06-22.
