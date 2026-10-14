# Stage 1 technical checkpoint — 14 October 2026

**Decision: CONDITIONAL TECHNICAL PASS; NOT A COMMERCIAL GO.** All data fictional. No real agency data or buyer evidence.

## Verified
- 20 fictional projects; 17 have calculable contribution, 3 withheld for unresolved labour rates, missing hours or revenue allocation.
- Independently recalculated from the CSVs: posted revenue €327,700 all projects; calculable subset revenue €264,700 and contribution €63,394 (23.95% margin). **No whole-portfolio contribution**.
- Four projects show negative contribution; five are below an illustrative 20% margin threshold; eight have recorded hours above planned hours. No claim of realised savings.
- Source IDs are available for reconciliation. Draft invoices/expenses and credits are handled explicitly. Python automated tests passed on GitHub Actions at commit c2f92f375eb07494a06a1dd517369c12ee3f7a74 (the later report-wording-only commit does not change arithmetic).
- A sample report exists at SAMPLE_REVIEW.md and can be regenerated with generate_report.py.

## Still missing before full Stage 1 GO
1. **Input realism:** validate whether an ordinary 5–50-person agency can actually export reliable per-project hours, fully burdened cost rates, credits and change orders with manageable preparation. Synthetic data cannot establish this.
2. **Data semantics:** distinguish posted invoice convention from true revenue recognition; test retainer allocation, write-offs and shared costs against real workflows. The sample uses a simplified operational convention.
3. **Delivery effort:** measure data cleaning, exceptions, report checking and founder time on a representative permissioned dataset; no cost-to-deliver measurement yet.
4. **Analytical value:** current observations are descriptive (losses and overruns). Repeated quoting errors, controlled pricing-floor sensitivities and counterfactual cost-to-serve need stronger evidence before the review can be sold as diagnostic.
5. **Code convergence:** two independent calculation/report paths (analyse.py/build_report.py and engine.py/generate_report.py) currently coexist. Choose one canonical pipeline before any real pilot; independent comparison is useful for this synthetic check, but duplicate production authorities are not.

## Next gated action
Improve the synthetic diagnosis and cost-to-quote scenarios without inventing savings; reconcile duplicate generators; prepare the Stage 2 competitor substitution matrix only after Stage 1 deliverable quality review. Do not contact prospects, deploy or ingest customer data.
