# Story 3.1: Checkout API with Tokenized Card and PIX Support

**Epic:** Fast & Secure Checkout  
**Status:** ready-for-dev  
**Created:** 2026-06-23  

---

## Story Summary

As a shopper, I want a secure, fast checkout API that accepts tokenized card payments and PIX, so that my payment is processed safely without storing sensitive card data.

**Dependencies:** Story 2.1-2.3 (AI Match & Cart Conversion) – Supplies cart and subscription data.

**References:** FR7, FR8, FR9, NFR6, NFR7, NFR8

**Source Documents:**
- PRD sections 9, 10, 11
- Architecture sections 4, 5, 7, 9
- docs/api-specs.yaml

---

## Acceptance Criteria

### AC1: POST /api/checkout Endpoint with Payment Processing
**Given** cart items and subscription data from mini-cart  
**When** checkout form is submitted  
**Then** the endpoint creates an order and processes payment  
**And** returns success with order_id and receipt metadata.

**Task Breakdown:**
- [ ] POST `/api/checkout` accepts request: `{ cart_items, subscription, shipping_address, billing_address, payment_method, idempotency_key }`
- [ ] Validates all required fields: name, email, phone, address, payment method
- [ ] Creates order in `orders` table: order_id (UUID), user_id (if logged in), cart_items, subscription_data, total_amount, status=pending
- [ ] Processes payment via Stripe token or PIX:
  - [ ] Credit/Debit card: Uses Stripe tokenized card (obtained from frontend)
  - [ ] PIX: Generates PIX qr_code and payment_id, returns for user to scan
- [ ] Updates order status: pending → paid (card) or pending → awaiting_pix_confirmation (PIX)
- [ ] Returns response: `{ order_id, status, receipt_url, pix_qr_code (if PIX), total_amount, next_shipment_date }`
- [ ] Response time < 2s (p95) for card payments, < 5s for PIX
- [ ] Idempotency key prevents duplicate charges if request retried

### AC2: PII Protection & Tokenization
**Given** sensitive payment data enters the system  
**When** the checkout endpoint receives payment input  
**Then** no raw card numbers or PII are logged or stored  
**And** all data uses tokenized references.

**Task Breakdown:**
- [ ] Frontend captures card details via Stripe Elements (Story 3.2 responsibility)
- [ ] Frontend creates Stripe token (payment method ID) from card
- [ ] Checkout API receives ONLY stripe_token, never raw card data
- [ ] Backend logs: `{ order_id, payment_method_type, last_four_digits, status }`
- [ ] Logs never include: full card number, CVV, PII (full email, full phone)
- [ ] Shipping/billing addresses stored in orders table (not in logs)
- [ ] Stripe handles encryption; backend never touches raw card data
- [ ] GDPR compliant: PII retention policy < 90 days unless subscription active

### AC3: Subscription Data Integration
**Given** a shopper selects a subscription cadence  
**When** checkout is submitted  
**Then** subscription data (cadence, start_date, recurring_price) is persisted  
**And** recurring billing is configured in Stripe (for card subscriptions).

**Task Breakdown:**
- [ ] Accept `subscription` object: `{ cadence, start_date, initial_price, recurring_price }`
- [ ] Create `subscriptions` table record with: subscription_id (UUID), order_id, cadence (enum: one-time, monthly, bi-weekly, three-month), status (active), start_date, next_billing_date
- [ ] For card payments: Create Stripe recurring subscription if cadence != 'one-time'
  - [ ] Stripe subscription_id stored in subscriptions table
  - [ ] Recurring charges scheduled: next_billing_date = start_date + cadence_interval
- [ ] For PIX: Store subscription_id but manual processing for now (future: PIX auto-renewal)
- [ ] For one-time: Set cadence='one-time', no recurring_price, no Stripe subscription
- [ ] On success: Return next_shipment_date to frontend

### AC4: Order Persistence & Audit Trail
**Given** an order is created  
**When** payment is processed  
**Then** all order data is persisted with full audit trail  
**And** order state can be queried and tracked.

