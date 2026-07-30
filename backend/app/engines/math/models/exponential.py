"""Exponential least squares: y = a·e^(bx).

The model is nonlinear, but taking natural logarithms linearizes it:

    ln y = ln a + b·x

which is a straight line in (x, ln y). Fitting that line with the standard
linear normal equations and recovering a = e^(ln a) gives the classic
log-linearized exponential fit.

Requirement: every y value must be strictly positive, otherwise ln y is
undefined. The service layer validates this before calling ``fit``.

Note: goodness-of-fit metrics are computed in the *original* y space so
the reported R²/RMSE describe the exponential curve itself, not the
linearized proxy.
"""

from __future__ import annotations

import numpy as np

from app.engines.math import gaussian_solver, normal_equations, summations
from app.engines.math.formatting import build_exponential_equation
from app.engines.math.types import Coefficient, FloatArray, ModelComputation


class NonPositiveYError(ValueError):
    """Raised when the exponential model receives y <= 0."""

    def __init__(self, offending_indices: list[int]) -> None:
        self.offending_indices = offending_indices
        super().__init__(
            "Exponential fitting requires strictly positive y values; "
            f"rows {offending_indices} have y <= 0 (ln y is undefined there)."
        )


def fit(x: FloatArray, y: FloatArray, precision: int = 4) -> ModelComputation:
    """Fit y = a·e^(bx) by least squares on the linearized data.

    Args:
        x: 1-D array of x values (n >= 2, not all equal).
        y: 1-D array of strictly positive y values.
        precision: Decimals used in the formatted equation.

    Returns:
        ModelComputation with coefficients [a, b]; ``predict`` evaluates in
        the original y space.

    Raises:
        NonPositiveYError: If any y <= 0 (carries the offending row indices).
        SingularMatrixError: If all x values are identical.
    """
    bad = np.nonzero(y <= 0)[0].tolist()
    if bad:
        raise NonPositiveYError(bad)

    sums = summations.exponential_summations(x, y)
    system = normal_equations.build_exponential_system(sums, precision)
    result = gaussian_solver.solve(system.matrix, system.vector)

    ln_a, b = result.solution[0], result.solution[1]
    a = float(np.exp(ln_a))
    plain, latex = build_exponential_equation(a, b, precision)

    def predict(xq: FloatArray) -> FloatArray:
        """Evaluate the fitted exponential curve at the given x values."""
        return a * np.exp(b * np.asarray(xq, dtype=np.float64))

    return ModelComputation(
        model="exponential",
        degree=1,
        coefficients=[Coefficient("a", a), Coefficient("b", b)],
        predict=predict,
        summations=sums,
        normal_equations=system,
        solver_steps=result.steps,
        condition_warning=result.condition_warning,
        notes=[
            f"Linearized as ln y = ln a + bx with ln a = {ln_a:.6g}; "
            "goodness-of-fit metrics are computed in the original y space."
        ],
    )
