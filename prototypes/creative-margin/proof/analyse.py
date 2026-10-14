"""Deterministic, conservative contribution analysis for the fictional agency fixture.

Run: python3 prototypes/creative-margin/proof/analyse.py
Only Python standard library required. Does not process customer data.
"""
import csv
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ZERO = Decimal("0")

def read_csv(name):
    with (ROOT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def amount(value):
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid monetary value: {value!r}")

def fmt(value):
    return None if value is None else str(value.quantize(Decimal("0.01")))

def calculate():
    projects = read_csv("projects.csv")
    timesheets = read_csv("timesheets.csv")
    invoices = read_csv("invoices.csv")
    expenses = read_csv("expenses.csv")
    rate_rows = read_csv("rates.csv")
    rates = {r["rate_code"]: r for r in rate_rows}
    ids = [p["project_id"] for p in projects]
    if len(ids) != 20 or len(set(ids)) != 20:
        raise ValueError("Fixture must contain exactly 20 distinct projects")
    if any(len({r[key] for r in rows}) != len(rows) for rows, key in
           ((timesheets, "entry_id"), (invoices, "invoice_line_id"), (expenses, "expense_id"))):
        raise ValueError("Duplicate source identifier")
    for name, rows in (("timesheets", timesheets), ("invoices", invoices), ("expenses", expenses)):
        if any(row["project_id"] not in ids for row in rows):
            raise ValueError(f"Orphan project reference in {name}")

    grouped = {}
    for name, rows in (("timesheets", timesheets), ("invoices", invoices), ("expenses", expenses)):
        index = defaultdict(list)
        for row in rows:
            index[row["project_id"]].append(row)
        grouped[name] = index

    results = []
    for p in projects:
        pid = p["project_id"]
        warnings = []
        invoice_sources = []
        revenue = ZERO
        for row in grouped["invoices"][pid]:
            if row["status"] != "posted":
                warnings.append(f"Excluded unposted invoice {row['invoice_line_id']}")
                continue
            if row["line_type"] not in ("invoice", "credit"):
                raise ValueError("Unsupported invoice line type")
            value = amount(row["amount_eur"])
            if value < ZERO:
                raise ValueError("Invoice/credit amount must be nonnegative")
            revenue += value if row["line_type"] == "invoice" else -value
            invoice_sources.append(row["invoice_line_id"])

        expense_sources = []
        direct_cost = ZERO
        for row in grouped["expenses"][pid]:
            if row["status"] != "posted":
                warnings.append(f"Excluded unposted expense {row['expense_id']}")
                continue
            value = amount(row["amount_eur"])
            if value < ZERO:
                raise ValueError("Expense amount must be nonnegative")
            direct_cost += value
            expense_sources.append(row["expense_id"])

        labour_sources = []
        hours = ZERO
        labour_cost = ZERO
        labour_known = True
        for row in grouped["timesheets"][pid]:
            raw = row["hours"].strip()
            rate = rates.get(row["rate_code"])
            if not raw:
                warnings.append(f"Missing hours {row['entry_id']}")
                labour_known = False
                continue
            h = amount(raw)
            if h < ZERO:
                raise ValueError("Negative hours not supported")
            hours += h
            if not rate or rate["status"] != "known" or not rate["fully_burdened_eur_per_hour"].strip():
                warnings.append(f"Unresolved rate {row['entry_id']} ({row['rate_code']})")
                labour_known = False
                continue
            labour_cost += h * amount(rate["fully_burdened_eur_per_hour"])
            labour_sources.append(row["entry_id"])

        if "unbilled" in p["scope_notes"].lower():
            warnings.append("Unbilled scope requires reconciliation")
        if "retainer" in p["scope_notes"].lower():
            warnings.append("Retainer revenue allocation requires verification")
        if "change order" in p["scope_notes"].lower():
            warnings.append("Change order must be verified against approved scope")
        if "allocation unclear" in p["scope_notes"].lower():
            warnings.append("Revenue allocation uncertain; project contribution withheld")
            labour_known = False
        contribution = revenue - labour_cost - direct_cost if labour_known else None
        margin = contribution / revenue * 100 if contribution is not None and revenue != ZERO else None
        results.append({
            "project_id": pid, "project_type": p["project_type"],
            "quoted_fee_eur": fmt(amount(p["quoted_fee_eur"])),
            "planned_hours": fmt(amount(p["planned_hours"])),
            "recorded_hours_partial_if_flagged": fmt(hours),
            "recognised_revenue_eur": fmt(revenue),
            "known_labour_cost_eur_partial_if_flagged": fmt(labour_cost),
            "direct_cost_eur": fmt(direct_cost),
            "contribution_eur": fmt(contribution),
            "contribution_margin_pct": fmt(margin),
            "calculable": contribution is not None,
            "warnings": warnings,
            "source_ids": {"invoices": invoice_sources, "timesheets_costed": labour_sources, "expenses": expense_sources},
        })
    complete = [r for r in results if r["calculable"]]
    portfolio_revenue = sum((amount(r["recognised_revenue_eur"]) for r in results), ZERO)
    complete_revenue = sum((amount(r["recognised_revenue_eur"]) for r in complete), ZERO)
    complete_contribution = sum((amount(r["contribution_eur"]) for r in complete), ZERO)
    return {
        "label": "FICTIONAL SAMPLE — NOT CUSTOMER RESULTS",
        "definitions": "Recognised posted invoices net of posted credits; contribution excludes overhead and non-project time.",
        "projects": results,
        "summary": {
            "project_count": len(results),
            "calculable_count": len(complete),
            "uncalculable_count": len(results) - len(complete),
            "all_project_recognised_revenue_eur": fmt(portfolio_revenue),
            "calculable_subset_revenue_eur": fmt(complete_revenue),
            "calculable_subset_contribution_eur": fmt(complete_contribution),
            "calculable_subset_margin_pct": fmt(complete_contribution / complete_revenue * 100) if complete_revenue else None,
            "whole_portfolio_contribution_eur": None if len(complete) != len(results) else fmt(complete_contribution),
        },
    }

if __name__ == "__main__":
    print(json.dumps(calculate(), indent=2))