**Task Breakdown:**
- [ ] Create PostgreSQL `orders` table:
  - [ ] Columns: order_id (UUID, PK), user_id (UUID, FK), email, status (enum: pending, paid, shipped, delivered, cancelled), cart_items (JSONB), subscription_data (JSONB), shipping_address (JSONB), total_amount (DECIMAL), currency (VARCHAR), created_at (TIMESTAMPTZ), updated_at (TIMESTAMPTZ)
- [ ] Create `order_events` table for audit trail: order_id, event_type (checkout_started, payment_processing, payment_success, payment_failed, shipped, delivered), timestamp, metadata (JSONB)
- [ ] Log order events on state changes (pending → paid, paid → shipped, etc.)
- [ ] Provide GET `/api/orders/{order_id}` endpoint to retrieve order details
- [ ] Status transitions: pending → paid (on success) or pending → failed (on error)

### AC5: Error Handling & Recovery
**Given** payment processing fails or request times out  
**When** checkout endpoint encounters errors  
**Then** error is logged, idempotency key prevents double-charge  
**And** user receives actionable error message.

**Task Breakdown:**
- [ ] Handle Stripe errors: card declined, insufficient funds, expired card, network timeout
- [ ] Handle validation errors: missing fields, invalid address format, invalid email
- [ ] Handle edge cases: duplicate order (same idempotency_key), subscription mismatch, cart expired
- [ ] Return HTTP error codes: 400 (bad request), 402 (payment required), 408 (timeout), 500 (server error)
- [ ] Error response: `{ error_code, error_message, retry_after_seconds, order_id (if partial) }`
- [ ] Log all errors with session_id for troubleshooting (not customer-facing)
- [ ] On payment decline: Log error event, return 402 with "Payment declined. Please try another card."
- [ ] On timeout: Return 408 with "Payment processing took too long. Please retry."
- [ ] Idempotency: If same idempotency_key re-submitted, return previous response (no double-charge)

---

## Implementation Context

### Database Schema

**orders table:**
```sql
CREATE TABLE orders (
  order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,  -- NULL for guest checkout
  email VARCHAR(255) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, paid, failed, shipped, delivered, cancelled
  cart_items JSONB NOT NULL,  -- [{book_id, title, price, quantity}, ...]
  subscription_data JSONB NOT NULL,  -- {cadence, start_date, initial_price, recurring_price, stripe_subscription_id}
  shipping_address JSONB NOT NULL,  -- {name, street, city, state, postal_code, country}
  billing_address JSONB,  -- NULL if same as shipping
  total_amount DECIMAL(10,2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  payment_method VARCHAR(20),  -- card, pix
  payment_details JSONB,  -- {stripe_payment_intent_id, pix_qr_code, last_four_digits}
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT valid_status CHECK (status IN ('pending', 'paid', 'failed', 'shipped', 'delivered', 'cancelled'))
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_email ON orders(email);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);

CREATE TABLE subscriptions (
  subscription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(order_id),
  user_id UUID,
  cadence VARCHAR(20) NOT NULL,  -- one-time, monthly, bi-weekly, three-month
  status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active, paused, cancelled
  start_date DATE NOT NULL,
  next_billing_date DATE NOT NULL,
  stripe_subscription_id VARCHAR(255),  -- Stripe subscription ID for recurring billing
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT valid_cadence CHECK (cadence IN ('one-time', 'monthly', 'bi-weekly', 'three-month'))
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_next_billing_date ON subscriptions(next_billing_date);

CREATE TABLE order_events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(order_id),
  event_type VARCHAR(50) NOT NULL,  -- checkout_started, payment_processing, payment_success, payment_failed, shipped, delivered
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB,  -- {error_code, error_message, stripe_error, reason}
  CONSTRAINT valid_event_type CHECK (event_type IN ('checkout_started', 'payment_processing', 'payment_success', 'payment_failed', 'shipped', 'delivered', 'cancelled'))
);

CREATE INDEX idx_order_events_order_id ON order_events(order_id);
CREATE INDEX idx_order_events_event_type ON order_events(event_type);
```

**order_events table:**
- Audit trail of all state changes
- Helps with troubleshooting and compliance

### API Request/Response

