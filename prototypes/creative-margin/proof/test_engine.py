"""Run with: python -m unittest discover -s prototypes/creative-margin/proof -p 'test_*.py'"""
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import calculate


class ContributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = calculate()
        cls.by_id = {p["project_id"]: p for p in cls.report["projects"]}

    def test_twenty_projects(self):
        self.assertEqual(self.report["summary"]["projects"], 20)

    def test_missing_or_ambiguous_excluded(self):
        for pid in ("P006", "P013", "P017"):
            self.assertEqual(self.by_id[pid]["status"], "not_calculable")
            self.assertIsNone(self.by_id[pid]["contribution_eur"])

    def test_posted_change_order_included(self):
        self.assertEqual(self.by_id["P004"]["recognised_revenue_eur"], Decimal("11000"))

    def test_credit_deducted(self):
        self.assertEqual(self.by_id["P012"]["recognised_revenue_eur"], Decimal("26200"))

    def test_draft_invoice_excluded(self):
        self.assertEqual(self.by_id["P015"]["recognised_revenue_eur"], Decimal("10000"))
        self.assertEqual(self.by_id["P019"]["recognised_revenue_eur"], Decimal("14000"))

    def test_draft_expense_excluded(self):
        self.assertEqual(self.by_id["P011"]["posted_direct_cost_eur"], Decimal("1900"))

    def test_p001_arithmetic(self):
        p = self.by_id["P001"]
        self.assertEqual(p["known_labour_cost_eur"], Decimal("5976"))
        self.assertEqual(p["contribution_eur"], Decimal("4524"))
        self.assertEqual(p["margin"], Decimal("0.377"))

    def test_portfolio_reconciles_only_calculable_subset(self):
        subset = [p for p in self.report["projects"] if p["status"] == "calculable"]
        self.assertEqual(self.report["summary"]["calculable_projects"], len(subset))
        self.assertEqual(self.report["summary"]["calculable_subset_contribution_eur"],
                         sum(p["contribution_eur"] for p in subset))
        self.assertEqual(self.report["summary"]["uncalculable_projects"], 3)

    def test_all_headlines_have_source_ids(self):
        self.assertTrue(all(p["source_ids"] for p in self.report["projects"]))


if __name__ == "__main__":
    unittest.main()
