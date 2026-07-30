"""Exponential least squares, base-b form: y = a·b^x.

Taking natural logarithms linearizes the model:

    ln y = ln a + x·ln b

a straight line in (x, ln y) whose unknowns are ln a and ln b. Solving the
standard 2×2 normal equations and recovering a = e^(ln a), b = e^(ln b)
gives the fitted curve.

Requirement: every y value must be strictly positive (ln y is undefined
otherwise). The service layer validates this before calling ``fit``.

Note: goodness-of-fit metrics are computed in the *original* y space so
the reported R²/RMSE describe the exponential curve itself, not the
linearized proxy.
"""

from __future__ import annotations

import numpy as np

from app.engines.math import gaussian_solver, normal_equations, summations
from app.engines.math.formatting import build_abx_equation
from app.engines.math.models.exponential import NonPositiveYError
from app.engines.math.types import Coefficient, FloatArray, ModelComputation


def fit(x: FloatArray, y: FloatArray, precision: int = 4) -> ModelComputation:
    """Fit y = a·b^x by least squares on the linearized data.

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
    system = normal_equations.build_abx_system(sums, precision)
    result = gaussian_solver.solve(system.matrix, system.vector)

    ln_a, ln_b = result.solution[0], result.solution[1]
    a = float(np.exp(ln_a))
    b = float(np.exp(ln_b))
    build_abx_equation(a, b, precision)

    def predict(xq: FloatArray) -> FloatArray:
        """Evaluate the fitted curve a·b^x at the given x values."""
        return a * np.power(b, np.asarray(xq, dtype=np.float64))

    return ModelComputation(
        model="exponential_abx",
        degree=1,
        coefficients=[Coefficient("a", a), Coefficient("b", b)],
        predict=predict,
        summations=sums,
        normal_equations=system,
        solver_steps=result.steps,
        condition_warning=result.condition_warning,
        notes=[
            f"Linearized as ln y = ln a + x·ln b with ln a = {ln_a:.6g}, "
            f"ln b = {ln_b:.6g}; goodness-of-fit metrics are computed in "
            "the original y space."
        ],
    )
