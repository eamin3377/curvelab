"""Tests for the chart-data engine (curve sampling, band, calc table)."""

from __future__ import annotations

import numpy as np
import pytest

from app.engines.math import graph_data
from app.engines.math.models import linear, polynomial


def test_sample_curve_is_monotone_and_padded() -> None:
    """The sampled grid covers the data range plus a 5% pad, sorted."""
    x = np.array([1.0, 2.0, 5.0, 9.0])
    y = 2.0 * x
    comp = linear.fit(x, y)
    curve = graph_data.sample_curve(x, comp.predict, samples=50)
    grid = curve["x"]
    assert len(grid) == 50
    assert grid[0] < 1.0 and grid[-1] > 9.0
    assert all(grid[i] < grid[i + 1] for i in range(len(grid) - 1))


def test_confidence_band_brackets_curve() -> None:
    """upper >= curve >= lower at every grid point."""
    rng = np.random.default_rng(2)
    x = np.linspace(0.0, 10.0, 30)
    y = 1.0 + x + rng.normal(0.0, 0.5, size=x.size)
    comp = linear.fit(x, y)
    y_hat = comp.predict(x)
    sse = float(np.sum((y - y_hat) ** 2))
    curve = graph_data.sample_curve(x, comp.predict)
    band = graph_data.confidence_band(x, curve["x"], curve["y"], sse, n_params=2)
    upper = np.asarray(band["upper"])
    lower = np.asarray(band["lower"])
    mid = np.asarray(curve["y"])
    assert np.all(upper >= mid) and np.all(mid >= lower)
    assert band["approximate"] is False


def test_confidence_band_polynomial_is_flagged_approximate() -> None:
    """Polynomial bands use the same formula but must be flagged."""
    x = np.linspace(0.0, 5.0, 12)
    y = 1.0 + x**2
    comp = polynomial.fit(x, y, degree=2)
    y_hat = comp.predict(x)
    sse = float(np.sum((y - y_hat) ** 2))
    curve = graph_data.sample_curve(x, comp.predict)
    band = graph_data.confidence_band(x, curve["x"], curve["y"], sse, n_params=3)
    assert band["approximate"] is True


def test_calculation_table_linear_columns_and_sums() -> None:
    """Linear table has x, y, x², xy, ŷ, residual, residual² with a sum row."""
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([2.0, 4.0, 6.0])
    comp = linear.fit(x, y)
    y_hat = comp.predict(x)
    residuals = y - y_hat
    table = graph_data.calculation_table(x, y, comp, y_hat, residuals)
    assert table["columns"] == ["x", "y", "x2", "xy", "y_hat", "residual", "residual2"]
    assert table["truncated"] is False
    sums = table["sums"]
    assert sums[0] == pytest.approx(6.0)   # Σx
    assert sums[2] == pytest.approx(14.0)  # Σx²
    assert sums[3] == pytest.approx(28.0)  # Σxy


def test_calculation_table_exponential_columns() -> None:
    """Exponential table replaces xy with ln y and x·ln y columns."""
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([1.0, 2.0, 4.0])
    comp = linear.fit(x, y)
    comp.model = "exponential"  # simulate the exponential computation shape
    y_hat = comp.predict(x)
    table = graph_data.calculation_table(x, y, comp, y_hat, y - y_hat)
    assert table["columns"][:5] == ["x", "y", "ln_y", "x2", "x_ln_y"]


def test_calculation_table_truncates_at_cap() -> None:
    """Tables beyond the row cap are truncated and marked."""
    n = graph_data.TABLE_ROW_CAP + 10
    x = np.arange(float(n))
    y = 2.0 * x
    comp = linear.fit(x, y)
    table = graph_data.calculation_table(x, y, comp, comp.predict(x), y - comp.predict(x))
    assert table["truncated"] is True
    assert len(table["rows"]) == graph_data.TABLE_ROW_CAP
    assert table["total_rows"] == n


def test_t_critical_lookup() -> None:
    """The t-table returns textbook values and approaches 1.96."""
    assert graph_data.t_critical_95(1) == pytest.approx(12.706)
    assert graph_data.t_critical_95(30) == pytest.approx(2.042)
    assert graph_data.t_critical_95(10_000) == pytest.approx(1.96, abs=1e-3)
