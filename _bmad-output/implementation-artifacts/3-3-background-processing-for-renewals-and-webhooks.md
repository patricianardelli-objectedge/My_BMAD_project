# Story 3.3: Background Processing for Renewals and Webhooks

**Epic:** Fast & Secure Checkout  
**Status:** ready-for-dev  
**Created:** 2026-06-23  

---

## Story Summary

As the Blind Date Book service, I want to process subscription renewals in the background and handle payment webhooks, so that recurring subscriptions work automatically without customer intervention.

**Dependencies:** Story 3.1 (Checkout API) – Creates subscriptions and Stripe subscription IDs.

**References:** FR5, FR10, NFR5, NFR9

**Source Documents:**
- PRD sections 10, 11
- Architecture sections 5, 9
- docs/api-specs.yaml

---

## Acceptance Criteria

### AC1: Stripe Webhook Handler for Payment Events
**Given** a customer's subscription payment is processed  
**When** Stripe sends a webhook event (payment_intent.succeeded, charge.failed)  
**Then** the webhook endpoint receives and processes the event  
**And** order status is updated accordingly.

**Task Breakdown:**
- [ ] POST `/api/webhooks/stripe` endpoint that accepts Stripe webhook events
- [ ] Verify webhook signature using Stripe secret
- [ ] Handle events:
  - [ ] `payment_intent.succeeded` → Update order status to `paid`
  - [ ] `charge.failed` → Update order status to `failed`, log reason
  - [ ] `customer.subscription.updated` → Update subscription metadata
  - [ ] `customer.subscription.deleted` → Update subscription status to `cancelled`
- [ ] Create `webhook_events` table for audit trail: event_id, stripe_event_id, event_type, timestamp, status (processed/failed)
- [ ] Log webhook event: event_id, order_id, event_type, status
- [ ] Response: Return 200 OK to Stripe immediately (async processing)
- [ ] Retry failed webhooks: Store failed events, retry up to 3 times with exponential backoff
- [ ] Response time: < 1s before returning 200 OK to Stripe

### AC2: Subscription Renewal Scheduler
**Given** a subscription with monthly/bi-weekly/3-month cadence  
**When** the next billing date arrives  
**Then** a renewal order is created automatically  
**And** payment is charged via Stripe subscription.

**Task Breakdown:**
- [ ] Background job (APScheduler or Celery): Runs daily at 2 AM UTC
- [ ] Job finds all subscriptions with status=active and next_billing_date <= today
- [ ] For each subscription:
  - [ ] Create new order: copy previous order's cart_items, set status=pending
  - [ ] Update previous subscription: next_billing_date += interval (30 days for monthly, 14 for bi-weekly, 90 for 3-month)
  - [ ] If Stripe subscription_id exists:
    - [ ] Stripe handles recurring charge automatically (no manual call needed)
    - [ ] On webhook: payment_intent.succeeded updates new order status → paid
  - [ ] If no Stripe subscription (PIX or manual):
    - [ ] Send email reminder: "Your subscription renewal is due. Click here to pay."
    - [ ] Manual payment needed (future: auto-refresh via PIX API)
- [ ] Log renewal job: `{ job_id, subscriptions_processed, renewals_created, timestamp }`
- [ ] Handle errors: If renewal fails, log error, send alert to ops

### AC3: Payment Failure Handling & Retry Logic
**Given** a subscription renewal payment fails (card expired, insufficient funds)  
**When** Stripe webhook reports charge.failed  
**Then** the order status is set to failed  
**And** customer is notified to update payment method.

**Task Breakdown:**
- [ ] Webhook event `charge.failed` updates order status → `failed`
- [ ] Log failure reason: card_declined, expired_card, insufficient_funds, etc.
- [ ] Send email to customer: "Payment failed. Please update your payment method."
- [ ] Retry logic: Stripe handles retries (2-3 attempts over 3 days) based on failure type
- [ ] After final retry failure: Set subscription status → `payment_failed`
- [ ] Email reminder: "Your subscription is paused. Update payment to resume deliveries."
- [ ] UI endpoint GET `/api/subscriptions/{subscription_id}/update-payment` for customer self-service
- [ ] If payment succeeds after pause: Reactivate subscription, resume shipments

### AC4: Webhook Event Logging & Auditing
**Given** webhooks are processed  
**When** each webhook is received and processed  
**Then** full audit trail is created for compliance  
**And** webhook events can be queried and retried.

