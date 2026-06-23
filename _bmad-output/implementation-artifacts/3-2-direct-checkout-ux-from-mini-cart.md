# Story 3.2: Direct Checkout UX from Mini-Cart

**Epic:** Fast & Secure Checkout  
**Status:** ready-for-dev  
**Created:** 2026-06-23  

---

## Story Summary

As a shopper, I want to proceed directly to checkout from the mini-cart without extra steps, so that I can complete my purchase quickly with minimal friction.

**Dependencies:** Story 2.3 (Mini Cart Subscriptions) – Supplies cart and subscription data.

**References:** FR9, NFR2, NFR3, UX-DR3

**Source Documents:**
- PRD sections 9, 10
- UX DESIGN sections Checkout Form, Success Page
- docs/api-specs.yaml

---

## Acceptance Criteria

### AC1: Checkout Modal Opens from Mini-Cart CTA
**Given** the mini-cart is open with items and subscription selected  
**When** user clicks "Complete checkout" button  
**Then** checkout modal opens with pre-filled cart summary  
**And** checkout form displays payment, shipping, and billing fields.

**Task Breakdown:**
- [ ] Mini-cart footer "Complete checkout" button wired to open checkout modal
- [ ] Checkout modal displays: cart summary (item, quantity, price), subscription choice (Monthly, Bi-weekly, etc.), total amount
- [ ] Cart summary shows: 1 line item: "[Book Title] by [Author] – $[price]"
- [ ] Subscription line: "[Cadence] starting [date]"
- [ ] Total: "Total: $[amount]" in large, bold text
- [ ] Modal header: "Complete Your Order"
- [ ] Form fields visible: name, email, phone, address fields, payment method
- [ ] No page reload; smooth transition from mini-cart
- [ ] Modal has close button (X) to return to mini-cart without submitting

### AC2: Minimal Checkout Form (5 Required Fields)
**Given** checkout modal is open  
**When** user sees form fields  
**Then** only 5 required fields are shown (fast path)  
**And** billing address is optional (defaults to shipping).

**Task Breakdown:**
- [ ] Required fields (5):
  - [ ] Full Name (text input, min 3 chars)
  - [ ] Email (email input, validated format)
  - [ ] Phone (tel input, formatted as (555) 123-4567)
  - [ ] Street Address (text input)
  - [ ] City, State, Postal Code (3 fields in one row)
- [ ] Optional field (collapsed):
  - [ ] "Billing address different?" checkbox → expands billing address fields
- [ ] Checkbox "I agree to terms & privacy policy" (required to submit)
- [ ] Form validation: Show inline error messages on blur or submit
- [ ] No address field for State if country != US (future: country selector)
- [ ] All fields have placeholders and helpful labels

### AC3: Payment Method Selection (Card or PIX)
**Given** checkout form is displayed  
**When** user selects payment method  
**Then** appropriate payment input appears (Stripe card form or PIX display).

**Task Breakdown:**
- [ ] Radio buttons for payment method:
  - [ ] "Credit / Debit Card" (default selected)
  - [ ] "PIX" (Brazil-only, conditional visibility)
- [ ] Card payment:
  - [ ] Stripe Elements iframe for card input (cc number, exp, CVC)
  - [ ] Card element shows live validation (red border if invalid)
  - [ ] Card brand icon shown (Visa, Mastercard, Amex)
- [ ] PIX payment:
  - [ ] Info message: "A unique PIX code will be generated after you submit"
  - [ ] Instructions: "You'll have 30 minutes to scan the QR code in your banking app"
- [ ] Payment method required before form submission
- [ ] On submit: Send payment method type + Stripe token (for card) to `/api/checkout`

### AC4: Form Submission & Loading State
**Given** all required fields are filled  
**When** user clicks "Complete Purchase" button  
**Then** form is submitted, loading state shows, payment is processed  
**And** user is redirected to success page or shown error message.

**Task Breakdown:**
- [ ] "Complete Purchase" button disabled until form valid
- [ ] On click: Disable button, show spinner + "Processing..."
- [ ] Call `/api/checkout` endpoint with form data
- [ ] Handle response:
  - [ ] Success (order_id, status=paid): Redirect to `/success?order_id=...`
  - [ ] PIX (status=awaiting_pix): Redirect to `/pix-qr?order_id=...`
  - [ ] Error: Show error message, re-enable button, highlight failed field
