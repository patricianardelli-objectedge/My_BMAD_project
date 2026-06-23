# Story 2.2: Recommendation Summary Card and One-Click Add-to-Cart

**Epic:** AI Match and Cart Conversion  
**Status:** done  
**Created:** 2026-06-23  

---

## Story Summary

As a shopper, I want a transparent recommendation summary and a one-click add action, so that I can trust the pick and move to checkout quickly.

**Dependencies:** Story 2.1 (Decision Engine) – Provides book recommendation API response.

**References:** FR4, FR6, NFR2, UX-DR5

**Source Documents:**
- PRD sections 8.1, 9
- UX DESIGN sections Recommendation Card, Typography & Colors
- docs/api-specs.yaml

---

## Acceptance Criteria

### AC1: Recommendation Card Display
**Given** a decision result exists  
**When** the recommendation card renders  
**Then** it displays genre fit, mood fit, and safety checks in human-readable language  
**And** provides a single primary add-to-cart CTA.

**Task Breakdown:**
- [ ] Recommendation card displays: book cover (thumbnail), title, author, price
- [ ] Card shows reasoning in plain language:
  - [ ] "Great match for mystery lovers" (if genre_match > 0.7)
  - [ ] "Perfect for a cozy evening" (if mood_match > 0.6)
  - [ ] "Age-appropriate for you" (if age_safety = 1.0)
- [ ] Card includes confidence badge: "92% match" or "Good pick"
- [ ] Runner-up option visible (optional): "Not sure? Try 'Tea & Alibis' instead"
- [ ] Single prominent "Add to Kit" CTA button (emerald primary style)
- [ ] Card is responsive: 100% width on mobile, 400px on desktop
- [ ] Card has hover state: subtle elevation, background tint

### AC2: One-Click Add-to-Cart Flow
**Given** the shopper clicks add-to-cart  
**When** cart state updates  
**Then** the blind date kit and selected book data appear in mini cart  
**And** quantity and price totals are recalculated immediately.

**Task Breakdown:**
- [ ] Add button click calls `addToCart(book)` with recommendation data
- [ ] currentCartItem updated: `{ book_id, title, author, price, cover_url, quantity: 1 }`
- [ ] Mini cart automatically opens (slide in from right)
- [ ] Mini cart header shows: "Your Gift Kit"
- [ ] Mini cart displays: book title, unit price, quantity, total
- [ ] Cart badge in header updates: "1" (quantity)
- [ ] Total price recalculated: `quantity * price`
- [ ] No page reload; smooth UX transition from recommendation → mini cart
- [ ] Focus moves to mini cart header on open

### AC3: Transparent Scoring Display
**Given** a shopper wants to understand the recommendation  
**When** they view the card or click "Why this book?"  
**Then** they see the scoring breakdown explained in accessible language.

**Task Breakdown:**
- [ ] Reasoning visible on card or in collapsible section:
  - [ ] Genre Match: "Loved mysteries? This book has mystery & cozy elements"
  - [ ] Mood Match: "Perfect for a relaxing, thoughtful read"
  - [ ] Age Safety: "Curated for readers 20-30"
  - [ ] Confidence: "92% sure you'll love this pick"
- [ ] No technical jargon (avoid "Jaccard similarity", "weighted score", etc.)
- [ ] Human-readable format with icons or visual indicators
- [ ] Optional: "See all options" link to show runner-ups (Story 2.2b)

### AC4: Price & Kit Summary
**Given** the shopper adds the book to cart  
**When** mini cart renders  
**Then** it shows blind date kit details and total cost  
**And** price is displayed with currency symbol and precision (2 decimals).

**Task Breakdown:**
- [ ] Mini cart item shows: `<book_title> - $<price>.00`
- [ ] Kit description: "Blind Date Book Kit: Curated book selection + gift wrapping + care note"
- [ ] Total line: "Total: $<price>.00"
- [ ] Price matches API response (no rounding errors)
- [ ] Multi-currency support (future): Display in USD or BRL based on locale
- [ ] No hidden fees; price displayed is final (before shipping, which is set at checkout)

---

## Implementation Context

### Frontend File Structure

**Primary Implementation:**  
`design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html`

**Styling:**  
`design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/styles.css`

**Dependencies:**
- Story 2.1: API response from `/api/ai/decide`
- Story 2.2: Recommendation card modal (new or reuse agent modal)
- Story 1.2: Mini cart component already exists

### Recommendation Card UX

