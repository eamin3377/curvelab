"""Construction of normal equation systems A·c = b from summations.

Minimizing S = Σ(yᵢ − ŷᵢ)² with respect to each coefficient yields, for a
degree-m polynomial, the symmetric (m+1)×(m+1) system:

    A[i][j] = Σx^(i+j)        (i, j = 0 .. m)
    b[i]    = Σx^i · y        (i = 0 .. m)

The linear model is the special case m = 1. The exponential model reuses
the m = 1 system on the transformed data (x, ln y).
"""

from __future__ import annotations

from app.engines.math.formatting import latex_number
from app.engines.math.types import NormalEquations


def build_polynomial_system(
    summations: dict[str, float], degree: int, precision: int = 4
) -> NormalEquations:
    """Assemble the normal equations for a degree-m polynomial.

    Args:
        summations: Output of ``summations.polynomial_summations`` (needs
            n, sum_x..sum_x{2m}, sum_y, sum_xy..sum_x{m}y).
        degree: Polynomial degree m.
        precision: Decimals used in the substituted LaTeX rendering.

    Returns:
        NormalEquations with numeric matrix/vector and both LaTeX forms.
    """
    from app.engines.math.summations import cross_key, power_key

    size = degree + 1
    matrix = [
        [summations["n"] if i + j == 0 else summations[power_key(i + j)] for j in range(size)]
        for i in range(size)
    ]
    vector = [
        summations["sum_y"] if i == 0 else summations[cross_key(i)] for i in range(size)
    ]
    return NormalEquations(
        matrix=matrix,
        vector=vector,
        latex_symbolic=_symbolic_latex(degree),
        latex_substituted=_substituted_latex(matrix, vector, size, precision),
    )


def build_exponential_system(
    summations: dict[str, float], precision: int = 4
) -> NormalEquations:
    """Assemble the 2×2 system for the linearized exponential model.

    Works on (x, ln y):

        n·ln a + b·Σx     = Σln y
        ln a·Σx + b·Σx²   = Σx·ln y

    Args:
        summations: Output of ``summations.exponential_summations``.
        precision: Decimals used in the substituted LaTeX rendering.
    """
    n = summations["n"]
    sx = summations["sum_x"]
    sx2 = summations["sum_x2"]
    slny = summations["sum_ln_y"]
    sxlny = summations["sum_x_ln_y"]

    matrix = [[n, sx], [sx, sx2]]
    vector = [slny, sxlny]
    symbolic = (
        "\\begin{cases} n\\ln a + b\\sum x_i = \\sum \\ln y_i \\\\[4pt]"
        " \\ln a\\sum x_i + b\\sum x_i^2 = \\sum x_i \\ln y_i \\end{cases}"
    )
    substituted = (
        "\\begin{cases}"
        f" {latex_number(n, precision)}\\ln a + {latex_number(sx, precision)}\\,b"
        f" = {latex_number(slny, precision)} \\\\[4pt]"
        f" {latex_number(sx, precision)}\\ln a + {latex_number(sx2, precision)}\\,b"
        f" = {latex_number(sxlny, precision)}"
        " \\end{cases}"
    )
    return NormalEquations(
        matrix=matrix,
        vector=vector,
        latex_symbolic=symbolic,
        latex_substituted=substituted,
    )


def _symbolic_latex(degree: int) -> str:
    """Render the generic degree-m normal equations as a LaTeX cases block."""
    lines: list[str] = []
    for i in range(degree + 1):
        terms = []
        for j in range(degree + 1):
            power = i + j
            coeff = "n" if power == 0 else ("\\sum x_i" if power == 1 else f"\\sum x_i^{{{power}}}")
            terms.append(f"{coeff}\\,a_{j}")
        rhs = "\\sum y_i" if i == 0 else ("\\sum x_i y_i" if i == 1 else f"\\sum x_i^{{{i}}} y_i")
        lines.append(" + ".join(terms) + f" = {rhs}")
    return "\\begin{cases} " + " \\\\[4pt] ".join(lines) + " \\end{cases}"


def _substituted_latex(
    matrix: list[list[float]], vector: list[float], size: int, precision: int
) -> str:
    """Render the normal equations with the dataset's numbers substituted."""
    lines: list[str] = []
    for i in range(size):
        terms = [
            f"{latex_number(matrix[i][j], precision)}\\,a_{j}" for j in range(size)
        ]
        lines.append(" + ".join(terms) + f" = {latex_number(vector[i], precision)}")
    return "\\begin{cases} " + " \\\\[4pt] ".join(lines) + " \\end{cases}"
