"""Polynomial least squares: y = a0 + a1·x + a2·x² + ... + am·x^m.

The normal equations form the symmetric (m+1)×(m+1) system

    [ n    Σx    Σx²  ... ] [a0]   [ Σy  ]
    [ Σx   Σx²   Σx³  ... ] [a1] = [ Σxy ]
    [ Σx²  Σx³   Σx⁴  ... ] [a2]   [ Σx²y]
    [ ...                   ] [...]  [ ... ]

Numerical stability
-------------------
Raw power sums grow like x^(2m) and quickly ill-condition the system. When
the degree is 4 or higher, or the x range is large (max|A| > 1e12), the
x values are first mapped to z = (x − μ)/s with μ = mean(x) and
s = max|x − μ|. The system is solved in z-space and the coefficients are
transformed back via the binomial expansion

    z^k = ((x − μ)/s)^k  ⇒  a_j = Σ_{k≥j} c_k · C(k,j) · (−μ)^(k−j) / s^k

so the reported equation is always expressed in the original x.
"""

from __future__ import annotations

import math

import numpy as np

from app.engines.math import gaussian_solver, normal_equations, summations
from app.engines.math.formatting import build_polynomial_equation
from app.engines.math.types import Coefficient, FloatArray, ModelComputation

MAX_MATRIX_ENTRY = 1e12
SCALING_DEGREE_THRESHOLD = 4


def fit(
    x: FloatArray, y: FloatArray, degree: int = 2, precision: int = 4
) -> ModelComputation:
    """Fit a polynomial of the given degree by least squares.

    Args:
        x: 1-D array of x values (n >= degree + 1, not all equal).
        y: 1-D array of y values, same length as x.
        degree: Polynomial degree m (1..6 supported by the UI; any m >= 1
            is accepted here).
        precision: Decimals used in the formatted equation.

    Returns:
        ModelComputation with m+1 coefficients (constant first), the
        prediction callable, summations, normal equations and solver steps.

    Raises:
        ValueError: If degree < 1 or n <= degree.
        SingularMatrixError: If the system has no unique solution.
    """
    if degree < 1:
        raise ValueError("Polynomial degree must be at least 1")
    if len(x) <= degree:
        raise ValueError(
            f"A degree-{degree} fit needs at least {degree + 1} data points "
            f"(got {len(x)})"
        )

    sums = summations.polynomial_summations(x, y, degree)
    system = normal_equations.build_polynomial_system(sums, degree, precision)
    notes: list[str] = []

    largest = max(abs(v) for row in system.matrix for v in row)
    use_scaling = degree >= SCALING_DEGREE_THRESHOLD or largest > MAX_MATRIX_ENTRY

    if use_scaling:
        coefficients, solver_result = _solve_scaled(x, y, degree)
        notes.append(
            "x values were centered and scaled, z = (x − μ)/s, for numerical "
            "stability; the reported coefficients are transformed back to "
            "the original x space."
        )
    else:
        solver_result = gaussian_solver.solve(system.matrix, system.vector)
        coefficients = solver_result.solution

    plain, latex = build_polynomial_equation(coefficients, precision)
    coeffs = coefficients  # local alias for the closure

    def predict(xq: FloatArray) -> FloatArray:
        """Evaluate the fitted polynomial at the given x values."""
        xq = np.asarray(xq, dtype=np.float64)
        out = np.zeros_like(xq)
        for c in reversed(coeffs):
            out = out * xq + c
        return out

    return ModelComputation(
        model="polynomial",
        degree=degree,
        coefficients=[Coefficient(f"a{i}", c) for i, c in enumerate(coefficients)],
        predict=predict,
        summations=sums,
        normal_equations=system,
        solver_steps=solver_result.steps,
        condition_warning=solver_result.condition_warning,
        notes=notes,
    )


def _solve_scaled(
    x: FloatArray, y: FloatArray, degree: int
) -> tuple[list[float], gaussian_solver.SolverResult]:
    """Solve the normal equations in centered/scaled z-space.

    Args:
        x, y: Original data.
        degree: Polynomial degree.

    Returns:
        (coefficients in original x-space, solver result from z-space).
    """
    mu = float(np.mean(x))
    scale = float(np.max(np.abs(x - mu))) or 1.0
    z = (x - mu) / scale

    z_sums = summations.polynomial_summations(z, y, degree)
    z_system = normal_equations.build_polynomial_system(z_sums, degree)
    result = gaussian_solver.solve(z_system.matrix, z_system.vector)
    return _transform_back(result.solution, mu, scale), result


def _transform_back(c: list[float], mu: float, scale: float) -> list[float]:
    """Convert z-space coefficients to x-space via the binomial expansion.

    z = (x − μ)/s and y = Σ c_k·z^k implies

        a_j = Σ_{k=j}^{m} c_k · C(k, j) · (−μ)^(k−j) / s^k

    Args:
        c: Coefficients in z-space, constant first.
        mu: Centering offset used for z.
        scale: Scaling factor used for z.

    Returns:
        Coefficients a_j in the original x-space, constant first.
    """
    m = len(c) - 1
    a = [0.0] * (m + 1)
    for k in range(m + 1):
        for j in range(k + 1):
            a[j] += c[k] * math.comb(k, j) * ((-mu) ** (k - j)) / (scale**k)
    return a