**Desktop (1024px+):**
```
┌─────────────────────────────────────────────────────┐
│ Recommendation Card                                  │
├─────────────────────────────────────────────────────┤
│ [Book Cover Image]    Title: Midsummer Manor Mystery │
│ 400px x 300px         Author: Jane Author             │
│                       Price: $14.99                   │
│                                                       │
│ ⭐ 92% Match                                          │
│ • Great for mystery lovers (Genre: 80%)              │
│ • Perfect for cozy evenings (Mood: 75%)              │
│ • Age-appropriate for you (20s reader)               │
│                                                       │
│ [Add to Kit →]        [See all options]              │
└─────────────────────────────────────────────────────┘
```

**Mobile (375-767px):**
```
┌────────────────────────────────────────┐
│ Recommendation Card                     │
├────────────────────────────────────────┤
│   [Book Cover Image]                   │
│      300px x 250px                     │
│                                         │
│ Title: Midsummer Manor Mystery          │
│ Author: Jane Author                    │
│ Price: $14.99                          │
│                                         │
│ ⭐ 92% Match                            │
│ • Great for mystery lovers             │
│ • Perfect for cozy evenings            │
│ • Age-appropriate for you              │
│                                         │
│ [Add to Kit →]                         │
│ [See all options]                      │
└────────────────────────────────────────┘
```

### Data Flow

**Story 2.1 API Response → Story 2.2 Display:**
```javascript
// After Story 1.4 (confirmation continue):
const preferences = { ... };  // From preference capture

// Call Story 2.1 API
fetch('/api/ai/decide', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ...' },
  body: JSON.stringify({
    preferences: preferences,
    session_id: agentState.selectedTrail,
    exclude_books: []
  })
})
.then(res => res.json())
.then(recommendation => {
  // recommendation has: book_id, title, author, cover_url, price, score, reason, confidence, candidates
  displayRecommendation(recommendation);  // Story 2.2 renders card
})
```

**Add-to-Cart Flow:**
```javascript
function addToCart(book) {
  currentCartItem = {
    book_id: book.book_id,
    title: book.title,
    author: book.author,
    cover_url: book.cover_url,
    price: book.price,
    quantity: 1,
    recommendation_score: book.score
  };
  
  renderCartItem();  // Update mini cart display
  openMiniCart();    // Slide in mini cart
  
  // Log add-to-cart event
  console.log({ event: 'add_to_cart', book_id: book.book_id, price: book.price });
}
```

---

## Testing Requirements

### Unit Tests (JavaScript)

- [ ] `test_add_to_cart_updates_state()` – currentCartItem populated with book data
- [ ] `test_add_to_cart_opens_mini_cart()` – openMiniCart() called after addToCart()
- [ ] `test_price_calculation()` – quantity * price = total (no rounding errors)
- [ ] `test_cart_badge_updated()` – Cart count badge shows quantity
- [ ] `test_recommendation_card_renders()` – Card displays with all expected fields

### Functional Tests (Frontend)

- [ ] Recommendation card displays with book cover, title, author, price
- [ ] Reasoning displayed in human-readable format (no technical jargon)
- [ ] Confidence badge shows "XX% match"
- [ ] "Add to Kit" button visible and clickable
- [ ] Clicking "Add to Kit" opens mini cart (slide transition)
- [ ] Mini cart shows: book title, unit price, quantity (1), total
- [ ] Cart badge in header shows "1"
- [ ] Total price calculation correct (quantity * price)
- [ ] Price displayed with currency ($) and 2 decimals (.00)

### UI/UX Tests

- [ ] Recommendation card layout matches UX design (alignment, spacing, colors)
- [ ] Card responsive on mobile (375px), tablet (768px), desktop (1024px)
- [ ] Hover state on card: subtle elevation, background tint
- [ ] "Add to Kit" button styled as primary (emerald, 12px 16px padding)
- [ ] Button focus state visible (gold outline)
- [ ] Mini cart slide animation smooth (<300ms)
- [ ] No layout shift when mini cart opens (CLS < 0.1)

### Accessibility Tests

- [ ] Recommendation card has proper heading hierarchy
- [ ] "Add to Kit" button keyboard-operable (Tab focus, Enter to activate)
- [ ] Cover image has alt text: "Cover of [book title] by [author]"
- [ ] Reasoning text is readable (not just visual icons)
- [ ] Color contrast: text >= 4.5:1, accent >= 3:1
- [ ] Focus visible on all interactive elements (gold outline)
- [ ] Screen reader announces: "Recommended book: [title] by [author], 92% match"

### Integration Tests

