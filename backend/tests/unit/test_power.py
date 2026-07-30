"""Tests for the power-law least squares model y = a·x^b."""

from __future__ import annotations

import numpy as np
import pytest

from app.engines.math.models import power
from app.engines.math.models.exponential import NonPositiveYError
from app.engines.math.models.power import NonPositiveXError


def test_exact_power_recovered() -> None:
    """Data generated from y = 2.5·x^1.6 returns a = 2.5, b = 1.6."""
    x = np.linspace(0.5, 6.0, 16)
    y = 2.5 * np.power(x, 1.6)
    result = power.fit(x, y)
    assert result.coefficients[0].value == pytest.approx(2.5, rel=1e-9)
    assert result.coefficients[1].value == pytest.approx(1.6, rel=1e-9)


def test_negative_exponent_recovered() -> None:
    """Decaying power laws y = 10·x^(-0.8) are fitted as well."""
    x = np.linspace(1.0, 10.0, 20)
    y = 10.0 * np.power(x, -0.8)
    result = power.fit(x, y)
    assert result.coefficients[0].value == pytest.approx(10.0, rel=1e-8)
    assert result.coefficients[1].value == pytest.approx(-0.8, rel=1e-8)


def test_zero_x_rejected_with_indices() -> None:
    """x <= 0 raises NonPositiveXError listing the offending rows."""
    x = np.array([0.0, 1.0, -2.0, 3.0])
    y = np.array([1.0, 2.0, 4.0, 8.0])
    with pytest.raises(NonPositiveXError) as excinfo:
        power.fit(x, y)
    assert excinfo.value.offending_indices == [0, 2]


def test_zero_y_rejected_with_indices() -> None:
    """y <= 0 raises NonPositiveYError listing the offending rows."""
    x = np.array([1.0, 2.0, 3.0, 4.0])
    y = np.array([1.0, 0.0, 9.0, 16.0])
    with pytest.raises(NonPositiveYError) as excinfo:
        power.fit(x, y)
    assert excinfo.value.offending_indices == [1]


def test_predict_matches_manual_evaluation() -> None:
    """predict(x) equals a·x^b computed by hand."""
    x = np.linspace(1.0, 5.0, 9)
    y = 4.0 * np.power(x, 0.5)
    result = power.fit(x, y)
    q = np.array([2.25])
    np.testing.assert_allclose(
        result.predict(q), [4.0 * 2.25**0.5], rtol=1e-9
    )


def test_linearization_note_present() -> None:
    """The computation documents the log-log linearization it used."""
    x = np.array([1.0, 2.0, 4.0])
    y = np.array([1.0, 2.0, 4.0])
    result = power.fit(x, y)
    assert result.notes and "ln x" in result.notes[0]
