# Amazon catalogue management — adversarial second kill

Date: 2026-10-13. V3.5 diagnostic follow-up to 20 exploratory probes. **Not a new distinct attempt** and no 761-series ID allocated.

## Scope and economic evidence
- Buyer: UK Amazon marketplace merchant with recurring listing changes, suppressed SKUs and Seller Central operational exceptions. Trigger: catalogue changes, rejected listing, or suppressed ASIN.
- MySellerOps advertises £249/month excl. VAT for operational Amazon Seller Central services and £499/month for higher tier: https://www.mysellerops.com/uk/amazon-product-listing-services . **M2 current public offer, not confirmed purchase.** Seller testimonials on provider site are not independently verified.
- Skale10x advertises UK Amazon management from £599/month: https://skale10x.com/amazon-agency-uk . Different bundle including PPC; not a like-for-like software-replaceable premium.
- FlatFilePro advertises software from $99/month on a vendor article, including bulk edits, listing backups and error checks: https://flatfile.pro/uncategorized/stop-manual-edits-amazon-listing-software/ . Vendor claim, price not independently checked at checkout.

## Complete purchased result versus software scope
The customer pays a human provider to **keep listings correct and live**, including Seller Support cases and escalations, not simply to transform spreadsheets. A bounded software scope could: ingest seller catalogue, validate current product-type schema, generate JSON listing feed, submit via SP-API, poll processing outcomes, flag unresolved issues and log results. But it cannot guarantee live ASIN restoration, Amazon support intervention, policy adjudication or seller-specific appeals. Calling this a complete replacement would be false.

## Documentation and verification
- D3: Amazon official Listings Items API describes preview/patch/get, issue responses and JSON_LISTINGS_FEED; the first write response does not include issues that occur after processing: https://developer-docs.amazon.com/sp-api/lang-en_EN/docs/listings-items-api . D4 not established: no verified accepted end-to-end fixture covering real seller catalogue, suppression and restoration.
- Official migration guide states legacy XML and flat-file feeds no longer supported through Feeds API from July 31 2025; modern feeds use JSON_LISTINGS_FEED. Do not design a new API-based business around deprecated flat-file uploads: https://developer-docs.amazon/sp-api/docs/listings-management-workflow-migration .
- Amazon SP-API roles require application approval; operational risk and account access are material: https://developer-docs.amazon/sp-api/lang-en_EN/docs/roles-in-the-selling-partner-api .

## Competition and substitution
- **C4 for generic catalogue editing and error detection**: FlatFilePro markets live API editing, backups, error detection, recovery and approval workflow: https://flatfile.pro/home/ . Vendor functionality claims not independently product-tested.
- Amazon itself operates a Service Provider Network with cataloguing/account-management providers, verified reviews and reference prices: https://sell.amazon.com/tools/service-provider-network . This establishes a route to existing human alternatives, not proof of any particular seller's spend.
- AI substitution test 1: an LLM can draft listing content, map known attributes and help diagnose error messages, weakening a text-only entrant.
- AI substitution test 2: existing API-integrated listing products and service providers can add AI-based remediation and absorb the same proposed feature.
- V3.2 sidecar test: a standalone export/validator might coexist, but it does not provide the complete paid outcome and has a weak separate purchase case.

## Strongest second kill
A £249/month human service already promises broad operational completion; a $99/month incumbent offers substantial automated editing. A new solo-founder product would require Amazon developer authorization, ongoing product-type changes, reliable post-submission issue handling, seller trust and exception escalation while still failing to replace the human service's most valuable responsibility. The pricing wedge is squeezed from both sides.

## Commercial verdict
**KILL general Amazon seller catalogue-operations SaaS** for this founder. No DESK-VALIDATION/OUTREACH-READY promotion, no buyer contact, no build. This does not claim all possible Amazon micro-workflows are impossible, only that this proposition lacks a defensible complete-result/selection wedge on the evidence.

## Implication for V3.5
Continue only with a sharper filter: documented digital outputs, substantial observable paid delegation, accessible inputs, minimal privileged integration, and low exception ownership. Stop broad physical/relationship concierge searches. Do not count this validation as attempt 761.
