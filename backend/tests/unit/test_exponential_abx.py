"""Tests for the base-b exponential least squares model y = a·b^x."""

from __future__ import annotations

import numpy as np
import pytest

from app.engines.math.models import exponential_abx
from app.engines.math.models.exponential import NonPositiveYError


def test_exact_abx_recovered() -> None:
    """Data generated from y = 3·(1.8)^x returns a = 3, b = 1.8."""
    x = np.linspace(0.0, 6.0, 16)
    y = 3.0 * np.power(1.8, x)
    result = exponential_abx.fit(x, y)
    assert result.coefficients[0].value == pytest.approx(3.0, rel=1e-9)
    assert result.coefficients[1].value == pytest.approx(1.8, rel=1e-9)


def test_decay_base_below_one_recovered() -> None:
    """A decay curve y = 50·(0.7)^x is fitted as well (0 < b < 1)."""
    x = np.linspace(0.0, 9.0, 20)
    y = 50.0 * np.power(0.7, x)
    result = exponential_abx.fit(x, y)
    assert result.coefficients[0].value == pytest.approx(50.0, rel=1e-8)
    assert result.coefficients[1].value == pytest.approx(0.7, rel=1e-8)


def test_zero_y_rejected_with_indices() -> None:
    """y <= 0 raises NonPositiveYError listing the offending rows."""
    x = np.array([0.0, 1.0, 2.0, 3.0])
    y = np.array([1.0, -4.0, 4.0, 0.0])
    with pytest.raises(NonPositiveYError) as excinfo:
        exponential_abx.fit(x, y)
    assert excinfo.value.offending_indices == [1, 3]


def test_predict_matches_manual_evaluation() -> None:
    """predict(x) equals a·b^x computed by hand."""
    x = np.linspace(0.0, 4.0, 9)
    y = 2.0 * np.power(2.5, x)
    result = exponential_abx.fit(x, y)
    q = np.array([1.5])
    np.testing.assert_allclose(
        result.predict(q), [2.0 * 2.5**1.5], rtol=1e-9
    )


def test_equivalence_with_aebx_form() -> None:
    """y = a·b^x and y = a·e^(bx) describe the same curve family:
    fitting the same data must give b_abx ≈ e^(b_aebx)."""
    from app.engines.math.models import exponential

    x = np.linspace(0.0, 5.0, 15)
    y = 2.5 * np.exp(0.4 * x)
    abx = exponential_abx.fit(x, y)
    aebx = exponential.fit(x, y)
    assert abx.coefficients[0].value == pytest.approx(
        aebx.coefficients[0].value, rel=1e-9
    )
    assert abx.coefficients[1].value == pytest.approx(
        np.exp(aebx.coefficients[1].value), rel=1e-9
    )


def test_linearization_note_present() -> None:
    """The computation documents the ln-linearization it used."""
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([1.0, 2.0, 4.0])
    result = exponential_abx.fit(x, y)
    assert result.notes and "ln b" in result.notes[0]
