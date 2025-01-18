import unittest
from typing import List, Set

from preq_pmob.equation import Equation


class TestEquation(unittest.TestCase):
    def test_equation_initialization(self) -> None:
        eq_str: str = "y = x1 + x2"
        variables: List[str] = ["y", "x1", "x2"]
        eq: Equation = Equation(eq_str, variables)
        self.assertEqual(eq.equation_str, eq_str)
        expected_vars: Set[str] = {"x1", "x2", "y"}
        self.assertEqual(eq.variables, expected_vars)

    def test_equation_with_constants(self) -> None:
        eq_str: str = "x2 = 1"
        variables: List[str] = ["x2"]
        eq: Equation = Equation(eq_str, variables)
        self.assertEqual(eq.equation_str, eq_str)
        expected_vars: Set[str] = {"x2"}
        self.assertEqual(eq.variables, expected_vars)


if __name__ == "__main__":
    unittest.main()
