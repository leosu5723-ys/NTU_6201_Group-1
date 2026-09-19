import unittest

from cost_model import (
    break_even_success_rate,
    cost_to_serve,
    sensitivity_table,
    token_cost,
)


class CostModelTests(unittest.TestCase):
    def test_three_layer_cost_model(self):
        variable = token_cost(43_200, 1_200, 0.10, 0.40)
        self.assertAlmostEqual(variable, 0.0048)
        result = cost_to_serve(
            variable_cost=variable,
            success_rate=0.90,
            failure_cost=7.60,
            monthly_volume=8_000,
            fixed_monthly=500,
        )
        self.assertAlmostEqual(result["expected_fallback_per_task"], 0.76)
        self.assertAlmostEqual(result["monthly_total"], (0.0048 + 0.76) * 8000 + 500)

    def test_break_even_matches_brief_logic(self):
        value = break_even_success_rate(
            cheap_variable_cost=0.005,
            expensive_cost_to_serve=0.657,
            failure_cost=7.60,
        )
        self.assertAlmostEqual(value, 0.9142105263)

    def test_break_even_is_not_clipped_when_observed_costs_imply_out_of_range_rate(self):
        value = break_even_success_rate(
            cheap_variable_cost=0.01,
            expensive_cost_to_serve=10.0,
            failure_cost=7.60,
        )
        self.assertLess(value, 0.0)

    def test_sensitivity_varies_success_rate_by_ten_points(self):
        rows = sensitivity_table(
            variable_cost=0.01,
            success_rate=0.85,
            failure_cost=7.60,
            monthly_volume=8_000,
            fixed_monthly=0,
        )
        self.assertEqual([row["success_rate"] for row in rows], [0.75, 0.85, 0.95])
        self.assertGreater(rows[0]["monthly_total"], rows[-1]["monthly_total"])


if __name__ == "__main__":
    unittest.main()
