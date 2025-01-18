from itertools import combinations, product
from typing import Dict, List, Set

from .equation import Equation
from .equation_group import EquationGroup


class ModelBuilder:
    def __init__(
        self,
        equations: List[Equation],
        input_vars: List[str],
        output_vars: List[str],
        method: str = "exhaustive",
    ) -> None:
        self.equations: List[Equation] = equations
        self.input_vars: Set[str] = set(input_vars)
        self.output_vars: Set[str] = set(output_vars)
        self.required_vars: Set[str] = self.input_vars.union(self.output_vars)
        self.method: str = method

        if method in [
            "exhaustive",
            "gradual",
            "refined_gradual",
        ]:
            self.var_to_eq_map: Dict[str, Set[Equation]] = (
                self._create_var_to_eq_map()
            )

    def _create_var_to_eq_map(self) -> Dict[str, Set[Equation]]:
        mapping: Dict[str, Set[Equation]] = {}
        for eq in self.equations:
            for var in eq.variables:
                if var not in mapping:
                    mapping[var] = set()
                mapping[var].add(eq)
        return mapping

    def build_models(self) -> List[EquationGroup]:
        if self.method == "exhaustive":
            return self.build_models_exhaustive()
        elif self.method == "gradual":
            return self.build_models_gradual()
        elif self.method == "refined_gradual":
            return self.build_models_refined_gradual()
        else:
            raise ValueError("Invalid method.")

    def build_models_exhaustive(self) -> List[EquationGroup]:
        output_models: List[EquationGroup] = []

        for n in range(1, len(self.equations) + 1):
            for eq_combination in combinations(self.equations, n):
                eq_group = EquationGroup(list(eq_combination))
                if eq_group.check_desirability_at_once(
                    self.input_vars, self.required_vars
                ):
                    output_models.append(eq_group)
        return output_models

    def build_models_gradual(self) -> List[EquationGroup]:
        output_models: List[EquationGroup] = []

        candidate_models, pending_models = (
            self.build_candidate_models_by_product(
                self.required_vars, self.var_to_eq_map
            )
        )
        output_models.extend(candidate_models)
        for pending_model in pending_models:
            redundant_var_to_eq_map = self.identify_redundant_variables(
                pending_model
            )
            if redundant_var_to_eq_map:
                new_candidate_models, _ = (
                    self.build_candidate_models_by_product(
                        set(redundant_var_to_eq_map.keys()),
                        redundant_var_to_eq_map,
                        pending_model,
                    )
                )
                output_models.extend(new_candidate_models)

        return output_models

    def build_models_refined_gradual(self) -> List[EquationGroup]:
        output_models: List[EquationGroup] = []

        # step 1: conducted by product
        candidate_models, pending_models = (
            self.build_candidate_models_by_product(
                self.required_vars, self.var_to_eq_map
            )
        )
        output_models.extend(candidate_models)

        # step 2: conducted by combination
        for pending_model in pending_models:
            all_redundant_var_to_eq_map = self.identify_all_redundant_vars(
                pending_model
            )
            new_candidate_models, _ = (
                self.build_candidate_models_by_combination(
                    set(all_redundant_var_to_eq_map.keys()),
                    all_redundant_var_to_eq_map,
                    pending_model,
                    evaluate_pending_models=False,
                )
            )
            output_models.extend(new_candidate_models)

        return output_models

    def identify_redundant_variables(
        self, pending_model: EquationGroup
    ) -> Dict[str, Set[Equation]]:
        redundant_vars = pending_model.variables - self.required_vars

        # Remove var appearing in only one eq with a single var
        for eq in pending_model.equations:
            if len(eq.variables) == 1:
                redundant_vars -= eq.variables

        redundant_var_to_eq_map = {}
        for var in redundant_vars:
            redundant_var_to_eq_map[var] = self.var_to_eq_map[var] - set(
                pending_model.equations
            )
            if not redundant_var_to_eq_map[var]:
                del redundant_var_to_eq_map[var]

        return redundant_var_to_eq_map

    def identify_all_redundant_vars(
        self, pending_model: EquationGroup
    ) -> Dict[str, Set[Equation]]:
        """
        Identify all redundant variables by iteratively expanding
        'additional_eq_group.'
        Returns a dictionary mapping each redundant variable to the set of
        new candidate equations that contain that variable.
        """

        redundant_vars = pending_model.variables - self.required_vars

        additional_eq_group = EquationGroup([])
        candidate_eqs: Set[Equation] = set()
        while redundant_vars != (
            additional_eq_group.variables - self.required_vars
        ):
            redundant_vars = (
                redundant_vars.union(additional_eq_group.variables)
                - self.required_vars
            )
            for var in redundant_vars:
                candidate_eqs = set(
                    list(additional_eq_group.equations)
                    + list(self.var_to_eq_map.get(var, set()))
                )
                additional_eq_group = EquationGroup(list(candidate_eqs))

        candidate_eqs = set(additional_eq_group.equations) - set(
            pending_model.equations
        )
        all_redundant_var_to_eq_map: Dict[str, Set[Equation]] = {}
        for var in redundant_vars:
            equations = {eq for eq in candidate_eqs if var in eq.variables}
            if equations:
                all_redundant_var_to_eq_map[var] = equations

        return all_redundant_var_to_eq_map

    def build_candidate_models_by_product(
        self,
        variables: Set[str],
        var_to_eq_map: Dict[str, Set[Equation]],
        prev_pending_model: EquationGroup = EquationGroup([]),
    ) -> tuple:
        """
        Generate candidate models that include specified variables
        from all possible combinations of equations by calculating
        products of equations for each variable.

        Args:
            vars (Set[str]): A set of variables that must be included.
            var_to_eq_map (Dict[str, Set[Equation]]): A dictionary that maps
                variables to equations. Equations are picked from dict_v_to_eq.
            prev_pending_model (EquationGroup): A model that includes
                equations that are already selected.

        Returns:
            Set[tuple]: A set of candidate models that include vars.
        """
        candidate_models: Set[EquationGroup] = set()
        pending_models: Set[EquationGroup] = set()

        pending_eq_groups = set(
            tuple(set(eqs))
            for eqs in product(*[var_to_eq_map[v] for v in variables])
        )

        for pending_eq_group in pending_eq_groups:
            eq_group = EquationGroup(
                list(
                    set(prev_pending_model.equations).union(
                        set(pending_eq_group)
                    )
                )
            )

            if eq_group.check_desirability_at_once(
                self.input_vars, self.required_vars
            ):
                candidate_models.add(eq_group)
            elif eq_group.is_not_overdetermined():
                pending_models.add(eq_group)

        return candidate_models, pending_models

    def build_candidate_models_by_combination(
        self,
        variables: Set[str],
        var_to_eq_map: Dict[str, Set[Equation]],
        prev_pending_models: EquationGroup = EquationGroup([]),
        evaluate_pending_models: bool = True,
    ) -> tuple:
        """
        Generate candidate models that include specified variables
        from all possible combinations of equations by calculating
        combinations of equations for each variable.

        Args:
            vars (Set[str]): A set of variables that must be included.
            var_to_eq_map (Dict[str, Set[Equation]]): A dictionary that maps
                variables to equations. Equations are picked from dict_v_to_eq.
            prev_pending_models (EquationGroup): A model that includes
                equations that are already selected.

        Returns:
            Set[tuple]: A set of candidate models that include vars.
        """
        candidate_models: Set[EquationGroup] = set()
        pending_models: Set[EquationGroup] = set()

        equations: Set[Equation] = {
            eq for v in variables for eq in var_to_eq_map.get(v, set())
        }

        for n in range(1, min(len(equations), len(variables)) + 1):
            for eq_combination in combinations(equations, n):
                eq_group = EquationGroup(
                    prev_pending_models.equations + list(eq_combination)
                )
                if eq_group.check_desirability_at_once(
                    self.input_vars, self.required_vars
                ):
                    candidate_models.add(eq_group)
                elif not evaluate_pending_models:
                    continue
                elif eq_group.has_required_variables(variables):
                    pending_models.add(eq_group)

        return candidate_models, pending_models

    def build_models_two_step_combination(self) -> List[EquationGroup]:
        output_models: List[EquationGroup] = []

        # step 1: conducted by combination
        candidate_models, pending_models = (
            self.build_candidate_models_by_combination(
                self.required_vars, self.var_to_eq_map
            )
        )
        output_models.extend(candidate_models)

        # step 2: conducted by combination
        for pending_model in pending_models:
            all_redundant_var_to_eq_map = self.identify_all_redundant_vars(
                pending_model
            )
            new_candidate_models, _ = (
                self.build_candidate_models_by_combination(
                    set(all_redundant_var_to_eq_map.keys()),
                    all_redundant_var_to_eq_map,
                    pending_model,
                    evaluate_pending_models=False,
                )
            )
            output_models.extend(new_candidate_models)

        return output_models

    def build_models_product_recursive_combination(
        self,
    ) -> List[EquationGroup]:
        output_models: List[EquationGroup] = []

        # step 1: conducted by product
        candidate_models, pending_models = (
            self.build_candidate_models_by_product(
                self.required_vars, self.var_to_eq_map
            )
        )
        output_models.extend(candidate_models)

        processed_models: Set[EquationGroup] = set()
        model_queue = list(pending_models)

        while model_queue:
            pending_model = model_queue.pop(0)
            if pending_model in processed_models:
                continue
            processed_models.add(pending_model)
            redundant_var_to_eq_map = self.identify_redundant_variables(
                pending_model
            )
            new_candidate_models, new_pending_models = (
                self.build_candidate_models_by_combination(
                    set(redundant_var_to_eq_map.keys()),
                    redundant_var_to_eq_map,
                    pending_model,
                )
            )
            output_models.extend(new_candidate_models)
            new_models = {
                model
                for model in new_pending_models
                if model not in processed_models
            }
            model_queue.extend(new_models)
        return output_models
