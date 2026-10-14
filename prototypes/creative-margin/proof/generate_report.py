"""Generate a labelled fictional customer review from deterministic calculations."""
from decimal import Decimal
from pathlib import Path
from engine import calculate

ROOT = Path(__file__).resolve().parent


def eur(value):
    return "Not calculable" if value is None else f"€{value:,.2f}"


def render():
    data = calculate()
    summary = data["summary"]
    projects = data["projects"]
    calculable = [p for p in projects if p["status"] == "calculable"]
    below = [p for p in calculable if p["margin"] < Decimal("0.20")]
    over = [p for p in projects if p["recorded_hours"] > p["planned_hours"]]
    lines = [
        "# SAMPLE Project Profitability Review — FICTIONAL DATA",
        "",
        "> Demonstration only. All clients, amounts and projects are invented. Not audited accounts or evidence of actual savings.",
        "",
        "## Executive summary",
        f"- Reviewed **{summary['projects']}** synthetic completed projects; **{summary['calculable_projects']}** have calculable contribution and **{summary['uncalculable_projects']}** require clarification.",
        f"- Recognised invoice revenue across all projects: **{eur(summary['total_recognised_revenue_eur'])}**. This is **not** a portfolio profitability figure.",
        f"- Calculable subset contribution: **{eur(summary['calculable_subset_contribution_eur'])}** on **{eur(summary['calculable_subset_revenue_eur'])}** revenue (margin **{summary['calculable_subset_margin']:.1%}**). Excludes unresolved projects; do not extrapolate.",
        f"- **{len(below)}** calculable projects have contribution margin below an illustrative 20% review threshold (not a verified agency target).",
        f"- **{len(over)}** projects have recorded hours exceeding planned hours. Missing time means this comparison may understate overruns.",
        "",
        "## Project reconciliation",
        "| Project | Recognised revenue | Recorded hours / planned | Direct costs | Contribution | Margin | Status |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for p in projects:
        margin = f"{p['margin']:.1%}" if p["margin"] is not None else "N/A"
        lines.append(
            f"| {p['project_id']} | {eur(p['recognised_revenue_eur'])} | "
            f"{p['recorded_hours']} / {p['planned_hours']} | {eur(p['posted_direct_cost_eur'])} | "
            f"{eur(p['contribution_eur'])} | {margin} | {p['status']} |"
        )
    lines += ["", "## Exceptions and evidence", ""]
    for p in projects:
        if p["warnings"]:
            lines.append(f"- **{p['project_id']}**: {'; '.join(p['warnings'])}. Source IDs: {', '.join(p['source_ids'])}.")
    lines += [
        "", "## Interpretation and potential actions",
        "- Review low-margin projects against the actual pricing and scope records; do not assume each represents a loss.",
        "- Investigate projects with hours above plan before revising future estimates. Missing or misallocated hours may alter the pattern.",
        "- Confirm all draft invoices, credits, change orders and retainer allocations before making financial decisions.",
        "- A pricing-floor sensitivity requires validated cost rates, overhead policy and a target margin; no guaranteed savings are claimed.",
        "",
        "## Method and boundaries",
        "- Revenue = posted invoice lines minus posted credit lines; draft invoices excluded. This is a synthetic operational convention, not a general accounting revenue-recognition policy.",
        "- Labour = known recorded project hours × known fully burdened hourly rates. Missing hours or rates make contribution not calculable.",
        "- Contribution = recognised revenue − labour − posted direct vendor expenses. Unallocated overhead, tax, cash collection and non-project time excluded.",
        "- This is **project contribution**, not net profit, audited profit or a complete financial statement.",
        "- Source IDs in the exception list and CSV inputs permit manual recomputation; engine.py is the deterministic calculation authority.",
        "",
        "## Minimum real-customer inputs (future, subject to approval)",
        "1. Project register and estimates, including change-order history.",
        "2. Posted invoices, credit notes and allocation rules; clarify accounting basis.",
        "3. Timesheets with person/role, project, date, hours and completeness statement.",
        "4. Labour cost rates and burdening methodology, without unnecessary employee personal details.",
        "5. Project vendor expenses, freelancer classification and overhead allocation policy.",
        "6. Retainer period/allocation method, exception owners and a reconciliation contact.",
        "",
        "## Confidentiality boundary",
        "Do not send customer financial files to this prototype. A real pilot requires explicit permission, a documented secure transfer/storage/deletion process, access controls and a data minimisation review before processing.",
        "",
        "## Stage 1 gate",
        "Pending: run automated tests, independently spot-check multiple projects and confirm realistic source availability. This sample does **not** establish willingness to pay.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    path = ROOT / "SAMPLE_REVIEW.md"
    path.write_text(render(), encoding="utf-8")
    print(path)
