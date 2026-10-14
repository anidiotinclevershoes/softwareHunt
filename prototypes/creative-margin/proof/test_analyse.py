"""Run from repository root: python3 -m unittest discover -s prototypes/creative-margin/proof -p 'test_*.py'"""
import unittest
from decimal import Decimal
from pathlib import Path
import importlib.util

path = Path(__file__).with_name("analyse.py")
spec = importlib.util.spec_from_file_location("margin_analysis", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestContribution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = module.calculate()
        cls.by_id = {r["project_id"]: r for r in cls.report["projects"]}

    def test_project_count(self):
        self.assertEqual(len(self.by_id), 20)

    def test_missing_hours_is_not_zero_cost(self):
        self.assertFalse(self.by_id["P017"]["calculable"])
        self.assertIsNone(self.by_id["P017"]["contribution_eur"])

    def test_ambiguous_rate_is_not_zero_cost(self):
        self.assertFalse(self.by_id["P006"]["calculable"])

    def test_credit_reduces_recognised_revenue(self):
        self.assertEqual(self.by_id["P012"]["recognised_revenue_eur"], "26200.00")

    def test_draft_invoice_excluded(self):
        self.assertEqual(self.by_id["P015"]["recognised_revenue_eur"], "11500.00")

    def test_change_order_included_only_if_posted(self):
        self.assertEqual(self.by_id["P004"]["recognised_revenue_eur"], "11000.00")

    def test_simple_contribution(self):
        # P001: revenue 12000, 90h designer @54, 18h PM @62, vendor 1500
        self.assertEqual(self.by_id["P001"]["contribution_eur"], "4524.00")

    def test_portfolio_not_falsely_complete(self):
        self.assertIsNone(self.report["summary"]["whole_portfolio_contribution_eur"])
        self.assertEqual(self.report["summary"]["uncalculable_count"], 2)

    def test_all_calculable_reconciled(self):
        for p in self.report["projects"]:
            if not p["calculable"]:
                continue
            revenue = Decimal(p["recognised_revenue_eur"])
            labour = Decimal(p["known_labour_cost_eur_partial_if_flagged"])
            direct = Decimal(p["direct_cost_eur"])
            self.assertEqual(Decimal(p["contribution_eur"]), revenue - labour - direct)

if __name__ == "__main__":
    unittest.main()