- [ ] Timeout (>5s): Show message "Payment taking longer than expected. Please wait..."
- [ ] Network error: Show "Connection lost. Please check and try again."

### AC5: Mobile Responsiveness
**Given** checkout form on mobile device (375px width)  
**When** user views and interacts with form  
**Then** all elements are readable, inputs are 44px+ touch targets  
**And** form fields stack vertically without overflow.

**Task Breakdown:**
- [ ] Cart summary responsive: Stacks vertically on mobile
- [ ] Form fields: Full-width on mobile, 2-column grid on desktop
- [ ] City/State/Postal: Stack vertically on mobile, horizontal on desktop
- [ ] Buttons: Full-width on mobile, 100% height for touch (min 44px)
- [ ] Font size: Min 16px to prevent iOS zoom-on-focus
- [ ] Stripe card element: Responsive width, shows full on mobile
- [ ] No horizontal scroll
- [ ] Modal max-width: 520px (existing modal style)

---

## Implementation Context

### Checkout Form UX

**Desktop Layout:**
```
┌──────────────────────────────────────────────────┐
│ Complete Your Order                           × │
├──────────────────────────────────────────────────┤
│ Order Summary                                    │
│ ────────────────────────────────────────────     │
│ Midsummer Manor Mystery - $14.99                 │
│ Monthly subscription starting July 23            │
│                                                   │
│ Total: $24.99                                    │
│                                                   │
│ Shipping Address                                 │
│ ──────────────────                               │
│ Full Name: [ Jane Doe          ]                │
│ Email:     [ jane@example.com  ]                │
│ Phone:     [ (555) 123-4567    ]                │
│                                                   │
│ Street Address: [ 123 Main St          ]        │
│ City: [ Portland  ] State: [ ME ] ZIP: [ 04101 ]│
│                                                   │
│ ☐ Billing address different?                    │
│                                                   │
│ Payment Method                                   │
│ ──────────────                                   │
│ ○ Credit / Debit Card                           │
│ ○ PIX                                            │
│                                                   │
│ [Stripe Card Element ────────────────────]       │
│                                                   │
│ ☑ I agree to terms & privacy policy             │
│                                                   │
│ [Complete Purchase]  [Cancel]                   │
└──────────────────────────────────────────────────┘
```

**Mobile Layout:**
```
┌──────────────────────────────┐
│ Complete Your Order        × │
├──────────────────────────────┤
│ Order Summary                │
│ Midsummer Manor Mystery      │
│ $14.99 × 1                   │
│ Monthly starting July 23     │
│                              │
│ Total: $24.99                │
│                              │
│ Full Name                    │
│ [Jane Doe              ]     │
│                              │
│ Email                        │
│ [jane@example.com     ]     │
│                              │
│ Phone                        │
│ [(555) 123-4567       ]     │
│                              │
│ Street Address               │
│ [123 Main Street      ]     │
│                              │
│ City                         │
│ [Portland             ]     │
│                              │
│ State                        │
│ [ME                   ]     │
│                              │
│ Postal Code                  │
│ [04101                ]     │
│                              │
│ ☐ Billing different?         │
│                              │
│ Payment Method               │
│ ○ Credit / Debit Card        │
│ ○ PIX                        │
│                              │
│ [Card Element ───────]       │
│                              │
│ ☑ I agree to terms          │
│                              │
│ [Complete Purchase]          │
│ [Cancel]                     │
└──────────────────────────────┘
```

### Data Flow

**Form → API:**
```javascript
{
  "cart_items": [...],  // From agentState/currentCartItem
  "subscription": {...},  // From subscriptionState
  "shipping_address": {
    "name": "Jane Doe",
    "street": "123 Main Street",
    "city": "Portland",
    "state": "ME",
    "postal_code": "04101"
  },
  "billing_address": null,  // or {...} if different
  "payment_method": "card",
  "stripe_token": "pm_1234567890",  // Created by Stripe Elements
  "email": "jane@example.com",
  "phone": "(555) 123-4567",
  "idempotency_key": "checkout-uuid-123"
}
```

### Success Page (/success)

**URL:** `/success?order_id=order-uuid-123`