- [ ] Story 2.1 API call succeeds with preferences
- [ ] Recommendation card displays returned book data
- [ ] Click "Add to Kit" → currentCartItem updated → mini cart opens
- [ ] Multiple add-to-cart: clicking again updates quantity (if allowed)
- [ ] Mini cart state persists on page navigation

### Performance Tests

- [ ] Recommendation card render < 500ms
- [ ] Mini cart slide animation 60 FPS (no jank)
- [ ] Images lazy-loaded if necessary
- [ ] No memory leaks on repeated add-to-cart

---

## Developer Implementation Checklist

### HTML Structure

- [ ] Create recommendation card container (modal or inline div)
- [ ] Book image element with alt text
- [ ] Title, author, price display
- [ ] Confidence badge ("92% match")
- [ ] Reasoning list with icons or checkmarks:
  - [ ] Genre match reason
  - [ ] Mood match reason
  - [ ] Age safety message
- [ ] "Add to Kit" button (primary CTA)
- [ ] "See all options" link (optional, Story 2.2b)

### CSS Styling

- [ ] Recommendation card layout: image + text side-by-side (desktop), stacked (mobile)
- [ ] Card background: white (#FEFCF8)
- [ ] Border: 1px solid rgba(30,42,68,0.12)
- [ ] Border radius: 16px (modal) or 12px (inline)
- [ ] Hover state: box-shadow, subtle background tint
- [ ] "Add to Kit" button: emerald background, white text, 12px 16px padding, 8px border-radius
- [ ] Button hover: rgba(201,162,39,0.16) background overlay
- [ ] Button focus-visible: 3px gold outline
- [ ] Confidence badge: emerald background, white text, 14px font, 8px padding
- [ ] Reasoning list: bullet points or checkmarks, 14px font, line-height 1.5
- [ ] Responsive: Full-width mobile, 400px card on desktop

### JavaScript Logic

- [ ] `displayRecommendation(book)` – Render card with book data
- [ ] `addToCart(book)` – Update currentCartItem, open mini cart, log event
- [ ] `renderCartItem()` – Update mini cart display (already exists, no changes)
- [ ] Event listener on "Add to Kit" button → `addToCart()`
- [ ] Format price: `$${price.toFixed(2)}`
- [ ] Build reasoning text from score breakdown (genre_match, mood_match, age_safety)
- [ ] Handle edge cases: no cover image (use placeholder), missing author (show "Unknown")

### API Integration

- [ ] After modal continue (Story 1.4), call `/api/ai/decide` endpoint
- [ ] Pass preferences, session_id, exclude_books=[]
- [ ] Handle error response: show fallback recommendation or error message
- [ ] Timeout handling: if decision engine times out, show user-friendly message

### Logging & Analytics

- [ ] Log recommendation displayed: book_id, score, session_id
- [ ] Log add-to-cart: book_id, price, session_id, timestamp
- [ ] Optional: Send events to analytics backend (GA, Mixpanel, etc.)

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Card render speed | < 500ms | Time from API response to card visible |
| Add-to-cart conversion | >= 90% | Users who see card and add to cart / users who see card |
| Mini cart open delay | < 300ms | Time from button click to mini cart visible |
| Price accuracy | 100% | No rounding errors in quantity * price calculation |
| Accessibility compliance | WCAG AA | axe/WAVE scan of recommendation card |
| Mobile responsiveness | >= 95% | Card readable on 3 device sizes (mobile/tablet/desktop) |

---

## Deployment and Handoff

**Story Status Transitions:**
- [ ] Implement: Status remains `ready-for-dev`
- [ ] Submit for review: Update story artifact to `Status: review`
- [ ] Code review complete, ready to merge: Update to `Status: done`
- [ ] Update sprint-status.yaml: Move story from backlog → review → done

**File Updates After Implementation:**
- Update `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html` with recommendation card HTML and displayRecommendation() JS
- Update `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/styles.css` with recommendation card styling
- Commit changes with message: `Story 2.2: Recommendation summary card with one-click add-to-cart`

**Next Story:** Story 2.3 (Mini Cart Subscription Options & Pricing)

---

## References

- **Story 2.1:** Rule-Based Decision Engine (provides recommendation data)
- **UX Design:** design-artifacts/E-Development/ux-blind-date-book-2026-06-22/DESIGN.md
- **PRD:** _bmad-output/implementation-artifacts/prd-blind-date-book.md sections 8.1, 9
- **Story Context:** _bmad-output/planning-artifacts/epics.md (Epic 2 Story 2.2)
