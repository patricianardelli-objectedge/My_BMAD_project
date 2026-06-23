# Story 4.2: Delivered History Tracking & Duplicate Exclusion

**Epic:** User Profile & Preferences  
**Status:** ready-for-dev  
**Created:** 2026-06-23  

---

## Story Summary

As a subscriber, I want to see my delivery history and ensure the AI never recommends books I've already received, so that every blind date kit feels fresh and surprising.

**Dependencies:** Story 3.1-3.3 (Checkout & Renewals), Story 4.1 (User Profile) – Supplies orders and user avoid-list.

**References:** FR3, FR4, NFR1, NFR4

**Source Documents:**
- PRD sections 4, 5, 6
- Architecture section 6
- docs/api-specs.yaml

---

## Acceptance Criteria

### AC1: Delivery History Tracking
**Given** a user has completed orders and received shipments  
**When** they view their order history  
**Then** they see all past orders with dates, items, and delivery status  
**And** can filter by date range or status.

**Task Breakdown:**
- [ ] Create `order_history` table: order_history_id, order_id, user_id, books_received (array), delivery_date, delivery_status (pending/in-transit/delivered/returned), created_at
- [ ] GET `/api/users/{user_id}/orders` returns paginated list of orders: order_id, date, items, status, total_amount
- [ ] Order items show: book_id, title, author, cover_url, genre, mood_keywords
- [ ] Status flow: pending → in-transit → delivered (via webhook or manual update)
- [ ] Sorting: By date (recent first), status, amount
- [ ] Filtering: By date range, status (all, pending, delivered, cancelled)
- [ ] Pagination: 10 items per page, supports offset/limit

### AC2: Automatic Duplicate Exclusion in Recommendations
**Given** a user receives a recommendation  
**When** the decision engine scores books  
**Then** books already received are automatically excluded  
**And** user never gets duplicate recommendations.

**Task Breakdown:**
- [ ] On recommendation request: Get user's delivery history
- [ ] Extract book_ids from delivered orders
- [ ] Call avoid-list endpoint: already_read_books = get_user_avoid_list(user_id) + delivered_book_ids
- [ ] Decision engine filters: exclude_books = already_read_books + user_avoid_list
- [ ] Scoring only considers: catalog_books NOT IN exclude_books
- [ ] If < 5 valid candidates: Return fallback recommendation with warning "Catalog depleted for your preferences"
- [ ] Log exclusion: Which books excluded, why (delivery history or avoid-list)

### AC3: Order History UI Page
**Given** a logged-in user visits `/orders` route  
**When** they view order history  
**Then** they see table of past orders with filtering and sorting  
**And** can click order to see details.

**Task Breakdown:**
- [ ] New page: `/orders` (authenticated)
- [ ] Table columns: Order #, Date, Items, Status, Total, Actions
- [ ] Status badges: "Pending" (yellow), "Delivered" (green), "Cancelled" (gray)
- [ ] Sort buttons: Date ↑↓, Status, Amount
- [ ] Filter form: Date range (from/to), Status dropdown
- [ ] Pagination: "Previous/Next" buttons, page indicator
- [ ] "View Details" link per order → order details page
- [ ] Order details page shows: Items received, delivery address, payment method, receipt
- [ ] Empty state: "No orders yet" message if no orders
- [ ] Mobile responsive: Collapse columns, show summary cards

### AC4: Automatic Avoid-List Population on Delivery
**Given** a shipment has been delivered to user  
**When** order status changes to "delivered"  
**Then** all books in that order are automatically added to avoid-list  
**And** user is notified (optional) that these books are excluded from future recommendations.

**Task Breakdown:**
- [ ] Webhook handler (Story 3.3): On delivery confirmation
- [ ] Extract book_ids from order
- [ ] For each book: Call `add_to_avoid_list(user_id, book_id, reason='delivered')`
- [ ] Log action: timestamp, user_id, books added
- [ ] Email notification (optional): "You received [Book Title]. This book will be excluded from future recommendations."
- [ ] UI notification (optional): Display "Book marked as read" badge
- [ ] Allow manual override: User can remove from avoid-list if they want re-recommendation

