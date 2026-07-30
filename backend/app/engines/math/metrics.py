"""Goodness-of-fit metrics for a fitted model.

All quantities are computed in the original y space:

    SSE = Σ(yᵢ − ŷᵢ)²          (sum of squared errors)
    SST = Σ(yᵢ − ȳ)²           (total sum of squares)
    R²  = 1 − SSE / SST        (coefficient of determination)
    R̄²  = 1 − (1 − R²)(n − 1)/(n − p − 1)   (adjusted, p parameters)
    MSE = SSE / n,  RMSE = √MSE,  MAE = Σ|yᵢ − ŷᵢ| / n
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.engines.math.types import FloatArray


@dataclass
class FitMetrics:
    """Container for the standard goodness-of-fit statistics."""

    r2: float
    adj_r2: float | None
    rmse: float
    mse: float
    mae: float
    sse: float
    sst: float
    residuals: list[float]
    y_hat: list[float]


def compute(y: FloatArray, y_hat: FloatArray, n_params: int) -> FitMetrics:
    """Compute goodness-of-fit metrics for predicted values ŷ.

    Args:
        y: Observed y values.
        y_hat: Model predictions at the same x values.
        n_params: Number of fitted parameters p (2 for linear/exponential,
            degree + 1 for polynomial) — used for the adjusted R².

    Returns:
        FitMetrics. ``adj_r2`` is None when n <= p + 1 (undefined).
        R² is 1.0 for a perfect fit of constant data (SST = 0) and 0.0
        when a nonzero-error fit is compared against constant data.
    """
    y = np.asarray(y, dtype=np.float64)
    y_hat = np.asarray(y_hat, dtype=np.float64)
    n = len(y)

    residuals = y - y_hat
    sse = float(np.sum(residuals**2))
    sst = float(np.sum((y - np.mean(y)) ** 2))

    if sst == 0.0:
        r2 = 1.0 if sse < 1e-12 else 0.0
    else:
        r2 = 1.0 - sse / sst

    adj_r2: float | None = None
    if n > n_params + 1:
        adj_r2 = 1.0 - (1.0 - r2) * (n - 1) / (n - n_params - 1)

    mse = sse / n
    return FitMetrics(
        r2=r2,
        adj_r2=adj_r2,
        rmse=float(np.sqrt(mse)),
        mse=mse,
        mae=float(np.mean(np.abs(residuals))),
        sse=sse,
        sst=sst,
        residuals=residuals.tolist(),
        y_hat=y_hat.tolist(),
    )
