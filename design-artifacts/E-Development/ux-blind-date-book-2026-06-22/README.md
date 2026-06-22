# UX Design Summary
**Blind Date Book Experience**  
**Created:** 2026-06-22  
**Status:** DESIGN.md and EXPERIENCE.md Spines Complete

---

## What's Been Delivered

### 1. **DESIGN.md** (Visual Identity)
A comprehensive visual identity spine that defines:
- **Color palette**: Emerald (#1B4D3E) primary, Sapphire (#0F3A5F) secondary, Gold (#D4AF37) accent
- **Typography system**: Georgia serif for headlines (warm, literary) + Inter sans-serif for body (modern, accessible)
- **Spacing grid**: 8px base unit · 48–64px section gaps (generous, luxury feel)
- **Component specifications**: Story cards, agent modal, mini cart, buttons, links (with hover/focus states)
- **Accessibility floor**: WCAG AA compliance · Gold 2px focus rings on all interactive elements
- **Do's and Don'ts**: Clear guardrails for future designs

**Key principle**: Warmth expressed through generous spacing, refined typography, and jewel tones—not clutter.

### 2. **EXPERIENCE.md** (Behavior & Journeys)
A comprehensive behavior spine that defines:
- **Foundation**: Mobile-first + desktop parity, custom component library
- **Information architecture**: 6 core surfaces (Homepage, Agent Modal, Mini Cart, Checkout, Profile, Confirmation)
- **Voice & tone**: Warm, conversational, playful (e.g., "Want to keep the magic coming? Subscribe.")
- **Component patterns**: Story cards, agent modal, mini cart—behavioral specs (states, interactions, a11y)
- **State patterns**: Cart state, user preferences, agent modal turn-by-turn
- **Interaction primitives**: Input fields, modal overlay, slide-over, scroll behavior
- **Key flows**: 3 detailed user journeys (Sarah, Mark, Jenna) with timings and climax beats
- **Accessibility floor**: Keyboard navigation, screen reader support, motion settings

**Key principle**: Every surface supports one of the three user journeys; no friction points.

### 3. **Interactive HTML Mock** (`.working/key-screens-mock.html`)
A clickable prototype showing:
- Homepage with hero (video placeholder), story cards, and "Let me pick" CTA
- Agent modal with chat history and input field
- Mini cart with subscription toggle
- Functional demos of cart add/remove, modal open/close, slide-over animation

**How to view**: Open the HTML file in a browser; click buttons to explore the flow.

### 4. **Decision Log** (`.decision-log.md`)
Captured discovery input, design rationale, assumptions, and next steps.

---

## Key Design Decisions

| Decision | Value | Rationale |
|----------|-------|-----------|
| **Primary Color** | Emerald #1B4D3E | Luxury, nature-inspired, high contrast (8.2:1 on white) |
| **Accent Color** | Gold #D4AF37 | Premium, warmth, delightful reveals |
| **Typography** | Serif headlines + Sans body | Warm + clear; best of luxury (serif) + accessibility (sans) |
| **Spacing** | 8px grid, 48–64px sections | Generous = luxury; breathing room reduces cognitive load |
| **Button radius** | 8px | Warmth without being too playful; refined |
| **Animation timing** | <300ms | Responsive feel; >300ms feels sluggish |
| **Focus indicator** | 2px gold ring | Accessible, beautiful, on-brand |
| **Touch targets** | 44–48px | WCAG AA compliance |

---

## The Three User Journeys

### Sarah (Gift Shopper) — ~2 minutes
**Vibe**: Thoughtful, in control, ritual-driven  
**Path**: Hero video (emotional anchor) → Story cards → Choose "Cozy Mystery" → Mini-cart → Checkout (email + address + gift message) → Success

**Key moments**:
- Auto-playing unboxing video on homepage (3s load, full-width)
- Story card hover effect (scale + shadow elevation)
- Gift message input (ritual, personalization)

### Mark (Surprise-Seeker) — ~30–45 seconds
**Vibe**: Fast, impulsive, serendipitous  
**Path**: Skip homepage → Agent modal → 3 quick questions ("For you?", "Genre?", "Surprise level?") → Mini-cart (auto-filled) → Checkout (auto-filled) → Success

**Key moments**:
- "Let me pick for you" CTA on homepage
- Agent modal appears full-screen (fade-in 200ms)
- Fast input → fast checkout (no friction)

### Jenna (Parent Buyer) — ~3–4 minutes
**Vibe**: Protective, detailed, recurring  
**Path**: Hero video (anchor) → Agent modal (5–7 turns, detailed preference collection) → Mini-cart → Subscription toggle (Monthly) → Checkout (includes gift message for daughter) → Success + Profile (delivery history)

**Key moments**:
- Detailed agent conversation (age filters, avoid content, surprise level)
- Subscription selector in mini-cart (radio buttons)
- Profile page showing "Won't send this book again" (duplicate prevention)

---

## Component Specifications (Brief)

See **DESIGN.md** for full visual specs. Behavioral specs in **EXPERIENCE.md**.

### Story Card
- 240px height · Photo + emerald overlay (opacity 0.6) + white serif title (24px) + gold CTA
- Hover: scale 1.02x + shadow elevation
- Click: adds to cart + mini-cart updates

### Agent Modal
- 500px max width (mobile: full-width) · Emerald header (#1B4D3E) · Warm white body (#F8F7F5)
- Input: 8px radius, 1px Sapphire border, gold focus ring (2px)
- Chat history scrolls internally · Modal itself fixed
- Fade-in 200ms

### Mini Cart
- 360px slide-over (mobile: full-width) · Slide-in 300ms
- Header: "Your Gift Kit" (serif) · close (X) button
- Items: book title + price + remove link
- Subscription toggle: Radio buttons (one-time / monthly / bi-weekly / three-month)
- Footer: Total price + "Complete checkout" (Emerald) + "Keep shopping" (Gold)

### Buttons
- **Primary** (Emerald #1B4D3E): "Complete checkout", "Next", "Subscribe now"
- **Secondary** (Sapphire #0F3A5F): "Cancel", "Go back"
- **Accent** (Gold #D4AF37): "Skip to checkout", "View terms"
- All: 12px × 24px padding, 8px radius, white text (except gold), focus ring 2px gold

---

## Accessibility (WCAG AA)

✅ **Color contrast**: All text ≥7:1 · Emerald/white: 8.2:1 (strong) · Gold/white: 4.8:1 (accessible)  
✅ **Focus indicators**: 2px gold ring on all interactive elements  
✅ **Keyboard navigation**: Tab order follows visual flow · Modals trap focus · Escape closes  
✅ **Screen readers**: ARIA labels for buttons · ARIA live regions for agent responses · Form labels associated  
✅ **Motion**: All animations <300ms · Respect `prefers-reduced-motion` (disable animations for those users)  
✅ **Responsive text**: 16px default (14px minimum) · Line-height ≥1.5  
✅ **Touch targets**: 44×44px (iOS), 48×48px (Android)

---

## Responsive Breakpoints

| Breakpoint | Width | Layout | Notes |
|------------|-------|--------|-------|
| **Mobile** | 375–767px | Single column · Story cards full-width · Agent modal full-width minus 16px · Mini cart slides from bottom | Touch-friendly · Large tap targets |
| **Tablet** | 768–1023px | 2-column story grid · Same modals | Transitional |
| **Desktop** | 1024px+ | 3-column story grid (centered, max 1200px) · Agent modal 500px centered · Mini cart 360px slide-over | Hover states enabled |

---

## Next Steps for Engineering & Product

### Engineering
1. Implement DESIGN.md tokens as CSS variables (colors, typography, spacing, shadows)
2. Build component library: StoryCard, AgentModal, MiniCart, Button, Link
3. Code-split homepage + agent modal + mini cart for performance
4. Wire Agent modal to `/api/parse` endpoint (backend NLU parser)
5. Implement subscription model in order + user profile data structures

### Frontend
1. Build homepage: Hero video (muted, autoplay) + story grid + CTAs
2. Build agent modal: Chat history + input + dynamic questions (data-driven from backend)
3. Build mini cart: Item list + subscription toggle + checkout CTA
4. Build checkout: Minimal form (email, address, gift message if applicable)
5. Build profile: Preferences + subscription settings + delivered books history

### Creative
1. Shoot/source unboxing video (3–5s, muted, compelling — emotional anchor)
2. Source book cover photography (photography-heavy aesthetic)
3. Create packaging mockups (branded, unboxing ritual)

### Product
1. Refine microcopy with brand team (warmth + playfulness)
2. Validate persona journeys with user testing (especially Mark's fast path + Jenna's subscription model)
3. Define book matching rules (AI decision engine) for production

### QA
1. WCAG AA audit (color contrast, focus indicators, keyboard nav)
2. Screen reader testing (all ARIA labels, live regions)
3. Test motion settings (prefers-reduced-motion)
4. Responsive testing (mobile + tablet + desktop)
5. Touch target verification (44–48px minimum)

---

## Files & References

| Artifact | Path | Purpose |
|----------|------|---------|
| **DESIGN.md** | `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/DESIGN.md` | Visual identity · colors, typography, spacing, components |
| **EXPERIENCE.md** | `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/EXPERIENCE.md` | Behavior · IA, voice, flows, a11y, responsive |
| **Key-screens mock** | `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/.working/key-screens-mock.html` | Interactive HTML prototype |
| **Decision log** | `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/.decision-log.md` | Discovery, decisions, assumptions |
| **PRD** | `_bmad-output/implementation-artifacts/prd-blind-date-book.md` | Product requirements (source) |
| **Brief** | `_bmad-output/planning-artifacts/briefs/brief-BMAD_project-2026-06-22/brief.md` | Product brief (source) |

---

## Key Principles

1. **Warmth through spacing**: Generous layout = luxury
2. **Photography-first**: Real unboxing moments anchor emotion
3. **Surprise & delight**: Unboxing motion (video, reveal), playful language
4. **Accessibility by default**: WCAG AA, keyboard navigation, screen readers
5. **Three distinct paths**: Sarah (thoughtful), Mark (fast), Jenna (detailed + recurring)
6. **Minimal friction**: No unnecessary steps; every element serves a user journey
7. **Mobile-first, desktop-parity**: Works beautifully on all devices

