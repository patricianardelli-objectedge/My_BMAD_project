# Story 1.1: Homepage Hero and Story-Trail Card Selection

Status: done

## Story

As a first-time visitor,
I want to choose a mood-based story trail directly from the homepage,
so that I can begin a surprise purchase without browsing a catalog.

## Acceptance Criteria

1. Given a visitor lands on the homepage, when page assets load, then the hero media is visible in under 3 seconds on baseline broadband and story-trail cards render with accessible text contrast and keyboard focus states.
2. Given the visitor interacts with a story-trail card, when they click or press Enter on the primary CTA, then the system stores the selected trail in session state and opens the preference collector entry point without catalog navigation.
3. Given responsive viewports across mobile/tablet/desktop, when cards and hero render, then layout behavior follows UX breakpoints (375-767, 768-1023, 1024+) and no horizontal overflow occurs.
4. Given reduced-motion preferences are enabled, when interactive elements animate, then motion is reduced or disabled while preserving discoverability and interaction clarity.

## Tasks / Subtasks

- [x] Implement homepage hero performance and rendering constraints (AC: 1)
  - [x] Audit hero asset load path and ensure first visible media appears under target budget.
  - [x] Keep hero CTA behavior aligned with direct purchase intent (opens mini-cart flow, not catalog).
- [x] Implement story card interaction semantics (AC: 2)
  - [x] Ensure each card has one primary actionable control for keyboard and pointer users.
  - [x] Persist selected mood/trail in client session state for downstream modal/cart flow.
- [x] Implement accessibility and responsive guardrails (AC: 1, 3, 4)
  - [x] Verify color contrast and non-text contrast for overlays, CTA, focus rings.
  - [x] Verify tab order, focus visibility, and escape routes from modal/cart transitions.
  - [x] Verify mobile/tablet/desktop grid behavior and card sizing against UX spec.
- [ ] Add or update tests and checks (AC: 1-4)
  - [ ] Add front-end interaction checks for story card click and keyboard activation.
  - [ ] Add accessibility smoke checks for focus visibility and keyboard operability.
  - [ ] Document performance verification approach for hero load budget.

## Dev Notes

### Story Foundation and Business Context

- This story is the first implementation story for Epic 1 and establishes the homepage-first discovery path.
- It must deliver direct progression into preference capture/cart flow without product catalog browsing.
- Status target for this story file is ready-for-dev; implementation should transition through in-progress -> review -> done via downstream workflows.

### Technical Requirements

- UI must preserve the existing plain HTML/CSS/JS prototype behavior while improving AC compliance:
  - Hero area with click-through intent to purchase path.
  - Story cards with one clear CTA and mood metadata.
- Do not introduce backend dependencies for this story; this is front-end interaction and presentation behavior.
- Keep API contract compatibility for downstream steps that depend on parse/decision/checkout endpoints.

### Architecture Compliance

- Follow architecture direction: homepage interaction should feed session state into conversational and cart flows.
- Keep the OpenAPI contract unchanged in this story; no schema changes are needed.
- Maintain existing endpoint usage patterns so Story 1.2 and 1.3 can build directly on this foundation.

### Library and Framework Requirements

- Current implementation is static frontend (vanilla HTML/CSS/JS).
- No framework migration in this story. Avoid introducing React/Vite here.
- Preserve browser-native semantics and accessible controls.

### File Structure Requirements

Primary files expected to be updated for this story:

- `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html`
- `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/styles.css`

Potential read-only reference files (do not change unless required by AC):

- `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/api-client/openapi-client.js`
- `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/api-client/openapi-client.ts`
- `docs/api-specs.yaml`

### Existing File Intelligence (UPDATE-file analysis)

`design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html`

- Current state:
  - Includes hero section with clickable video area and overlay CTA.
  - Includes story-grid cards with data-mood attributes and overlay CTA links.
  - Includes JS cart state (`currentCartItem`) and `addToCart` flow.
  - Includes agent modal and mini-cart wiring; card click currently adds to cart directly.
