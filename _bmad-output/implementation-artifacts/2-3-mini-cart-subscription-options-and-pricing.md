# Story 2.3: Mini Cart Subscription Options and Pricing

**Epic:** AI Match and Cart Conversion  
**Status:** done  
**Created:** 2026-06-23  

---

## Story Summary

As a shopper, I want to choose one-time, monthly, bi-weekly, or three-month delivery, so that the purchase matches how often I want to gift or receive books.

**Dependencies:** Story 2.2 (Recommendation Card) – Mini cart already exists but needs subscription options.

**References:** FR5, FR6, UX-DR4

**Source Documents:**
- PRD sections 8.1, 8.2
- UX DESIGN sections Mini Cart, Subscription Options
- docs/api-specs.yaml

---

## Acceptance Criteria

### AC1: Subscription Option Selection
**Given** mini cart is open  
**When** subscription options are displayed  
**Then** one-time and three subscription cadence options are selectable  
**And** selected cadence updates order summary labels and totals.

**Task Breakdown:**
- [ ] Mini cart displays 4 radio button options:
  - [ ] "One-time purchase" (default selected)
  - [ ] "Subscription - Monthly" (every 30 days)
  - [ ] "Subscription - Bi-weekly" (every 14 days)
  - [ ] "Subscription - Three-month" (every 90 days)
- [ ] Radio buttons styled consistently with design system (Inter font, 14px)
- [ ] Clear labels: Include frequency description
- [ ] One option selected at a time (radio behavior, not checkboxes)
- [ ] Selection updates order summary immediately (no page reload)
- [ ] Selected option highlighted with emerald color or checkmark

### AC2: Price Updates by Cadence
**Given** a subscription cadence is selected  
**When** user changes the selection  
**Then** cadence is persisted into checkout payload  
**And** cart state remains consistent on refresh/back navigation.

**Task Breakdown:**
- [ ] One-time purchase: Price = book price + kit fee (e.g., $24.99)
- [ ] Monthly subscription: Price = (book price + kit fee) / 3 for first 3 months, then recurring
  - [ ] Display: "Pay $X now, then $X monthly starting [date]"
  - [ ] Or simplified: "Pay $X/month" with note "First shipment in [date]"
- [ ] Bi-weekly subscription: Price = (book price + kit fee) / 2 for first 2 periods
  - [ ] Display: "Pay $X now, then $X every 2 weeks"
- [ ] Three-month subscription: Price = (book price + kit fee) × 3 upfront
  - [ ] Display: "Pay $X now for 3 kits" or "Pay $X/kit, 3 times"
- [ ] Price updates in real-time when cadence changes
- [ ] Total line updates: "Total: $X.XX" or "Total (first shipment): $X.XX"
- [ ] Subscription start date indicated if applicable

### AC3: Subscription State Persistence
**Given** a subscription cadence is selected  
**When** user navigates away and back to mini cart  
**Then** selected cadence and prices are retained  
**And** form state does not reset.

**Task Breakdown:**
- [ ] Mini cart state stored in agentState or localStorage
- [ ] On page refresh: Radio selection persists (form field value saved)
- [ ] On close/reopen mini cart: Cadence and totals unchanged
- [ ] On navigate to checkout: Subscription data passed in checkout payload
- [ ] Cadence value: `{ type: 'one-time' | 'monthly' | 'bi-weekly' | 'three-month' }`
- [ ] Example checkout payload: `{ cart_items: [...], subscription: { cadence: 'monthly', start_date: '2026-07-23' }, ... }`

### AC4: Checkout Flow Integration
**Given** a shopper completes subscription selection  
**When** they proceed to checkout  
**Then** the subscription choice is visible on the checkout form  
**And** payment is processed according to the selected cadence.

**Task Breakdown:**
- [ ] Checkout form displays subscription summary: "Monthly delivery | First kit on [date]"
- [ ] Checkout form has hidden field or displays selected cadence
- [ ] Checkout summary shows: "Book + Kit: $X | Subscription: [cadence]"
- [ ] Payment processor receives subscription flag and cadence
- [ ] For one-time: normal payment, no subscription record
- [ ] For subscription: Create subscription object (future: Stripe subscription, webhook handling)

---

## Implementation Context

### Frontend File Structure

**Primary Implementation:**  
`design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html`

**Styling:**  
`design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/styles.css`

**Dependencies:**
- Story 2.2: Mini cart already exists (Story 1.2 implementation)
- Radio buttons for subscription selection
- Price calculation logic

### Mini Cart with Subscription UI

