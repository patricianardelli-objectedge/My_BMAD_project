# Story 4.3: Subscription Lifecycle Controls

**Epic:** User Profile & Preferences  
**Status:** ready-for-dev  
**Created:** 2026-06-23  

---

## Story Summary

As a subscriber, I want to pause, resume, or cancel my subscription anytime, so that I have full control over my blind date book deliveries and can adjust based on my reading pace.

**Dependencies:** Story 3.1-3.3 (Checkout & Renewals), Story 4.1 (User Profile) – Supplies subscription data and user management.

**References:** FR5, FR10, NFR5, NFR9

**Source Documents:**
- PRD sections 5, 10, 11
- Architecture sections 5, 9
- docs/api-specs.yaml

---

## Acceptance Criteria

### AC1: Pause Subscription
**Given** a subscriber with an active subscription  
**When** they click "Pause" on the subscription management page  
**Then** subscription status changes to "paused"  
**And** no renewal charges occur until resumed  
**And** pause reason is optional (e.g., "reading backlog", "temporary").

**Task Breakdown:**
- [ ] PATCH `/api/subscriptions/{subscription_id}` accepts action='pause', optional reason
- [ ] Update subscription status: active → paused
- [ ] Update `next_billing_date`: Set to null (no billing while paused)
- [ ] Email confirmation: "Your subscription has been paused. Restart anytime."
- [ ] Log pause event: user_id, reason, timestamp
- [ ] If paused at renewal time: Cancel scheduled charge immediately
- [ ] If paused during Stripe cycle: Contact Stripe to cancel upcoming charge
- [ ] UI shows: "Your subscription is paused. Next kit ships when you resume."
- [ ] Display date/reason for pause in profile

### AC2: Resume Subscription
**Given** a paused subscription  
**When** user clicks "Resume"  
**Then** subscription status changes back to active  
**And** next_billing_date is set to next occurrence  
**And** billing resumes normally.

**Task Breakdown:**
- [ ] PATCH `/api/subscriptions/{subscription_id}` accepts action='resume'
- [ ] Update status: paused → active
- [ ] Calculate next_billing_date: today + cadence_interval
- [ ] If subscription has Stripe ID: Resume Stripe subscription (update next_billing_date)
- [ ] Email confirmation: "Your subscription has resumed. Next kit ships on [date]."
- [ ] Log resume event: user_id, timestamp
- [ ] Clear pause_reason field
- [ ] UI shows: "Subscription active. Next shipment: [date]"

### AC3: Cancel Subscription
**Given** a subscriber with active or paused subscription  
**When** they click "Cancel"  
**Then** a confirmation modal appears  
**And** after confirmation, subscription is permanently cancelled  
**And** no future charges occur.

**Task Breakdown:**
- [ ] PATCH `/api/subscriptions/{subscription_id}` accepts action='cancel', optional feedback_reason
- [ ] Confirmation modal: "Are you sure? You can't undo this. Would you like to tell us why?" (optional feedback)
- [ ] Update status: active/paused → cancelled
- [ ] Set next_billing_date: null
- [ ] If Stripe subscription_id exists: Call Stripe to cancel subscription
- [ ] Email confirmation: "Your subscription has been cancelled. You won't be charged again."
- [ ] Collect feedback (optional): "Why are you cancelling?" (dropdown: too-expensive, reading-pace, disappointed, other)
- [ ] Log cancellation: user_id, reason, feedback, timestamp
- [ ] UI shows: "Subscription cancelled. (Resubscribe)"

### AC4: Subscription Status Dashboard
**Given** a logged-in subscriber on their profile  
**When** they view subscription details  
**Then** they see: current cadence, next shipment date, status, pause/resume/cancel buttons  
**And** can perform actions directly.

**Task Breakdown:**
- [ ] Profile page section: "Subscription Status"
- [ ] Display:
  - [ ] Cadence: "Monthly" / "Bi-weekly" / "3-month"
  - [ ] Status badge: Active (green), Paused (yellow), Cancelled (gray)
  - [ ] Next shipment: "[Date]" or "Paused" or "Cancelled"
  - [ ] Action buttons: Pause / Resume / Cancel (shown based on status)
  - [ ] Edit cadence: "Change to..." dropdown (monthly ↔ bi-weekly ↔ 3-month)
  - [ ] Billing history: "Manage payment method", "View receipts"
- [ ] Status-specific UI:
  - [ ] Active: "Pause | Cancel"
  - [ ] Paused: "Resume | Cancel"
  - [ ] Cancelled: "Resubscribe"
- [ ] Mobile responsive: Buttons stack vertically

