"""Prediction helpers: evaluate a fitted model at arbitrary x values.

Predictions outside the observed x range are flagged as extrapolations so
the UI can warn the user that the model is being applied beyond the data
it was fitted on.
"""

from __future__ import annotations

import numpy as np

from app.engines.math.types import FloatArray, PredictFn


def predict(
    predict_fn: PredictFn,
    x_train: FloatArray,
    x_query: list[float],
) -> list[dict[str, float | bool]]:
    """Evaluate the model at each requested x and flag extrapolations.

    Args:
        predict_fn: Callable produced by a fitted model.
        x_train: The x values the model was fitted on (defines the
            interpolation range [min, max]).
        x_query: x values to evaluate.

    Returns:
        A list of ``{"x": ..., "y_hat": ..., "extrapolated": ...}`` entries,
        one per query point, in input order.
    """
    x_min = float(np.min(x_train))
    x_max = float(np.max(x_train))
    queries = np.asarray(x_query, dtype=np.float64)
    values = predict_fn(queries)
    return [
        {
            "x": float(xq),
            "y_hat": float(yh),
            "extrapolated": bool(xq < x_min or xq > x_max),
        }
        for xq, yh in zip(queries, values)
    ]
