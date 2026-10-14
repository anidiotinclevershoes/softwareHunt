# Creative Margin Engine — ChatGPT Project Handoff
**Prepared:** 14 October 2026
**Status:** pre-customer proof-of-value experiment; no product-market fit, customer commitment or approval to launch a SaaS.
**Source context:** the independent V2 Software / Software Opportunity Hunt conversations. This is a **new, isolated ChatGPT project**, not a continuation of the V2 Software working space.

## 1. Purpose
Find out if an Irish or UK creative agency will **pay for a reliable, specific historical project profitability diagnosis**, and whether that service could lead to reusable software, recurring customer relationships and ultimately **€5,000+ MRR** with manageable operating profit. The founder works full-time, needs affordable, low-risk AI-assisted delivery and a viable customer acquisition route. Do not assume demand or achievable pricing just because other providers advertise it.

**The first job is not to build a SaaS platform.** It is to demonstrate a complete useful paid *outcome*: a defensible Project Profitability Review assembled from ordinary data an agency is likely to have. After verifying technical output, create a credible sample and commercial landing page, then test real customer acquisition and willingness to pay.

## 2. Why this opportunity, and why caution
Hypothesis: Small-to-medium creative/design/marketing/production agencies undertake quoted and fixed-fee projects but sometimes cannot see how quoted budget, actual time, contractors, direct costs and scope changes affect net project contribution and later quoting. A review of 10–20 completed jobs may expose pricing and estimation patterns without migrating their PSA, CRM or finance system. First entry market is creative agencies; **adjacent future expansion** may be cleaning, maintenance, HVAC or IT-service fixed-contract margin/renewal reviews. Do not try to serve both from day one.

**Current evidence: supplier offers, not customer commitments.**
- Parakeeto advertises a one-off agency profitability assessment from **US$4,999** and management from **US$1,499/month**: https://www.parakeeto.com/pricing/ . Its done-for-you analytics model is a direct competitor, not proof of our price or ability to deliver it.
- Productive https://productive.io/profitability/ and Scoro https://support.scoro.com/hc/en-us/articles/13751242247437-Step-7-Get-detailed-project-profitability-insights already compute project profitability. Spreadsheet/AI, accountants and in-house finance are alternatives.
- Agency prospecting sources: Ireland https://iapi.ie/members/ , UK https://www.dba.org.uk/ . Public names are not qualified buyer leads or permission to cold email.
- Website acquisition and Claude-assisted public-company research may be part of the plan, but **no verified conversions, SEO position, prospect replies or paid customers exist**.

The previous contractor documentation pilot is a fallback, not the current product; a generic O&M-manual generator was previously killed. CPO land-rights was separately OUTREACH-READY and six user-reported emails produced no reply as of the recent conversation; no automatic resend. #825 personal photo-organising remains banked, not a live SaaS candidate. Do not relabel historical statuses.

## 3. Goals and stage gates (not a promise of revenue)
### Stage 1 — prove the delivered outcome, NOW
- Create a **clearly fictional** dataset representing 20 completed projects for a plausible 5–50-person creative agency. Inputs should resemble imperfect actual exports (estimates, invoices, timesheets, vendor expenses), not idealised numbers.
- Implement **small, deterministic, testable** calculations; do not use an LLM as the arithmetic or reconciliation authority. AI can draft explanations of verified figures but not invent missing values.
- Distinguish invoiced vs actually recognised project revenue, planned vs actual hours, salary-based vs fully burdened labour rates, freelancer/vendor costs, adjustments and unallocated overhead. Define assumptions and disallow silent double counting. Report *contribution margin* correctly; do not describe it as audited business profit.
- Include anomalies: missing time, inconsistent or ambiguous personnel rates, scope creep/change orders, unbilled work, incomplete invoices, non-project time, retainer allocation and misleading high-margin/low-margin examples. Do not use false precision. Clearly separate "known", "assumed" and "not calculable".
- Deliver a complete sample **customer-facing Project Profitability Review** and machine-checkable supporting numbers. Ideally display the agency's true repeat quoting errors and pricing-floor sensitivity, with uncertainty warnings.
- Provide a **minimum real-customer data checklist**, confidentiality/storage boundaries and what can/cannot be responsibly concluded.
- Gate: each headline can be traced and recomputed; no invented savings; exceptions do not get buried; source material available without integrations or domain-specialist labour in an ordinary agency.

### Stage 2 — paid proposition / competitive second kill
- Compare the completed sample against Parakeeto, Scoro, Productive and a competent spreadsheet/Claude user. State a concrete *purchase reason* for our bounded historical assessment.
- Prepare **one** credible landing page using a synthetic labelled sample report, data checklist and clear call to action. No web-app accounts, dashboard, payment integration or subscription.
- Price is a **test hypothesis**; any actual customer price requires scoped workload and buyer evidence. No SEO traffic or conversion promises.
- Gate: an agency with an incumbent tool can still give a reason to purchase our standalone review; otherwise STOP or switch candidate.