**Request:**
```json
{
  "cart_items": [
    {
      "book_id": "book-001",
      "title": "Midsummer Manor Mystery",
      "author": "Jane Ashworth",
      "price": 14.99,
      "quantity": 1
    }
  ],
  "subscription": {
    "cadence": "monthly",
    "start_date": "2026-07-23",
    "initial_price": 24.99,
    "recurring_price": 24.99
  },
  "shipping_address": {
    "name": "Jane Doe",
    "street": "123 Main Street",
    "city": "Portland",
    "state": "ME",
    "postal_code": "04101",
    "country": "US"
  },
  "billing_address": null,  // Use shipping if null
  "payment_method": "card",
  "stripe_token": "pm_1234567890abcdef",  // Tokenized payment method
  "email": "jane@example.com",
  "phone": "(555) 123-4567",
  "idempotency_key": "uuid-1234-5678-9abc-def0"
}
```

**Response (Success):**
```json
{
  "order_id": "order-uuid-123",
  "status": "paid",
  "total_amount": 24.99,
  "currency": "USD",
  "payment_method": "card",
  "last_four_digits": "4242",
  "subscription": {
    "cadence": "monthly",
    "next_billing_date": "2026-07-23",
    "stripe_subscription_id": "sub_123456"
  },
  "shipping_address": {
    "name": "Jane Doe",
    "city": "Portland"
  },
  "receipt_url": "https://example.com/receipts/order-uuid-123",
  "next_shipment_date": "2026-07-15",
  "created_at": "2026-06-23T11:05:34Z"
}
```

**Response (PIX):**
```json
{
  "order_id": "order-uuid-456",
  "status": "awaiting_pix_confirmation",
  "payment_method": "pix",
  "pix_qr_code": "00020126360014br.gov.bcb.brcode...",
  "pix_copy_paste": "00020126360014br.gov.bcb.brcode...",
  "pix_request_id": "pix-123456",
  "expires_at": "2026-06-23T12:05:34Z",
  "total_amount": 24.99,
  "currency": "BRL"
}
```

### Stripe Integration

**Payment Flow:**
1. Frontend collects card via Stripe Elements
2. Frontend creates payment method token (stripe_token)
3. Frontend sends token + order data to `/api/checkout`
4. Backend receives token, validates, creates Stripe payment intent
5. Stripe processes payment, returns confirmation
6. Backend updates order status → paid, returns receipt