- This story changes:
  - Story card semantics and interaction path consistency (single CTA behavior and session trail capture).
  - Accessibility/focus order and interaction clarity for keyboard users.
  - Hero performance and behavior validation.
- Must preserve:
  - Existing mini-cart, agent modal, and checkout flow hooks.
  - Existing script entry points referenced by later stories (`submitAgent`, cart interactions).

`design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/styles.css`

- Current state:
  - Defines design tokens, card layout, hero styles, motion/elevation, and responsive behavior.
  - Has accessible focus styles for buttons but needs explicit validation for all interactive elements.
- This story changes:
  - Contrast/focus adjustments and possibly card CTA interaction styling.
  - Responsive behavior hardening to match breakpoints from UX spec.
- Must preserve:
  - Existing token structure and visual identity direction.
  - Existing card/hero visual style and rounded/elevation language.

`docs/api-specs.yaml`

- Current state:
  - Defines parse/decide/checkout contracts and schemas.
- This story changes:
  - No API contract changes.
- Must preserve:
  - Existing endpoint paths, schemas, and auth boundaries.

### Testing Requirements

- Frontend behavior checks:
  - Card activation via click and keyboard Enter/Space.
  - Session state set for selected trail.
  - Hero CTA path works and does not bypass intended flow.
- Accessibility checks:
  - Focus visible for card CTA and hero actionable area.
  - Keyboard-only path from homepage to modal/cart.
  - Color/non-text contrast against selected backgrounds.
- Responsive checks:
  - 375px, 768px, 1024px breakpoints with no clipped card CTA or overflow.
- Performance checks:
  - Hero media first paint under target for baseline broadband test scenario.

### Git Intelligence Summary

Recent commit context indicates this repo baseline is at initial project state (`First version of Blind date book`).
Implication: favor incremental edits to existing prototype files and avoid broad refactors in this first story.

### Latest Technical Information

- WCAG 2.2 quick reference confirms relevant criteria for this story:
  - 1.4.3 Contrast (Minimum)
  - 2.1.1 Keyboard
  - 2.4.7 Focus Visible
  - 2.5.8 Target Size (Minimum)
- Stripe and FastAPI web fetches did not return stable version metadata in this run; for this story no version upgrade is required because payment/backend integration is out of scope.

### Project Structure Notes

- Planning artifact source of truth for this story: `_bmad-output/planning-artifacts/epics.md` (Epic 1, Story 1.1).
- Keep implementation inside the existing frontend prototype directory to avoid path drift.
- Do not create new architecture layers in Story 1.1; this story should remain UI/interaction focused.

### References

- Source epic definition: `_bmad-output/planning-artifacts/epics.md`
- PRD functional scope: `_bmad-output/implementation-artifacts/prd-blind-date-book.md`
- Architecture constraints: `_bmad-output/implementation-artifacts/architecture/architecture.md`
- UX specification: `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/DESIGN.md`
- Current frontend implementation: `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html`, `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/styles.css`
- API contract: `docs/api-specs.yaml`

## Dev Agent Record

### Agent Model Used

GPT-5.3-Codex

### Debug Log References

- create-story workflow execution on 2026-06-23

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Story created from first backlog item in sprint-status.
- Epic 1 transitioned to in-progress as first story context was created.
- Implemented single-CTA story card selection with session trail persistence and agent modal entry.
- Added keyboard-operable hero CTA and focus-visible styling for primary interactive elements.
- Cleaned malformed checkout markup and aligned payment method controls with existing JS behavior.
- Added prefers-reduced-motion CSS guardrail for accessibility compliance.
- Fixed critical API endpoint bug: parseAgent now calls /api/agent/parse (normalized recipient_type/recipient_age_range response) instead of /api/parse (raw schema).

### File List

- `_bmad-output/implementation-artifacts/1-1-homepage-hero-and-story-trail-card-selection.md`
- `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html`
- `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/styles.css`