**Display:**
- Order confirmation: "Thank you for your order!"
- Order ID: "Order #[order-id]"
- Receipt summary: Items, subscription, total amount
- Next steps: "Your first shipment will arrive by [date]"
- For subscriptions: "Your next shipment is scheduled for [next_date]"
- "View full receipt" link (or email receipt)
- CTA: "Continue shopping" or "Return home"

### PIX Success Page (/pix-qr)

**URL:** `/pix-qr?order_id=order-uuid-456`

**Display:**
- "Scan to Pay"
- QR code (generated from Story 3.1 API response)
- Copy-paste code option
- Countdown timer: "Expires in 30:00"
- Instructions: "Scan with your banking app"
- "Payment confirmed?" link to check status
- On confirmation: Redirect to `/success?order_id=...`

---

## Testing Requirements

### Functional Tests (Frontend)

- [ ] Checkout modal opens on "Complete checkout" button click
- [ ] Cart summary shows book title, quantity, price correctly
- [ ] Subscription shows correct cadence and date
- [ ] Total calculates and displays correctly
- [ ] All 5 required fields visible: name, email, phone, street, city/state/zip
- [ ] "Billing address different?" expands/collapses correctly
- [ ] Payment method radio buttons work (Card default, PIX option)
- [ ] Stripe card element renders and accepts card input
- [ ] Form validation: blank name → inline error "Name required"
- [ ] Form validation: invalid email → error "Invalid email format"
- [ ] Form validation: blank address → error "Address required"
- [ ] Checkbox "I agree..." required before submit
- [ ] "Complete Purchase" button disabled until form valid
- [ ] On submit: Button shows spinner, text changes to "Processing..."
- [ ] On success: Redirect to /success?order_id=...
- [ ] On error: Error message shown, button re-enabled
- [ ] "Cancel" button returns to mini-cart without submitting

### UI/UX Tests

