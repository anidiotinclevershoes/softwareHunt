# Software Opportunity Hunt V3.4 — attempts 661–760 commercial decision

**Run date:** 2026-10-12  
**Decision:** **No commercial survivor.** 97 KILLED, 2 INCOMPLETE, 1 ANOMALY, 0 OUTREACH-READY, 0 BUILD-READY.

## Count audit

The final ledger contains 100 unique IDs and 100 distinct jobs: 40 paid-coexistence, 30 boundary-completion and 30 underserved-entry cases. Four initially searched cases were excluded because the legacy ledger had already covered their underlying jobs:

| Excluded probe | Historical collision | Replacement |
|---|---|---|
| Shopify digital-product-passport records | Digital Product Passports / PPWR | #690 Shopify orders → Norwegian VOEC return dataset |
| Lloyd’s delegated-authority bordereau | insurance bordereaux | #717 product master → GS1 GDSN CIN message |
| craft-brewery alcohol-duty return | alcohol-duty reconciliation | #737 AD operator → Ofgem sustainability reports |
| timber-importer EUDR statement | timber / EUDR | #746 apparel seller → French textile-EPR declaration |

The current jobs were checked against 634 extractable historical rows plus the legacy graveyard. Close current-run pairs were retained only when buyer, trigger, standard and accepted output differ. Historical uniqueness before this run is still not exact; the lifetime total is **at most 753**. Numeric IDs through 760 are allocated and the next unused ID is 761.

## Survivors

**None.** No case passed the complete-result, adoption-friction, repeatability, founder-operation, buyer-access and demonstrated-spend gates together.

## Banked anomaly — #742 digital calibration certificates

A calibration lab converts its existing certificate data into a schema-valid, signed Digital Calibration Certificate (DCC) XML package.

- **Why it remains:** PTB publishes the schema and field documentation; NPL/NCC demonstrated Excel-to-DCC generation and schema validation; SIKA and Kessler show real implementations. This is D4: a founder can learn, implement and test the workflow from documents and fixtures without taking a metrology course.
- **Why it is not a survivor:** the retrieved evidence is dominated by pilots, standards work and vendor capability. It does not establish broad customer requests, current manual spend or a recurring software budget. Some instrument vendors can generate DCC natively.
- **Customer access:** [UKAS Find an Organisation](https://www.ukas.com/find-an-organisation/) exposes accredited calibration laboratories; NPL/PTB project material exposes early adopters. This proves reachability only.
- **AI tests:** AI can accelerate schema mapping and test generation. It also makes an internal Excel-to-XML generator easier, so a paid product needs active customer demand, maintained mappings, signatures and integrations.
- **Verdict:** **ANOMALY**, not OUTREACH-READY.

## Decisive second-kill findings

| Case | Evidence that first looked attractive | Strongest commercial kill |
|---|---|---|
| #686 Word/Zotero → JATS XML | standard, validator and repeat publishing trigger | exact API is $2.50–$3.50/article; human-reviewed service starts around $19 |
| #691 Shopify/Woo → UK packaging EPR | official RPD file and recurring legal obligation | exact platform starts at £29/month and an exact Shopify app exists |
| #692 Shopify → Windsor parcel dataset | Shopify stopped selling the affected labels | Royal Mail, Parcelforce and ShipStation already collect/route the data at shipment |
| #699 Zendesk → FCA complaints return | upcoming taxonomy change and regulated recurring return | Civica, ResolveCX and complaints suites already own the full handling/reporting workflow |
| #720 PCF → PACT JSON | D4 schema, test cases and Fujitsu adoption | buyers purchase carbon calculation/supplier programs; PACT supplies conformance and platforms already exchange it |
| #731 installer → G98/G99 pack | 1–3 hours saved per install and clear buyer directory | CLRD already completes routing, SLD, submission and audit trail for £69/month/25 packs; Kflows and Gridflow also compete |
| #741 lab → ISO 17025 uncertainty report | services sell for $600–$1,500 per function | selecting significant contributors remains specialist judgment; calculators and lab software already cover arithmetic |
| #759 laundry → EN 14065 evidence | detailed checklist and recurring process logs | laundry systems/machine logs collect evidence and an external auditor still certifies the result |

## Commercial and AI result

V3.4 did create more **implementable** cases: schemas, examples, validators and official APIs were common. It did not create more purchasable whitespace. D4 cases repeatedly failed because a native platform already completed the job, a free official validator compressed the price, or the accepted result still required case-specific approval or specialist judgment.

Every final case records a repeated-execution AI test and an AI-assisted-build test. AI strengthened the conclusion in both directions: it makes deterministic converters cheaper to build, but also makes DIY/incumbent substitution cheaper; it cannot create missing source measurements, proprietary inputs, regulatory approval or accountable professional judgment.

## Real customer-access evidence

| Buyer class | Public route | What it proves |
|---|---|---|
| calibration laboratories | [UKAS accredited-organisation search](https://www.ukas.com/find-an-organisation/) | identifiable prospects for #742, not demand |
| solar installers | [MCS installer directory](https://mcscertified.com/find-an-installer/) | identifiable prospects for #731; direct products already serve them |
| journal publishers | [DOAJ journal directory](https://doaj.org/search/journals) | identifiable prospects for #686; exact cheap competitors exist |
| regulated financial firms | [FCA Financial Services Register](https://register.fca.org.uk/s/) | identifiable prospects for #699; incumbent suites exist |
| commercial laundries | [TSA laundry directory](https://tsa-uk.org/laundrymembers/) | identifiable prospects for #759; certification remains external |

No contact, reply, pain admission or willingness-to-pay evidence was obtained in this run. The existing CPO tracker remains unchanged: six user-reported contacts, with send dates and outcomes unknown.

## Next decisive action

Do **not** build #742 yet. Select ten UKAS-accredited calibration laboratories and ask four factual questions:

1. Has any customer required DCC XML in the last 90 days?
2. How many certificates per month would need DCC output?
3. How is DCC produced today, and which step consumes paid staff time?
4. Would the lab trial a maintained Excel/LIMS-to-validated-DCC generator, and what budget already pays for that result?

Promote only if at least three laboratories report an active recurring request, a non-trivial certificate volume, a paid/manual process the product fully replaces, and willingness to trial. Otherwise kill #742 and resume discovery from ID 761.

## Research operations and limits

125 Exa searches were executed: 104 discovery probes (four excluded as historical duplicates, leaving 100 counted), 14 deep second-kill searches and seven access/adoption checks. They requested 459 result slots. Slots are not unique sources. No external page fetch, customer interview, outreach, pilot, payment, production build, spend or merge occurred.
