import unittest
from typing import Set

from preq_pmob.equation import Equation
from preq_pmob.equation_group import EquationGroup


class TestEquationGroup(unittest.TestCase):
    def test_equation_group_initialization(self) -> None:
        eq1: Equation = Equation("y = x1 + x2", ["y", "x1", "x2"])
        eq2: Equation = Equation("x2 = 1", ["x2"])
        group: EquationGroup = EquationGroup([eq1, eq2])
        expected_vars: Set[str] = {
            "y",
            "x1",
            "x2",
        }
        self.assertEqual(group.variables, expected_vars)
        self.assertEqual(group.num_equations, 2)

    def test_has_required_variables(self) -> None:
        eq1: Equation = Equation("y = x1 + x2", ["y", "x1", "x2"])
        eq2: Equation = Equation("x2 = 1", ["x2"])
        group: EquationGroup = EquationGroup([eq1, eq2])
        required_vars: Set[str] = {"y", "x1"}
        self.assertTrue(group.has_required_variables(required_vars))

    def test_degrees_of_freedom(self) -> None:
        eq1: Equation = Equation("y = x1 + x2", ["y", "x1", "x2"])
        eq2: Equation = Equation("x2 = 1", ["x2"])
        group: EquationGroup = EquationGroup([eq1, eq2])
        self.assertEqual(
            group.degrees_of_freedom(), 1
        )  # 3 variables - 2 equations

    def test_has_correct_dof(self) -> None:
        eq1: Equation = Equation("y = x1 + x2", ["y", "x1", "x2"])
        eq2: Equation = Equation("x2 = 1", ["x2"])
        group: EquationGroup = EquationGroup([eq1, eq2])
        input_vars: Set[str] = {"x1"}
        self.assertTrue(group.has_correct_dof(input_vars))

        eq3: Equation = Equation("x1 = 2 * x2", ["x1", "x2"])
        group_full: EquationGroup = EquationGroup([eq1, eq2, eq3])
        self.assertFalse(group_full.has_correct_dof(input_vars))


if __name__ == "__main__":
    unittest.main()
