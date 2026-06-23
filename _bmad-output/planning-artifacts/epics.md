---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
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

FR1: Epic 1 - Homepage-first discovery with story-trail selection and direct path to purchase.

FR2: Epic 1 - Conversational preference collector modal for detailed preference capture.

FR3: Epic 1 - Free-text gift input parsing into structured preference fields.

FR4: Epic 2 - Rule-based AI decision engine with scored candidate selection.

FR5: Epic 2 - One-time and subscription cadence options in cart and order flow.

FR6: Epic 2 - Mini cart slide-over with gift kit summary and total.

FR7: Epic 3 - Direct checkout flow with minimal required shipping/billing/payment fields.

FR8: Epic 4 - User profile storing preferences, subscription settings, and delivery history.

FR9: Epic 4 - Duplicate prevention based on delivered title history.

FR10: Epic 5 - Blind date kit product and packaging definition in order workflow.

FR11: Epic 5 - Operations packing checklist and fulfillment guidance for pilot orders.

FR12: Epic 4 - Editable and removable preference and avoid-list profile controls.

FR13: Epic 1 - Agent skip flow to default matching or manual profile entry.

FR14: Epic 1 - Ambiguous parse event logging for pilot tuning.

## Epic List

### Epic 1: Discovery and Preference Capture
Shoppers discover the experience from the homepage, choose a story trail, and provide clear preferences via conversational input or skip path.
**FRs covered:** FR1, FR2, FR3, FR13, FR14

### Epic 2: AI Match and Cart Conversion
Shoppers receive a transparent surprise recommendation, add a gift kit quickly, and configure one-time or subscription purchase options.
**FRs covered:** FR4, FR5, FR6

### Epic 3: Fast and Secure Checkout
Shoppers complete payment from the homepage flow with minimal friction using secure tokenized payment methods.
**FRs covered:** FR7

### Epic 4: Profiles and Duplicate Prevention
Returning users manage preferences and subscription controls while the system prevents duplicate book deliveries.
**FRs covered:** FR8, FR9, FR12

### Epic 5: Fulfillment and Pilot Operations
Operations teams assemble and ship consistent blind date kits with documented fulfillment guidance and order metadata.
**FRs covered:** FR10, FR11

<!-- Repeat for each epic in epics_list (N = 1, 2, 3...) -->

## Epic 1: Discovery and Preference Capture

Deliver the homepage-first discovery and conversational preference experience so a first-time shopper can begin and complete gift intent capture quickly.

### Story 1.1: Homepage Hero and Story-Trail Card Selection

As a first-time visitor,
I want to choose a mood-based story trail directly from the homepage,
So that I can begin a surprise purchase without browsing a catalog.

**Acceptance Criteria:**

**Given** a visitor lands on the homepage
**When** page assets load
**Then** the hero media is visible in under 3 seconds on baseline broadband
**And** story-trail cards render with accessible text contrast and keyboard focus states.

**Given** the visitor interacts with a story-trail card
**When** they click or press Enter on the primary CTA
**Then** the system stores the selected trail in session state
**And** opens the preference collector entry point without requiring catalog navigation.

**References:** FR1, NFR2, NFR3, UX-DR2, UX-DR6, UX-DR9
**Source Hints:** PRD sections 4, 8.1, 9; UX DESIGN sections Story Card, Layout & Spacing.

### Story 1.2: Conversational Agent Modal and Guided Preference Flow

As a shopper selecting a gift,
I want a conversational modal that gathers recipient and taste preferences in plain language,
So that the recommendation engine can personalize the surprise.

**Acceptance Criteria:**

**Given** a shopper starts the preference flow
**When** the modal opens
**Then** the modal appears in under 1 second with accessible focus management
**And** supports keyboard-only navigation and reduced-motion behavior.

**Given** the shopper answers prompts
**When** the flow is completed in 5-7 turns
**Then** the system captures recipient type, age band, genres, mood, surprise level, and avoid preferences
**And** displays a confirmation summary before continuing.

**References:** FR2, NFR1, NFR3, UX-DR3, UX-DR7, UX-DR10
**Source Hints:** PRD sections 7, 8.1, 9; Architecture sections 1-3.

### Story 1.3: Parse Service Integration with Ambiguity Logging

As a product team,
I want free-text user input parsed into structured preferences with ambiguity logging,
So that the pilot can improve matching quality over time.

**Acceptance Criteria:**

**Given** the frontend submits free-text gift intent
**When** `/api/agent/parse` receives the request
**Then** the API returns a structured preference object aligned to the OpenAPI contract
**And** the parser output is versioned and test-covered.

**Given** user input is ambiguous or partially parsed
**When** parser confidence or rule coverage is insufficient
**Then** the event is logged with reason codes for human review
**And** the UX receives a safe clarification prompt instead of silent failure.

