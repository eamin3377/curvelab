"""Tests for the exponential least squares model."""

from __future__ import annotations

import numpy as np
import pytest

from app.engines.math.models import exponential
from app.engines.math.models.exponential import NonPositiveYError


def test_exact_exponential_recovered() -> None:
    """Data generated from y = 2.5·e^(0.4x) returns a = 2.5, b = 0.4."""
    x = np.linspace(0.0, 5.0, 15)
    y = 2.5 * np.exp(0.4 * x)
    result = exponential.fit(x, y)
    assert result.coefficients[0].value == pytest.approx(2.5, rel=1e-10)
    assert result.coefficients[1].value == pytest.approx(0.4, rel=1e-10)


def test_decay_recovered() -> None:
    """Negative growth rates (decay) are fitted as well."""
    x = np.linspace(0.0, 8.0, 20)
    y = 100.0 * np.exp(-0.3 * x)
    result = exponential.fit(x, y)
    assert result.coefficients[0].value == pytest.approx(100.0, rel=1e-9)
    assert result.coefficients[1].value == pytest.approx(-0.3, rel=1e-9)


def test_zero_y_rejected_with_indices() -> None:
    """y <= 0 raises NonPositiveYError listing the offending rows."""
    x = np.array([0.0, 1.0, 2.0, 3.0])
    y = np.array([1.0, 0.0, 4.0, -2.0])
    with pytest.raises(NonPositiveYError) as excinfo:
        exponential.fit(x, y)
    assert excinfo.value.offending_indices == [1, 3]


def test_predict_matches_manual_evaluation() -> None:
    """predict(x) equals a·e^(bx) computed by hand."""
    x = np.linspace(0.0, 4.0, 9)
    y = 3.0 * np.exp(0.25 * x)
    result = exponential.fit(x, y)
    q = np.array([1.5])
    np.testing.assert_allclose(
        result.predict(q), [3.0 * np.exp(0.25 * 1.5)], rtol=1e-10
    )


def test_linearization_note_present() -> None:
    """The computation documents the ln-linearization it used."""
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([1.0, 2.0, 4.0])
    result = exponential.fit(x, y)
    assert result.notes and "ln y" in result.notes[0]
