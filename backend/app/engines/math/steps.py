"""Pedagogical step-by-step solution builder.

Transforms a finished :class:`ModelComputation` plus its metrics into an
ordered list of teaching steps mirroring how the method is written out on
paper:

1. Model formula            — the equation being fitted
2. Summations               — every Σ value computed from the data
3. Normal equations         — symbolic, then with numbers substituted
4. Gaussian elimination     — recorded row operations (condensed)
5. Coefficients             — the solved values
6. Final equation           — coefficients substituted into the model
7. Goodness of fit          — R², RMSE, MAE, MSE with their formulas
"""

from __future__ import annotations

from app.engines.math.formatting import latex_number
from app.engines.math.metrics import FitMetrics
from app.engines.math.types import ModelComputation

_SUMMATION_LATEX = {
    "sum_x": "\\sum x_i",
    "sum_y": "\\sum y_i",
    "sum_xy": "\\sum x_i y_i",
    "sum_x2": "\\sum x_i^2",
    "sum_x3": "\\sum x_i^3",
    "sum_x4": "\\sum x_i^4",
    "sum_x5": "\\sum x_i^5",
    "sum_x6": "\\sum x_i^6",
    "sum_x2y": "\\sum x_i^2 y_i",
    "sum_ln_y": "\\sum \\ln y_i",
    "sum_x_ln_y": "\\sum x_i \\ln y_i",
}

_MODEL_FORMULA = {
    "linear": "y = a + bx",
    "polynomial": "y = a_0 + a_1 x + a_2 x^2 + \\cdots + a_m x^m",
    "exponential": "y = a\\,e^{bx}",
}


def _summation_latex(key: str) -> str:
    """Map a summation dict key (e.g. 'sum_x3') to its LaTeX symbol."""
    if key in _SUMMATION_LATEX:
        return _SUMMATION_LATEX[key]
    if key.startswith("sum_x") and key.endswith("y"):
        power = key[5:-1]
        return f"\\sum x_i^{{{power}}} y_i" if power else "\\sum y_i"
    if key.startswith("sum_x"):
        return f"\\sum x_i^{{{key[5:]}}}"
    return key


def build_steps(
    computation: ModelComputation,
    metrics: FitMetrics,
    precision: int = 4,
) -> list[dict[str, object]]:
    """Build the ordered, human-readable solution steps for a fit.

    Args:
        computation: The fitted model's full computation record.
        metrics: Goodness-of-fit metrics for the fit.
        precision: Decimals used when numbers are rendered into LaTeX.

    Returns:
        A list of step dicts ``{index, title, description, latex}``.
    """
    n = int(computation.summations["n"])
    steps: list[dict[str, object]] = []

    steps.append(
        {
            "index": 1,
            "title": "Choose the model",
            "description": (
                f"We fit the {computation.model} model to all {n} data points by "
                "minimizing the sum of squared residuals S."
            ),
            "latex": (
                f"{_MODEL_FORMULA[computation.model]}, \\qquad "
                f"S = \\sum_{{i=1}}^{{{n}}} (y_i - \\hat{{y}}_i)^2 \\rightarrow \\min"
            ),
        }
    )

    sum_terms = ",\\; ".join(
        f"{_summation_latex(k)} = {latex_number(v, precision)}"
        for k, v in computation.summations.items()
        if k != "n"
    )
    steps.append(
        {
            "index": 2,
            "title": "Compute the summations",
            "description": (
                "Every power sum required by the normal equations is evaluated "
                "directly from the data table."
            ),
            "latex": f"n = {n}, \\quad {sum_terms}",
        }
    )

    steps.append(
        {
            "index": 3,
            "title": "Form the normal equations",
            "description": (
                "Setting each partial derivative ∂S/∂a_k to zero yields the normal "
                "equation system; the second rendering substitutes your data."
            ),
            "latex": (
                f"{computation.normal_equations.latex_symbolic} "
                f"\\;\\Longrightarrow\\; {computation.normal_equations.latex_substituted}"
            ),
        }
    )

    elim = computation.solver_steps
    condensed = "\\;\\;".join(
        step.description.replace("←", "\\leftarrow") for step in elim[:6]
    )
    if len(elim) > 6:
        condensed += f" \\;\\;\\cdots\\;\\; ({len(elim)}\\ \\text{{operations total}})"
    steps.append(
        {
            "index": 4,
            "title": "Solve by Gaussian elimination",
            "description": (
                "Partial pivoting keeps the elimination numerically stable; each "
                "row operation is recorded and can be replayed."
                + (" " + computation.notes[0] if computation.notes else "")
            ),
            "latex": condensed or "A\\,\\mathbf{c} = \\mathbf{b}",
        }
    )

    coeff_terms = ",\\quad ".join(
        f"{c.name} = {latex_number(c.value, precision)}" for c in computation.coefficients
    )
    steps.append(
        {
            "index": 5,
            "title": "Coefficients",
            "description": "Back substitution produces the least squares coefficients.",
            "latex": coeff_terms,
        }
    )

    return steps


def final_steps(
    computation: ModelComputation,
    metrics: FitMetrics,
    equation_latex: str,
    precision: int = 4,
) -> list[dict[str, object]]:
    """Append the final-equation and goodness-of-fit steps to the solution.

    Kept separate from :func:`build_steps` because they need the fully
    formatted equation string, which the service layer assembles.
    """
    return [
        {
            "index": 6,
            "title": "Final equation",
            "description": "Substituting the coefficients into the model gives the regression equation used for prediction and plotting.",
            "latex": equation_latex,
        },
        {
            "index": 7,
            "title": "Goodness of fit",
            "description": (
                "R² measures the share of variance explained by the fit; RMSE, MAE "
                "and MSE summarize the residual sizes in original y units."
            ),
            "latex": (
                f"R^2 = 1 - \\frac{{\\sum (y_i - \\hat{{y}}_i)^2}}{{\\sum (y_i - \\bar{{y}})^2}}"
                f" = {latex_number(metrics.r2, precision)}, \\quad "
                f"\\mathrm{{RMSE}} = \\sqrt{{\\tfrac{{\\mathrm{{SSE}}}}{{n}}}}"
                f" = {latex_number(metrics.rmse, precision)}, \\quad "
                f"\\mathrm{{MAE}} = {latex_number(metrics.mae, precision)}, \\quad "
                f"\\mathrm{{MSE}} = {latex_number(metrics.mse, precision)}"
            ),
        },
    ]