**Current Mini Cart (from Story 1.2):**
```html
<div class="mini-cart" id="mini-cart">
  <div class="mini-cart-header">Your Gift Kit</div>
  <div class="mini-cart-content">
    <!-- Book item displayed -->
  </div>
  <div class="mini-cart-footer">
    <div>Delivery Type</div>
    <div style="display:flex;flex-direction:column;gap:8px;">
      <label><input type="radio" name="sub" value="one-time" checked/> One-time purchase</label>
      <label><input type="radio" name="sub" value="monthly"/> Subscription - monthly</label>
      <label><input type="radio" name="sub" value="bi-month"/> Subscription - Bi-month</label>
      <label><input type="radio" name="sub" value="three-month"/> Subscription - Three-month</label>
    </div>
    <div>Total: <span id="cart-total">$24.99</span></div>
    <button class="btn btn-primary" id="checkout-btn">Complete checkout</button>
  </div>
</div>
```

**Updated Design (Story 2.3):**
```
┌────────────────────────────────────┐
│ Your Gift Kit                    × │
├────────────────────────────────────┤
│ Midsummer Manor Mystery            │
│ Unit price: $14.99                 │
│ Qty: [1]                           │
│ Total: $24.99         [Remove]     │
├────────────────────────────────────┤
│ Delivery Type                      │
│ ○ One-time purchase                │
│ ○ Subscription - Monthly           │
│ ○ Subscription - Bi-weekly         │
│ ○ Subscription - Three-month       │
│                                    │
│ First shipment: $24.99             │
│ Then: $24.99/month starting [date] │
│                                    │
│ Total: $24.99   [Details ↓]        │
│                                    │
│ [Complete checkout]                │
└────────────────────────────────────┘
```

### Subscription Pricing Model

**One-time Purchase:**
- Price = book_price + kit_fee = $14.99 + $10 = $24.99
- Payment: Single charge at checkout
- No recurring billing

**Monthly Subscription:**
- Price = $24.99/month for ongoing shipments
- Initial payment: $24.99 (first kit)
- Recurring: $24.99 billed monthly on same day
- Start date: Next month from order date
- Display: "Pay $24.99 now, then $24.99/month starting [date]"

**Bi-weekly Subscription:**
- Price = $24.99 every 14 days
- Initial payment: $24.99 (first kit)
- Recurring: $24.99 billed every 2 weeks
- Start date: 2 weeks from order date
- Display: "Pay $24.99 now, then $24.99 every 2 weeks starting [date]"

**Three-month Subscription:**
- Price = $24.99 × 3 = $74.97 upfront
- Covers 3 shipments over 3 months
- Initial payment: $74.97 (all 3 kits prepaid)
- No recurring billing (unless auto-renewal enabled in future)
- Display: "Pay $74.97 now for 3 kits (1 per month)"

### Data Flow

**Subscription State:**
```javascript
let subscriptionState = {
  cadence: 'one-time',  // 'one-time' | 'monthly' | 'bi-weekly' | 'three-month'
  start_date: null,      // ISO8601 date for recurring shipments
  initial_price: 24.99,  // First payment
  recurring_price: 24.99, // Per-period price (null if one-time)
  frequency_label: 'monthly' // Human-readable frequency
};
```

**Radio Button Change Handler:**
```javascript
document.querySelectorAll('input[name="sub"]').forEach(radio => {
  radio.addEventListener('change', () => {
    subscriptionState.cadence = radio.value;
    updateSubscriptionDisplay();
    updateCheckoutPayload();
  });
});

function updateSubscriptionDisplay() {
  const pricing = {
    'one-time': { label: 'One-time purchase', initial: 24.99, recurring: null, display: 'Pay $24.99 now' },
    'monthly': { label: 'Monthly', initial: 24.99, recurring: 24.99, display: 'Pay $24.99 now, then $24.99/month' },
    'bi-month': { label: 'Bi-weekly', initial: 24.99, recurring: 24.99, display: 'Pay $24.99 now, then $24.99 every 2 weeks' },
    'three-month': { label: '3-month', initial: 74.97, recurring: null, display: 'Pay $74.97 now for 3 kits' }
  };
  
  const chosen = pricing[subscriptionState.cadence];
  document.getElementById('cart-total').textContent = '$' + chosen.initial.toFixed(2);
  // Update pricing details display
}
```

---

## Testing Requirements

### Unit Tests (JavaScript)

- [ ] `test_subscription_cadence_selection()` – Radio button change updates subscriptionState
- [ ] `test_price_calculation_one_time()` – One-time = $24.99
- [ ] `test_price_calculation_monthly()` – Monthly initial = $24.99
- [ ] `test_price_calculation_bi_weekly()` – Bi-weekly initial = $24.99
- [ ] `test_price_calculation_three_month()` – Three-month = $74.97
- [ ] `test_total_updates_on_cadence_change()` – Changing radio updates cart total
- [ ] `test_subscription_state_persists()` – Selected cadence saved after page reload

### Functional Tests (Frontend)

- [ ] All 4 subscription options visible in mini cart
- [ ] One-time selected by default
- [ ] Clicking each radio button: state updates, total updates, no page reload
- [ ] Price correct for each cadence (one-time $24.99, three-month $74.97)
- [ ] Pricing details display correct (e.g., "then $24.99/month starting [date]")
- [ ] Clicking "Complete checkout" with subscription cadence selected → checkout receives cadence
- [ ] Refreshing page: previously selected cadence retained
- [ ] Closing and reopening mini cart: cadence selection retained

