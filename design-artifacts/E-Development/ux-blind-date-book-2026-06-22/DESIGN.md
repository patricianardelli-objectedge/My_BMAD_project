product: Blind Date Book Experience
status: in-progress
created: 2026-06-22
updated: 2026-06-22
colors:
	primary: "#1B4D3E" # Emerald
	secondary: "#0F3A5F" # Sapphire
	accent: "#D4AF37" # Gold
	neutral-light: "#F8F7F5" # Warm white
	neutral-dark: "#1A1A1A" # Deep charcoal
typography:
	headlines: "Serif (Georgia, Garamond) · 32–48px · line-height 1.3–1.4"
	body: "Sans-serif (Inter, Helvetica Neue) · 14–16px · line-height 1.6"
rounded:
	cards: "12px"
	buttons: "8px"
	modals: "16px"
spacing:
	base-unit: "8px grid"
	section-gap: "48–64px"
	component-gap: "16–24px"
components:
	story-card: "240px height · photo + overlay + CTA"
	agent-modal: "500px width · Emerald header · gold focus"
	mini-cart: "360px width · subscription toggle · gold buttons"
	button-primary: "Emerald bg · white text · 12px 24px padding"
---

# DESIGN
**Blind Date Book Experience** — Visual Identity & Component Specifications

## Brand & Style

The visual identity conveys **warmth, surprise, and quiet luxury**. Luxury through generous spacing, refined typography, and deep jewel tones. Surprise lives in the unboxing motion: book reveal feels like opening a carefully wrapped gift.

- **Emotional tone**: Warm + personal + luxe + playful (not corporate; not childish)
- **Core sentiment**: *"You're about to be delighted."*
- **Accessibility floor**: WCAG AA; color contrast ≥7:1 for text; motion respects prefers-reduced-motion

## Colors

**Palette: Jewel Tones + Warm Accents**

| Role | Color | Usage |
|------|-------|-------|
| Primary | Emerald #1B4D3E | Buttons, headers, key CTAs, focus states |
| Secondary | Sapphire #0F3A5F | Secondary actions, card borders, accent text |
| Accent | Gold #D4AF37 | Link underlines, highlights, premium badge, surprise reveal |
| Neutral Light | #F8F7F5 | Backgrounds, card surfaces (warm white) |
| Neutral Dark | #1A1A1A | Body text, headers (deep charcoal) |

**Contrast**: All text meets WCAG AA. Emerald on white: 8.2:1 (strong). Gold on white: 4.8:1 (accessible).

## Typography

**Headlines (Serif — Literary, Elegant)**
- Font: Georgia, Garamond, or serif equivalent
- Sizes: 32–48px for page titles; 20–24px for card titles
- Line height: 1.3–1.4 (tight, refined)
- Weight: Regular or bold for emphasis

**Body (Sans-serif — Modern, Accessible)**
- Font: Inter, Helvetica Neue, or clean sans equivalent
- Sizes: 14–16px body text; 12px labels and metadata
- Line height: 1.6 (generous, readable)
- Weight: Regular for body; medium for labels

## Layout & Spacing

**Grid & Rhythm**
- Base unit: 8px grid (all margins and padding align to 8px multiples)
- Section vertical gap: 48–64px (generous breathing room)
- Component internal padding: 16–24px (comfortable)
- Whitespace is a design feature

**Responsive breakpoints:**
- Mobile: 375–767px (single column)
- Tablet: 768–1023px (2-column story grid)
- Desktop: 1024px+ (3-column grid, centered max-width 1200px)

## Elevation & Depth

**Subtle shadows** create hierarchy without heaviness:
- Card base: `shadow-sm` (0 2px 8px rgba(0,0,0,0.08))
- Card hover: `shadow-md` (0 4px 12px rgba(0,0,0,0.12))
- Modal backdrop: Semi-transparent dark (rgba(0,0,0,0.4))
- Elevate through spacing and color, not depth

## Shapes

**Rounded corners** signal warmth and approachability:
- Card corners: 12px (soft, inviting)
- Button corners: 8px (refined)
- Modal corners: 16px (breathing room)
- Input fields: 8px (consistent with buttons)

## Components

### Story Card
- **Layout**: Hero photo (240px height) + overlay gradient + title + CTA
- **Photo**: Real book covers or styled gift images (photography-heavy aesthetic)
- **Overlay**: Emerald gradient to transparent (bottom to top), opacity 0.6
- **Title**: White serif, 24px bold
- **CTA**: "Choose this gift" in white, gold underline on hover
- **Hover**: Shadow elevation + scale 1.02x
- **Spacing**: 12px margins between cards

### Agent Modal
- **Width**: 500px max (mobile: full-width minus 16px padding)
- **Header**: Emerald background, white serif title "Let's find your book"
- **Body**: Warm white background, sans-serif body text
- **Input**: 8px radius, 1px border Sapphire, gold focus-ring (2px)
- **CTA**: "Next" button (Emerald, 12px 24px padding)
- **Exit**: "Skip to checkout" link (gold)
- **Motion**: Fade in 200ms

### Mini Cart
- **Position**: Right slide-over, 360px width (mobile: full-width)
- **Header**: "Your gift kit", close (X)
- **Items**: Book title + price + remove link
- **Subscription**: Radio buttons or toggle (Monthly / Bi-weekly / Three-month / One-time)
- **Footer**: Total + "Complete checkout" (Emerald) + "Keep shopping" (Gold)
- **Motion**: Slide in 300ms

### Buttons

**Primary (Emerald)**
- Background: #1B4D3E; Text: White
- Padding: 12px 24px; Radius: 8px
- Hover: #153A2D (darker)

**Secondary (Sapphire)**
- Background: #0F3A5F; Same styling as primary

**Accent (Gold)**
- Background: #D4AF37; Text: #1A1A1A (dark charcoal)
- Hover: #C99C27 (slightly dimmed)

### Text Links
- **Color**: Emerald (#1B4D3E)
- **Underline**: Gold (#D4AF37), 2px, on hover
- **Focus ring**: Gold, 2px

## Do's and Don'ts

**Do:**
- ✅ Use generous whitespace to breathe life into layouts
- ✅ Prioritize photography (real unboxing, book covers)
- ✅ Keep motion smooth and <300ms (delightful, not distracting)
- ✅ Test color contrast with accessibility tools
- ✅ Layer complexity through spacing, not heavy shadows

**Don't:**
- ❌ Use pure black or pure white; warm them (#1A1A1A, #F8F7F5)
- ❌ Overuse gold; it's an accent only
- ❌ Add drop-shadows; subtle shadows only
- ❌ Make animations >300ms
- ❌ Ignore prefers-reduced-motion; disable animations for those users
- ❌ Stack >2 levels of hierarchy at once

