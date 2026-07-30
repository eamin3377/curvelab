"""Tests for the summation builders."""

from __future__ import annotations

import numpy as np
import pytest

from app.engines.math import summations


def test_power_sums_hand_computed() -> None:
    """Σx^k for x = [1, 2, 3] checked against hand values."""
    x = np.array([1.0, 2.0, 3.0])
    sums = summations.power_sums(x, 4)
    assert sums[1] == 6.0
    assert sums[2] == 14.0
    assert sums[3] == 36.0
    assert sums[4] == 98.0


def test_cross_sums_hand_computed() -> None:
    """Σx^k·y checked against hand values."""
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([2.0, 4.0, 6.0])
    sums = summations.cross_sums(x, y, 2)
    assert sums[1] == 28.0  # 2 + 8 + 18
    assert sums[2] == 72.0  # 2 + 16 + 54


def test_linear_summations_keys_and_values() -> None:
    """Linear model exposes exactly n, Σx, Σy, Σxy, Σx²."""
    x = np.array([0.0, 1.0, 2.0, 3.0])
    y = np.array([1.0, 3.0, 5.0, 7.0])
    s = summations.linear_summations(x, y)
    assert set(s) == {"n", "sum_x", "sum_y", "sum_xy", "sum_x2"}
    assert s["n"] == 4.0 and s["sum_x"] == 6.0
    assert s["sum_y"] == 16.0 and s["sum_xy"] == 34.0 and s["sum_x2"] == 14.0


def test_polynomial_summations_cover_2m() -> None:
    """A degree-m fit produces power sums up to Σx^(2m) and Σx^m·y."""
    x = np.linspace(0.0, 5.0, 12)
    y = x**2
    s = summations.polynomial_summations(x, y, degree=3)
    for k in range(1, 7):
        key = summations.power_key(k)
        assert key in s
        assert s[key] == pytest.approx(float(np.sum(x**k)))
    for k in range(1, 4):
        key = summations.cross_key(k)
        assert s[key] == pytest.approx(float(np.sum((x**k) * y)))


def test_exponential_summations() -> None:
    """Exponential sums use ln y instead of raw y."""
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([1.0, np.e, np.e**2])
    s = summations.exponential_summations(x, y)
    assert s["sum_ln_y"] == pytest.approx(3.0)  # 0 + 1 + 2
    assert s["sum_x_ln_y"] == pytest.approx(5.0)  # 0 + 1 + 4


def test_large_dataset_matches_numpy() -> None:
    """Vectorized sums agree with direct NumPy on 50k points."""
    rng = np.random.default_rng(7)
    x = rng.uniform(-100.0, 100.0, size=50_000)
    y = rng.uniform(-50.0, 50.0, size=50_000)
    s = summations.linear_summations(x, y)
    assert s["sum_x"] == pytest.approx(float(np.sum(x)), rel=1e-12)
    assert s["sum_xy"] == pytest.approx(float(np.sum(x * y)), rel=1e-12)