### Stage 3 — acquisition test (requires founder approval for external contact)
- Identify 10–30 relevant Irish then UK agencies, with sourced company-level fit, current tools if verifiable, live project/service triggers and appropriate role. Claude may support compliant research and personalisation; no fabricated prospects or bulk unsolicited messages. Do not assume email responses based on cold outreach (CPO had six unanswered messages).
- Test multiple real acquisition paths: sample-report website, trusted introductions, suitable industry communities, relevant inbound intent, partnerships and lawful narrowly targeted outreach.
- Gate: actual qualified engagement and ideally **one paid, scoped assessment**; distinguish channel failure from no market demand. Record channel denominator, response and qualification objectively.

### Stage 4 — paid repeatability
- Obtain authorised, securely shared client inputs; deliver accepted report and measure hours, error corrections, support, actual cost and whether customer buys another review/retainer.
- No full SaaS until **real paid outcomes** and a credible reason clients would buy regularly; €5k MRR is gross and must be modelled separately from profit and time.

## 4. Decision rules
- Explicitly challenge assumptions and founder suggestions when the data contradicts them. A hard STOP is acceptable.
- No tiny wedge that cannot plausibly expand. No rescue by endless narrowing.
- Optimise speed to first money and path to recurring revenue **together**.
- Compare total delivery (not just automatable slice), realistic customer data availability, compliance/privacy, service labour, incumbent substitution and acquisition economics.
- Do not invent buyer testimonials, revenues, lead conversion, staff costs or output accuracy.
- Do not send emails, message prospects, spend money, sign contracts, deploy, process third-party confidential files, or merge branches without clear founder approval.

## 5. GitHub separation and source-of-truth
Repository: https://github.com/anidiotinclevershoes/softwareHunt

**Opportunity-hunt authority:** branch `research/fresh-discovery-2026-10-12-partial`, draft PR #3, unmerged. Consult when checking historic research/verdicts; do not edit its frozen random batches or arbitrarily rewrite the graveyard.

**Creative Margin prototype branch:** `prototype/creative-margin-proof-v1` (branched from `main` to keep implementation isolated). All future proof files belong under `prototypes/creative-margin/`, e.g.:
- `prototypes/creative-margin/PROJECT_HANDOFF.md` — this project contract
- `prototypes/creative-margin/PROJECT_INSTRUCTIONS.md` — short ChatGPT Project settings
- `prototypes/creative-margin/proof/` — fictional fixtures, deterministic calculations, tests, sample report
- `prototypes/creative-margin/validation/` — commercial tests, competitor evidence, acquisition decisions

Other experiments can live in sibling `prototypes/<experiment>/` folders, ideally their own branches; **no new GitHub repo needed for each experiment**. Don't alter the other prototype's code or move the whole hunt into this ChatGPT project. Prefer well-separated files, clear tests, one owner per idea, and clean branch/PR controls. Avoid turning the repository into an overarchitected monorepo until more than one build genuinely needs shared tooling.

Reading order for background (not mandatory to restudy before every proof calculation):
1. This handoff and its project instructions.
2. Current comparison: https://github.com/anidiotinclevershoes/softwareHunt/blob/research/fresh-discovery-2026-10-12-partial/research/2026-10-14-final-historical-service-first-comparison.md
3. Historical re-ranking: https://github.com/anidiotinclevershoes/softwareHunt/blob/research/fresh-discovery-2026-10-12-partial/research/2026-10-14-revenue-first-retrospective-shortlist.md
4. Hunt authority/board if material: `AGENTS.md`, `START_HERE.md`, `HUNT_AGENT_PROMPT.md` and newer amendments on the research branch.

**The V3 hunt's 100-attempt discovery process is not the Stage 1 proof-of-value workflow.** Respect economic evidence and historical kills, but avoid returning to endless general opportunity discovery in this isolated project.

## 6. Start in the new ChatGPT project
Ask:
> Read the attached Creative Margin Engine project handoff and project instructions. Verify the dedicated `prototype/creative-margin-proof-v1` branch and source references. Proceed with Stage 1: design and create the synthetic 20-job agency fixtures, transparent deterministic margin calculations, automated checks and a sample Project Profitability Review. Keep the prototype inside `prototypes/creative-margin/`, explain uncertainties and deliver a go/no-go on whether the promised outcome is genuinely useful. Do not build a SaaS UI, contact anyone, or start acquisition spend. Take initiative and don't stop for routine approval.

## 7. Current decisions vs open issues
**Decided:** standalone ChatGPT Project for this opportunity; same GitHub repo with strict prototype isolation; Stage 1 demo-first rather than cold emails; avoid building software before proving the customer-facing result; acquisition must be viable; founder welcomes dissent.
**Open:** whether agency time/cost inputs are good enough; whether full review can be delivered correctly from ordinary data; whether buyer wants external independent review when incumbents exist; achievable pilot price/time; actual legal/secure handling for future customer data; affordable website/Claude-led acquisition; recurring demand.
