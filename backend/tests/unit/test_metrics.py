"""Tests for goodness-of-fit metrics and the predictor."""

from __future__ import annotations

import numpy as np
import pytest

from app.engines.math import metrics
from app.engines.math.predictor import predict


def test_perfect_fit_scores() -> None:
    """SSE = 0 implies R² = 1 and all error metrics vanish."""
    y = np.array([1.0, 2.0, 3.0, 4.0])
    m = metrics.compute(y, y.copy(), n_params=2)
    assert m.r2 == pytest.approx(1.0)
    assert m.rmse == 0.0 and m.mae == 0.0 and m.sse == 0.0
    assert m.adj_r2 is not None


def test_constant_y_guard() -> None:
    """SST = 0 (all y equal): perfect predictions give R² = 1, else R² = 0."""
    y = np.full(5, 3.0)
    assert metrics.compute(y, y.copy(), n_params=1).r2 == 1.0
    off = y.copy()
    off[0] = 4.0
    assert metrics.compute(y, off, n_params=1).r2 == 0.0


def test_hand_computed_values() -> None:
    """Metrics checked against hand computation on a 3-point example.

    y = [1, 2, 3], ŷ = [1, 2, 4] → residuals [0, 0, −1]:
    SSE = 1, SST = 2, R² = 0.5, MSE = 1/3, MAE = 1/3.
    """
    y = np.array([1.0, 2.0, 3.0])
    y_hat = np.array([1.0, 2.0, 4.0])
    m = metrics.compute(y, y_hat, n_params=1)
    assert m.sse == pytest.approx(1.0)
    assert m.sst == pytest.approx(2.0)
    assert m.r2 == pytest.approx(0.5)
    assert m.mse == pytest.approx(1.0 / 3.0)
    assert m.mae == pytest.approx(1.0 / 3.0)
    assert m.rmse == pytest.approx(np.sqrt(1.0 / 3.0))
    assert m.residuals == pytest.approx([0.0, 0.0, -1.0])


def test_adjusted_r2_undefined_when_too_few_points() -> None:
    """adj-R² needs n > p + 1; otherwise it is reported as None."""
    y = np.array([1.0, 2.0, 3.0])
    m = metrics.compute(y, y, n_params=2)  # n = 3, p = 2 → n = p + 1
    assert m.adj_r2 is None


def test_predict_flags_extrapolation() -> None:
    """Points outside [min x, max x] are flagged as extrapolations."""
    x_train = np.array([0.0, 1.0, 2.0, 3.0])
    fn = lambda q: 1.0 + 2.0 * np.asarray(q)  # noqa: E731
    out = predict(fn, x_train, [-1.0, 1.5, 5.0])
    assert [r["extrapolated"] for r in out] == [True, False, True]
    assert out[1]["y_hat"] == pytest.approx(4.0)
