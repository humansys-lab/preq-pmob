import csv
import json
import re
import warnings
from pathlib import Path

import numpy as np


def extract_case_data(log_content: str) -> dict:
    cases: dict = {}
    sections = log_content.split(
        "INFO - =================================================="
    )
    for section in sections:
        if not section.strip():
            continue
        case_name_match = re.search(r"Running (.+?)\.\.\.", section)
        if not case_name_match:
            continue
        case_name = case_name_match.group(1).strip()

        conditions = {}
        match = re.search(
            r"Number of input variables \(input_variables\): (\d+)", section
        )
        if match:
            conditions["input_vars"] = int(match.group(1))

        match = re.search(
            r"Number of output variables \(output_variables\): (\d+)", section
        )
        if match:
            conditions["output_vars"] = int(match.group(1))

        match = re.search(r"Number of equations: (\d+)", section)
        if match:
            conditions["num_equations"] = int(match.group(1))

        match = re.search(r"Expected: (\d+)", section)
        if match:
            conditions["num_expected_models"] = int(match.group(1))

        methods = {}
        method_sections = section.split(
            "--------------------------------------------------"
        )
        for method_section in method_sections:
            method_name_match = re.search(r"(.+?) method", method_section)
            if method_name_match:
                method_name = method_name_match.group(1).split(" ")[-1]
            else:
                continue

            time_seconds, result, built, correct = 0.0, "N/A", 0, 0

            match = re.search(r"took (.+?) seconds", method_section)
            if match:
                time_seconds = float(match.group(1))

            match = re.search(
                f"{method_name} method:" + r"(.+?)\n",
                method_section,
                re.DOTALL,
            )
            if match:
                result = match.group(1).strip()
            match = re.search(
                r"Expected: (\d+), Built: (\d+), Correct: (\d+)",
                method_section,
            )
            if match:
                built = int(match.group(2))
                correct = int(match.group(3))

            methods[method_name] = {
                "time_seconds": time_seconds,
                "result": result,
                "built": built,
                "correct": correct,
            }
        cases[case_name] = {"conditions": conditions, "methods": methods}

    return cases


def calculate_average_times(folder_paths: list) -> dict:
    all_cases = {}

    for folder_path in folder_paths:
        log_path = Path(folder_path) / "experiment.log"
        if not log_path.exists():
            print(f"cannot find log file: {log_path}")
            continue

        with log_path.open("r") as file:
            case_data = extract_case_data(file.read())

        for case_name, case_info in case_data.items():
            if case_name not in all_cases:
                all_cases[case_name] = {
                    "conditions": case_info["conditions"],
                    "methods": {},
                }
            for method_name, method_data in case_info["methods"].items():
                if method_name not in all_cases[case_name]["methods"]:
                    all_cases[case_name]["methods"][method_name] = {
                        "result": [],
                        "time_seconds": [],
                        "built": [],
                        "correct": [],
                    }
                all_cases[case_name]["methods"][method_name]["result"].append(
                    method_data["result"]
                )
                all_cases[case_name]["methods"][method_name][
                    "time_seconds"
                ].append(method_data["time_seconds"])
                all_cases[case_name]["methods"][method_name]["built"].append(
                    method_data["built"]
                )
                all_cases[case_name]["methods"][method_name]["correct"].append(
                    method_data["correct"]
                )

    averages = {}
    for case_name, case_info in all_cases.items():
        averages[case_name] = {
            "conditions": case_info["conditions"],
            "methods": {},
        }
        for method_name, method_data in case_info["methods"].items():
            if len(set(method_data["result"])) != 1:
                warnings.warn(
                    "method_data['result'] has more than one value: "
                    + f"{method_data['result']}"
                )
            if len(set(method_data["built"])) != 1:
                warnings.warn(
                    "method_data['built'] has more than one value: "
                    + f"{method_data['built']}"
                )
            if len(set(method_data["correct"])) != 1:
                warnings.warn(
                    "method_data['correct'] has more than one value: "
                    + f"{method_data['correct']}"
                )
            averages[case_name]["methods"][method_name] = {
                "mean_time": np.mean(method_data["time_seconds"]),
                "std_dev_time": np.std(method_data["time_seconds"]),
                "result": method_data["result"][0],
                "count": len(method_data["time_seconds"]),
                "built": method_data["built"][0],
                "correct": method_data["correct"][0],
            }
    return averages


results_dir = Path("./results")
experiment_dir = results_dir / "Experiment_on_MBA_m3"
folder_paths = [
    str(folder) for folder in experiment_dir.iterdir() if folder.is_dir()
]

averages = calculate_average_times(folder_paths)

output_file = experiment_dir / "averages.json"
with output_file.open("w") as json_file:
    json.dump(averages, json_file, indent=2, ensure_ascii=False)

print(f"Results saved to {output_file}")


def save_to_csv(
    averages: dict, output_csv_file: Path, precision: int = 5
) -> None:
    column_names = [
        "case_name",
        "input_vars",
        "output_vars",
        "n_equations",
        "n_expected_models",
        "method_name",
        "result",
        "n_built_models",
        "n_correct_models",
        "mean_time",
        "std_time",
    ]

    float_format = f".{precision}e"
    with output_csv_file.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_names)
        writer.writeheader()

        for case_name, case_info in averages.items():
            conditions = case_info["conditions"]
            for method_name, method_data in case_info["methods"].items():
                writer.writerow(
                    {
                        "case_name": case_name,
                        "input_vars": conditions["input_vars"],
                        "output_vars": conditions["output_vars"],
                        "n_equations": conditions["num_equations"],
                        "n_expected_models": conditions["num_expected_models"],
                        "method_name": method_name,
                        "result": method_data["result"],
                        "n_built_models": method_data["built"],
                        "n_correct_models": method_data["correct"],
                        "mean_time": format(
                            method_data["mean_time"], float_format
                        ),
                        "std_time": format(
                            method_data["std_dev_time"], float_format
                        ),
                    }
                )

    print(f"CSV file saved to {output_csv_file}")


# 保存先のCSVファイルを指定
output_csv_file = experiment_dir / "averages.csv"
save_to_csv(averages, output_csv_file)
