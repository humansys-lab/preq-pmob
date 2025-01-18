import json
import logging
import platform
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, FrozenSet, List, Set

import psutil
from tap import Tap

from preq_pmob.equation import Equation
from preq_pmob.equation_group import EquationGroup
from preq_pmob.model_builder import ModelBuilder


class Args(Tap):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_dir: Path = Path("data/cases/generated_cases")
    result_dir: Path = Path("results") / timestamp
    result_dir.mkdir(parents=True, exist_ok=True)
    log_filename = result_dir / "experiment.log"


def setup_logging(log_filename: Path) -> None:
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s - %(message)s",
    )
    logging.info("Logging setup complete.")


def display_environment() -> None:
    logging.info("Python version: %s", sys.version)
    logging.info("Platform: %s %s", platform.system(), platform.release())
    logging.info("Machine: %s", platform.machine())
    logging.info("Processor: %s", platform.processor())
    logging.info(
        "Total RAM: %.2f GB",
        round(psutil.virtual_memory().total / (1024**3), 2),
    )


def load_cases(data_dir: Path) -> List[Dict]:
    cases = []
    for filepath in data_dir.iterdir():
        if filepath.suffix == ".json":
            with filepath.open("r") as f:
                case = json.load(f)
                cases.append(case)
    cases.sort(key=lambda case: case.get("name"))
    return cases


def parse_equations(equations_data: List[Dict]) -> List[Equation]:
    equations = []
    for eq_data in equations_data:
        eq_str = eq_data["equation"]
        variables = eq_data["variables"]
        equation = Equation(eq_str, variables)
        equations.append(equation)
    return equations


def parse_symbols(variable_names: List[str]) -> List[str]:
    return [var for var in variable_names]


def equation_group_to_set(eq_group: EquationGroup) -> FrozenSet[str]:
    return frozenset(eq.equation_str for eq in eq_group.equations)


def extract_equations_from_correct_models(
    correct_models: List[Dict[str, List[str]]]
) -> Set[FrozenSet[str]]:
    return set(frozenset(model["equations"]) for model in correct_models)


def compare_models(
    built_models: List[EquationGroup], expected_set: Set[FrozenSet[str]]
) -> Dict:
    built_set = set(equation_group_to_set(model) for model in built_models)
    success = built_set == expected_set
    n_expected = len(expected_set)
    n_built = len(built_set)
    n_correct = len(built_set & expected_set)

    recall = n_correct / n_expected
    precision = n_correct / n_built if n_built > 0 else 0
    f1 = (
        2 * (recall * precision) / (recall + precision)
        if recall + precision > 0
        else 0
    )

    result = {
        "success": success,
        "n_expected": n_expected,
        "n_built": n_built,
        "n_correct": n_correct,
        "recall": recall,
        "precision": precision,
        "f1": f1,
    }
    return result


def run_case(case: Dict) -> None:
    case_name = case.get("name", "Unnamed Case")
    logging.info(f"Running {case_name}...")

    input_variables = parse_symbols(case["variables"]["input_variables"])
    output_variables = parse_symbols(case["variables"]["output_variables"])
    equations = parse_equations(case["equations"])

    logging.info(
        f"  Number of input variables (input_variables): "
        f"{len(input_variables)}\n"
        f"  Number of output variables (output_variables): "
        f"{len(output_variables)}\n"
        f"  Number of equations: {len(equations)}"
    )

    correct_models = extract_equations_from_correct_models(
        case["correct_models"]
    )

    for method in [
        "exhaustive",
        "gradual",
        "refined_gradual",
    ]:
        logging.info("-" * 50)
        print(f"    Running {method} method...")

        start_time = time.time()
        builder = ModelBuilder(
            equations, input_variables, output_variables, method=method
        )
        models = builder.build_models()
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"  {method} method took {elapsed_time:.2e} seconds")

        result = compare_models(models, correct_models)

        if result["n_expected"] == result["n_correct"]:
            logging.info(f"  {method} method: PASS")
        else:
            logging.info(f"  {method} method: FAIL")
        logging.info(
            f"  Expected: {result['n_expected']}, "
            f"Built: {result['n_built']}, "
            f"Correct: {result['n_correct']}"
        )

        filename = f"{case_name}_{method}.json"
        filepath = args.result_dir / filename
        with open(filepath, "w") as f:
            json.dump(
                {
                    "built_models": [
                        list(equation_group_to_set(model)) for model in models
                    ],
                    "success": result["success"],
                    "n_expected": result["n_expected"],
                    "n_built": result["n_built"],
                    "n_correct": result["n_correct"],
                    "recall": result["recall"],
                    "precision": result["precision"],
                    "f1": result["f1"],
                    "elapsed_time": elapsed_time,
                },
                f,
                indent=2,
            )


def main(args: Args) -> None:
    setup_logging(args.log_filename)
    display_environment()
    cases = load_cases(args.data_dir)
    if not cases:
        logging.info("No cases found in the JSON file.")
        return

    for case in cases:
        logging.info("=" * 50)
        print(f"Running case: {case['name']}")
        run_case(case)


if __name__ == "__main__":
    args = Args().parse_args()
    main(args)
