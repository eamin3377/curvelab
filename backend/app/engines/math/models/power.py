"""Power-law least squares: y = a·x^b.

Taking natural logarithms linearizes the model:

    ln y = ln a + b·ln x

a straight line in (ln x, ln y). Solving the standard 2×2 normal equations
on the transformed data and recovering a = e^(ln a) gives the fitted curve.

Requirements: every x must be strictly positive (ln x) AND every y must be
strictly positive (ln y). The service layer validates both before calling
``fit`` so it can report exact row indices.

Note: goodness-of-fit metrics are computed in the *original* y space so
the reported R²/RMSE describe the power curve itself, not the linearized
proxy.
"""

from __future__ import annotations

import numpy as np

from app.engines.math import gaussian_solver, normal_equations, summations
from app.engines.math.formatting import build_power_equation
from app.engines.math.models.exponential import NonPositiveYError
from app.engines.math.types import Coefficient, FloatArray, ModelComputation


class NonPositiveXError(ValueError):
    """Raised when the power model receives x <= 0."""

    def __init__(self, offending_indices: list[int]) -> None:
        self.offending_indices = offending_indices
        super().__init__(
            "Power-law fitting (y = a·x^b) requires strictly positive x values; "
            f"rows {offending_indices} have x <= 0 (ln x is undefined there)."
        )


def fit(x: FloatArray, y: FloatArray, precision: int = 4) -> ModelComputation:
    """Fit y = a·x^b by least squares on the log-log transformed data.

    Args:
        x: 1-D array of strictly positive x values (n >= 2, not all equal).
        y: 1-D array of strictly positive y values.
        precision: Decimals used in the formatted equation.

    Returns:
        ModelComputation with coefficients [a, b]; ``predict`` evaluates in
        the original y space.

    Raises:
        NonPositiveXError: If any x <= 0 (carries the offending row indices).
        NonPositiveYError: If any y <= 0 (carries the offending row indices).
        SingularMatrixError: If all x values are identical.
    """
    bad_x = np.nonzero(x <= 0)[0].tolist()
    if bad_x:
        raise NonPositiveXError(bad_x)
    bad_y = np.nonzero(y <= 0)[0].tolist()
    if bad_y:
        raise NonPositiveYError(bad_y)

    sums = summations.power_summations(x, y)
    system = normal_equations.build_power_system(sums, precision)
    result = gaussian_solver.solve(system.matrix, system.vector)

    ln_a, b = result.solution[0], result.solution[1]
    a = float(np.exp(ln_a))
    build_power_equation(a, b, precision)

    def predict(xq: FloatArray) -> FloatArray:
        """Evaluate the fitted power curve a·x^b at the given x values."""
        return a * np.power(np.asarray(xq, dtype=np.float64), b)

    return ModelComputation(
        model="power",
        degree=1,
        coefficients=[Coefficient("a", a), Coefficient("b", b)],
        predict=predict,
        summations=sums,
        normal_equations=system,
        solver_steps=result.steps,
        condition_warning=result.condition_warning,
        notes=[
            f"Linearized as ln y = ln a + b·ln x with ln a = {ln_a:.6g}; "
            "goodness-of-fit metrics are computed in the original y space."
        ],
    )
