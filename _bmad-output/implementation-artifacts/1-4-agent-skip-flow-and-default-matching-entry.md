# Story 1.4: Agent Skip Flow and Default Matching Entry

**Epic:** Discovery and Preference Capture  
**Status:** done  
**Created:** 2026-06-23  

---

## Story Summary

As a shopper in a hurry, I want to skip the conversational flow and continue with defaults or manual entry, so that I can still complete a purchase with minimal friction.

**Dependencies:** Story 1.2 (Conversational Agent Modal) - Story 1.4 implements the "Skip" button behavior and default matching path.

**References:** FR13, NFR2, NFR5

**Source Documents:**
- PRD sections 7, 8.1
- UX DESIGN sections Agent Modal, Skip Flow
- docs/api-specs.yaml

---

## Acceptance Criteria

### AC1: Skip Button Behavior
**Given** the modal is open  
**When** the shopper selects Skip  
**Then** the system offers default matching and manual profile entry paths  
**And** records that skip mode was chosen.

**Task Breakdown:**
- [ ] Skip button visible in agent modal ("Skip flow" text or icon)
- [ ] Skip button click closes chat flow section and shows skip confirmation
- [ ] Skip confirmation message: "No problem! I'll match you with the best pick based on what you've told me so far."
- [ ] If no turns completed yet, default message: "I'll match you with a popular pick tailored to the mood you selected."
- [ ] Skip flow transitions to confirmation summary (same as normal flow end)
- [ ] Confirmation summary shows collected fields + defaults for any missing fields
- [ ] Skip mode indicator recorded in agentState.skip_mode = true

### AC2: Default Matching Path
**Given** skip mode is used  
**When** the shopper continues to recommendation/cart  
**Then** the flow proceeds without blocked fields  
**And** unresolved preference values are marked as optional or unknown.

**Task Breakdown:**
- [ ] Unresolved fields populated with defaults: `{ recipient: 'self', age_range: null, genres: [], avoid: [], surprise_level: 'balanced', mood: null }`
- [ ] Confirmation summary displays defaults clearly: e.g., "For: You (default)", "Surprise: Balanced (default)"
- [ ] Continue button enabled even with empty fields (no validation blocking)
- [ ] No "required field" error messages on skip path
- [ ] AI decision engine (Story 2.1) receives default preferences and generates recommendation
- [ ] Checkout flow after skip mode works identically to normal path

### AC3: Manual Profile Entry Option (Future Extensibility)
**Given** a user chooses skip  
**When** presented with options  
**Then** the system allows inline field editing before continuing  
**And** changes are saved to confirmation summary.

**Task Breakdown:**
- [ ] Confirmation summary fields are editable (not just display-only)
- [ ] User can click on any field (e.g., "For: You") to inline-edit
- [ ] Field editing UI: simple text input with Apply/Cancel buttons
- [ ] Edit changes update confirmation summary immediately
- [ ] Edited values override defaults in API call to AI decision
- [ ] No new form page needed; all edits inline in confirmation section

### AC4: Analytics and Tracking
**Given** a user takes the skip path  
**When** the flow completes  
**Then** the skip mode choice is logged and queryable  
**And** pilot team can analyze skip rate and success metrics.

**Task Breakdown:**
- [ ] Skip mode recorded in agentState object
- [ ] Skip event logged when skip button clicked: `{ event: 'skip_clicked', turn: agentState.currentTurn, session_id }`
- [ ] Skip flow completion logged: `{ event: 'skip_completed', fields_collected: {...}, session_id }`
- [ ] Browser console logs skip events for debugging
- [ ] Skip mode persists to any analytics/tracking system (future integration point)

---

## Implementation Context

### Frontend File Structure

**Primary Implementation:**  
`design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html`

**Styling:**  
`design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/styles.css`

**Dependencies:**
- Story 1.2 agentState object and modal functions already in place
- Skip button already wired to `agentSkip.addEventListener('click', ...)`

### Skip Flow State Machine