**Task Breakdown:**
- [ ] `webhook_events` table: event_id (UUID), stripe_event_id (from Stripe), event_type, resource_type (charge, customer, subscription), resource_id (order_id or subscription_id), status (received, processing, processed, failed), created_at, processed_at, error_message (if failed)
- [ ] Log every webhook received (even before processing)
- [ ] Log processing result: success or failure reason
- [ ] Indices: stripe_event_id (unique), status, created_at DESC
- [ ] Provide admin endpoint: GET `/api/admin/webhooks/events` to query webhook history
- [ ] Support webhook replay: POST `/api/admin/webhooks/replay/{event_id}` for manual retry
- [ ] Never process same event twice (Stripe ensures unique event_id, check for duplicates)

### AC5: Subscription Status Lifecycle
**Given** a subscription exists in various states  
**When** events occur (payment success, cancellation, pause)  
**Then** subscription status transitions correctly  
**And** each state is well-defined.

**Task Breakdown:**
- [ ] Subscription status enum: active, paused, cancelled, payment_failed
- [ ] State transitions:
  - [ ] active → paused: Payment failed, awaiting customer action
  - [ ] paused → active: Payment updated, resuming shipments
  - [ ] active → cancelled: Customer requested cancellation
  - [ ] active → payment_failed: Multiple failed payment attempts
  - [ ] any → cancelled: Never reverts (final state)
- [ ] GET `/api/subscriptions/{subscription_id}` returns: subscription details, current status, next_billing_date, payment_status, error_message (if any)
- [ ] PATCH `/api/subscriptions/{subscription_id}` accepts: action (pause, resume, cancel), reason (optional)
- [ ] Cancellation: Set status=cancelled, next_billing_date=null, log reason
- [ ] Logging: Log state change with timestamp, reason, user_id (if customer-initiated)

---

## Implementation Context

### Webhook Flow

**Stripe → Webhook Endpoint:**
```
1. Customer's card is charged (subscription renewal)
2. Stripe processes payment
3. Stripe sends webhook: payment_intent.succeeded
4. Backend receives webhook at POST /api/webhooks/stripe
5. Backend verifies signature (using STRIPE_WEBHOOK_SECRET)
6. Backend processes event:
   - Find order by payment_intent_id
   - Update order status → paid
   - Create order_event: payment_success
7. Return 200 OK immediately
8. Async: Log event, update subscription next_billing_date
```

**Webhook Event Structure:**
```json
{
  "id": "evt_1234567890",
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_1234567890",
      "amount": 2499,
      "charges": {
        "data": [
          {
            "id": "ch_1234567890",
            "amount": 2499,
            "status": "succeeded",
            "payment_method_details": {
              "card": {
                "last4": "4242"
              }
            }
          }
        ]
      },
      "metadata": {
        "order_id": "order-uuid-123"
      }
    }
  },
  "created": 1687534800
}
```

### Renewal Job Flow

**Daily at 2 AM UTC:**
```
1. Job starts: SELECT subscriptions WHERE status=active AND next_billing_date <= NOW()
2. For each subscription:
   a. Get original order (find by subscription's order_id)
   b. Create new renewal order with same cart_items, new order_id
   c. If stripe_subscription_id exists:
      - Stripe auto-charges customer (already set up)
      - Wait for webhook: payment_intent.succeeded
      - On webhook: Update new order status → paid
   d. Update subscription.next_billing_date += interval
3. Log results: X subscriptions renewed, Y payment failures
4. Send alerts if failures > threshold
```

### Database Schema

**webhook_events table:**
```sql
CREATE TABLE webhook_events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_event_id VARCHAR(255) UNIQUE NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  resource_type VARCHAR(50),  -- charge, customer, subscription, payment_intent
  resource_id VARCHAR(255),  -- order_id or subscription_id
  order_id UUID REFERENCES orders(order_id),
  subscription_id UUID REFERENCES subscriptions(subscription_id),
  status VARCHAR(20) NOT NULL DEFAULT 'received',  -- received, processing, processed, failed
  payload JSONB,  -- Full webhook payload
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  CONSTRAINT valid_status CHECK (status IN ('received', 'processing', 'processed', 'failed'))
);

CREATE INDEX idx_webhook_events_stripe_event_id ON webhook_events(stripe_event_id);
CREATE INDEX idx_webhook_events_order_id ON webhook_events(order_id);
CREATE INDEX idx_webhook_events_subscription_id ON webhook_events(subscription_id);
CREATE INDEX idx_webhook_events_status ON webhook_events(status);
CREATE INDEX idx_webhook_events_created_at ON webhook_events(created_at DESC);

-- Add to subscriptions table:
ALTER TABLE subscriptions ADD COLUMN stripe_subscription_id VARCHAR(255);
ALTER TABLE subscriptions ADD COLUMN payment_status VARCHAR(50) DEFAULT 'pending';  -- pending, active, failed, paused
ALTER TABLE subscriptions ADD COLUMN error_message TEXT;
```