- [ ] Form layout matches UX design (alignment, spacing, colors)
- [ ] Cart summary visually distinct from form (different background or border)
- [ ] All buttons have hover states
- [ ] Focus visible on all interactive elements (gold outline)
- [ ] Stripe card element styled to match form (borders, fonts)
- [ ] Loading spinner animation smooth (<300ms rotate)
- [ ] Error messages in red (#d32f2f or similar) and readable
- [ ] Success page shows confirmation with order details
- [ ] PIX QR page shows QR code + countdown timer

### Accessibility Tests

- [ ] Form labels associated with inputs (<label for="id">)
- [ ] Required fields marked with * and aria-required="true"
- [ ] Error messages linked to inputs via aria-describedby
- [ ] Keyboard navigation: Tab through fields in order
- [ ] Keyboard submit: Enter key submits form
- [ ] Screen reader announces: "Checkout form, 5 required fields"
- [ ] Color contrast: Labels >= 4.5:1, error messages >= 4.5:1
- [ ] Focus visible on all buttons

### Responsive Tests

- [ ] Mobile (375px): Form readable, no horizontal scroll
- [ ] Tablet (768px): 2-column layout works
- [ ] Desktop (1024px+): Full layout as designed
- [ ] Touch targets: Buttons >= 44px, input fields >= 44px tall
- [ ] Font size: Min 16px on mobile (no zoom-on-focus)
- [ ] Stripe card element responsive on all sizes

### Integration Tests

- [ ] Submit form → Calls `/api/checkout` with correct data
- [ ] Success response → Redirect to /success page
- [ ] Error response → Show error message, don't redirect
- [ ] Timeout → Show timeout message after 5s
- [ ] Network error → Show connection error
- [ ] Billing address different: Send both addresses to API
- [ ] Billing address same: Send only shipping_address (null billing)

### Performance Tests

- [ ] Checkout modal open < 300ms
- [ ] Form validation < 50ms per field
- [ ] Stripe token creation < 1s
- [ ] Form submit → API call < 100ms (network latency varies)
- [ ] Success page load < 500ms
- [ ] No memory leaks on form reset/cancel

---

## Developer Implementation Checklist

### HTML Structure (index.html)

- [ ] Checkout modal markup (already exists, expand)
- [ ] Cart summary section: item name, price, quantity, subscription details
- [ ] Shipping address fieldset: 5 required fields
- [ ] Billing address fieldset: optional, hidden by default
- [ ] Payment method fieldset: radio buttons for card/PIX
- [ ] Stripe card element container
- [ ] Terms checkbox
- [ ] Form buttons: "Complete Purchase", "Cancel"
- [ ] Loading spinner (hidden, shown on submit)
- [ ] Error message container (hidden)

### CSS Styling (styles.css)

- [ ] Cart summary styling: padding, background, borders
- [ ] Form fieldset: padding, border-radius, margins
- [ ] Form labels: font-size 14px, font-weight 600
- [ ] Form inputs: padding 12px, border 1px solid, border-radius 8px
- [ ] Input focus: gold outline
- [ ] Error state: red border, error text color
- [ ] Stripe card element: match form input styling
- [ ] Button disabled: opacity 0.5, cursor not-allowed
- [ ] Loading spinner: animation rotate 360deg 1s infinite
- [ ] Responsive: Mobile stacking, tablet 2-column
- [ ] Mobile: Font min 16px, input min height 44px

### JavaScript Logic (index.html script)

- [ ] `openCheckout()` – Show checkout modal
- [ ] `closeCheckout()` – Hide checkout modal
- [ ] `validateCheckoutForm()` – Check required fields, email format, address
- [ ] `buildCheckoutPayload()` – Create request object from form
- [ ] `submitCheckout()` – Call `/api/checkout` endpoint
- [ ] `showCheckoutError(message)` – Display error in modal
- [ ] `hideCheckoutError()` – Clear error
- [ ] `setCheckoutLoading(isLoading)` – Show/hide spinner
- [ ] `handleCheckoutSuccess(response)` – Redirect to /success or /pix-qr
- [ ] `handleCheckoutError(error)` – Show error, re-enable form
- [ ] Billing address toggle: show/hide on checkbox change
- [ ] Stripe token creation: On form submit (before API call)

### Stripe Integration

- [ ] Load Stripe.js library from CDN
- [ ] Initialize Stripe with public key
- [ ] Create CardElement for card input
- [ ] Mount card element to DOM
- [ ] On form submit: Call `stripe.createToken(cardElement)` to get token
- [ ] Pass token (not card data) to `/api/checkout`
- [ ] Handle Stripe errors: Show user-friendly message

### Success Page (success.html or route)

- [ ] Display "Thank you for your order!"
- [ ] Show order ID
- [ ] Show items ordered with prices
- [ ] Show subscription details if applicable
- [ ] Show next shipment date
- [ ] "View receipt" link
- [ ] "Continue shopping" button

### PIX QR Page (pix-qr.html or route)

- [ ] Display QR code image (from API response)
- [ ] Display copy-paste code
- [ ] Countdown timer (30 minutes)
- [ ] "Scan with your banking app" instructions
- [ ] "Check payment status" button (polls API)
- [ ] On confirmed: Redirect to success page

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Form completion rate | >= 95% | Users who start form / users who complete purchase |
| Form validation accuracy | 100% | Invalid forms rejected, valid forms accepted |
| Mobile usability | >= 90% | Mobile users able to complete form without errors |
| Accessibility compliance | WCAG AA | axe/WAVE scan shows no critical issues |
| Checkout load time | < 500ms | Time from button click to modal visible |
| Success page render | < 300ms | After redirect from API |

---

## Deployment and Handoff

**Story Status Transitions:**
- [ ] Implement: Status remains `ready-for-dev`
- [ ] Submit for review: Update to `Status: review`
- [ ] Code review complete: Update to `Status: done`

**File Updates After Implementation:**
- Update `frontend/index.html` with checkout form + success page
- Update `frontend/styles.css` with checkout form styling
- Create `frontend/success.html` or success route
- Create `frontend/pix-qr.html` or pix-qr route
- Commit: `Story 3.2: Direct checkout UX from mini-cart`

**Next Story:** Story 3.3 (Background Processing for Renewals and Webhooks)

---

## References

- **Stripe Elements:** https://stripe.com/docs/stripe-js/elements/information-collection
- **UX Design:** design-artifacts/E-Development/ux-blind-date-book-2026-06-22/DESIGN.md
- **PRD:** _bmad-output/implementation-artifacts/prd-blind-date-book.md sections 9, 10
- **Story Context:** _bmad-output/planning-artifacts/epics.md (Epic 3 Story 3.2)