**References:** FR3, FR14, Additional Requirements 1-2, NFR5
**Source Hints:** PRD sections 7, 11; Architecture sections 2-3, 9; docs/api-specs.yaml.

### Story 1.4: Agent Skip Flow and Default Matching Entry

As a shopper in a hurry,
I want to skip the conversational flow and continue with defaults or manual entry,
So that I can still complete a purchase with minimal friction.

**Acceptance Criteria:**

**Given** the modal is open
**When** the shopper selects Skip
**Then** the system offers default matching and manual profile entry paths
**And** records that skip mode was chosen.

**Given** skip mode is used
**When** the shopper continues to recommendation/cart
**Then** the flow proceeds without blocked fields
**And** unresolved preference values are marked as optional or unknown.

**References:** FR13, NFR2, NFR5
**Source Hints:** PRD sections 7, 8.1.

## Epic 2: AI Match and Cart Conversion

Deliver recommendation transparency and mini-cart conversion so users can trust and buy the proposed surprise kit quickly.

### Story 2.1: Rule-Based Decision Engine with Candidate Scoring

As a shopper,
I want the system to choose a best-match book using my preferences and safety constraints,
So that the surprise feels relevant and appropriate.

**Acceptance Criteria:**

**Given** structured preferences and optional exclusion history
**When** `/api/ai/decide` is invoked
**Then** the engine ranks candidates and returns a selected book with rationale metadata
**And** respects age appropriateness and avoid lists.

**Given** the same input is replayed for audit
**When** decision logs are reviewed
**Then** reason fields show which rules influenced ranking
**And** metadata can be persisted on order records.

**References:** FR4, Additional Requirements 1, 7, 9, NFR9
**Source Hints:** PRD sections 8.2, 9; Architecture sections 2-3.

### Story 2.2: Recommendation Summary Card and One-Click Add-to-Cart

As a shopper,
I want a transparent recommendation summary and a one-click add action,
So that I can trust the pick and move to checkout quickly.

**Acceptance Criteria:**

**Given** a decision result exists
**When** the recommendation card renders
**Then** it displays genre fit, mood fit, and safety checks in human-readable language
**And** provides a single primary add-to-cart CTA.

**Given** the shopper clicks add-to-cart
**When** cart state updates
**Then** the blind date kit and selected book data appear in mini cart
**And** quantity and price totals are recalculated immediately.

**References:** FR4, FR6, NFR2, UX-DR5
**Source Hints:** PRD sections 8.1, 9; UX DESIGN button and component specs.

### Story 2.3: Mini Cart Subscription Options and Pricing

As a shopper,
I want to choose one-time, monthly, bi-weekly, or three-month delivery,
So that the purchase matches how often I want to gift or receive books.

**Acceptance Criteria:**

**Given** mini cart is open
**When** subscription options are displayed
**Then** one-time and three subscription cadence options are selectable
**And** selected cadence updates order summary labels and totals.

**Given** a subscription cadence is selected
**When** user proceeds to checkout
**Then** cadence is persisted into checkout payload
**And** cart state remains consistent on refresh/back navigation.

**References:** FR5, FR6, UX-DR4
**Source Hints:** PRD sections 8.1, 8.2; Architecture sections 3, 8.

## Epic 3: Fast and Secure Checkout

Deliver an end-to-end checkout path that is low-friction for users and secure for payment operations.

### Story 3.1: Checkout API with Tokenized Card and PIX Support

As a shopper,
I want secure payment options that do not expose my raw card details,
So that I can checkout safely with my preferred payment method.

**Acceptance Criteria:**

**Given** checkout payload is submitted
**When** `/api/checkout` processes payment details
**Then** the backend accepts tokenized card methods and PIX payloads only
**And** rejects raw PAN/card-number fields.

**Given** payment provider responses are returned
**When** order processing completes
**Then** the API returns order id and payment status
**And** emits webhook-compatible metadata for async reconciliation.

**References:** FR7, Additional Requirements 4, NFR6
**Source Hints:** PRD sections 8.2, 9; Architecture sections 1-4.

### Story 3.2: Direct Checkout UX from Mini Cart

As a shopper,
I want to enter shipping and billing details with minimal fields,
So that I can complete checkout in under two clicks from mini cart.

**Acceptance Criteria:**

**Given** a ready mini cart state
**When** user clicks Complete Checkout
**Then** checkout opens directly from mini cart with required fields only
**And** interaction path from cart to payment is no more than two clicks.

**Given** required fields are valid
**When** user submits checkout
**Then** an order confirmation state is shown with next steps
**And** checkout completion instrumentation is logged.

**References:** FR7, NFR2, NFR8, UX-DR4
**Source Hints:** PRD sections 8.1, 9.

### Story 3.3: Background Processing for Renewals and Webhooks

As an operations team,
I want background workers to process renewals and payment/fulfillment webhooks,
So that recurring orders and event handling remain reliable.

