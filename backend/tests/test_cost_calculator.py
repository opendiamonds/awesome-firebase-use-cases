"""Property-based tests for cost_calculator."""

import unittest
from decimal import Decimal

from hypothesis import given, strategies as st

from cost.cost_calculator import (
    hourly_from_monthly,
    is_overspent,
    line_subtotal,
    pie_buckets,
    total_priced,
)


class TestCostCalculator(unittest.TestCase):
    def test_hourly_from_monthly_730(self):
        self.assertEqual(hourly_from_monthly(Decimal("730")), Decimal("1.00"))

    def test_line_subtotal_zero_hours(self):
        self.assertEqual(line_subtotal(Decimal("1"), 0), Decimal("0.00"))

    def test_negative_hours_raises(self):
        with self.assertRaises(ValueError):
            line_subtotal(Decimal("1"), -1)

    @given(st.integers(min_value=0, max_value=24), st.decimals(min_value=0, max_value=100, places=2))
    def test_pie_sum_equals_total(self, hours, hourly):
        hourly = Decimal(hourly)
        lines = [
            {
                "status": "priced",
                "hourly": hourly,
                "hours": hours,
                "category": "compute",
            }
        ]
        total = total_priced(lines)
        pie = pie_buckets(lines)
        self.assertEqual(sum(pie.values()), total)

    def test_is_overspent_none_budget(self):
        self.assertFalse(is_overspent(Decimal("10.00"), None))

    def test_unpriced_excluded_from_total(self):
        lines = [
            {"status": "unpriced", "hourly": Decimal("1"), "hours": 24, "category": "other"},
            {
                "status": "priced",
                "hourly": Decimal("0.10"),
                "hours": 24,
                "category": "compute",
            },
        ]
        self.assertEqual(total_priced(lines), line_subtotal(Decimal("0.10"), 24))


if __name__ == "__main__":
    unittest.main()
