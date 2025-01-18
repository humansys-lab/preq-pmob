from typing import List, Set


class Equation:
    def __init__(self, equation_str: str, variables: List[str]) -> None:
        self.equation_str: str = equation_str
        self.variables: Set[str] = set(var for var in variables)

    def __repr__(self) -> str:
        return f"Equation('{self.equation_str}')"

    def __lt__(self, other: "Equation") -> bool:
        return self.equation_str < other.equation_str