```
User clicks "Skip flow" button (at any turn 1-6)
  ↓
Close chat section, show skip confirmation message
  ↓
Populate agentState with collected data + defaults for missing fields
  ↓
agentState.skip_mode = true
  ↓
Log skip event
  ↓
Show confirmation summary (same UI as normal flow)
  ↓
User sees all fields (collected + defaults)
  ↓
Optional: User can edit fields inline (Future: AC3)
  ↓
User clicks "Continue to matches"
  ↓
Modal closes, call AI decision API with preferences
  ↓
Add recommended book to cart, open mini-cart
```

### Skip Flow UX Details

**Skip Confirmation Message:**
- If turns completed: "No problem! I'll match you with the best pick based on what you've told me so far."
- If no turns completed: "I'll match you with a popular pick tailored to the mood you selected."

**Confirmation Summary on Skip:**
```
┌────────────────────────────────────────────────┐
│ Here's what I understood:                       │
├────────────────────────────────────────────────┤
│ For: You (default)                             │
│ Age: (not specified)                           │
│ Genres: (not specified - will recommend broad) │
│ Mood: (from trail: Adventure)                  │
│ Avoid: (none)                                  │
│ Surprise: Balanced (default)                   │
├────────────────────────────────────────────────┤
│ [Continue to matches] [Edit answers]           │
└────────────────────────────────────────────────┘
```

**Defaults Applied on Skip:**
```javascript
const skipDefaults = {
  recipient_type: agentState.recipient_type || 'self',
  recipient_age_range: null, // Unknown, let AI decide
  genres: agentState.genres, // Keep what was collected
  mood: agentState.mood || 'balanced', // From selected trail
  avoid: agentState.avoid, // Keep what was collected
  surprise_level: agentState.surprise_level || 'balanced'
};
```

### Data Flow

**Skip Event → API Call:**
```javascript
// When user clicks "Continue to matches" after skip
const preferences = {
  recipient_type: agentState.recipient_type || 'self',
  recipient_age_range: agentState.recipient_age_range,
  genres: agentState.genres || [],
  avoid: agentState.avoid || [],
  surprise_level: agentState.surprise_level || 'balanced',
  skip_mode: true,
  turns_completed: agentState.currentTurn,
  session_id: agentState.selectedTrail
};

// Call AI decision API (Story 2.1)
POST /api/ai/decide
{
  "preferences": preferences,
  "session_id": agentState.selectedTrail
}
```

---

## Testing Requirements

### Unit Tests (JavaScript)

- [ ] `test_skip_button_click()` – Skip button click triggers correct state change
- [ ] `test_skip_applies_defaults()` – Unspecified fields populated with defaults
- [ ] `test_skip_preserves_collected_data()` – Already-parsed data kept (not overwritten)
- [ ] `test_skip_mode_flag()` – agentState.skip_mode set to true
- [ ] `test_skip_at_different_turns()` – Skip works at turn 1, 3, and 6 (all turns)
- [ ] `test_skip_confirmation_message()` – Correct message shown based on turns completed
- [ ] `test_skip_confirmation_summary_renders()` – All fields displayed in confirmation (collected + defaults)

### Functional Tests (Frontend)

- [ ] Skip button visible on modal
- [ ] Clicking skip closes chat section, shows confirmation
- [ ] Confirmation summary renders all 6 fields with values or "(default)" label
- [ ] Continue button enabled (no validation errors)
- [ ] Edit button (if implemented) allows inline field changes
- [ ] Clicking Continue closes modal and calls AI decision API
- [ ] Skip works from turn 1 (immediate skip, all defaults)
- [ ] Skip works from turn 6 (partial data collected + defaults for missing)
- [ ] Focus management: Focus moves to confirmation title on skip

### UI/UX Tests

- [ ] Skip button text clear and accessible
- [ ] Skip confirmation message is friendly and reassuring
- [ ] Confirmation summary layout readable with collected/default indicators
- [ ] Inline edit controls (if AC3 implemented) are obvious and intuitive
- [ ] No visual glitches when switching from chat section to confirmation
- [ ] Mobile: Skip button visible and touch-friendly on all screen sizes
- [ ] Responsive: Confirmation summary readable on mobile/tablet/desktop

### Accessibility Tests

- [ ] Skip button keyboard-operable (Tab focus, Enter to activate)
- [ ] Confirmation summary has proper heading hierarchy
- [ ] Field labels and values properly associated (not just visual alignment)
- [ ] Focus visible on all interactive elements
- [ ] Screen reader announces "Skipped preference collection" or similar
- [ ] No focus traps or unreachable elements

