"""Summation builders for least squares curve fitting.

Every normal equation system is assembled from power sums of the data:

    Σx^k   for k = 0 .. 2m
    Σx^k·y for k = 0 .. m

where m is the polynomial degree (m = 1 for the linear model). All sums use
float64 NumPy arrays with pairwise summation for numerical robustness on
large datasets.
"""

from __future__ import annotations

import numpy as np

from app.engines.math.types import FloatArray


def power_sums(x: FloatArray, max_power: int) -> dict[int, float]:
    """Compute Σx^k for k = 1 .. max_power.

    Args:
        x: Input x values (float64).
        max_power: Highest power to compute. For a degree-m polynomial this
            should be 2m.

    Returns:
        Mapping of exponent k -> Σx^k.
    """
    sums: dict[int, float] = {}
    xk = x.copy()
    for k in range(1, max_power + 1):
        sums[k] = float(np.sum(xk))
        xk = xk * x
    return sums


def cross_sums(x: FloatArray, y: FloatArray, max_power: int) -> dict[int, float]:
    """Compute Σx^k·y for k = 1 .. max_power.

    Args:
        x: Input x values.
        y: Input y values.
        max_power: Highest power of x multiplying y. For a degree-m
            polynomial this should be m.

    Returns:
        Mapping of exponent k -> Σx^k·y.
    """
    sums: dict[int, float] = {}
    xk = x.copy()
    for k in range(1, max_power + 1):
        sums[k] = float(np.sum(xk * y))
        xk = xk * x
    return sums


def linear_summations(x: FloatArray, y: FloatArray) -> dict[str, float]:
    """Summations for the linear model y = a + bx.

    Returns:
        Dict with n, sum_x, sum_y, sum_xy, sum_x2.
    """
    sx = power_sums(x, 2)
    return {
        "n": float(len(x)),
        "sum_x": sx[1],
        "sum_y": float(np.sum(y)),
        "sum_xy": cross_sums(x, y, 1)[1],
        "sum_x2": sx[2],
    }


def polynomial_summations(x: FloatArray, y: FloatArray, degree: int) -> dict[str, float]:
    """Summations for a degree-m polynomial y = a0 + a1·x + ... + am·x^m.

    Computes Σx^k for k = 1..2m and Σx^k·y for k = 1..m.

    Returns:
        Dict with n, sum_x, sum_x2, ..., sum_x2m, sum_y, sum_xy, ..., sum_xmy.
    """
    result: dict[str, float] = {"n": float(len(x))}
    for k, v in power_sums(x, 2 * degree).items():
        result[power_key(k)] = v
    result["sum_y"] = float(np.sum(y))
    for k, v in cross_sums(x, y, degree).items():
        result[cross_key(k)] = v
    return result


def power_key(k: int) -> str:
    """Canonical dict key for Σx^k ('sum_x' for k=1, else 'sum_x{k}')."""
    return "sum_x" if k == 1 else f"sum_x{k}"


def cross_key(k: int) -> str:
    """Canonical dict key for Σx^k·y ('sum_xy' for k=1, else 'sum_x{k}y')."""
    return "sum_xy" if k == 1 else f"sum_x{k}y"


def exponential_summations(x: FloatArray, y: FloatArray) -> dict[str, float]:
    """Summations for the exponential models y = a·e^(bx) and y = a·b^x,
    both linearized on (x, ln y).

    Requires all y > 0 (validated upstream).

    Returns:
        Dict with n, sum_x, sum_x2, sum_ln_y, sum_x_ln_y.
    """
    ln_y = np.log(y)
    sx = power_sums(x, 2)
    return {
        "n": float(len(x)),
        "sum_x": sx[1],
        "sum_x2": sx[2],
        "sum_ln_y": float(np.sum(ln_y)),
        "sum_x_ln_y": float(np.sum(x * ln_y)),
    }


def power_summations(x: FloatArray, y: FloatArray) -> dict[str, float]:
    """Summations for the power model y = a·x^b, linearized as
    ln y = ln a + b·ln x (a straight line in (ln x, ln y)).

    Requires all x > 0 and all y > 0 (validated upstream).

    Returns:
        Dict with n, sum_ln_x, sum_ln_x2, sum_ln_y, sum_ln_x_ln_y.
    """
    ln_x = np.log(x)
    ln_y = np.log(y)
    return {
        "n": float(len(x)),
        "sum_ln_x": float(np.sum(ln_x)),
        "sum_ln_x2": float(np.sum(ln_x * ln_x)),
        "sum_ln_y": float(np.sum(ln_y)),
        "sum_ln_x_ln_y": float(np.sum(ln_x * ln_y)),
    }
