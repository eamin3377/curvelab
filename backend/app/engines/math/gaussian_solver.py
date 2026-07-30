"""Gaussian elimination with partial pivoting, implemented from scratch.

This is the academic centerpiece of the solver: instead of delegating to
``numpy.linalg.solve``, the normal equations are solved by hand and every
row operation is recorded so the UI can replay the elimination step by step.

Algorithm
---------
Given A·c = b with A an n×n matrix:

1. Forward elimination — for each column k, swap the row with the largest
   |A[i][k]| (i >= k) into the pivot position (partial pivoting), then
   eliminate the entries below it:  R_i ← R_i − (A[i][k] / A[k][k]) · R_k
2. Back substitution — solve the resulting upper-triangular system from
   the last unknown upwards.

A pivot with |value| < 1e-12 marks the system as singular (collinear or
insufficiently varied data) and raises :class:`SingularMatrixError`.
"""

from __future__ import annotations

from app.engines.math.types import EliminationStep, SolverResult

PIVOT_TOLERANCE = 1e-12
ILL_CONDITION_RATIO = 1e10


class SingularMatrixError(ValueError):
    """Raised when the normal equation system cannot be solved uniquely."""

    def __init__(self, message: str = "The normal equation system is singular") -> None:
        super().__init__(message)
        self.suggestion = (
            "The data may be collinear or insufficiently varied. "
            "Try a lower polynomial degree or add more distinct x values."
        )


def _snapshot(aug: list[list[float]]) -> list[list[float]]:
    """Deep-copy the augmented matrix for a step snapshot."""
    return [row[:] for row in aug]


def solve(matrix: list[list[float]], vector: list[float]) -> SolverResult:
    """Solve A·c = b by Gaussian elimination with partial pivoting.

    Args:
        matrix: Square coefficient matrix A (n×n).
        vector: Right-hand side b (length n).

    Returns:
        SolverResult with the solution, every recorded elimination step and
        an optional conditioning warning.

    Raises:
        SingularMatrixError: If a pivot smaller than 1e-12 is encountered.
        ValueError: If the matrix/vector shapes are inconsistent.
    """
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix) or len(vector) != n:
        raise ValueError("Expected a square n×n matrix and a length-n vector")

    aug = [list(matrix[i]) + [vector[i]] for i in range(n)]
    steps: list[EliminationStep] = []
    max_pivot = 0.0
    min_pivot = float("inf")

    for k in range(n):
        pivot_row = max(range(k, n), key=lambda i: abs(aug[i][k]))
        pivot_value = aug[pivot_row][k]

        if abs(pivot_value) < PIVOT_TOLERANCE:
            raise SingularMatrixError(
                f"Column {k + 1} has no usable pivot (best |value| = {abs(pivot_value):.2e})"
            )

        if pivot_row != k:
            aug[k], aug[pivot_row] = aug[pivot_row], aug[k]
            steps.append(
                EliminationStep(
                    kind="pivot",
                    description=(
                        f"Swap R{k + 1} ↔ R{pivot_row + 1} "
                        f"(largest |pivot| = {pivot_value:.6g})"
                    ),
                    matrix=_snapshot(aug),
                )
            )

        max_pivot = max(max_pivot, abs(pivot_value))
        min_pivot = min(min_pivot, abs(pivot_value))

        for i in range(k + 1, n):
            factor = aug[i][k] / aug[k][k]
            if factor == 0.0:
                continue
            for j in range(k, n + 1):
                aug[i][j] -= factor * aug[k][j]
            aug[i][k] = 0.0
            steps.append(
                EliminationStep(
                    kind="eliminate",
                    description=f"R{i + 1} ← R{i + 1} − ({factor:.6g}) · R{k + 1}",
                    matrix=_snapshot(aug),
                )
            )

    solution = [0.0] * n
    for i in range(n - 1, -1, -1):
        rhs = aug[i][n] - sum(aug[i][j] * solution[j] for j in range(i + 1, n))
        solution[i] = rhs / aug[i][i]
        steps.append(
            EliminationStep(
                kind="back_substitution",
                description=f"c{n - i} = {solution[i]:.6g}  (from row {i + 1})",
                matrix=_snapshot(aug),
            )
        )

    warning = None
    if min_pivot > 0 and max_pivot / min_pivot > ILL_CONDITION_RATIO:
        warning = (
            "The normal equation system is ill-conditioned (pivot ratio "
            f"{max_pivot / min_pivot:.2e}). Coefficients may be sensitive to "
            "rounding; consider a lower degree or rescaling the x values."
        )

    return SolverResult(solution=solution, steps=steps, condition_warning=warning)
