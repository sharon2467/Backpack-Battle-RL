"""Semantic and accounting checks for the isolated RNG analysis."""
import unittest
import numpy as np
import sympy as sp
from analyze_balanced_rng import range_step, range_stationary, roll_step, roll_probability, exact_roll_counts


class BalancedRngAnalysisTests(unittest.TestCase):
    def test_range_accounting_and_bounds(self):
        rng = np.random.default_rng(21)
        for low, high in [(0, 0), (0, 1), (-3, 0), (2, 6), (0, 10)]:
            acc = np.zeros(512)
            total = np.zeros(512)
            for n in range(1, 129):
                raw = rng.integers(low, high + 1, 512)
                value, acc = range_step(acc, raw, low, high)
                total += value
                self.assertTrue(np.all((value >= low) & (value <= high)))
                np.testing.assert_array_equal(acc, total - n * (low + high) / 2)
                self.assertTrue(np.all(np.abs(acc) <= high - low))

    def test_range_stationary_solution(self):
        for width in range(11):
            row = range_stationary(width)
            self.assertAlmostEqual(sum(row["pmf"]), 1)
            self.assertGreater(min(row["pmf"]), -1e-12)
            self.assertAlmostEqual(row["mean"], width / 2)
            self.assertLess(row["residual"], 1e-12)
        np.testing.assert_allclose(range_stationary(1)["pmf"], [.5, .5])
        np.testing.assert_allclose(range_stationary(4)["pmf"], np.array([26,20,23,20,26]) / 115)
        # Independent exact rational matrices, ordered by acc=-2,-1,0,1,2.
        transition = sp.Matrix([[1,1,3,0,0],[1,1,1,2,0],[1,1,1,1,1],[0,2,1,1,1],[0,0,3,1,1]]) / 5
        emission = sp.Matrix([[0,0,1,1,3],[0,1,1,1,2],[1,1,1,1,1],[2,1,1,1,0],[3,1,1,0,0]]) / 5
        mass = (transition.T - sp.eye(5)).nullspace()[0]
        mass /= sum(mass)
        exact_pmf = mass.T * emission
        self.assertEqual(list(exact_pmf), [sp.Rational(v,115) for v in [26,20,23,20,26]])
        self.assertEqual(sum(exact_pmf[i] * (i-2)**2 for i in range(5)), sp.Rational(248,115))
        edges = [[(0,2),(1,3),(2,4),(2,4),(2,4)],
                 [(0,1),(1,2),(2,3),(3,4),(3,4)],
                 [(0,0),(1,1),(2,2),(3,3),(4,4)],
                 [(1,0),(1,0),(2,1),(3,2),(4,3)],
                 [(2,0),(2,0),(2,0),(3,1),(4,2)]]
        next_mean = emission * sp.Matrix(range(5))
        product = sum(mass[i] * value * next_mean[j] / 5 for i in range(5) for j, value in edges[i])
        self.assertEqual((product-4) / sp.Rational(248,115), -sp.Rational(229,620))

    def test_roll_source_edges(self):
        expected, wins, last = np.array([.2, -.2]), np.array([2, 1]), np.array([True, False])
        result, e, w, l = roll_step(expected, wins, last, np.array([0., 1.]), np.array([0., 1.]))
        np.testing.assert_array_equal(result, [False, True])
        for actual, original in [(e, expected), (w, wins), (l, last)]:
            np.testing.assert_array_equal(actual, original)
        self.assertEqual(roll_probability(0, 0, False, .75), 1)
        self.assertEqual(roll_probability(.3, 0, False, .25), .25)
        self.assertAlmostEqual(roll_probability(.31, 0, False, .25), .25 * .93)
        self.assertEqual(roll_probability(0, 0, True, .4), .4)
        self.assertEqual(roll_probability(0, 0, False, .6), .6)
        self.assertEqual(roll_probability(0, 0, True, .25), .125)
        # Vectorized translation vs independent scalar probability for all histories sampled here.
        rng = np.random.default_rng(22)
        expected = rng.uniform(-3, 3, 1024)
        wins = rng.integers(0, 4, 1024)
        last = rng.random(1024) < .5
        targets = rng.uniform(.001, .999, 1024)
        u = rng.random(1024)
        result, _, _, _ = roll_step(expected, wins, last, targets, u)
        scalar = [draw <= roll_probability(e, w, l, p) for e, w, l, p, draw in zip(expected, wins, last, targets, u)]
        np.testing.assert_array_equal(result, scalar)

    def test_roll_exact_counts(self):
        for p in [0, .1, .25, .5, .75, 1]:
            pmf = exact_roll_counts(p, 32)
            self.assertAlmostEqual(pmf.sum(), 1)
            self.assertGreaterEqual(pmf.min(), 0)
        self.assertEqual(exact_roll_counts(0, 32)[0], 1)
        self.assertEqual(exact_roll_counts(1, 32)[32], 1)
        for p, success in [(.25, .25), (.5, .5), (.75, 1)]:
            np.testing.assert_allclose(exact_roll_counts(p, 1), [1-success, success])
        # Two calls at .25: q2=.25/(3*.75)*.5 after success, .25 after failure.
        np.testing.assert_allclose(exact_roll_counts(.25, 2), [9/16, 61/144, 1/72])


if __name__ == "__main__":
    unittest.main()
