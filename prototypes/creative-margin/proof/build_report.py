"""Generate a Markdown review and machine-readable evidence from the fictional fixture.

Run: python3 prototypes/creative-margin/proof/build_report.py
"""
from pathlib import Path
import json
from analyse import calculate

ROOT = Path(__file__).resolve().parent

def build():
    data = calculate()
    rows = data["projects"]
    summary = data["summary"]
    lines = [
        "# FICTIONAL SAMPLE — Project Profitability Review",
        "",
        "> Demonstration only. No customer data, validated savings, or audited profit.",
        "",
        "## Executive summary",
        "",
        f"- Completed projects represented: **{summary['project_count']}**.",
        f"- Projects with fully calculable contribution: **{summary['calculable_count']}**.",
        f"- Projects with unresolved labour inputs: **{summary['uncalculable_count']}**.",
        f"- Posted recognised revenue across all projects: **€{summary['all_project_recognised_revenue_eur']}**.",
        f"- Contribution of calculable subset only: **€{summary['calculable_subset_contribution_eur']}** on €{summary['calculable_subset_revenue_eur']} revenue (**{summary['calculable_subset_margin_pct']}%**).",
        "- **No whole-portfolio contribution is reported** because some projects have unresolved labour or revenue allocation.",
        "",
        "## Project-level contribution",
        "",
        "| Project | Revenue | Labour cost* | Direct costs | Contribution | Margin | Reliability |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        status = "Calculated" if r["calculable"] else "Incomplete"
        lines.append(f"| {r['project_id']} | €{r['recognised_revenue_eur']} | €{r['known_labour_cost_eur_partial_if_flagged']} | €{r['direct_cost_eur']} | {('€' + r['contribution_eur']) if r['calculable'] else 'N/A'} | {(r['contribution_margin_pct'] + '%') if r['calculable'] else 'N/A'} | {status} |")
    lines += [
        "",
        "*Labour costs are partial where inputs are missing; never use partial figures as final project costs.*",
        "",
        "## Exceptions requiring investigation",
        "",
    ]
    for r in rows:
        for warning in r["warnings"]:
            lines.append(f"- **{r['project_id']}**: {warning}.")
    lines += [
        "",
        "## What an agency owner could do next",
        "",
        "1. Reconcile missing time and ambiguous rates before relying on portfolio-wide margin.",
        "2. Review unbilled scope and draft invoices; neither is automatically earned revenue.",
        "3. Compare repeat project types only after confirming labour cost basis and scope differences.",
        "4. Use project contribution for quoting discussions, not as a substitute for net business profit.",
        "",
        "## Method and limits",
        "",
        "Recognised revenue = posted invoice lines minus posted credits, excluding draft lines. Labour = recorded hours × explicit fully burdened hourly rate. Direct vendor costs = posted attributable expenses. Contribution = revenue − labour − direct costs. No overhead allocation, tax, collections, or non-project labour is included. These are synthetic records; source IDs, warnings and underlying calculations are in analysis.json.",
        "",
        "## Minimum real-customer input checklist (future only; do not upload yet)",
        "",
        "- Project IDs, fixed-fee estimates and scope/change orders.",
        "- Posted invoice lines and credits with project linkage and dates.",
        "- Project-linked time entries, role codes and rate basis.",
        "- Vendor/freelancer costs with project IDs and posted status.",
        "- Retainer allocations, non-project time, and any exclusions.",
        "- Written permission and an agreed secure transfer, retention and deletion process before any real customer records.",
        "",
        "## Decision",
        "",
        "**Stage 1 gate pending.** This is a calculation-backed fictional sample, not proof of customer demand or that ordinary agencies can provide complete inputs. Independent test execution and qualitative review are required.",
        "",
    ]
    (ROOT / "analysis.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (ROOT / "SAMPLE_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print("Wrote analysis.json and SAMPLE_REPORT.md")

if __name__ == "__main__":
    build()