**renewal_jobs table (audit):**
```sql
CREATE TABLE renewal_jobs (
  job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_date DATE NOT NULL,
  subscriptions_found INT,
  renewals_created INT,
  renewal_failures INT,
  status VARCHAR(20) DEFAULT 'completed',  -- completed, failed
  error_message TEXT,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  CONSTRAINT valid_status CHECK (status IN ('completed', 'failed'))
);

CREATE INDEX idx_renewal_jobs_job_date ON renewal_jobs(job_date DESC);
CREATE INDEX idx_renewal_jobs_status ON renewal_jobs(status);
```

### Renewal Job Pseudocode

```python
@scheduler.scheduled_job('cron', hour=2, minute=0, timezone='UTC')
def process_subscription_renewals():
    job = RenewalJob(job_date=today())
    
    try:
        # Find subscriptions due for renewal
        subscriptions = Subscription.query.filter(
            status='active',
            next_billing_date <= today()
        ).all()
        
        job.subscriptions_found = len(subscriptions)
        
        for subscription in subscriptions:
            try:
                # Get previous order for cart_items
                previous_order = Order.get_by_id(subscription.order_id)
                
                # Create new renewal order
                renewal_order = Order(
                    order_id=uuid.uuid4(),
                    cart_items=previous_order.cart_items,
                    subscription_data={...},
                    status='pending',
                    created_at=now()
                )
                db.session.add(renewal_order)
                
                # Update subscription next_billing_date
                interval = get_interval_days(subscription.cadence)  # 30, 14, 90
                subscription.next_billing_date += timedelta(days=interval)
                
                # Stripe handles charge via subscription (already set up)
                # Webhook will update order status when payment succeeds
                
                job.renewals_created += 1
                log_event('subscription_renewal', subscription.id, renewal_order.id)
                
            except Exception as e:
                job.renewal_failures += 1
                log_error(f"Renewal failed for {subscription.id}: {str(e)}")
        
        db.session.commit()
        job.status = 'completed'
        job.completed_at = now()
        
    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        log_alert(f"Renewal job failed: {str(e)}")
    
    finally:
        db.session.add(job)
        db.session.commit()
```

### Webhook Handler Pseudocode

```python
@app.route('/api/webhooks/stripe', methods=['POST'])
def handle_stripe_webhook():
    try:
        # Get webhook signature from header
        sig = request.headers.get('Stripe-Signature')
        
        # Verify signature
        event = stripe.Webhook.construct_event(
            request.data, sig, STRIPE_WEBHOOK_SECRET
        )
        
        # Log webhook received
        webhook_event = WebhookEvent(
            stripe_event_id=event['id'],
            event_type=event['type'],
            status='received',
            payload=event
        )
        db.session.add(webhook_event)
        db.session.commit()
        
        # Process event
        if event['type'] == 'payment_intent.succeeded':
            order_id = event['data']['object']['metadata'].get('order_id')
            order = Order.get_by_id(order_id)
            if order:
                order.status = 'paid'
                db.session.commit()
                webhook_event.status = 'processed'
        
        elif event['type'] == 'charge.failed':
            # Handle payment failure
            order_id = event['data']['object']['metadata'].get('order_id')
            order = Order.get_by_id(order_id)
            if order:
                order.status = 'failed'
                # Send email to customer
                send_email(order.email, "Payment failed...")
                db.session.commit()
                webhook_event.status = 'processed'
        
        db.session.commit()
        return jsonify({'success': True}), 200
        
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        log_error(f"Webhook processing error: {str(e)}")
        return jsonify({'error': 'Processing error'}), 500
```

---

## Testing Requirements

### Unit Tests (Python - webhook_handler.py, renewal_scheduler.py)

- [ ] `test_webhook_signature_verification()` – Valid sig accepted, invalid rejected
- [ ] `test_payment_intent_succeeded_updates_order()` – Order status → paid
- [ ] `test_charge_failed_updates_order()` – Order status → failed
- [ ] `test_duplicate_webhook_not_processed()` – Same event_id processed once
- [ ] `test_renewal_job_finds_due_subscriptions()` – Correct subs selected
- [ ] `test_renewal_creates_new_order()` – New order created with same items
- [ ] `test_renewal_updates_next_billing_date()` – Date incremented correctly
- [ ] `test_renewal_handles_failure()` – Failed renewal logged, alert sent
- [ ] `test_subscription_status_transitions()` – active → paused, paused → active, etc.

### Integration Tests (Webhook Endpoint)