### AC5: Graceful Handling of Edge Cases
**Given** various subscription edge cases  
**When** user attempts actions or state changes occur  
**Then** system handles safely with clear messaging  
**And** data remains consistent.

**Task Breakdown:**
- [ ] Cancel during renewal window: Verify Stripe cancellation processed
- [ ] Pause, then payment attempt fails: Mark as payment_failed, not paused
- [ ] Resume with expired card: Show "Update payment method first" message
- [ ] Multiple pause/resume within 1 hour: Prevent action, show rate-limit message
- [ ] Cancel already-cancelled subscription: Return 409 conflict, no error
- [ ] Subscription with no Stripe ID (PIX): Handle manually (email notification to ops)
- [ ] User logged out, session expires: Redirect to login, preserve intent
- [ ] Network timeout during cancel: Retry, verify state in DB before confirming
- [ ] Webhook confirms cancellation after UI close: Update UI on next load

---

## Implementation Context

### API Endpoints

**Subscription Management:**
- GET `/api/subscriptions/{subscription_id}` – Get subscription status
- PATCH `/api/subscriptions/{subscription_id}` – Update (pause/resume/cancel)
- GET `/api/users/{user_id}/subscriptions` – List all user subscriptions

### Request/Response Examples

**Pause Subscription:**
```json
PATCH /api/subscriptions/sub-uuid-123
{
  "action": "pause",
  "reason": "reading-backlog"  // optional
}

Response:
{
  "subscription_id": "sub-uuid-123",
  "status": "paused",
  "cadence": "monthly",
  "paused_at": "2026-06-23T12:00:00Z",
  "pause_reason": "reading-backlog",
  "message": "Your subscription is paused. Resume anytime from your profile."
}
```

**Resume Subscription:**
```json
PATCH /api/subscriptions/sub-uuid-123
{
  "action": "resume"
}

Response:
  "subscription_id": "sub-uuid-123",
  "status": "active",
  "next_billing_date": "2026-07-23",
  "message": "Your subscription has resumed. Next kit ships on July 23, 2026."
}
```

**Cancel Subscription:**
```json
PATCH /api/subscriptions/sub-uuid-123
{
  "action": "cancel",
  "feedback_reason": "too-expensive"  // optional
}

Response (requires confirmation first):
{
  "confirmation_required": true,
  "message": "Are you sure? You can't undo this. After confirmation, no further charges will occur."
}

// After confirmation:
{
  "subscription_id": "sub-uuid-123",
  "status": "cancelled",
  "next_billing_date": null,
  "cancelled_at": "2026-06-23T12:05:00Z",
  "message": "Your subscription has been cancelled."
}
```

### State Transition Diagram

```
         Resume
          ←――――
         │     ↑
         ↓     │
    [Active] ⟷ [Paused]
         ↓         ↓
         └→ [Cancelled] ←―
              (final state)
```

### Stripe Integration

**Cancel Subscription:**
```python
import stripe

stripe.Subscription.delete(
  subscription_id,
  invoice_settings={'custom_fields': [{...}]}
)
```

**Update Subscription (Resume):**
```python
stripe.Subscription.modify(
  subscription_id,
  pause_collection=False  # Resume billing
)
```

---

## Testing Requirements

### Unit Tests

- [ ] `test_pause_subscription_success()` – Status changes to paused, billing_date nulled
- [ ] `test_pause_already_paused()` – Idempotent, no error
- [ ] `test_pause_with_reason_logged()` – Reason stored in DB
- [ ] `test_resume_subscription_success()` – Status changes to active, next_billing_date set
- [ ] `test_resume_calculates_correct_date()` – Cadence interval applied
- [ ] `test_cancel_subscription_success()` – Status changes to cancelled
- [ ] `test_cancel_already_cancelled()` – 409 conflict, safe
- [ ] `test_cancel_feedback_stored()` – Feedback reason logged
- [ ] `test_stripe_subscription_paused()` – Stripe pause_collection updated
- [ ] `test_stripe_subscription_resumed()` – Stripe subscription reactivated

### Integration Tests

- [ ] `test_pause_prevents_next_charge()` – Next renewal job skips paused subscriptions
- [ ] `test_resume_resumes_charges()` – Renewal job processes resumed subscriptions
- [ ] `test_cancel_stops_all_charges()` – Stripe cancellation verified
- [ ] `test_pause_cancel_resume_flow()` – Full lifecycle works
- [ ] `test_subscription_page_shows_status()` – UI displays correct state
- [ ] `test_buttons_shown_based_on_status()` – Active shows Pause, Paused shows Resume

### UI Tests

