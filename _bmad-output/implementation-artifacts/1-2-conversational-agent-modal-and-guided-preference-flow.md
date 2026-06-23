# Story 1.2: Conversational Agent Modal and Guided Preference Flow

**Epic:** Discovery and Preference Capture  
**Status:** done  
**Created:** 2026-06-23  

---

## Story Summary

As a shopper selecting a gift, I want a conversational modal that gathers recipient and taste preferences in plain language, so that the recommendation engine can personalize the surprise.

**Dependencies:** Story 1.1 (Homepage Hero and Trail Selection) - Requires session trail state.

**References:** FR2, NFR1, NFR3, UX-DR3, UX-DR7, UX-DR10

**Source Documents:**
- PRD sections 7, 8.1, 9
- Architecture sections 1-3
- UX DESIGN sections Agent Modal, Preference Flow, Typography & Colors
- docs/api-specs.yaml

---

## Acceptance Criteria

### AC1: Modal Appearance and Accessibility
**Given** a shopper starts the preference flow  
**When** the modal opens  
**Then** the modal appears in under 1 second with accessible focus management  
**And** supports keyboard-only navigation and reduced-motion behavior.

**Task Breakdown:**
- [ ] Modal renders with 500px max-width, emerald (#1B4D3E) header, white body background
- [ ] Modal appears in under 1 second (CSS fade/slide transition <300ms)
- [ ] Initial focus moves to modal title on open (aria-label="Preference Collection Modal")
- [ ] Keyboard navigation works: Tab through inputs, Escape closes modal, Enter submits form
- [ ] Focus trap active: Tab from last field loops to first field in modal
- [ ] Modal uses @media (prefers-reduced-motion: reduce) with animation-duration: 0.01ms
- [ ] aria-live region exists for turn-by-turn agent responses
- [ ] Modal closes cleanly and returns focus to trigger button (chooseTrail CTA)
- [ ] Contrast ratios meet WCAG AA: text >= 4.5:1, interactive elements >= 3:1

### AC2: Preference Capture in 5–7 Turns
**Given** the shopper answers prompts  
**When** the flow is completed in 5-7 turns  
**Then** the system captures recipient type, age band, genres, mood, surprise level, and avoid preferences  
**And** displays a confirmation summary before continuing.

**Task Breakdown:**
- [ ] Turn sequence: Intro → Recipient Type → Age Band → Genres → Mood/Occasion → Avoid List → Surprise Level
- [ ] Each turn advances automatically after user submits input (Enter or Submit button click)
- [ ] Turn counter or progress indicator visible (e.g., "Question 1 of 6")
- [ ] Agent response rendered in aria-live region for screen readers
- [ ] User input field always visible and keyboard-operable (no text input hiding)
- [ ] Summary data collected: { recipient_type, recipient_age_range, genres, mood, surprise_level, avoid, trail }
- [ ] Summary confirmation card displays before proceeding to AI decision engine
- [ ] User can Edit (go back one turn) or Continue from confirmation
- [ ] Confirmation summary passes validation before allowing Continue

### AC3: Integration with Parse Service
**Given** the shopper submits free-text preference input  
**When** the frontend calls `/api/agent/parse`  
**Then** structured preference data is returned and displayed in a confirmation  
**And** silent parse failures do not block progression.

**Task Breakdown:**
- [ ] Frontend submits text input and selectedTrail (from Story 1.1 session state) to `/api/agent/parse`
- [ ] API response includes: { recipient, age_range, genres, avoid, surprise_level, raw }
- [ ] Frontend normalizes response keys: recipient → recipient_type, age_range → recipient_age_range
- [ ] Parsed data is rendered in confirmation summary with human-readable labels
- [ ] If parse fails or returns empty fields, default values are applied: { recipient_type: 'self', genres: [], avoid: [], surprise_level: 'medium' }
- [ ] Ambiguity events logged and user prompted for clarification (error message in aria-live)
- [ ] Retry mechanism: User can resubmit turn without closing modal

### AC4: Modal Responsive Design and Touch Accessibility
**Given** a shopper on mobile/tablet  
**When** the modal is displayed  
**Then** it adapts to screen width with readable text and touch-friendly controls  
**And** input fields are keyboard-operable on all platforms.

**Task Breakdown:**
- [ ] Desktop (1024px+): Modal 500px max-width, centered, with semi-transparent backdrop
- [ ] Tablet (768–1023px): Modal 90vw width, max 500px, full-screen height overflow scrollable
- [ ] Mobile (375–767px): Modal full-width with safe area inset, scrollable turns, sticky footer with Submit button
- [ ] Input field font-size >= 16px on all devices (prevents auto-zoom on iOS)
- [ ] Touch targets (buttons, inputs) >= 44px height on mobile
- [ ] Visible focus ring on inputs: 2px gold outline, 2px offset
- [ ] Viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`

---

## Implementation Context

### Frontend File Structure

**Primary Implementation:**  
`design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html`

**Styling:**  
`design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/styles.css`

**Dependencies:**
- `openapi-client.js` – Provides `window.BlindDateApi.parseAgent(text)` for `/api/agent/parse` calls
- `session storage` – Retrieves selectedTrail (set by Story 1.1)

### UX Design Specification Reference

**Design System Tokens (from UX DESIGN):**
- **Colors:**  
  - Primary: Emerald #1B4D3E  
  - Secondary: Sapphire #0F3A5F  
  - Accent: Gold #D4AF37  
  - White: #FEFCF8  
  - Text: #153A2D  
- **Typography:**  
  - Headlines: Georgia (serif), 700 weight  
  - Body: Inter (sans-serif), 400 weight, 14–16px  
  - Modal title: Georgia 24px, emerald  
  - Input labels: Inter 14px, #153A2D  
  - Agent response: Inter 15px, warm white on emerald  
- **Layout & Spacing:**  
  - Base grid: 8px  
  - Modal padding: 24px  
  - Card border-radius: 12px  
  - Modal border-radius: 16px  
  - Input border-radius: 8px  
  - Focus ring: 2px gold, 2px offset  
- **Interaction:**  
  - Modal entrance: Fade + slide up (<300ms cubic-bezier(0.34, 1.56, 0.64, 1))  
  - Modal exit: Fade out (<200ms ease-in)  
  - Input focus: 3px gold outline, no shadow  

**Agent Modal Layout** (from UX DESIGN):
```
┌────────────────────────────────────────────────────┐
│ Emerald Header (#1B4D3E)                           │ 24px height
│ "Let's find your next read"  (Georgia, 24px, white)│
│ [X] Close button (top-right)                       │
├────────────────────────────────────────────────────┤
│ White body, padding 24px                           │
│                                                    │
│ [Agent turn response] (aria-live)                  │
│ Lorem ipsum dolor sit amet...                      │
│                                                    │
│ <input type="text" placeholder="..." />            │
│ [Submit] button (emerald, 12px 16px padding)       │
│                                                    │
│ ─────────────────────────────────────────────────  │
│ Question 1 of 6                                    │
└────────────────────────────────────────────────────┘
```

### Turn Flow State Machine

```
Turn 1: Intro
  Agent: "Tell me about the lucky person. Who is this gift for?"
  Parse: recipient type (self, parent, sibling, friend, partner, colleague, other)
  
Turn 2: Age Band
  Agent: "How old are they?"
  Parse: age_range (teen, 20s, 30s, 40s, 50s, 60+)
  
Turn 3: Genres & Interests
  Agent: "What genres do they love? (e.g., romance, sci-fi, mystery, memoir)"
  Parse: genres array + mood (adventurous, cozy, thought-provoking, etc.)
  
Turn 4: Occasion & Mood
  Agent: "What's the occasion? Birthday, holiday, just-because?"
  Parse: occasion, mood hints for scoring
  
Turn 5: Content Avoidance
  Agent: "Anything they should avoid? (violence, explicit content, heavy themes)"
  Parse: avoid array
  
Turn 6: Surprise Level
  Agent: "How adventurous should this pick be? (safe/balanced/wildcard)"
  Parse: surprise_level (safe, balanced, wildcard)
  
Turn 7: Confirmation
  System: Displays summary of all collected fields
  User: Edit (back) or Continue to AI decision
```

### State Variables to Preserve

```javascript
{
  selectedTrail: String,              // From Story 1.1 session storage
  recipient_type: String,             // 'self' | 'parent' | 'sibling' | 'friend' | 'partner' | 'colleague' | 'other'
  recipient_age_range: String,        // 'teen' | '20s' | '30s' | '40s' | '50s' | '60+'
  genres: Array<String>,              // ['romance', 'sci-fi', ...]
  mood: String,                       // 'adventurous' | 'cozy' | 'thought-provoking' | ...
  avoid: Array<String>,               // ['violence', 'explicit', ...]
  surprise_level: String,             // 'safe' | 'balanced' | 'wildcard'
  currentTurn: Number,                // 1–7 tracking position
  isModalOpen: Boolean,               // Modal visibility state
  parseErrors: Array<String>          // Collect ambiguity/parse failures for logging
}
```

### API Integration Points

**Endpoint:** `POST /api/agent/parse` (public, no auth)

**Request:**
```json
{
  "text": "Gift for my 8-year-old niece who loves fantasy",
  "session_id": "optional_session_uuid",
  "context": {
    "turn": 2,
    "selected_trail": "adventure"
  }
}
```

**Response:**
```json
{
  "recipient": "sibling",             // Maps to recipient_type
  "age_range": "teen",                // Maps to recipient_age_range (note: parser returns 'teen' not 'tween')
  "genres": ["fantasy"],
  "avoid": [],
  "surprise_level": "balanced",
  "raw": "Gift for my 8-year-old niece who loves fantasy",
  "confidence": 0.92,
  "ambiguities": []
}
```

**Frontend Normalization:**
```javascript
const normalized = {
  recipient_type: data.recipient,
  recipient_age_range: data.age_range,
  genres: data.genres || [],
  avoid: data.avoid || [],
  surprise_level: data.surprise_level || 'balanced',
  raw_input: data.raw
};
```

---

## Testing Requirements

### Unit Tests (JavaScript)

- [ ] `parseModalState()` – Initializes state with correct defaults
- [ ] `advanceTurn()` – Increments turn counter, validates data, triggers agent response
- [ ] `submitTurn(userInput)` – Calls `/api/agent/parse`, normalizes response, updates state
- [ ] `handleBackTurn()` – Reverts to previous turn, preserves user input
- [ ] `buildConfirmationSummary()` – Renders all captured fields in human-readable format
- [ ] `normalizeParsedData(apiResponse)` – Maps raw keys to frontend schema

### Keyboard Navigation Tests

- [ ] Tab navigation cycles through modal inputs (focus trap)
- [ ] Escape key closes modal
- [ ] Enter in input field submits turn (or Enter on Submit button)
- [ ] Focus returns to trigger CTA on close
- [ ] No keyboard traps or unreachable elements
- [ ] Focus-visible applied to all interactive elements

### Accessibility Tests (Lighthouse, axe)

- [ ] Color contrast >= 4.5:1 for text, >= 3:1 for UI components
- [ ] aria-label on modal and form fields
- [ ] aria-live region announces agent responses
- [ ] Keyboard navigable without a mouse
- [ ] Screen reader announces turn progress ("Question 1 of 6")
- [ ] Error messages announced in aria-live region

### Integration Tests (Static Frontend)

- [ ] Modal opens on Story 1.1 CTA click
- [ ] Session storage retains selectedTrail after Story 1.1
- [ ] Modal submits parsed data correctly to `/api/agent/parse`
- [ ] Confirmation summary displays all parsed fields
- [ ] Continue button transitions to AI decision engine (Story 2.1 integration point)
- [ ] Modal closes on Escape or after completion
- [ ] Page refresh mid-flow persists state or clears gracefully

### Responsive Design Tests

- [ ] Desktop (1024px): 500px centered modal
- [ ] Tablet (768–1023px): 90vw modal with scroll
- [ ] Mobile (375–767px): Full-width modal with safe inset
- [ ] Touch targets >= 44px
- [ ] Input font-size >= 16px (no iOS auto-zoom)
- [ ] Modal scrolls without body scroll

### Performance Tests

- [ ] Modal CSS + JS < 50KB (gzipped)
- [ ] Parse API request/response < 500ms (p95)
- [ ] Modal open-to-visible < 1000ms
- [ ] No layout shift on modal enter/exit (CLS < 0.1)

---

## Developer Implementation Checklist

### HTML Structure
- [ ] Modal container with backdrop semi-transparent overlay
- [ ] Modal header with title and close button [X]
- [ ] Form with input field, agent response region (aria-live)
- [ ] Submit button (styled as emerald primary button)
- [ ] Progress indicator (Turn 1 of 6)
- [ ] Confirmation summary section (hidden by default)
- [ ] Edit/Continue buttons on confirmation

### CSS Styling
- [ ] Modal entrance animation (fade + slide, <300ms)
- [ ] Modal exit animation (fade, <200ms)
- [ ] Input focus-visible: 2px gold outline, 2px offset
- [ ] Button hover states: emerald with rgba gold background overlay
- [ ] Modal responsive breakpoints (desktop/tablet/mobile)
- [ ] prefers-reduced-motion: remove all animations
- [ ] Color contrast checks passed (axe/Lighthouse)
- [ ] Touch-friendly sizing (44px+ targets)

### JavaScript Logic
- [ ] Initialize modal state on Story 1.1 trail selection
- [ ] Retrieve selectedTrail from sessionStorage
- [ ] Parse `/api/agent/parse` response and normalize keys
- [ ] Advance turn on form submit
- [ ] Validate turn data before advancing
- [ ] Handle parse failures with fallback defaults
- [ ] Display confirmation summary
- [ ] Transition to AI decision (Story 2.1) on Continue
- [ ] Manage focus trap and focus return on close
- [ ] Log parseErrors for pilot tuning

### API Integration
- [ ] Call `/api/agent/parse` with normalized payload
- [ ] Handle network errors gracefully (retry or fallback)
- [ ] Map API response keys to frontend schema
- [ ] Log ambiguities to parseErrors array

### Accessibility Audit
- [ ] WAVE/axe scan: 0 errors, 0 contrast failures
- [ ] Keyboard-only navigation complete
- [ ] Screen reader testing (NVDA/JAWS): All controls announced
- [ ] Focus management: Escape, Tab trap, return focus on close

---

## File Intelligence and Analysis

### Existing index.html Usage Patterns

**From Story 1.1 implementation:**
- Modal pattern: `#agent-modal { display: flex; opacity: 0; pointer-events: none; transition: opacity 0.3s; }`
- Opening modal: Set `#agent-modal.open { opacity: 1; pointer-events: auto; }`
- Focus trap pattern: In event listener, check if (e.key === 'Tab')
- Session storage pattern: `sessionStorage.setItem('selectedTrail', mood)` for trail persistence
- aria-live pattern: `<p id="selected-trail" role="status" aria-live="polite">` for announcing updates

**Expected inline JavaScript structure:**
```javascript
function openAgentModal() {
  const modal = document.getElementById('agent-modal');
  modal.classList.add('open');
  // Focus to modal title or first input
  document.getElementById('agent-input').focus();
}

function submitTurn() {
  const userInput = document.getElementById('agent-input').value;
  const selectedTrail = sessionStorage.getItem('selectedTrail') || 'balanced';
  
  // Call parseAgent from API client
  window.BlindDateApi.parseAgent(userInput)
    .then(data => {
      const normalized = normalizeParsedData(data);
      updateModalState(normalized);
      advanceTurn();
    })
    .catch(err => handleParseError(err));
}

function handleEscapeKey(e) {
  if (e.key === 'Escape' && modal.classList.contains('open')) {
    closeAgentModal();
  }
}
```

### Existing styles.css Usage Patterns

**From Story 1.1 implementation:**
- Modal backdrop: `.modal-backdrop { position: fixed; background: rgba(0,0,0,0.2); }`
- Focus-visible pattern: `.agent-input:focus-visible { outline: 2px solid #D4AF37; outline-offset: 2px; }`
- Button patterns: `.button.primary { background: #1B4D3E; color: #FEFCF8; }`
- Responsive grid patterns: `@media (min-width: 768px) { ... }`
- prefers-reduced-motion pattern: `@media (prefers-reduced-motion: reduce) { animation-duration: 0.01ms; }`

---

## Deployment and Handoff

**Story Status Transitions:**
- [ ] Implement: Status remains `ready-for-dev`
- [ ] Submit for review: Manually update story artifact to `Status: review`
- [ ] Code review complete, ready to merge: Manually update to `Status: done`
- [ ] Update sprint-status.yaml: Move story from backlog → review → done

**File Updates After Implementation:**
- Update `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html` with modal markup and JS logic
- Update `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/styles.css` with modal styling and animations
- Commit changes with message: `Story 1.2: Conversational agent modal with 5-7 turn preference flow`

**Next Story:** Story 1.3 (Parse Service Integration with Ambiguity Logging)

---

## References

- **Design Document:** design-artifacts/E-Development/ux-blind-date-book-2026-06-22/DESIGN.md
- **UX Scenarios:** design-artifacts/C-UX-Scenarios/
- **API Specification:** docs/api-specs.yaml
- **Architecture:** _bmad-output/implementation-artifacts/architecture/architecture.md
- **NLU Parser:** _bmad-output/implementation-artifacts/nlu/parser.py
- **API Client:** design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/api-client/openapi-client.js
