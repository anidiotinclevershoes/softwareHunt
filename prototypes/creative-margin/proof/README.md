# Stage 1A — fictional agency fixture
All data in this folder is synthetic. This fixture is not customer evidence.

Agency: fictional 18-person design agency, 20 completed projects. Currency EUR. Source files represent imperfect exports.

## Definitions
- Recognised revenue: posted invoice lines less posted credit notes, excluding VAT. Draft invoices and unbilled scope are not recognised.
- Project labour cost: recorded project hours multiplied by explicit fully burdened hourly rate. Missing rates or hours make the contribution uncalculable; never silently use zero.
- Direct costs: posted vendor expense amounts attributable to project; freelancers recorded as vendor expense are not also counted as staff labour.
- Contribution: recognised revenue minus project labour and direct vendor costs. Contribution margin: contribution / recognised revenue, undefined at zero revenue.
- Unallocated overhead, non-project time, tax and cash collection are excluded. Contribution is not audited profit.
- Anomalies are deliberately present. A later engine must explicitly report uncertainty rather than treating incomplete inputs as reliable.

## Files
- projects.csv: project budgets, scope and billing context
- timesheets.csv: hours and staff rate codes, with missing values
- rates.csv: fully burdened rates and ambiguous code
- invoices.csv: posted/draft invoice and credit lines
- expenses.csv: posted/draft direct vendor expenses

## Stage 1A verification
20 distinct project IDs, no real people or clients, source IDs unique per file. Fixture deliberately includes draft billing, credits, missing time/rate and unbilled scope.
