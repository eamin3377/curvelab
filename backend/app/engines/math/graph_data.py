"""Chart-ready data produced alongside every fit.

The backend owns curve sampling, the residual series, the 95% confidence
band and the full calculation table so the frontend only has to render.

Confidence band (linear model)
------------------------------
95% confidence interval for the mean response at x₀:

    ŷ₀ ± t(0.975, n−2) · s · √( 1/n + (x₀ − x̄)² / Sxx )

with s² = SSE/(n−2) and Sxx = Σx² − n·x̄². For the polynomial and
exponential models the same construction is applied on the design-matrix /
linearized scale and flagged ``approximate``.
"""

from __future__ import annotations

import numpy as np

from app.engines.math.types import FloatArray, ModelComputation, PredictFn

CURVE_SAMPLES = 300
TABLE_ROW_CAP = 1000

# t(0.975, df) for df = 1..30, then the normal limit.
_T_TABLE = [
    12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228,
    2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110, 2.101, 2.093, 2.086,
    2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042,
]


def t_critical_95(df: int) -> float:
    """Return the two-tailed 95% t critical value for the given degrees of freedom."""
    if df < 1:
        return 1.96
    if df <= 30:
        return _T_TABLE[df - 1]
    return 1.96 + 2.36 / df  # smooth approach to the 1.96 limit


def sample_curve(
    x: FloatArray, predict_fn: PredictFn, samples: int = CURVE_SAMPLES
) -> dict[str, list[float]]:
    """Sample the fitted curve on a padded, evenly spaced x grid.

    Args:
        x: Training x values (defines the range; padded by 5% on each side).
        predict_fn: The fitted model's prediction callable.
        samples: Number of grid points (default 300).

    Returns:
        Dict with monotone ``x`` and corresponding ``y`` arrays.
    """
    x_min = float(np.min(x))
    x_max = float(np.max(x))
    pad = (x_max - x_min) * 0.05 or 1.0
    grid = np.linspace(x_min - pad, x_max + pad, samples)
    return {"x": grid.tolist(), "y": predict_fn(grid).tolist()}


def confidence_band(
    x: FloatArray,
    grid_x: list[float],
    curve_y: list[float],
    sse: float,
    n_params: int,
) -> dict[str, object]:
    """Compute the 95% confidence band for the mean response.

    Args:
        x: Training x values.
        grid_x: Grid produced by :func:`sample_curve`.
        curve_y: Fitted values on that grid.
        sse: Sum of squared errors of the fit.
        n_params: Number of fitted parameters (for degrees of freedom).

    Returns:
        Dict with ``upper``, ``lower`` arrays and an ``approximate`` flag
        (True whenever n − p − 1 < 1 or the model is nonlinear; the band is
        omitted as None arrays when it cannot be computed).
    """
    n = len(x)
    df = n - n_params
    grid = np.asarray(grid_x, dtype=np.float64)
    curve = np.asarray(curve_y, dtype=np.float64)

    if df < 1:
        return {"upper": None, "lower": None, "approximate": True}

    x_bar = float(np.mean(x))
    sxx = float(np.sum((x - x_bar) ** 2))
    if sxx == 0.0:
        return {"upper": None, "lower": None, "approximate": True}

    s = float(np.sqrt(sse / df))
    half = (
        t_critical_95(df)
        * s
        * np.sqrt(1.0 / n + ((grid - x_bar) ** 2) / sxx)
    )
    return {
        "upper": (curve + half).tolist(),
        "lower": (curve - half).tolist(),
        "approximate": n_params > 2,
    }


def calculation_table(
    x: FloatArray,
    y: FloatArray,
    computation: ModelComputation,
    y_hat: FloatArray,
    residuals: FloatArray,
) -> dict[str, object]:
    """Build the per-row calculation table shown in the UI and reports.

    Columns adapt to the model:
      - linear:      x, y, x², xy, ŷ, y−ŷ, (y−ŷ)²
      - polynomial:  x, y, x², ..., x^m, xy, ..., x^m·y, ŷ, y−ŷ, (y−ŷ)²
      - exponential: x, y, ln y, x², x·ln y, ŷ, y−ŷ, (y−ŷ)²

    The ``sums`` row aggregates every column; ``truncated`` is True when the
    row cap was applied (the full table is always available via CSV export).
    """
    model = computation.model
    degree = computation.degree

    columns: list[str] = ["x", "y"]
    cols: list[FloatArray] = [x, y]

    if model == "exponential":
        ln_y = np.log(y)
        columns += ["ln_y", "x2", "x_ln_y"]
        cols += [ln_y, x**2, x * ln_y]
    else:
        # The normal equations need powers up to x^m, and the display always
        # includes x² since even the linear model consumes Σx².
        for k in range(2, max(degree, 2) + 1):
            columns.append(f"x{k}")
            cols.append(x**k)
        for k in range(1, degree + 1):
            columns.append(f"x{k}y" if k > 1 else "xy")
            cols.append((x**k) * y)

    columns += ["y_hat", "residual", "residual2"]
    cols += [y_hat, residuals, residuals**2]

    n = len(x)
    truncated = n > TABLE_ROW_CAP
    limit = TABLE_ROW_CAP if truncated else n

    rows = [
        [float(col[i]) for col in cols] for i in range(limit)
    ]
    sums = [float(np.sum(col)) for col in cols]

    return {
        "columns": columns,
        "rows": rows,
        "sums": sums,
        "total_rows": n,
        "truncated": truncated,
    }