### Integration Tests

- [ ] Skip → Confirmation → Continue → AI decision API call succeeds
- [ ] Skip mode flag passed to AI decision endpoint
- [ ] Returned recommendation added to cart correctly
- [ ] Mini cart opens after skip flow completion
- [ ] Clicking "Edit answers" from confirmation goes back to chat section (if needed)

### Analytics Tests

- [ ] Skip event logged to console (or analytics backend)
- [ ] Skip completion event includes turn count and collected fields
- [ ] Session_id correlates skip event with other parse events
- [ ] No errors in event logging

---

## Developer Implementation Checklist

### HTML Structure
- [ ] Skip button exists in agent modal (already in Story 1.2)
- [ ] Skip confirmation message element (hidden by default)
- [ ] Skip message displays based on turns_completed state
- [ ] Confirmation summary shows "(default)" indicators for unparsed fields

### CSS Styling
- [ ] Skip confirmation message styled consistently with agent theme
- [ ] Field labels in confirmation marked as "(default)" with subtle styling (opacity 0.7 or gray text)
- [ ] Edit buttons (if AC3) styled as secondary buttons
- [ ] Responsive layout for confirmation summary on all breakpoints

### JavaScript Logic
- [ ] agentSkip button click handler calls `handleSkipFlow()`
- [ ] `handleSkipFlow()` function: close chat, show confirmation, set skip_mode=true
- [ ] Apply defaults for any null/empty fields
- [ ] Build confirmation summary with collected data + defaults
- [ ] Log skip event: `console.log({ event: 'skip_clicked', turn: agentState.currentTurn })`
- [ ] Handle edge case: skip on turn 1 (no data collected yet, use trail-based defaults)
- [ ] Confirmation Continue button calls same logic as normal flow confirmation continue

### Inline Edit Implementation (AC3 - Optional for v1)
- [ ] Confirmation summary fields are clickable (data attributes or event delegation)
- [ ] Clicking field shows inline input with current value
- [ ] Apply/Cancel buttons for inline edit
- [ ] Updated values reflected in confirmation summary and agentState
- [ ] Inline edits persist to API call

### Logging & Telemetry
- [ ] Skip event logged: turn number, session_id
- [ ] Skip completion event logged: fields_collected, fields_with_defaults, session_id
- [ ] Analytics integration point: emit custom event for skip flow (GA, Mixpanel, etc.)

---

## Success Criteria

| Metric | Target | How to Measure |
|--------|--------|-----------------|
| Skip button visible | 100% | Visual inspection on modal |
| Skip flow completion | >= 95% | No errors in console when skipping |
| Defaults applied correctly | 100% | Confirmation summary shows all 6 fields |
| Focus management | 100% | Keyboard navigation test (Tab, Enter) |
| Mobile friendliness | >= 95% | Responsive design test on 3 devices |
| Accessibility compliance | WCAG AA | axe/WAVE scan of confirmation screen |
| Analytics logging | 100% | Skip events logged to console/backend |

---

## Deployment and Handoff

**Story Status Transitions:**
- [ ] Implement: Status remains `ready-for-dev`
- [ ] Submit for review: Manually update story artifact to `Status: review`
- [ ] Code review complete, ready to merge: Manually update to `Status: done`
- [ ] Update sprint-status.yaml: Move story from backlog → review → done

**File Updates After Implementation:**
- Update `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html` with skip flow logic
- Update `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/styles.css` if new elements need styling
- Commit changes with message: `Story 1.4: Agent skip flow for users who want defaults without conversation`

**Next Story:** Story 2.1 (Rule-Based Decision Engine with Candidate Scoring) – Epic 2

---

## References

- **Story 1.2:** Conversational Agent Modal (depends on this for skip button and agentState)
- **UX Design:** design-artifacts/E-Development/ux-blind-date-book-2026-06-22/DESIGN.md
- **PRD:** _bmad-output/implementation-artifacts/prd-blind-date-book.md sections 7, 8.1
- **Story Context:** _bmad-output/planning-artifacts/epics.md (Epic 1 Story 1.4)