**Acceptance Criteria:**

**Given** recurring subscriptions and provider callbacks exist
**When** worker queues execute scheduled tasks
**Then** renewal jobs and webhook events are processed idempotently
**And** failures are retried with structured error logging.

**Given** operational monitoring is enabled
**When** queue processing health is reviewed
**Then** key metrics and traceable logs are available for parse, decide, and checkout paths
**And** alert thresholds can be configured.

**References:** Additional Requirements 6, 9, NFR7
**Source Hints:** Architecture sections 1, 5, 6.

## Epic 4: Profiles and Duplicate Prevention

Deliver account-level memory and controls so users can manage preferences and never receive duplicate titles.

### Story 4.1: User Profile Preferences and Avoid-List Management

As a returning user,
I want to manage saved preferences and author/content avoid lists,
So that future recommendations align with my changing tastes and boundaries.

**Acceptance Criteria:**

**Given** an authenticated user opens profile
**When** viewing preference settings
**Then** saved preference fields, whitelist/blacklist, and content avoid lists are displayed
**And** each field supports edit and delete actions.

**Given** profile changes are submitted
**When** backend validation succeeds
**Then** updates are persisted and reflected in subsequent recommendation requests
**And** audit timestamps are updated.

**References:** FR8, FR12, NFR5
**Source Hints:** PRD sections 8.1, 8.2.

### Story 4.2: Delivered History Tracking and Duplicate Exclusion

As a returning subscriber,
I want prior deliveries tracked and excluded from future selections,
So that I do not receive the same title twice.

**Acceptance Criteria:**

**Given** orders are fulfilled
**When** completion events are recorded
**Then** delivered history is appended with title, date, and match metadata
**And** profile history displays the same records.

**Given** a new recommendation is requested
**When** decision engine ranks candidates
**Then** titles in delivered history are excluded from eligible pool
**And** fallback behavior is defined when inventory is constrained.

**References:** FR9, NFR9
**Source Hints:** PRD sections 8.2, 9; Architecture sections 2-3.

### Story 4.3: Subscription Lifecycle Controls

As a subscriber,
I want to pause, resume, or cancel my subscription,
So that I can control recurring deliveries and charges.

**Acceptance Criteria:**

**Given** an active subscription exists
**When** user chooses pause, resume, or cancel
**Then** status changes are persisted with effective dates
**And** next renewal behavior respects the new state.

**Given** subscription status changes
**When** profile or order history is viewed
**Then** current plan, cadence, and next charge date are visible
**And** invalid transitions are blocked with clear errors.

**References:** FR5, FR8
**Source Hints:** PRD sections 8.2, 9; Architecture sections 2, 8.

## Epic 5: Fulfillment and Pilot Operations

Deliver pilot-ready fulfillment standards and packaging guidance so each blind date kit is assembled consistently.

### Story 5.1: Blind Date Kit BOM and Packaging Metadata

As an operations lead,
I want each order to carry explicit blind date kit component requirements,
So that assembly teams can fulfill every kit consistently.

**Acceptance Criteria:**

**Given** an order is created
**When** fulfillment metadata is generated
**Then** required kit components include wrapped book, love-note insert, and small gift item
**And** packaging/reveal flags are included in order payload.

**Given** order details are viewed by operations
**When** order metadata is rendered
**Then** kit component checklist fields are visible
**And** missing component data blocks fulfillment start.

**References:** FR10, NFR7
**Source Hints:** PRD sections 8.3, 10.

### Story 5.2: Packing Checklist Workflow and QA Gate

As a fulfillment operator,
I want a per-order packing checklist with QA confirmation,
So that pilot shipments are assembled correctly every time.

**Acceptance Criteria:**

**Given** an order enters packing state
**When** operator opens fulfillment checklist
**Then** each required packing step is presented with completion controls
**And** order cannot be marked packed until all mandatory steps are complete.

**Given** QA review is required
**When** checklist is complete
**Then** a QA confirmation step is recorded with timestamp and user id
**And** shipping handoff remains blocked until QA passes.

**References:** FR11, NFR7
**Source Hints:** PRD sections 8.3, 9, 14.

### Story 5.3: Surprise-Safe Shipping Notification Rules

As a gift buyer,
I want shipment updates that preserve surprise unless I explicitly reveal the title,
So that recipients keep the blind date experience intact.

**Acceptance Criteria:**

**Given** a shipment notification is generated
**When** recipient-facing content is composed
**Then** title metadata is omitted by default
**And** reveal mode is only used when sender opted in.

**Given** fulfillment notifications are sent
**When** audit logs are reviewed
**Then** reveal-mode decisions are traceable per order
**And** notification templates maintain consistent surprise-safe wording.

**References:** FR10, NFR5
**Source Hints:** PRD sections 8.3, 13.