- [ ] `test_webhook_payment_success_updates_order()` – End-to-end payment confirmation
- [ ] `test_webhook_payment_failure_sends_email()` – Customer notified of failure
- [ ] `test_webhook_invalid_signature_rejected()` – 400 response
- [ ] `test_webhook_response_time_under_1s()` – Returns 200 OK quickly
- [ ] `test_renewal_job_runs_daily()` – Scheduler triggers at 2 AM UTC
- [ ] `test_renewal_job_creates_orders()` – New orders in DB after job

### Database Tests

- [ ] `test_webhook_events_table_created()` – Schema correct
- [ ] `test_renewal_jobs_table_created()` – Schema correct
- [ ] `test_webhook_unique_constraint()` – Duplicate stripe_event_id rejected
- [ ] `test_subscription_status_enum()` – Invalid status rejected

### Security Tests

- [ ] Webhook signature verification mandatory
- [ ] Invalid signatures return 400
- [ ] No sensitive data in logs
- [ ] Webhook events logged with full payload (for audit)
- [ ] Webhook replay protected (same event_id never double-processed)

### Performance Tests

- [ ] Webhook processing < 1s
- [ ] Renewal job < 30s for 1000 subscriptions
- [ ] Database queries < 100ms per subscription
- [ ] Email sending async (doesn't block webhook response)

---

## Developer Implementation Checklist

### Stripe Webhook Handler (webhook_handler.py)

- [ ] Create `WebhookEvent` dataclass
- [ ] Implement `verify_webhook_signature(request)` – Verify Stripe sig
- [ ] Implement `process_payment_intent_succeeded(event)` – Update order status
- [ ] Implement `process_charge_failed(event)` – Log failure, send email
- [ ] Implement `process_subscription_updated(event)` – Update metadata
- [ ] Implement `log_webhook_event(event, status)` – Insert into DB
- [ ] Error handling: Log failed webhooks, allow retry

### Flask Webhook Endpoint

- [ ] POST `/api/webhooks/stripe` route
- [ ] Accept request body and headers
- [ ] Verify signature (use `stripe.Webhook.construct_event`)
- [ ] Call appropriate handler based on event type
- [ ] Return 200 OK immediately
- [ ] Async processing: Log, email, DB updates in background

### Renewal Scheduler (renewal_scheduler.py)

- [ ] Import APScheduler or Celery
- [ ] Implement renewal job function
- [ ] Schedule daily at 2 AM UTC
- [ ] Query subscriptions due for renewal
- [ ] For each subscription: Create order, update next_billing_date
- [ ] Handle errors: Log failures, send alerts
- [ ] Log job metrics: subscriptions_found, renewals_created, failures

### Database Migrations

- [ ] Create `webhook_events` table
- [ ] Create `renewal_jobs` table
- [ ] Add `stripe_subscription_id` to subscriptions
- [ ] Add `payment_status` to subscriptions
- [ ] Create indices for performance

### Configuration

- [ ] STRIPE_WEBHOOK_SECRET from env
- [ ] Renewal job schedule in config
- [ ] Email service for notifications
- [ ] Logging configuration

### Subscription Lifecycle Endpoints

- [ ] GET `/api/subscriptions/{id}` – Retrieve subscription status
- [ ] PATCH `/api/subscriptions/{id}` – Pause/resume/cancel
- [ ] POST `/api/subscriptions/{id}/update-payment` – Customer updates payment method

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Webhook processing latency | < 1s | P95 response time to Stripe |
| Webhook success rate | >= 99% | Successfully processed / received |
| Renewal job reliability | >= 99% | Successful renewals / due renewals |
| Payment failure detection | 100% | All failures logged and emailed |
| Webhook event uniqueness | 100% | No duplicate processing |
| Subscription status accuracy | 100% | Status matches order state |

---

## Deployment and Handoff

**Story Status Transitions:**
- [ ] Implement: Status remains `ready-for-dev`
- [ ] Submit for review: Update to `Status: review`
- [ ] Code review complete: Update to `Status: done`

**File Updates After Implementation:**
- Create `checkout/webhook_handler.py`
- Create `checkout/renewal_scheduler.py`
- Update `nlu/app.py` with webhook endpoint
- Create `checkout/001_webhook_events_table.sql` migration
- Update `docs/api-specs.yaml` with webhook documentation
- Commit: `Story 3.3: Background processing for renewals and webhooks`

**Epic 3 Complete!**

---

## References

- **Stripe Webhooks:** https://stripe.com/docs/webhooks
- **Stripe Subscriptions:** https://stripe.com/docs/billing/subscriptions/create
- **APScheduler:** https://apscheduler.readthedocs.io/
- **PRD:** _bmad-output/implementation-artifacts/prd-blind-date-book.md sections 10, 11
- **Story Context:** _bmad-output/planning-artifacts/epics.md (Epic 3 Story 3.3)
