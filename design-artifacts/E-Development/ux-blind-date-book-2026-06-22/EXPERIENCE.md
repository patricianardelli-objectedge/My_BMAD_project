product: Blind Date Book Experience
status: in-progress
created: 2026-06-22
updated: 2026-06-22
---

# EXPERIENCE
**Blind Date Book Experience** — Information Architecture, Behavior & Key Journeys

## Foundation

**Form Factor**: Mobile-first (primary), Desktop parity. The unboxing moment is emotional and tactile; mobile users experience the full joy on device. Desktop users (gift shoppers researching on laptop) see the same flows with wider breathing room.

**UI System**: Custom component library (no external design system dependency). DESIGN.md tokens (colors, typography, spacing) drive all surfaces. See DESIGN.md for visual specs; this document owns behavior, states, and interaction patterns.

**Brand Voice**: Warm, conversational, playful (never corporate or formal). Microcopy celebrates the gift-giving moment. When the agent speaks, it feels like a friend, not a chatbot. When the app delights (e.g., "🎁 Your surprise is on its way!"), it's genuine, not trying-too-hard.

## Information Architecture

**Core Surfaces:**
1. **Homepage** — Hero video + story cards + optional "dive deeper" CTA to agent
2. **Agent Modal** — Conversational preference collection (5–7 turns)
3. **Mini Cart** — Review, subscription selector, checkout CTA
4. **Checkout** — Email, address, gift message (minimal form, <2 clicks)
5. **Profile** — Saved preferences, subscription mgmt, delivered book history
6. **Order Confirmation** — Success page + shipping ETA

**Navigation**: Minimal. Homepage ← → Cart/Profile (sticky header). Agent modal is full-screen overlay (escape closes, "skip to checkout" link below fold). No top nav; clarity through flow.

## Voice and Tone

**Principles:**
- **Warm**: Address user by first name when known ("Hi Sarah! Ready for a surprise?")
- **Conversational**: Agent uses natural language ("Tell me who this is for" not "Recipient classification required")
- **Playful**: Celebrate moments ("You're one step away from delighting them!")
- **Clear**: No jargon. "Surprise level" → "Light hint or full surprise?"

**Microcopy Examples:**
- Hero CTA: "Choose your gift now" or "Let me pick for you"
- Agent greeting: "Hey! Let's find the perfect book for your friend."
- Skip link: "Surprise me with the defaults"
- Subscription toggle: "Want to keep the magic coming? Subscribe."
- Confirm checkout: "You're all set. Your book will arrive in 3–5 days."

## Component Patterns

**Story Card** (see DESIGN.md for visual specs)
- **States**: Default, Hover (shadow + scale), Selected (gold border + icon)
- **Interaction**: Click → Adds to cart + opens agent modal OR checkout (depends on user path)
- **Variant**: Can display mood ("Cozy mystery"), recipient suggestion ("Perfect for a friend"), or genre tag
- **A11y**: ARIA label: "Add {mood} book to cart"

**Agent Modal** (see DESIGN.md for visual specs)
- **States**:
	- Ready (input field focused, blinking cursor, placeholder text visible)
	- Thinking (spinner, "Hold on..." message)
	- Next turn (new question rendered, previous response visible in history)
	- Complete (summary shown, "All set! Your book is ready" CTA)
- **Interaction**: User types → hits Enter or clicks "Next" → agent parses (backend /api/parse) → new question or summary
- **A11y**: ARIA live region for dynamic questions; screen-reader announced after each turn

**Mini Cart** (see DESIGN.md for visual specs)
- **States**:
	- Empty (icon + "Your cart is empty" + CTA to browse)
	- 1 item (book title + price + remove link)
	- Subscription selected (radio checked, e.g., "Monthly subscription")
	- Hover on item (remove link highlight in emerald)
- **Interaction**: Click subscription radio → mini-cart shows recurring badge ("Renews every month"); click remove → fade out + recount
- **A11y**: Item count announced; subscription selection read as "Monthly subscription, currently selected"

**Buttons & Links** (see DESIGN.md for visual specs)
- **Primary button** (Emerald): "Complete checkout", "Next", "Subscribe now"
- **Secondary button** (Sapphire): "Cancel", "Go back"
- **Accent link** (Gold): "Skip to checkout", "View terms"
- **Focus states**: All interactive elements have 2px gold focus-ring
- **A11y**: All buttons have aria-label if icon-only; links are underlined; focus order follows visual flow

## State Patterns

**Cart State** (managed in LocalStorage or session state)
- `cart.items[]` — {id, title, price, mood, recipient_age}
- `cart.subscription_type` — "one-time" | "monthly" | "bi-weekly" | "three-month"
- `cart.count` — Item count (displayed in header badge)

