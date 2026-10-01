"""Run from the project root:  python -m unittest discover -v"""
import io
import unittest
from contextlib import redirect_stdout
from fractions import Fraction as F
from unittest.mock import patch

import main
from interpolation.helpers import step_size
from interpolation.newton import choose_method, interpolate
from interpolation.polynomial import build_polynomial, evaluate, polynomial_to_text
from interpolation.table import build_difference_table, visible_columns

CUBE_X = [F(i) for i in range(1, 7)]
CUBE_F = [F(i ** 3) for i in range(1, 7)]
SET2_X = [F(v) for v in (2, 4, 6, 8, 10, 12, 14)]
SET2_F = [F(v) for v in (23, 93, 259, 569, 1071, 1813, 2843)]
DEC_X = [F(v) for v in ("0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7")]
DEC_F = [F(v) for v in ("0.905", "0.819", "0.741",
                        "0.671", "0.607", "0.549", "0.497")]


class TestTable(unittest.TestCase):
    def test_cube_differences(self):
        t = build_difference_table(CUBE_F)
        self.assertEqual(t[1], [7, 19, 37, 61, 91])
        self.assertEqual(t[3], [6, 6, 6])
        self.assertEqual(visible_columns(t), 4)          # f, Df, D2f, D3f

    def test_decimals_are_exact(self):
        t = build_difference_table(DEC_F)
        self.assertEqual(t[1][0], F("-0.086"))

    def test_step_size(self):
        self.assertEqual(step_size(CUBE_X), 1)
        self.assertIsNone(step_size([F(v) for v in (1, 2, 4, 5)]))
        self.assertIsNone(step_size([F(v) for v in (3, 2, 1)]))


class TestInterpolation(unittest.TestCase):
    def setUp(self):
        self.t = build_difference_table(CUBE_F)

    def test_handout_forward(self):
        r = interpolate(CUBE_X, self.t, F(1), F("2.5"))
        self.assertEqual((r.method, r.x0, r.p, r.value),
                         ("FORWARD", 2, F(1, 2), F("15.625")))

    def test_handout_backward(self):
        r = interpolate(CUBE_X, self.t, F(1), F("5.5"))
        self.assertEqual((r.method, r.x0, r.p, r.value),
                         ("BACKWARD", 5, F(1, 2), F("166.375")))

    def test_p_is_always_below_one_inside_table(self):
        for q in ("1.1", "2.5", "3.5", "3.6", "5.9"):
            r = interpolate(CUBE_X, self.t, F(1), F(q))
            self.assertTrue(F(0) < r.p < F(1))

    def test_negative_p_shifts_origin_left(self):
        r = interpolate(CUBE_X, self.t, F(1), F("3.6"))
        self.assertEqual((r.method, r.x0, r.p), ("BACKWARD", 3, F(3, 5)))

    def test_extrapolation_flagged(self):
        r = interpolate(CUBE_X, self.t, F(1), F("7.5"))
        self.assertTrue(r.extrapolation)
        self.assertEqual(r.value, F("421.875"))
        self.assertEqual(choose_method(CUBE_X, F(0))[0], "FORWARD")

    def test_set2_with_h_equal_2(self):
        t = build_difference_table(SET2_F)
        for q in ("11.8", "10.5", "5", "3.3"):
            q = F(q)
            r = interpolate(SET2_X, t, F(2), q)
            self.assertEqual(r.value, q ** 3 + 7 * q + 1)
        self.assertEqual(interpolate(
            SET2_X, t, F(2), F("11.8")).method, "BACKWARD")

    def test_decimal_hand_value(self):
        t = build_difference_table(DEC_F)
        r = interpolate(DEC_X, t, F("0.1"), F("0.35"))
        self.assertEqual(r.value, F("0.70525"))


class TestPolynomial(unittest.TestCase):
    def test_cube(self):
        c = build_polynomial(CUBE_X, build_difference_table(CUBE_F), F(1))
        self.assertEqual(polynomial_to_text(c), "x^3")

    def test_set2(self):
        c = build_polynomial(SET2_X, build_difference_table(SET2_F), F(2))
        self.assertEqual(polynomial_to_text(c), "x^3 + 7x + 1")

    def test_decimals_pass_through_every_point(self):
        c = build_polynomial(DEC_X, build_difference_table(DEC_F), F("0.1"))
        self.assertEqual(len(c) - 1, 6)
        for xi, fi in zip(DEC_X, DEC_F):
            self.assertEqual(evaluate(c, xi), fi)


class TestWholeProgram(unittest.TestCase):
    def run_program(self, typed):
        out = io.StringIO()
        with patch("builtins.input", side_effect=typed), redirect_stdout(out):
            main.main()
        return out.getvalue()

    def test_handout_sample(self):
        text = self.run_program(
            ["6", "1 2 3 4 5 6", "1 8 27 64 125 216", "2.5", "5.5", "3", ""])
        for expected in ("NEWTON FORWARD", "NEWTON BACKWARD", "f(2.5) = 15.625",
                         "f(5.5) = 166.375", "tabulated point", "P(x) = x^3"):
            self.assertIn(expected, text)

    def test_bad_input_is_rejected(self):
        text = self.run_program(["0", "6", "1 2 3", "1 2 x 4 5 6", "1 2 4 5 6 7",
                                 "1 2 3 4 5 6", "1 8 27", "1 8 27 64 125 216", "abc", ""])
        for expected in ("between 2 and 50", "Expected 6 values", "Use numbers only",
                         "constant step", "Invalid query"):
            self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
