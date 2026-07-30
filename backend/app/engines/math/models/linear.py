"""Linear least squares: y = a + bx.

Minimizing S = Σ(yᵢ − a − b·xᵢ)² gives the normal equations

    n·a  + b·Σx  = Σy
    a·Σx + b·Σx² = Σxy

whose solution has the closed form

    b = (n·Σxy − Σx·Σy) / (n·Σx² − (Σx)²)
    a = ȳ − b·x̄

The module nevertheless routes the 2×2 system through the Gaussian solver
so the recorded elimination steps are available for the step-by-step view.
"""

from __future__ import annotations

import numpy as np

from app.engines.math import gaussian_solver, normal_equations, summations
from app.engines.math.formatting import build_polynomial_equation
from app.engines.math.types import Coefficient, FloatArray, ModelComputation


def fit(x: FloatArray, y: FloatArray, precision: int = 4) -> ModelComputation:
    """Fit y = a + bx to the data by least squares.

    Args:
        x: 1-D array of x values (n >= 2, not all equal).
        y: 1-D array of y values, same length as x.
        precision: Decimals used in the formatted equation.

    Returns:
        ModelComputation with coefficients [a, b], the prediction callable,
        summations, normal equations and recorded solver steps.

    Raises:
        SingularMatrixError: If all x values are identical (Σx² = (Σx)²/n).
    """
    sums = summations.linear_summations(x, y)
    system = normal_equations.build_polynomial_system(sums, degree=1, precision=precision)
    result = gaussian_solver.solve(system.matrix, system.vector)

    a, b = result.solution[0], result.solution[1]
    plain, latex = build_polynomial_equation([a, b], precision)

    def predict(xq: FloatArray) -> FloatArray:
        """Evaluate the fitted line at the given x values."""
        return a + b * np.asarray(xq, dtype=np.float64)

    return ModelComputation(
        model="linear",
        degree=1,
        coefficients=[Coefficient("a", a), Coefficient("b", b)],
        predict=predict,
        summations=sums,
        normal_equations=system,
        solver_steps=result.steps,
        condition_warning=result.condition_warning,
    )
