import unittest
from typing import List, Set

from preq_pmob.equation import Equation
from preq_pmob.equation_group import EquationGroup
from preq_pmob.model_builder import ModelBuilder


class TestModelBuilder(unittest.TestCase):
    def setUp(self) -> None:
        self.equations: List[Equation] = [
            Equation("y = x1 + x2", ["y", "x1", "x2"]),
            Equation("y = x2 ** 2", ["y", "x2"]),
            Equation("x2 = 1", ["x2"]),
            Equation("x1 = 2 * x2", ["x1", "x2"]),
            Equation("z = x1 + y", ["z", "x1", "y"]),
        ]
        self.input_vars: Set[str] = {"x1", "x2"}
        self.output_vars: Set[str] = {"y"}

    def test_build_models_exhaustive(self) -> None:
        builder: ModelBuilder = ModelBuilder(
            self.equations,
            list(self.input_vars),
            list(self.output_vars),
            method="exhaustive",
        )
        models: List[EquationGroup] = builder.build_models()
        self.assertTrue(len(models) > 0)
        for model in models:
            required_vars = self.input_vars.union(self.output_vars)
            self.assertTrue(model.has_required_variables(required_vars))
            self.assertEqual(model.degrees_of_freedom(), len(self.input_vars))

    def test_build_models_gradual(self) -> None:
        builder: ModelBuilder = ModelBuilder(
            self.equations,
            list(self.input_vars),
            list(self.output_vars),
            method="gradual",
        )
        models: List[EquationGroup] = builder.build_models()
        self.assertTrue(len(models) > 0)
        for model in models:
            required_vars = self.input_vars.union(self.output_vars)
            self.assertTrue(model.has_required_variables(required_vars))
            self.assertEqual(model.degrees_of_freedom(), len(self.input_vars))

    def test_build_models_refined_gradual(self) -> None:
        builder: ModelBuilder = ModelBuilder(
            self.equations,
            list(self.input_vars),
            list(self.output_vars),
            method="refined_gradual",
        )
        models: List[EquationGroup] = builder.build_models()
        self.assertTrue(len(models) > 0)
        for model in models:
            required_vars = self.input_vars.union(self.output_vars)
            self.assertTrue(model.has_required_variables(required_vars))
            self.assertEqual(model.degrees_of_freedom(), len(self.input_vars))


if __name__ == "__main__":
    unittest.main()
