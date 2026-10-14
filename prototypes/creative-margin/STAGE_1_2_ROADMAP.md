# Creative Margin Engine — Stage 1 and 2 gated roadmap
Updated 14 October 2026. Planning document; tasks are not claimed complete. Authority: PROJECT_HANDOFF.md and PROJECT_INSTRUCTIONS.md on this branch.

## Operating rules
- Short status reports: Status / Result / Your next action / Next.
- Founder steps: numbered, explicit, verifiable; agent does routine technical work.
- Default coding: existing Codex/ChatGPT access. No extra subscriptions, deployment, merges, customer data or outreach without explicit approval.
- No Vercel, Supabase, Stripe or production accounts required for Stages 1–2. A Stage 2 landing page can be drafted locally; publishing needs approval.

## Stage 1 — prove the outcome
**Goal:** Produce an independently reproducible, evidence-traceable Project Profitability Review from clearly fictional but messy 20-project agency data.

### 1A. Source fixtures and definitions
- Define agency context, 20 completed projects, estimates, timesheets, invoices, expenses, staff cost assumptions, change orders and record identifiers.
- Include missing hours, ambiguous rates, incomplete invoices, non-project time, retainers, unbilled work and conflicting records. Label every datum fictional.
- Define project contribution, revenue recognition rules, labour-cost basis, expenses, exclusions, uncertainties and missing-data policy before calculating.
**Exit:** Fixtures are internally plausible; each headline figure can trace to identified source records; assumptions are explicit.

### 1B. Deterministic engine and tests
- Implement a small reproducible calculation pipeline without LLM arithmetic.
- Compute planned versus actual hours, recognised project revenue, labour cost, direct expense, project contribution, contribution margin and relevant sensitivities.
- Handle missing/ambiguous values with exceptions or ranges, never fabricated precision. Avoid double counting adjustments and freelancer costs.
- Automated unit and fixture-level checks: reconciliations, negative/zero values, incomplete records, changed scope, and totals matching project details.
**Exit:** All automated tests pass; independent spot checks reproduce at least five materially different projects and portfolio totals.

### 1C. Customer-facing report
- Produce a polished sample Project Profitability Review with executive findings, project table, repeat quoting errors, change-order exposure, pricing-floor sensitivity, uncertainty, methodology and evidence links/IDs.
- Distinguish observed fictional results from inference, contribution from audited profit, and hypothetical impact from realised savings.
- Provide a minimum real-customer data checklist and confidentiality/secure-transfer boundaries; do not ingest real customer records.
**Exit:** Every major claim reconciles to the engine; exceptions remain visible; a nontechnical agency owner can identify a concrete action.

### 1D. Hard Stage 1 gate
**GO only if:** accurate reproducible arithmetic; ordinary agency inputs appear realistically obtainable; report gives actionable decisions beyond a cosmetic dashboard; delivery does not require specialist judgement for each transaction.
**STOP/REWORK if:** missing data routinely makes results misleading, conclusions are unverifiable, or delivery requires excessive manual reconstruction. Record uncertainties and decision, not a claim of market validation.

## Stage 2 — competitor second-kill and offer
**Prerequisite:** Stage 1 gate passed.

### 2A. Substitution test
- Compare sample result with Parakeeto, Productive, Scoro and a competent spreadsheet plus Claude/ChatGPT workflow.
- Assess complete outcome, data preparation burden, explanation quality, accuracy, cost, time, recurring value and incumbent switching friction.
- Specify one defensible purchase reason even for an agency already using a PSA tool.
**Exit:** Written competitor matrix and explicit kill decision. Stop if there is no meaningful differentiation.

### 2B. Bounded paid-offer design
- Define target agency profile, 10–20 project scope, input checklist, turnaround hypothesis, deliverables, exclusions and a price **hypothesis**, not a validated price.
- Estimate founder effort, software spend, support/rework and contribution per delivery. Show plausible route to repeat work and eventual €5k+ MRR without treating one-off fees as recurring revenue.
**Exit:** Offer can be explained in one paragraph; cost/time model is explicit and commercially plausible.

### 2C. One landing-page prototype (local only)
- Draft one concise offer page using the clearly labelled synthetic report, input requirements, limitations and a single call to action.
- No logins, database, checkout, CRM, analytics trackers or public launch by default.
**Exit:** Page and sample deliverable can be reviewed locally; all claims defensible. Publishing requires founder approval.

### 2D. Stage 2 gate
**GO to Stage 3 planning only if:** buyer profile, purchase reason, delivery economics and an ethical, realistic route to prospects are credible.
**STOP/PIVOT if:** incumbents or spreadsheet/AI can reproduce the full result at lower friction, or expected delivery effort destroys margin. Stage 3 external acquisition remains separately approval-gated.

## Immediate execution order
1. Inventory current prototype files and tests; do not overwrite existing work.
2. Implement missing Stage 1A fixtures and definitions.
3. Implement Stage 1B calculation engine and tests.
4. Generate Stage 1C report and checklist.
5. Record Stage 1D gate; only then proceed to Stage 2A–2D.

## Founder involvement
- Now: no account setup, hosting or purchase required.
- At Stage 1 gate: review sample and approve/reject whether it is useful.
- Before any external publishing, spending, outreach, customer financial data or merge: obtain explicit approval and provide detailed steps.