**User Preferences** (stored in profile after agent interaction)
- `preferences.recipient_type` — "self" | "gift"
- `preferences.recipient_age_range` — "under-12" | "18-24" | "25-34" | "35-44" | "45+"
- `preferences.genres[]` — ["romance", "horror", "history", ...]
- `preferences.avoid[]` — ["explicit", "violence", ...]
- `preferences.surprise_level` — "light_hint" | "moderate" | "full"

**Agent Modal State** (during conversation)
- `modal.turn` — 1–7 (current question number)
- `modal.history[]` — [{q, a}, ...] (all prior exchanges, displayed as chat)
- `modal.loading` — boolean (show spinner during parse)
- `modal.complete` — boolean (show summary, disable input, show CTA)

## Interaction Primitives

**Input Field**
- Placeholder: Contextual (e.g., "e.g., for my friend who loves mystery")
- On focus: Gold focus-ring appears, 2px
- On change: Validate (optional; no red errors, just helpful hints)
- On submit (Enter or "Next" click): Disable field, show spinner

**Modal Overlay**
- Background: Semi-transparent dark (rgba(0,0,0,0.4))
- Click outside: Closes modal (unless in middle of interaction; warn if unsaved)
- Escape key: Closes modal (same warning)
- Motion: Fade in 200ms, fade out 200ms

**Mini Cart Slide-Over**
- Position: Slides from right edge
- Click outside: Closes slide-over
- Motion: Slide in 300ms (easeOutCubic), slide out 200ms
- Stacking: If modal and cart open, modal above cart (z-index)

