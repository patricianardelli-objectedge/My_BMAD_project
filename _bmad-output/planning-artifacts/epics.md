---
stepsCompleted:
  - step-01-validate-prerequisites
inputDocuments:
  - _bmad-output/implementation-artifacts/prd-blind-date-book.md
  - _bmad-output/implementation-artifacts/architecture/architecture.md
  - design-artifacts/E-Development/ux-blind-date-book-2026-06-22/DESIGN.md
---

# BMAD_project - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for BMAD_project, decomposing the requirements from the PRD, UX Design, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Provide a homepage-first shopping experience where users select mood-based story-trail cards and proceed directly toward a surprise book purchase without browsing a product catalog.

FR2: Implement a conversational AI preference collector in a modal that guides users through natural-language input for recipient type, age, book gender/category, favorite genres, mood preferences, author whitelist/blacklist, content avoidances, and surprise level.

FR3: Support free-text gift input parsing for customer queries such as age, recipient relationship, desired genres, and avoid lists, mapping that input into structured preference fields.

FR4: Build an AI book-decision engine that selects a best-match book based on captured preferences, age appropriateness, delivered history, and content avoid lists.

FR5: Support one-time purchases and subscription purchase options with monthly, bi-weekly, and three-month cadence selection.

FR6: Provide a mini cart slide-over that summarizes the selected gift kit, quantity, subscription options, and total price before checkout.

FR7: Enable direct checkout from the homepage experience with minimal required fields for shipping, billing, and payment.

FR8: Implement a user profile page that stores preferences, subscription settings, delivered book history, and duplicate prevention metadata.

FR9: Track delivered books in user profiles and use that history to prevent sending duplicate titles in future orders.

FR10: Include a blind date kit product definition and fulfillment requirements for packaging, a love-note insert, and a small extra gift component.

FR11: Provide an operations packing checklist or fulfillment guidance to ensure consistent kit assembly for pilot orders.

FR12: Allow users to edit or remove saved preference fields and avoid lists from their profile.

FR13: Expose a skip flow in the conversational agent so users can bypass the NLU path and proceed with default matching or manual profile entry.

FR14: Log ambiguous parse events for human review and tuning during the pilot.

### NonFunctional Requirements

NFR1: The conversational agent should complete preference capture in 5-7 turns, with a goal of 2-3 minutes total interaction.

NFR2: Homepage video should load in under 3 seconds, the agent modal should appear in under 1 second, and checkout entry should require fewer than 2 clicks from the mini cart.

NFR3: Ensure the interface meets WCAG AA accessibility standards and maintains color contrast ratios of at least 7:1 for primary text and interface elements.

NFR4: Use warm, non-pure black and white tones for visual styling; rely on spacing and color hierarchy instead of heavy shadows.

NFR5: Preserve user privacy by storing only the preference fields required for matching and allowing users to edit or remove those preferences later.

NFR6: Do not send raw payment card data to the backend; payment tokenization must be used for card processing.

NFR7: Support a pilot fulfillment model with manual or small-scale assembly and clearly documented packing instructions.

NFR8: Achieve a checkout completion rate target of 70% or higher and a subscription adoption target of at least 15% of orders by month 3.

NFR9: Maintain duplicate prevention effectiveness for zero duplicate book sends during the pilot.

### Additional Requirements

- The Architecture specifies a production backend API using FastAPI with a documented OpenAPI contract for `/api/agent/parse`, `/api/ai/decide`, and `/api/checkout`.
- The backend must support a rule-based NLU parser for initial preference extraction and keep the parser ruleset under version control.
- Use PostgreSQL with JSONB storage for flexible preference objects, decision reason metadata, and delivered book history.
- Build payment integration using Stripe for credit card tokenization and add support for PIX payment flows for Brazil.
- Protect protected endpoints with JWT bearer authentication while keeping the parse endpoint public for the initial UX flow.
- Implement a background worker and scheduler with Redis and RQ/Celery for subscription renewals, order fulfillment tasks, and webhook processing.
- Store AI decision rationale and candidate scoring metadata in order records for auditability and tuning.
- Ensure the backend can enforce subscription renewal logic and avoid previously delivered books when selecting future shipment items.
- Provide operational logging, metrics, and tracing for parse and decision services.

### UX Design Requirements

UX-DR1: Implement a warm, luxe visual identity with jewel-tone colors, generous spacing, serif headlines, and san-serif body text to support the brand sentiment "You're about to be delighted."

UX-DR2: Design story cards as 240px-high hero photos with a gradient overlay, serif titles, CTA text, hover elevation, and clear single-CTA behavior.

UX-DR3: Build an agent modal with a 500px max width, emerald header, white serif title, warm white body, and gold focus styling on inputs.

UX-DR4: Create a responsive mini cart slide-over with a 360px width on desktop, full-width mobile behavior, subscription radio controls, and a prominent complete checkout CTA.

UX-DR5: Standardize button styles across primary emerald, secondary sapphire, and accent gold variants, with consistent padding, border radius, and accessible hover states.

UX-DR6: Define responsive breakpoints for mobile (375–767px), tablet (768–1023px), and desktop (1024px+), with a 3-column grid on desktop and single-column flow on mobile.

UX-DR7: Ensure motion is smooth and limited (<300ms) with a prefers-reduced-motion fallback and subtle modal fade/slide transitions.

UX-DR8: Specify rounded corners for cards (12px), buttons (8px), and modals (16px) to maintain warmth and consistency.

UX-DR9: Use a design language that relies on spacing and color hierarchy rather than heavy shadows, with subtle elevation only for cards and overlays.

UX-DR10: Provide accessible text link styling with emerald text, gold underline on hover, and visible focus rings.

### FR Coverage Map

{{requirements_coverage_map}}

## Epic List

{{epics_list}}

<!-- Repeat for each epic in epics_list (N = 1, 2, 3...) -->

## Epic {{N}}: {{epic_title_N}}

{{epic_goal_N}}

<!-- Repeat for each story (M = 1, 2, 3...) within epic N -->

### Story {{N}}.{{M}}: {{story_title_N_M}}

As a {{user_type}},
I want {{capability}},
So that {{value_benefit}}.

**Acceptance Criteria:**

<!-- for each AC on this story -->

**Given** {{precondition}}
**When** {{action}}
**Then** {{expected_outcome}}
**And** {{additional_criteria}}

<!-- End story repeat -->
