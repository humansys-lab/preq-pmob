from typing import List, Set

from .equation import Equation


class EquationGroup:
    def __init__(self, equations: List[Equation]) -> None:
        self.equations: List[Equation] = equations
        self.variables: Set[str] = self.get_all_variables()
        self.num_equations: int = len(self.equations)

    def __lt__(self, other: "EquationGroup") -> bool:
        # Compare the number of equations first
        if self.num_equations != other.num_equations:
            return self.num_equations < other.num_equations
        # Compare the equation strings
        return sorted(eq.equation_str for eq in self.equations) < sorted(
            eq.equation_str for eq in other.equations
        )

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.equations, key=lambda x: str(x))))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EquationGroup):
            return NotImplemented
        # Compare the number of equations first
        if self.num_equations != other.num_equations:
            return False
        # Compare the sorted EquationGroup
        self_eqs = sorted(eq.equation_str for eq in self.equations)
        other_eqs = sorted(eq.equation_str for eq in other.equations)
        return self_eqs == other_eqs

    def __repr__(self) -> str:
        eqs = ", ".join(sorted([eq.equation_str for eq in self.equations]))
        return f"EquationGroup([{eqs}])"

    def get_all_variables(self) -> Set[str]:
        vars_set: Set[str] = set()
        for eq in self.equations:
            vars_set.update(eq.variables)
        return vars_set

    def has_required_variables(self, required_variables: Set[str]) -> bool:
        return required_variables.issubset(self.variables)

    def degrees_of_freedom(self) -> int:
        return len(self.variables) - self.num_equations

    def has_correct_dof(self, input_variables: Set[str]) -> bool:
        return self.degrees_of_freedom() == len(input_variables)

    def is_solvable(self, required_variables: Set[str]) -> bool:
        """
        A model is unsolvable if there exists an internal variable
        (neither IV nor OV) that appears in only one equation in the model.
        """
        internal_vars = self.variables - required_variables
        var_counts = {var: 0 for var in internal_vars}

        for eq in self.equations:
            for var in eq.variables:
                if var in var_counts:
                    var_counts[var] += 1

        for count in var_counts.values():
            if count <= 1:
                return False

        return True

    def is_not_overdetermined(self) -> bool:
        """
        Checks if there are multiple equations with the same single variable,
        which are considered constant equations.
        """
        single_var_equations = {}
        for eq in self.equations:
            if len(eq.variables) == 1:
                var = next(iter(eq.variables))
                if var in single_var_equations:
                    return False
                single_var_equations[var] = eq
        return True

    def check_desirability_at_once(
        self, input_vars: Set[str], required_vars: Set[str]
    ) -> bool:
        return (
            self.has_correct_dof(input_vars)
            and self.has_required_variables(required_vars)
            and self.is_solvable(required_vars)
            and self.is_not_overdetermined()
        )