### AC5: Duplicate Prevention Algorithm
**Given** multiple overlapping avoid-lists (delivered history, user-marked avoid-list, system exclusions)  
**When** decision engine queries for exclusions  
**Then** deduplication merges all sources and returns unified exclude_list  
**And** algorithm scales efficiently even with thousands of excluded books.

**Task Breakdown:**
- [ ] Deduplication function: `get_unified_exclude_list(user_id) -> set[book_id]`
- [ ] Merge sources: avoid_list (user-marked) + delivered_books + system_exclusions
- [ ] Return as set (no duplicates by definition)
- [ ] Query optimization: Cache exclude-list for 1 hour per user (or invalidate on new order)
- [ ] Performance target: < 50ms to retrieve, even for users with 1000+ excluded books
- [ ] Caching strategy: Redis cache with TTL, invalidate on order completion

---

## Implementation Context

### Database Schema

**order_history table:**
```sql
CREATE TABLE order_history (
  order_history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(order_id),
  user_id UUID NOT NULL REFERENCES users(user_id),
  books_received TEXT[],  -- {book-001, book-002, ...}
  delivery_date DATE,
  delivery_status VARCHAR(50) DEFAULT 'pending',  -- pending, in-transit, delivered, returned
  tracking_number VARCHAR(100),
  delivered_to_address JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_order_history_user_id ON order_history(user_id);
CREATE INDEX idx_order_history_order_id ON order_history(order_id);
CREATE INDEX idx_order_history_delivery_status ON order_history(delivery_status);
CREATE INDEX idx_order_history_delivery_date ON order_history(delivery_date DESC);
```

### API Endpoints

**Order History:**
- GET `/api/users/{user_id}/orders` – List orders (with pagination, filtering, sorting)
- GET `/api/users/{user_id}/orders/{order_id}` – Order details
- PATCH `/api/users/{user_id}/orders/{order_id}` – Update delivery status

**Exclusion List:**
- GET `/api/users/{user_id}/excluded-books` – Get unified exclude-list (union of avoid-list + delivered)

### Query Examples

**Get All Orders (Paginated):**
```json
GET /api/users/user-123/orders?limit=10&offset=0&sort=date&order=desc&status=delivered

Response:
{
  "total": 24,
  "count": 10,
  "offset": 0,
  "orders": [
    {
      "order_id": "order-456",
      "date": "2026-06-15",
      "items": ["Midsummer Manor Mystery", "Cozy Autumn Reads"],
      "status": "delivered",
      "total": 49.98
    },
    ...
  ]
}
```

**Get Excluded Books:**
```json
GET /api/users/user-123/excluded-books

Response:
{
  "total": 15,
  "excluded_ids": ["book-001", "book-002", ...],
  "breakdown": {
    "delivered": 12,
    "user_marked": 3,
    "system": 0
  }
}
```

### Duplicate Prevention Flow

```
User requests recommendation:
1. Call GET /api/users/{user_id}/excluded-books
   - Returns union of: delivered_books ∪ avoid_list ∪ system_exclusions
2. Decision engine scores: candidates = all_books - excluded_books
3. Return top 3 with reasoning
```

---

## Testing Requirements

### Unit Tests

- [ ] `test_get_order_history_paginated()` – Retrieve orders with limit/offset
- [ ] `test_filter_orders_by_status()` – Only delivered orders returned
- [ ] `test_filter_orders_by_date_range()` – Orders between dates
- [ ] `test_sort_orders_by_date()` – Recent first
- [ ] `test_deduplication_merges_sources()` – Union of avoid-list + delivered
- [ ] `test_excluded_list_performance_under_1000_items()` – Returns < 50ms
- [ ] `test_automatic_avoid_list_on_delivery()` – Delivered books auto-added

### Integration Tests

