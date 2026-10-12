# Software Opportunity Hunt — V3.4 Documented-Workflow Implementability Amendment

**Approved:** 2026-10-12 by explicit user instruction  
**Status:** active authority; supplements V3/V3.1/V3.2/V3.3 without weakening commercial, customer-access, reliability or BUILD-READY gates  
**Scope:** founder expertise, domain knowledge, implementation feasibility, verification and specialist-operation risk

## Purpose

Earlier research sometimes treated an unfamiliar or technically specialised domain as if it necessarily required the founder to become a practitioner or operate a service. That is too restrictive.

The founder does not need prior domain expertise and is not expected to take a course. A domain is admissible when accessible, trustworthy documentation gives an engineer enough information to implement the required workflow confidently and verify its outputs. Technical vocabulary, specialist subject matter and substantial implementation learning are not kills by themselves.

The relevant boundary is whether the product can encode and execute the knowledge. The founder must not need to supply undocumented professional judgement on every transaction.

## 1. Revised implementability gate

Ask:

> Is there enough accessible, trustworthy documentation to implement a complete useful workflow and verify its outputs confidently, without requiring the founder to become a domain specialist or supply specialist judgement for each transaction?

“Acquire the necessary knowledge” means obtaining implementation-ready material: standards, official manuals, schemas, rule tables, algorithms, worked examples, accepted sample outputs, conformance requirements, validators, test fixtures or similarly reliable sources. It does not mean retraining the founder for a second profession.

A bounded paid review by a practitioner may validate the implementation when affordable. It must not conceal an absent specification, become required for every customer output, or turn normal operation into a specialist service.

## 2. Documentation evidence grades

Record the strongest level found:

| Grade | Evidence |
|---|---|
| D0 | No usable implementation material found |
| D1 | Explanatory article, marketing description or high-level workflow only |
| D2 | Substantive public procedure, manual, rule set, schema or algorithm |
| D3 | D2 plus worked examples, known-correct outputs, test fixtures or an independent validator |
| D4 | Official conformance suite, authoritative validator or machine-checkable acceptance process |

D0/D1 does not prove the workflow is undocumented; after targeted searches it normally leaves the case incomplete or kills only when missing documentation is itself decisive. D2–D4 supports technical feasibility but never proves demand, willingness to pay, distribution or founder economics.

## 3. Implementation feasibility test

For a candidate surviving initial commercial screening, establish:

1. **Specification:** the sources define what the output must contain or do.
2. **Inputs:** required inputs are obtainable by the buyer without prohibited access or unreasonable integration.
3. **Algorithmic boundary:** rules, transformations and supported decisions can be encoded; ambiguous cases can be identified.
4. **Verification oracle:** output can be checked using fixtures, invariants, a reference implementation, validator, sandbox, reversible comparison or clear acceptance test.
5. **Safe exceptions:** unsupported or low-confidence cases can be rejected or sent back with a precise reason rather than silently guessed.
6. **Change control:** standards, schemas and platform rules can be monitored and updated at manageable cost.
7. **Operating independence:** ordinary transactions do not require a practitioner to review, approve or repair the result.
8. **Commercial fit:** the ordinary V3 buyer, urgency, selection, adoption, support, economics, access and competition gates still pass.

A workflow may be complex to implement once and still be attractive if normal execution becomes deterministic, testable and low-touch.

## 4. What domain complexity does not kill

Do not kill solely because:

- the founder has not previously worked in the sector;
- the terminology is specialist or the implementation requires concentrated study;
- the rules span several documents;
- an expert review would be useful before launch;
- edge cases exist, provided they can be detected and safely refused;
- incumbents employ specialists, when the target bounded output has an implementable documented subset.

Do not equate professional service prices with software willingness to pay. Do not assume documentation makes the full service automatable when judgement, relationships, physical work or legal sign-off remain the purchased result.

## 5. Genuine specialist-operation kills

Kill or constrain the output when:

- authoritative rules are private, contractual, inaccessible or dependent on confidential platform material;
- acceptance turns on tacit judgement that cannot be specified or reliably tested;
- a licensed or accountable practitioner must approve each output;
- required facts cannot be obtained or verified from available inputs;
- the system cannot detect when it is outside its competence;
- false acceptance creates operating or liability exposure disproportionate to the opportunity;
- rules change too frequently or unpredictably for a solo operator to maintain;
- customer-specific configuration and exception support remain the core purchased value.

State the exact reason. “Requires domain knowledge” is no longer an adequate kill rationale.

## 6. AI tests under this amendment

For repeated-execution substitution, test whether a buyer with general AI and the same documents can consistently gather inputs, follow the full specification, validate outputs, preserve history and handle batches and exceptions. If occasional prompting completes and verifies the job, the product is weak.

For the AI-build test, distinguish “a model can generate plausible output” from “software can deterministically produce and verify an accepted output.” Documentation may make the latter buildable. It also makes the feature easier for incumbents and competitors to copy; commercial selection still needs evidence.

## 7. Treatment of earlier decisions

Do not silently rewrite historical verdicts. A case previously killed only because the founder lacked domain knowledge should be eligible for a dated reassessment against V3.4. Reopen it only if implementation-ready documentation, a verification oracle and the existing commercial gates support the change. Cases also killed by adequate competition, weak economics, inaccessible inputs, liability, poor distribution or recurring specialist operation remain killed unless new evidence addresses those reasons.

## 8. Next explicit 100-case run

For the next authorised 100-case continuation, retain V3.2's 40 paid-coexistence / 30 system-boundary / 30 underserved-entry composition. Bias discovery toward commercially meaningful jobs whose complexity may be encodable from documentation. For each case record the highest documentation grade and do not use unfamiliarity as a proxy for operating burden.

Competitor, documentation, validator, AI, access and second-kill searches are follow-ups and never additional attempts. A zero-survivor result remains valid.