**Stripe Configuration:**
- API key stored in env variable: `STRIPE_SECRET_KEY`
- Publishable key in frontend: `STRIPE_PUBLISHABLE_KEY`
- PIX support requires Stripe test mode (US-based account doesn't support PIX; use test data)

### PIX Integration (Brazil)

**PIX Flow:**
1. Backend calls PIX API (or Stripe PIX) to generate QR code
2. Returns QR code + copy-paste code to frontend
3. User scans QR or enters copy-paste code in banking app
4. Bank processes payment
5. Webhook confirms payment, updates order status
6. Backend marks order as paid

**Note:** For MVP, PIX implementation uses mock/test QR codes. Production requires PIX API integration (Brcode, central bank).

---

## Testing Requirements

### Unit Tests (Python - checkout_service.py)

- [ ] `test_validate_cart_items()` – Rejects empty cart, invalid prices
- [ ] `test_validate_shipping_address()` – Checks required fields, postal code format
- [ ] `test_validate_payment_method()` – Accepts card and PIX, rejects unknown
- [ ] `test_calculate_order_total()` – Sums cart items + kit fee, applies tax if applicable
- [ ] `test_idempotency_key_prevents_double_charge()` – Same key returns cached response
- [ ] `test_subscription_data_persisted()` – Subscription record created with correct cadence

### Integration Tests (FastAPI - /api/checkout)

- [ ] `test_checkout_card_payment_success()` – Valid card token → order created, status=paid
- [ ] `test_checkout_card_payment_declined()` – Declined card → 402 error, order status=failed
- [ ] `test_checkout_pix_payment_requested()` – PIX method → QR code generated, status=awaiting_pix
- [ ] `test_checkout_missing_fields()` – Missing email → 400 error
- [ ] `test_checkout_invalid_address()` – Blank street → 400 error
- [ ] `test_checkout_response_time()` – Card payment < 2s (p95)
- [ ] `test_order_persisted_in_database()` – Order record created with all fields
- [ ] `test_order_events_logged()` – Event records created for each state change

### Database Tests

- [ ] `test_orders_table_created()` – Schema correct, indices present
- [ ] `test_subscriptions_table_created()` – Foreign key constraints work
- [ ] `test_order_status_constraint()` – Invalid status rejected

### Security Tests

- [ ] No raw card data in logs
- [ ] No PII in error messages
- [ ] Stripe token used, never raw card number
- [ ] HTTPS enforced for checkout endpoint
- [ ] CORS restricted to allowed domains

### Performance Tests

- [ ] Order creation < 500ms
- [ ] Stripe API call < 1.5s (p95)
- [ ] Database query < 100ms
- [ ] Full checkout flow < 2s (p95)

---

## Developer Implementation Checklist

### Flask/FastAPI Checkout Service (checkout_service.py)

- [ ] Create `Order` dataclass with order_id, status, cart_items, subscription
- [ ] Implement `validate_cart_items(cart)` – Check not empty, valid prices
- [ ] Implement `validate_address(address)` – Check required fields, format
- [ ] Implement `calculate_order_total(cart_items, subscription)` – Sum amounts
- [ ] Implement `create_order(order_data) -> Order` – Insert into DB
- [ ] Implement `process_stripe_payment(token, amount) -> Dict` – Call Stripe API
- [ ] Implement `generate_pix_qr_code(amount) -> Dict` – Generate mock/real PIX QR
- [ ] Implement `handle_idempotency(key, request)` – Check cache, return if exists

### Flask Checkout Endpoint

- [ ] POST `/api/checkout` route
- [ ] Validate request JSON schema
- [ ] Load cart from request body
- [ ] Validate all required fields
- [ ] Call checkout_service functions
- [ ] Handle errors with appropriate HTTP codes
- [ ] Return formatted JSON response
- [ ] Log order_events for audit trail

### Database Setup

- [ ] Create orders table with schema
- [ ] Create subscriptions table
- [ ] Create order_events table
- [ ] Set up indices
- [ ] Run migration script

### Environment Configuration

- [ ] STRIPE_SECRET_KEY from .env
- [ ] STRIPE_PUBLISHABLE_KEY for frontend
- [ ] Database connection string
- [ ] Idempotency cache (Redis or in-memory for MVP)

### Logging & Monitoring

- [ ] Log order creation: order_id, email, total_amount
- [ ] Log payment events: order_id, payment_method, status
- [ ] Log errors: error_code, order_id, timestamp
- [ ] Metrics: checkout success rate, average time, error rate

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Checkout success rate | >= 98% | Successful payments / total attempts |
| Card payment latency p95 | < 2s | Measure 1000 successful card payments |
| PIX payment latency p95 | < 5s | Measure PIX QR generation + return |
| PII protection | 100% | Audit logs for raw card data (must be zero) |
| Order persistence | 100% | All paid orders appear in database |
| Idempotency accuracy | 100% | Same key never double-charges |

---

## Deployment and Handoff

**Story Status Transitions:**
- [ ] Implement: Status remains `ready-for-dev`
- [ ] Submit for review: Update to `Status: review`
- [ ] Code review complete: Update to `Status: done`

**File Updates After Implementation:**
- Create `_bmad-output/implementation-artifacts/checkout/checkout_service.py`
- Update `_bmad-output/implementation-artifacts/nlu/app.py` with `/api/checkout` endpoint
- Create `_bmad-output/implementation-artifacts/checkout/001_create_orders_tables.sql`
- Update `docs/api-specs.yaml` with /api/checkout endpoint documentation
- Commit: `Story 3.1: Checkout API with tokenized payments and PIX support`

**Next Story:** Story 3.2 (Direct Checkout UX from Mini-Cart)

---

## References

- **PRD:** _bmad-output/implementation-artifacts/prd-blind-date-book.md sections 9, 10, 11
- **Architecture:** _bmad-output/implementation-artifacts/architecture/architecture.md
- **Stripe Docs:** https://stripe.com/docs/payments
- **Story Context:** _bmad-output/planning-artifacts/epics.md (Epic 3 Story 3.1)
