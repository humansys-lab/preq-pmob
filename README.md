# PreqPMoB

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-black)](https://github.com/PyCQA/flake8)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Typing: mypy](https://img.shields.io/badge/typing-mypy-blue)](https://github.com/python/mypy)


**PreqPMoB** (Predefined Requirements-based Physical Model Builder) is a Python implementation for constructing physical models by combining equations extracted from scientific literature. The method ensures compliance with four predefined requirements to build accurate, consistent, and solvable models. This repository accompanies the paper:
*"Automated Physical Model Building from Literature Sources: Combining Equations Based on Four Predefined Requirements."*

---

## Features

- Automates the process of constructing physical models from equations.
- Supports handling complex and noisy datasets.
- Ensures models meet the following predefined requirements:
  1. **Required Variables Inclusion**
  2. **Degrees of Freedom Consistency**
  3. **Solvability**
  4. **Unique Constant Equations**
- Provides efficient and flexible algorithms, including the **Refined Gradual Method**.

---

## Getting Started

### Prerequisites

Ensure you have the following installed:
- Python 3.10.15 or higher
- Required Python libraries (listed in `pyproject.toml`)

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/humansys-lab/PreqPMoB.git
    cd PreqPMoB
    ```

2. Install dependencies:
    ```bash
    poetry install
    ```

---

## Usage

## Example Workflow

1. Prepare your input equations, defining input and output variables. The case studies in the paper can be generated using `notebooks/generate_case_study_datasets.ipynb`.
2. Run `experiments/run_experiments.py` to validate the method on the case studies. If you want to run more than one time, you can use the script `experiments/run_experiments.sh`.
3. Analyze and validate the constructed models by running `experiments/analyze_results.py`.

## General Usage

You can also use your own file to perform the model building process.

Note that the input file must be in JSON format and follow the structure below:
```json
{
    "name": "case_study_name",
    "variables": {
        "input_variables": ["input_var1", "input_var2"],
        "output_variables": ["output_var1", "output_var2"]
    },
    "equations": [
        {
            "equation": "equation1",
            "variables": ["var1", "var2"]
        },
        {
            "equation": "equation2",
            "variables": ["var3", "var4"]
        }
    ],
    "correct_models": [
        {
            "equations": [
                "equation1",
                "equation2"
            ],
            "variables": [
                "var1",
                "var2",
                "var3",
                "var4"
            ]
        }
    ]
}
```

If the file includes the correct models, the method will validate the constructed models against them.

---


## Repository Structure

- `data`: Datasets used in the experiments.
- `preq_pmob`: Core implementation of the PreqPMoB method.
- `experiments`: Scripts for running experiments and analyzing results.
- `notebooks`: Jupyter notebooks for generating case studies.
- `results`: Results of the experiments.
- `tests`: Unit tests for the library.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
