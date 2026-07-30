"""Tests for the linear least squares model."""

from __future__ import annotations

import numpy as np
import pytest

from app.engines.math.gaussian_solver import SingularMatrixError
from app.engines.math.models import linear


def test_exact_line_recovered(linear_exact: tuple[np.ndarray, np.ndarray]) -> None:
    """Data on y = 2 + 3x must return a = 2, b = 3 exactly."""
    x, y = linear_exact
    result = linear.fit(x, y)
    assert result.coefficients[0].value == pytest.approx(2.0, abs=1e-10)
    assert result.coefficients[1].value == pytest.approx(3.0, abs=1e-10)


def test_matches_numpy_polyfit(noisy: tuple[np.ndarray, np.ndarray]) -> None:
    """Coefficients agree with numpy.polyfit to >= 10 significant digits."""
    x, y = noisy
    result = linear.fit(x, y)
    ref_b, ref_a = np.polyfit(x, y, 1)
    assert result.coefficients[0].value == pytest.approx(ref_a, rel=1e-10)
    assert result.coefficients[1].value == pytest.approx(ref_b, rel=1e-10)


def test_residuals_sum_to_zero(noisy: tuple[np.ndarray, np.ndarray]) -> None:
    """Least squares with an intercept has Σ residuals = 0 (invariant)."""
    x, y = noisy
    result = linear.fit(x, y)
    residuals = y - result.predict(x)
    assert float(np.sum(residuals)) == pytest.approx(0.0, abs=1e-8)


def test_permutation_invariance(noisy: tuple[np.ndarray, np.ndarray]) -> None:
    """Shuffling the point order must not change the fitted line."""
    x, y = noisy
    rng = np.random.default_rng(3)
    order = rng.permutation(len(x))
    base = linear.fit(x, y)
    shuffled = linear.fit(x[order], y[order])
    assert shuffled.coefficients[0].value == pytest.approx(
        base.coefficients[0].value, rel=1e-12
    )
    assert shuffled.coefficients[1].value == pytest.approx(
        base.coefficients[1].value, rel=1e-12
    )


def test_constant_x_raises_singular() -> None:
    """All-equal x values make the normal equations singular."""
    x = np.full(5, 3.0)
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    with pytest.raises(SingularMatrixError):
        linear.fit(x, y)


def test_two_points_exact() -> None:
    """Two distinct points define the line through them exactly."""
    result = linear.fit(np.array([1.0, 4.0]), np.array([2.0, 11.0]))
    assert result.coefficients[0].value == pytest.approx(-1.0)
    assert result.coefficients[1].value == pytest.approx(3.0)


def test_equation_strings(linear_exact: tuple[np.ndarray, np.ndarray]) -> None:
    """Formatted equations contain the fitted coefficients."""
    x, y = linear_exact
    result = linear.fit(x, y, precision=2)
    assert "3.00x" in _plain_equation(result)


def _plain_equation(result) -> str:
    """Rebuild the plain equation via the shared formatter."""
    from app.engines.math.formatting import build_polynomial_equation

    plain, _ = build_polynomial_equation(
        [c.value for c in result.coefficients], precision=2
    )
    return plain
