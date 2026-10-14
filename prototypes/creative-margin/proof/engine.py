"""Deterministic synthetic project contribution calculation. Python 3.11+, stdlib only."""
import csv
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ZERO = Decimal("0")


def rows(name, folder=ROOT):
    with (folder / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def money(value):
    try:
        result = Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"Invalid numeric value: {value!r}")
    if not result.is_finite():
        raise ValueError("Non-finite amount")
    return result


def calculate(folder=ROOT):
    projects = rows("projects.csv", folder)
    ids = [p["project_id"] for p in projects]
    if len(ids) != 20 or len(set(ids)) != 20:
        raise ValueError("Expected 20 unique project IDs")
    known = set(ids)
    rates = {}
    for r in rows("rates.csv", folder):
        if r["rate_code"] in rates:
            raise ValueError("Duplicate rate code")
        rates[r["rate_code"]] = money(r["fully_burdened_eur_per_hour"]) if r["status"] == "known" else None
    sources = {}
    for name, key in [("timesheets.csv", "entry_id"), ("invoices.csv", "invoice_line_id"), ("expenses.csv", "expense_id")]:
        data = rows(name, folder)
        source_ids = [r[key] for r in data]
        if len(set(source_ids)) != len(source_ids):
            raise ValueError(f"Duplicate source ID in {name}")
        if any(r["project_id"] not in known for r in data):
            raise ValueError(f"Unknown project ID in {name}")
        sources[name] = defaultdict(list)
        for r in data:
            sources[name][r["project_id"]].append(r)
    result = []
    for p in projects:
        pid = p["project_id"]
        warnings = []
        refs = []
        revenue = ZERO
        labour = ZERO
        expenses = ZERO
        hours = ZERO
        complete = True
        for inv in sources["invoices.csv"][pid]:
            refs.append(inv["invoice_line_id"])
            amount = money(inv["amount_eur"])
            if amount < 0:
                raise ValueError("Negative invoice amount")
            if inv["status"] == "posted":
                if inv["line_type"] not in ("invoice", "credit"):
                    raise ValueError("Invalid posted invoice type")
                revenue += amount if inv["line_type"] == "invoice" else -amount
            elif inv["status"] == "draft":
                warnings.append("Draft invoice excluded")
            else:
                raise ValueError("Unknown invoice status")
        for t in sources["timesheets.csv"][pid]:
            refs.append(t["entry_id"])
            if not t["hours"].strip():
                complete = False
                warnings.append(f"Missing hours: {t['entry_id']}")
                continue
            h = money(t["hours"])
            if h < 0:
                raise ValueError("Negative hours")
            hours += h
            if t["rate_code"] not in rates or rates[t["rate_code"]] is None:
                complete = False
                warnings.append(f"Unknown labour rate: {t['entry_id']}")
            else:
                labour += h * rates[t["rate_code"]]
        for e in sources["expenses.csv"][pid]:
            refs.append(e["expense_id"])
            amount = money(e["amount_eur"])
            if amount < 0:
                raise ValueError("Negative expense")
            if e["status"] == "posted":
                expenses += amount
            elif e["status"] == "draft":
                warnings.append("Draft expense excluded")
            else:
                raise ValueError("Unknown expense status")
        if "Unbilled" in p["scope_notes"]:
            warnings.append("Potential unbilled scope; value unknown")
        if "allocation unclear" in p["scope_notes"]:
            complete = False
            warnings.append("Revenue allocation requires confirmation")
        if "Change order" in p["scope_notes"]:
            warnings.append("Change order: confirm scope and cost attribution")
        if "Retainer" in p["project_type"]:
            warnings.append("Retainer: confirm period and revenue allocation")
        contribution = revenue - labour - expenses if complete else None
        margin = contribution / revenue if contribution is not None and revenue != ZERO else None
        result.append({
            "project_id": pid, "project_type": p["project_type"],
            "quoted_fee_eur": money(p["quoted_fee_eur"]),
            "planned_hours": money(p["planned_hours"]),
            "recorded_hours": hours, "recognised_revenue_eur": revenue,
            "known_labour_cost_eur": labour, "posted_direct_cost_eur": expenses,
            "contribution_eur": contribution, "margin": margin,
            "status": "calculable" if complete else "not_calculable",
            "warnings": warnings, "source_ids": refs,
        })
    calculable = [p for p in result if p["contribution_eur"] is not None]
    summary = {
        "fictional": True, "projects": len(result),
        "calculable_projects": len(calculable),
        "uncalculable_projects": len(result) - len(calculable),
        "total_recognised_revenue_eur": sum((p["recognised_revenue_eur"] for p in result), ZERO),
        "calculable_subset_revenue_eur": sum((p["recognised_revenue_eur"] for p in calculable), ZERO),
        "calculable_subset_contribution_eur": sum((p["contribution_eur"] for p in calculable), ZERO),
    }
    summary["calculable_subset_margin"] = (
        summary["calculable_subset_contribution_eur"] / summary["calculable_subset_revenue_eur"]
        if summary["calculable_subset_revenue_eur"] else None
    )
    return {"summary": summary, "projects": result}


def json_safe(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(type(obj).__name__)


if __name__ == "__main__":
    print(json.dumps(calculate(), indent=2, default=json_safe))
