# Product Requirements Document (PRD)

Title: Blind Date Book Experience
Owner: Patricia (product)
Status: Draft
Created: 2026-06-22

## 1. Purpose
Deliver a surprise-first e-commerce experience that sells books via an emotional discovery journey. The initial launch prioritizes a homepage-first flow with story-trail selection, a one-click mini cart checkout, and a curated blind date kit. A lightweight conversational AI agent guides users to provide detailed preferences (book gender, themes, genres, avoid lists, and more), then an AI book-decision engine selects the best match. Support both one-time purchases and subscriptions (monthly, bi-weekly, three-month cycles). Track delivered books in user profiles to prevent sending duplicates on future purchases.

## 2. Background and Context
Derived from the approved product brief and brainstorming session (see planning artifact brief-BMAD_project-2026-06-22). Customers feel overwhelmed by traditional browsing; this product replaces title-centric discovery with mood-driven story trails, tactile unboxing rituals, and controlled personalization (whitelist/blacklist, surprise level).

## 3. Goals and Success Metrics
- Launch goal: MVP that enables a homepage story-trail selection, direct checkout, and physical blind date kit fulfillment.
- Business metrics:
  - Homepage story trail conversion rate >= 3% (target week 1 pilot)
  - Checkout completion rate >= 70%
  - Average order value (AOV) target: baseline + 15% with add-ons
  - Return rate for surprise selections < 5% within 30 days (target)
  - Subscription adoption rate >= 15% of orders by month 3
- User metrics:
  - Profile completion rate >= 25% within 30 days
  - NPS for unboxing experience >= 40 in pilot group
  - Repeat purchase rate >= 10% at 90 days
  - Duplicate prevention effectiveness: zero duplicate book sends in pilot

## 4. Scope
In-scope for MVP:
- Homepage story-trail cards and hero video/animation showing unboxing ritual
- Conversational AI preference collector that guides users through detailed preference capture (book gender, genres, themes, avoid lists, surprise level)
- AI book-decision engine (rule-based) that selects best-match books based on collected preferences
- One-time purchase and subscription model (monthly, bi-weekly, three-month options)
- User profile with delivered book history and duplicate prevention logic
- One-click add-to-cart and mini cart leading to direct checkout
- Blind date kit product definition (packaging, note insert, one small gift)
- Profile page capturing preferences, subscription settings, and delivered book history
- Simple UX: marketing video, agent questions modal, and 1-click checkout
- Pilot fulfillment (manual or small-scale assembly)

Out-of-scope for MVP:
- Full catalog browsing and PDPs
- Advanced ML recommendation engine
- Loyalty/points program
- Large-scale automated fulfillment

## 5. User Personas
- Sarah — Gift shopper, 34, buys thoughtful physical gifts, values ritual and presentation. Wants quick selection and safe content controls.
- Mark — Surprise-seeker, 27, enjoys serendipitous discovery and novelty. Low tolerance for friction; values one-click flows.
- Jenna — Parent buyer, 40, buys for kids; needs age-appropriate content and quick natural-language input (e.g., "gift for my 8-year-old who loves dinossaurs").

## 6. Key User Stories
- As a first-time visitor, I want to pick a mood-based story trail and checkout quickly so I can buy a surprise gift without reading titles.
- As a gift buyer, I want to tell the site who the gift is for in plain language (e.g., "friend, 40, likes horror") and have the system map that to safe, matched books.
- As a returning user, I want to save my preferences and whitelist/blacklist authors to influence future matches.
- As an operations lead, I want clear packing instructions and a checklist so assembled kits are consistent.

## 7. Conversational AI Preference Collector
Requirements:
- The AI agent runs as a modal on the homepage after story-trail selection or at checkout.
- It guides users through detailed preference capture via natural-language conversation: recipient type, age, book gender/category, favorite genres, preferred moods, author whitelist/blacklist, content themes to avoid, surprise level, and tone preference.
- The agent asks clarifying follow-up questions (e.g., "Do you prefer romance with mystery or pure contemporary?") to refine book selection confidence.
- Required speed: 5-7 conversational turns (goal: 2-3 minutes total interaction).
- Fail-safe: user can skip to default matching or manual profile entry.
- Privacy: store only fields required for matching; allow users to edit or remove preferences later.
- Output: structured preference object fed to the AI book-decision engine.

Example user inputs the agent must handle:
- "I am looking for a gift for my friend who is 40 years old and likes horror books."  
  -> Parse: recipient_type=gift, age=35-44, genres=[horror]
- "I want a gift for my son who is 8 and loves dinosaurs."  
  -> Parse: recipient_type=gift, age=under-12, genres=[children/dinosaurs]

Conversation flow (example):
1. Agent: "Who is this for? A friend, yourself, or a child?"  
2. User: "A friend, 40, likes horror."  
3. Agent: "Great — do you want any authors or themes avoided?"  
4. User: "No politics or explicit content."  
5. Agent: "Light hint or full surprise?"  
6. User: "Full surprise."  
7. Agent: Applies parsing and saves structured preferences; shows a one-line summary for confirmation.

Implementation notes:
- Start with rule-based NLU patterns and entity extraction (age, relationship, genres, themes to avoid).  
- Consider integrating a small NLU service (open-source library or lightweight cloud API) if available; initial implementation can be local regex-and-ontology-based.
- Log ambiguous parses and surface as human-review tags during pilot.

## 8. Features and Requirements