- [ ] `test_order_history_page_loads()` – GET /orders returns 200
- [ ] `test_filter_and_sort_works_end_to_end()` – UI filters apply correctly
- [ ] `test_delivered_books_excluded_from_recommendation()` – End-to-end: receive book → not recommended again
- [ ] `test_pagination_navigation()` – Next/Previous buttons work
- [ ] `test_order_details_page()` – Detailed view loads correctly

### Database Tests

- [ ] `test_order_history_table_created()` – Schema correct
- [ ] `test_indices_on_user_id_and_date()` – Query performance good

### Performance Tests

- [ ] Order list retrieval < 200ms
- [ ] Exclude-list retrieval < 50ms
- [ ] Decision engine with exclusions < 2s (same as without)
- [ ] Pagination with 10k orders still responsive

---

## Developer Implementation Checklist

### Flask Order History Service

- [ ] Implement `get_user_orders(user_id, limit, offset, sort, order, status_filter) -> list`
- [ ] Implement `get_order_details(order_id) -> dict`
- [ ] Implement `update_delivery_status(order_id, status) -> bool`
- [ ] Implement `add_delivered_books_to_avoid_list(order_id, user_id) -> bool`
- [ ] Implement `get_unified_exclude_list(user_id) -> set[book_id]`

### Flask Order History Endpoints

- [ ] GET `/api/users/{user_id}/orders` route with filtering/sorting
- [ ] GET `/api/users/{user_id}/orders/{order_id}` route
- [ ] GET `/api/users/{user_id}/excluded-books` route
- [ ] PATCH `/api/users/{user_id}/orders/{order_id}` route (update status)

### Frontend - Order History Page

- [ ] Create `/orders` route
- [ ] Table component with columns: Order #, Date, Items, Status, Total
- [ ] Status badges (Pending, Delivered, Cancelled)
- [ ] Sort buttons for Date, Status, Amount
- [ ] Filter form: Date range, Status dropdown
- [ ] Pagination: Previous/Next, page indicator
- [ ] Empty state for no orders
- [ ] Mobile responsive layout
- [ ] "View Details" links to order detail page
- [ ] Order detail page with full info + receipt

### Caching (Optional but Recommended)

- [ ] Redis cache for exclude-list per user (TTL: 1 hour)
- [ ] Invalidate cache on new order completion
- [ ] Implement cache key: `exclude_list:{user_id}`

### Database Setup

- [ ] Create `order_history` table with indices
- [ ] Migrate existing orders to order_history if needed
- [ ] Run migration script

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Duplicate recommendation rate | < 1% | Recommended books already received / total |
| Order history load time | < 200ms | P95 load time for /orders page |
| Exclude-list retrieval | < 50ms | P95 latency for unified exclude-list |
| Delivery tracking accuracy | 100% | Orders marked delivered match shipping data |
| User satisfaction (no dups) | >= 95% | Survey: "Never received duplicate books" |

---

## Deployment and Handoff

**Story Status Transitions:**
- [ ] Implement: Status remains `ready-for-dev`
- [ ] Submit for review: Update to `Status: review`
- [ ] Code review complete: Update to `Status: done`

**File Updates After Implementation:**
- Create `_bmad-output/implementation-artifacts/user/order_history_service.py`
- Update `_bmad-output/implementation-artifacts/nlu/app.py` with order endpoints
- Create `_bmad-output/implementation-artifacts/user/001_create_order_history_table.sql`
- Create `frontend/orders.html` or orders route
- Update `docs/api-specs.yaml` with order endpoints
- Commit: `Story 4.2: Delivered history tracking & duplicate exclusion`

**Next Story:** Story 4.3 (Subscription Lifecycle Controls)

---

## References

- **PRD:** _bmad-output/implementation-artifacts/prd-blind-date-book.md sections 4, 5, 6
- **Architecture:** _bmad-output/implementation-artifacts/architecture/architecture.md
- **Story Context:** _bmad-output/planning-artifacts/epics.md (Epic 4 Story 4.2)