### UI/UX Tests

- [ ] Radio buttons styled consistently with design system
- [ ] "Delivery Type" label clear and visible
- [ ] Selected radio button visually distinct (checked state)
- [ ] Pricing summary clear: "Total: $X.XX" or "First shipment: $X.XX, then $X.XX/month"
- [ ] No layout shift when subscription details update
- [ ] Responsive: Options readable on mobile (375px), tablet (768px), desktop (1024px)

### Accessibility Tests

- [ ] Radio buttons keyboard-operable (Tab focus, arrow keys to select)
- [ ] Radio labels associated with inputs (<label> for="id")
- [ ] Focus visible on radio buttons and text inputs
- [ ] Screen reader announces: "Subscription options: One-time purchase, selected" or "Monthly, not selected"
- [ ] Pricing details readable by screen reader (not just visual)
- [ ] Color contrast: text >= 4.5:1

### Integration Tests

- [ ] Add book to cart → mini cart opens with subscription options
- [ ] Select subscription cadence → total updates
- [ ] Click "Complete checkout" → cadence passed to checkout form/API
- [ ] Checkout form displays selected cadence
- [ ] Submit checkout with subscription → API receives subscription data
- [ ] One-time purchase → no subscription created (future: verify with backend)
- [ ] Monthly subscription → subscription created with start_date (future: verify with backend)

---

## Developer Implementation Checklist

### HTML Structure

- [ ] Radio button group for subscription options (already exists, no changes)
- [ ] Update label text: "Subscription - monthly" → "Subscription - Monthly" (capitalization)
- [ ] Add subscription details element (pricing, start date)
- [ ] Update total display: Support "Total (first shipment)" for subscriptions

### CSS Styling

- [ ] Radio buttons: Standard browser default or custom styled
- [ ] Labels: 14px Inter, emerald text, no additional styling needed
- [ ] Pricing details: 12px gray text, subtle styling
- [ ] Total line: Bold, 16px, primary color
- [ ] Responsive: All elements readable on mobile (375px+)

### JavaScript Logic

- [ ] `subscriptionState` object to track cadence, prices, dates
- [ ] Event listener on radio buttons → `updateSubscriptionDisplay()`
- [ ] `updateSubscriptionDisplay()` function:
  - [ ] Calculate price based on cadence
  - [ ] Format pricing details string (e.g., "then $24.99/month starting [date]")
  - [ ] Update DOM: total, pricing details
- [ ] `calculateSubscriptionDate(cadence)` → return ISO8601 start date
- [ ] `getCheckoutPayload()` function: Include subscription data
- [ ] localStorage persistence: Save subscriptionState on change, restore on page load

### API Integration (Checkout)

- [ ] Checkout endpoint receives subscription data: `{ cadence, start_date, initial_price, recurring_price }`
- [ ] For one-time: `{ cadence: 'one-time', initial_price: 24.99, recurring_price: null }`
- [ ] For subscriptions: `{ cadence: 'monthly', initial_price: 24.99, recurring_price: 24.99, start_date: '2026-07-23' }`

### Logging & Analytics

- [ ] Log subscription cadence selected: `{ event: 'subscription_selected', cadence, price }`
- [ ] Log checkout with subscription: `{ event: 'checkout_initiated', cadence, amount }`
- [ ] Optional: Track subscription abandonment (selected but didn't checkout)

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cadence selection usability | >= 95% | Users able to select all 4 options |
| Price accuracy | 100% | No rounding errors in subscription calculations |
| Persistence | 100% | Cadence retained after page refresh |
| Mobile responsiveness | >= 95% | Radio options readable and selectable on 375px width |
| Accessibility compliance | WCAG AA | axe/WAVE scan of mini cart with subscription options |
| Conversion rate | >= 90% | Users who open mini cart → proceed to checkout |

---

## Deployment and Handoff

**Story Status Transitions:**
- [ ] Implement: Status remains `ready-for-dev`
- [ ] Submit for review: Update story artifact to `Status: review`
- [ ] Code review complete, ready to merge: Update to `Status: done`
- [ ] Update sprint-status.yaml: Move story from backlog → review → done

**File Updates After Implementation:**
- Update `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html` with subscription logic
- Update `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/styles.css` if additional styling needed
- Commit changes with message: `Story 2.3: Mini cart subscription options with pricing`

**Next Epic:** Epic 3 (Fast and Secure Checkout) – Story 3.1, 3.2, 3.3

---

## References

- **Story 2.2:** Recommendation Card (precedes mini cart subscription flow)
- **UX Design:** design-artifacts/E-Development/ux-blind-date-book-2026-06-22/DESIGN.md
- **PRD:** _bmad-output/implementation-artifacts/prd-blind-date-book.md sections 8.1, 8.2
- **Story Context:** _bmad-output/planning-artifacts/epics.md (Epic 2 Story 2.3)