8.1 Frontend
- Homepage hero with auto-playing video/animation showing the unboxing ritual and gift reveal (emotional anchor).
- Story-trail cards with single-CTA leading to conversational agent modal.
- Conversational agent modal that guides detailed preference collection via natural-language prompts.
- AI book-decision summary card showing: genre match, mood fit, author check, and reason for selection (transparency).
- One-click add-to-cart and mini cart slide-over with subscription option selector (one-time, monthly, bi-weekly, three-month).
- Direct checkout (minimal form: email, address, gift message if applicable).
- Profile page with:
  - Editable preferences and subscription settings
  - Delivered book history (title, date, mood matched)
  - Duplicate prevention: "We won't send this book again"
  - Author whitelist/blacklist and content avoid lists

8.2 Backend
- AI book-decision engine (rule-based) that applies:
  - Preference signals from conversational collector (genres, moods, author whitelist/blacklist, avoid themes)
  - Age-appropriateness checks
  - Delivered book history (excludes previously sent books)
  - Subscription cycle logic (monthly, bi-weekly, three-month)
- Order model includes fields for:
  - subscription_type (one-time, monthly, bi-weekly, three-month)
  - subscription_id (if recurring)
  - surprise_level, reveal_style
  - recipient_details (if gift)
  - selected_add_ons
  - ai_decision_reason (metadata for transparency and tuning)
- Subscription management:
  - Renewal logic that fetches a new book from the pool while avoiding past deliveries
  - Pause/resume/cancel endpoints
  - Bill management (if applicable)
- User profile tracking: delivered_books array with {title, date, mood_match, genre_selected} for duplicate prevention
- Admin packing checklist exposed in the order details UI for fulfillment

8.3 Fulfillment
- Kit BOM: wrapped book, love-note insert, one small gift item, branded packaging.
- Packing checklist and QA step before shipping.
- Shipping notifications that maintain surprise (no title in shipping metadata visible to recipients unless sender allows).

8.4 Data and Privacy
- Keep stored preference fields minimal and editable.
- Provide clear OOB (opt-out) for marketing communications.
- Do not surface titles to recipients unless sender chooses to reveal.

## 9. Acceptance Criteria
- Users can complete a one-time purchase from homepage to checkout in under 60 seconds (including agent interaction).
- Conversational AI agent collects sufficient preference signals (>5 fields) from >85% of users in pilot.
- AI book-decision engine selects a book that matches user preferences in >85% of pilot orders (manual audit).
- Duplicate prevention logic: zero books sent twice to same user across multiple orders in pilot.
- Subscription orders renew successfully with correct book selection and no duplicates from past shipments.
- Profile page displays delivered book history accurately for 100% of orders.
- Packing checklist is used for 100% of pilot orders and audit shows consistent kit assembly.
- UX: homepage video loads in <3 seconds; agent modal loads in <1 second; checkout page <2 clicks to payment.

## 10. Milestones & Roadmap
MVP (Weeks 1-9):
- Week 1: Finalize kit definition & creative assets; shoot/produce homepage unboxing video.
- Week 2: Implement homepage hero video, story cards, and basic UX layout.
- Week 3: Build conversational AI modal (rule-based NLU) and test on sample queries.
- Week 4: Implement AI book-decision engine; integrate with profile and delivered-book history.
- Week 5: Build one-time purchase and subscription model (monthly, bi-weekly, three-month); implement subscription renewal logic.
- Week 6: Add duplicate prevention logic and user profile delivery history display.
- Week 7: Implement mini cart, one-click checkout, and order model.
- Week 8: Fulfillment pilot: assemble 50 kits, test packing QA, shipping, and book history tracking.
- Week 9: Soft launch to limited audience; collect metrics, feedback, and refine AI decision rules.

Scale (Weeks 10-16):
- Add more story trails and refine AI matching based on pilot feedback.
- Introduce lightweight personalization templates for the love-note insert.
- Evaluate ML-based recommendations for improved match accuracy.
- Expand subscription offering with gift subscriptions (e.g., 6-month gift pass).

## 11. Risks and Mitigations
- Risk: Mis-parsed gift inputs produce poor matches -> Mitigation: confirmation step and manual override/tag for human review during pilot.
- Risk: Return rate due to inappropriate content -> Mitigation: strong avoid-list enforcement and age-appropriate checks; conservative selection rules during pilot.
- Risk: Fulfillment inconsistency -> Mitigation: packing checklist, QA step, and small-batch manual assembly for pilot.

## 12. Dependencies
- Creative assets (hero video, packaging design)
- Suppliers for stationery and small gifts
- Basic order management and fulfillment processes (or integration partner)
- NLU/parsing library or service for conversational agent

## 13. Open Questions
- Which NLU provider or library is acceptable for the pilot (in-house regex vs. cloud NLP)?
- Who owns the matching rules (product vs. editorial vs. ops)?
- Should shipping labels ever include title metadata if the buyer requests gift reveal?

## 14. Handoff and Next Steps
- Produce packing checklists and assembly instructions for pilot fulfillment (owner: ops).
- Implement a lightweight NLU parser and test on sample gift queries (owner: engineering).
- UI: Build homepage story cards and mini cart (owner: frontend).

## Appendix: References
- Planning brief: _bmad-output/planning-artifacts/briefs/brief-BMAD_project-2026-06-22/brief.md
- Decision log: _bmad-output/planning-artifacts/briefs/brief-BMAD_project-2026-06-22/.decision-log.md
