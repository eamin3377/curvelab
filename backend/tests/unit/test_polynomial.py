"""Tests for the polynomial least squares model."""

from __future__ import annotations

import numpy as np
import pytest

from app.engines.math.models import polynomial
from app.engines.math.models.polynomial import _transform_back


def test_exact_quadratic_recovered() -> None:
    """Data on y = 1 + 2x + 3x² returns [1, 2, 3] to machine precision."""
    x = np.linspace(-3.0, 4.0, 12)
    y = 1.0 + 2.0 * x + 3.0 * x**2
    result = polynomial.fit(x, y, degree=2)
    values = [c.value for c in result.coefficients]
    np.testing.assert_allclose(values, [1.0, 2.0, 3.0], atol=1e-8)


def test_exact_cubic_with_scaling_path() -> None:
    """Degree 4+ exercises the centering/scaling branch and transform back.

    Data generated from y = 2 − x + 0.5x² + 0.25x³ + 0.1x⁴ on a wide x
    range forces the scaled solver; coefficients must still be recovered.
    """
    x = np.linspace(-50.0, 50.0, 30)
    y = 2.0 - x + 0.5 * x**2 + 0.25 * x**3 + 0.1 * x**4
    result = polynomial.fit(x, y, degree=4)
    values = [c.value for c in result.coefficients]
    np.testing.assert_allclose(
        values, [2.0, -1.0, 0.5, 0.25, 0.1], rtol=1e-6, atol=1e-6
    )
    assert result.notes, "scaled path should document the transformation"


def test_matches_numpy_polyfit() -> None:
    """Noisy quadratic agrees with numpy.polyfit to >= 10 significant digits."""
    rng = np.random.default_rng(5)
    x = np.linspace(0.0, 6.0, 25)
    y = 0.8 + 1.2 * x - 0.3 * x**2 + rng.normal(0.0, 0.05, size=x.size)
    result = polynomial.fit(x, y, degree=2)
    ref = np.polyfit(x, y, 2)  # highest power first
    ours = [c.value for c in result.coefficients]
    np.testing.assert_allclose(ours, ref[::-1], rtol=1e-9)


def test_minimum_points_exact_fit() -> None:
    """n = degree + 1 points are interpolated exactly."""
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([1.0, 4.0, 9.0])  # y = (x + 1)^2
    result = polynomial.fit(x, y, degree=2)
    np.testing.assert_allclose(result.predict(x), y, atol=1e-8)


def test_too_few_points_rejected() -> None:
    """degree 3 with only 3 points is underdetermined and must fail."""
    with pytest.raises(ValueError, match="at least"):
        polynomial.fit(np.array([0.0, 1.0, 2.0]), np.array([1.0, 2.0, 3.0]), degree=3)


def test_transform_back_matches_direct_expansion() -> None:
    """_transform_back(z-coeffs) must equal expanding Σ c_k ((x−μ)/s)^k."""
    c = [1.5, -2.0, 0.5, 3.0]
    mu, s = 7.0, 4.0
    a = _transform_back(c, mu, s)
    x = np.array([-3.0, 0.0, 11.0])
    z = (x - mu) / s
    via_z = sum(c[k] * z**k for k in range(len(c)))
    via_x = sum(a[j] * x**j for j in range(len(a)))
    np.testing.assert_allclose(via_x, via_z, rtol=1e-10)


def test_prediction_uses_horner() -> None:
    """Predictions equal the direct power-series evaluation."""
    x = np.linspace(0.0, 5.0, 9)
    y = 2.0 + x - x**2
    result = polynomial.fit(x, y, degree=2)
    q = np.array([0.5, 2.5])
    expected = 2.0 + q - q**2
    np.testing.assert_allclose(result.predict(q), expected, atol=1e-8)