- [ ] Pause button opens modal, shows confirmation
- [ ] Resume button works, confirms on profile
- [ ] Cancel button shows warning, requires confirmation
- [ ] Status badge updates immediately after action
- [ ] Next shipment date updates on resume
- [ ] Mobile: Buttons stack vertically
- [ ] Error message displays on network failure

### Performance Tests

- [ ] Pause/resume/cancel API response < 500ms
- [ ] Stripe API call latency < 2s (p95)
- [ ] Profile page load < 500ms with subscription data
- [ ] Bulk cancellation (1000 subscriptions) completes in < 30s

---

## Developer Implementation Checklist

### Flask Subscription Lifecycle Service

- [ ] Implement `pause_subscription(subscription_id, reason) -> bool`
- [ ] Implement `resume_subscription(subscription_id) -> bool`
- [ ] Implement `cancel_subscription(subscription_id, feedback) -> bool`
- [ ] Implement `get_subscription_status(subscription_id) -> dict`
- [ ] Implement `update_stripe_subscription(subscription_id, action) -> bool`
- [ ] Implement `validate_subscription_action(subscription_id, action) -> tuple(bool, error)`

### Flask Subscription Endpoints

- [ ] GET `/api/subscriptions/{subscription_id}` route
- [ ] PATCH `/api/subscriptions/{subscription_id}` route (pause/resume/cancel)
- [ ] GET `/api/users/{user_id}/subscriptions` route

### Stripe Integration

- [ ] Handle `pause_collection` for pause action
- [ ] Resume with `pause_collection=False`
- [ ] Delete subscription for cancel
- [ ] Verify actions in Stripe dashboard
- [ ] Error handling for Stripe API failures

### Frontend - Subscription Management UI

- [ ] Profile section: "Subscription Status"
- [ ] Display current cadence, next shipment, status
- [ ] Pause button: Opens confirmation, calls PATCH endpoint
- [ ] Resume button: Calls PATCH endpoint, updates UI
- [ ] Cancel button: Opens warning modal, collects feedback, calls endpoint
- [ ] Status badges: Active (green), Paused (yellow), Cancelled (gray)
- [ ] Confirmation modals with clear messaging
- [ ] Loading states during API calls
- [ ] Success/error notifications

### Database Updates

- [ ] Add columns to subscriptions: paused_at, pause_reason, cancelled_at, cancellation_feedback
- [ ] Create subscription_lifecycle_events table: subscription_id, event_type, timestamp, metadata
- [ ] Add indices on status, updated_at for query performance

### Email Notifications

- [ ] Email on pause: Subject "Your subscription is paused"
- [ ] Email on resume: Subject "Your subscription has resumed"
- [ ] Email on cancel: Subject "Your subscription has been cancelled"
- [ ] Include next shipment date or resubscribe link

### Logging & Monitoring

- [ ] Log pause/resume/cancel events
- [ ] Monitor cancellation rate (churn metric)
- [ ] Alert on bulk cancellations (> 10 in 1 hour)
- [ ] Track feedback reasons for product insights

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Pause/Resume success rate | >= 98% | Successful actions / attempts |
| Cancel confirmation rate | >= 95% | Users confirm cancellation / start |
| Time to pause action | < 500ms | API response time p95 |
| Stripe sync accuracy | 100% | Stripe state matches DB |
| Churn rate | < 5% | Cancelled subscriptions / active |
| Pause → Resume recovery | >= 40% | Paused users who resume / total paused |

---

## Deployment and Handoff

**Story Status Transitions:**
- [ ] Implement: Status remains `ready-for-dev`
- [ ] Submit for review: Update to `Status: review`
- [ ] Code review complete: Update to `Status: done`

**File Updates After Implementation:**
- Create `_bmad-output/implementation-artifacts/user/subscription_lifecycle_service.py`
- Update `_bmad-output/implementation-artifacts/nlu/app.py` with subscription endpoints
- Create `_bmad-output/implementation-artifacts/user/001_add_subscription_lifecycle_columns.sql`
- Update `frontend/profile.html` with subscription management UI
- Update `docs/api-specs.yaml` with subscription endpoints
- Commit: `Story 4.3: Subscription lifecycle controls`

**Epic 4 Complete!**

---

## References

- **PRD:** _bmad-output/implementation-artifacts/prd-blind-date-book.md sections 5, 10, 11
- **Architecture:** _bmad-output/implementation-artifacts/architecture/architecture.md
- **Stripe Billing:** https://stripe.com/docs/billing/subscriptions
- **Story Context:** _bmad-output/planning-artifacts/epics.md (Epic 4 Story 4.3)