**Scroll Behavior**
- Story cards: Horizontal scroll on mobile (snap to card width), grid on desktop
- Agent modal: Chat history scrolls internally; modal itself fixed (doesn't scroll with page)
- Profile: Standard vertical scroll, sticky header

## Accessibility Floor

**WCAG AA Minimum:**
- **Color contrast**: All text ≥7:1 (Emerald on white: 8.2:1)
- **Focus indicators**: 2px gold ring on all interactive elements
- **Keyboard navigation**: Tab order follows visual flow; modals trap focus (tab loops within modal)
- **Screen reader support**:
	- ARIA labels for buttons: "Add emerald card to cart" (not just "button")
	- ARIA live regions for agent responses: `role="status" aria-live="polite"`
	- Form labels explicitly associated: `<label for="agent-input">`
- **Motion**: All animations <300ms; respect prefers-reduced-motion (disable motion for those users)
- **Responsive text**: Default 16px font size (no smaller than 14px); >1.5 line-height
- **Touch targets**: All buttons ≥44x44px (iOS), ≥48x48px (Android)

## Key Flows

### Flow 1: Sarah's Journey — Gift Shopper, Thoughtful Path

**Protagonist**: Sarah, 34, buys thoughtful gifts, values ritual and presentation.  
**Context**: Homepage on desktop (browsing during lunch break); looking for a birthday gift for her friend.  
**Climax**: "I found the perfect gift, and I feel confident about it."

1. **Land on homepage** → Auto-plays unboxing hero video (3s load, full-width emotional anchor). Text overlay: "Surprise someone you love." Below: "Choose your mood or let us pick."
2. **Scroll story cards** → Sees 3–4 options (Cozy Mystery, Literary Romance, Adventure, Self-Help). Reads the moods.
3. **Click "Cozy Mystery" card** → Card highlights (gold border), mini-cart badge updates ("1 item").
4. **Mini cart opens** (right slide-over) → Shows: "Cozy Mystery Book · $24.99 · One-time purchase (selected)" + Subscription options (radio buttons). Sarah leaves as "One-time".
5. **Click "Complete checkout"** → Form: Email, Address, Gift message. Sarah fills in (~30s). Submits.
6. **Success page** → "🎁 Your gift is on the way! Arrives in 3–5 days." Confetti animation (respects prefers-reduced-motion).

**Total time**: ~2 min. **Story beaten**: Sarah feels in control; the ritual (video + card selection + gift message) made it special.

---

### Flow 2: Mark's Journey — Surprise-Seeker, Fast Path

**Protagonist**: Mark, 27, enjoys serendipity, low friction. "Just surprise me."  
**Context**: Mobile, late evening; impulse buy for himself.  
**Climax**: "Checkout complete in <30s. Let's see what I get."

1. **Land on homepage** → Hero video plays (Sarah watches; Mark scrolls past immediately).
2. **Tap "Let me pick for you" CTA** → Agent modal opens full-screen with "Hey! Quick question: Is this for you or a gift?"
3. **Mark types "me"** (or "myself"). Agent: "Got it. Any genres you absolutely love?"
4. **Mark types "sci-fi"** → Spinner (200ms parse). Agent: "Nice! Full surprise or a light hint?" Mark: "Full surprise."
5. **Agent summary** → "Perfect. We'll find you an epic sci-fi read with zero spoilers."  "That's it! Add to cart?"
6. **Tap "Add to cart"** → Mini cart opens. Mark sees "Sci-Fi Book · $24.99 · One-time". Taps "Complete checkout".
7. **Checkout form** (auto-filled email from browser, address from prior order). Tap "Buy now".
8. **Success** → "You're all set! Book ships tomorrow."

**Total time**: ~30–45s. **Story beaten**: Mark got what he wanted (a surprise, no friction).

---

### Flow 3: Jenna's Journey — Parent Buyer, Detail Path + Subscription

**Protagonist**: Jenna, 40, parent of two, buys for kids and herself. Wants to control content.  
**Context**: Desktop, evening research; gift for 8-year-old daughter.  
**Climax**: "She's going to love this book, and I'm set for monthly surprises too."

1. **Land on homepage** → Watches unboxing hero (emotional anchor; thinks about her daughter). Scrolls story cards; doesn't find one that says "kids".
2. **Tap "Let me pick for you"** → Agent modal opens. "Who's this for?"
3. **Jenna types** → "My 8-year-old daughter. She loves dinosaurs and adventure."  
4. **Agent (next turn)** → "Awesome! Any topics to avoid? (e.g., scary, too advanced)"  
5. **Jenna** → "No explicit content, nothing too dark." (Parsing detects "avoid" context; backend marks avoid=["explicit", "dark"]).
6. **Agent** → "Perfect parent filter set. Full surprise or should we give her a hint?" Jenna: "Mild hint—tell her it's about adventure."
7. **Agent summary** → "8-year-old adventure book, dinosaur themes, age-appropriate, light hint. We'll find the perfect match!"
8. **Add to cart** → Mini cart shows book title + price. Jenna notices subscription toggle.
9. **Jenna taps "Monthly subscription"** → Radio checks; card updates "Monthly subscription, renews every 30 days".
10. **Complete checkout** → Form includes gift recipient name ("Emma"). Jenna checks "Gift message". Enters: "Happy birthday, Em! This one's for you. Love, Mom." Submits.
11. **Success** → "Subscribed! Your first book arrives in 3–5 days. Then every 30 days. Your daughter will get a new adventure every month." Link: "Manage subscription" (goes to profile).
12. **Profile (later)** → Jenna sees "Delivered books: {Adventure Dinosaur Book · June 22}. Won't send this again. Subscription: Active · Monthly · Renew July 22."

**Total time**: ~3–4 min. **Story beaten**: Jenna feels in control (content filters), delighted (monthly surprises for daughter), and confident (history tracking prevents duplicates).

---

## Responsive & Platform Considerations

**Mobile (375–767px)**
- Single-column story cards (full-width minus padding)
- Agent modal: Full-width minus 16px padding
- Mini cart: Full-width (no slide-over; expands from bottom)
- Touch targets: 44x44px minimum
- Swipe to dismiss modals (optional; Escape key always works)

**Desktop (1024px+)**
- 3-column story card grid
- Agent modal: 500px fixed width, centered
- Mini cart: 360px slide-over from right (persistent, doesn't close unless user closes)
- Hover states on all interactive elements (no hover on mobile via CSS)

## Inspiration & Anti-patterns

**Inspiration**:
- Netflix homepage (mood-driven discovery, beautiful imagery)
- Airbnb card design (photo + overlay + clear CTA)
- Calm app (warm palette, conversational tone, motion restraint)
- Unfold app (unboxing aesthetic, photography-first)

**Anti-patterns to avoid**:
- ❌ Too many modals at once (modal overload → cognitive load)
- ❌ Auto-playing video with sound (aggressive; muted-by-default only)
- ❌ Endless scroll (ship with clear stopping point)
- ❌ Generic copy ("Click here", "Submit") → Use warm, specific language
- ❌ Heavy animations (>300ms; <prefers-reduced-motion awareness)

## Cross-references to DESIGN.md

- **Story Card layout** → See DESIGN.md § Components § Story Card
- **Agent Modal styling** → See DESIGN.md § Components § Agent Modal
- **Color palette for focus rings** → See DESIGN.md § Colors (gold #D4AF37)
- **Typography for labels** → See DESIGN.md § Typography (14px sans-serif)
- **Spacing grid** → See DESIGN.md § Layout & Spacing (8px base unit)
- **Motion timing** → See DESIGN.md § Components (fade/slide <300ms)

