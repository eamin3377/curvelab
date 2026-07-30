"""Tests for the from-scratch Gaussian elimination solver."""

from __future__ import annotations

import numpy as np
import pytest

from app.engines.math import gaussian_solver
from app.engines.math.gaussian_solver import SingularMatrixError


def test_solves_2x2_system() -> None:
    """Classic normal-equation-sized system with a known solution.

    2a + b = 5 ; a + 3b = 5  →  a = 2, b = 1.
    """
    result = gaussian_solver.solve([[2.0, 1.0], [1.0, 3.0]], [5.0, 5.0])
    assert result.solution[0] == pytest.approx(2.0)
    assert result.solution[1] == pytest.approx(1.0)


def test_partial_pivoting_is_applied() -> None:
    """A zero on the diagonal must trigger a row swap, not a failure."""
    result = gaussian_solver.solve([[0.0, 1.0], [1.0, 1.0]], [1.0, 3.0])
    assert result.solution[0] == pytest.approx(2.0)
    assert result.solution[1] == pytest.approx(1.0)
    assert any(step.kind == "pivot" for step in result.steps)


def test_singular_system_raises() -> None:
    """Linearly dependent rows produce a SingularMatrixError with advice."""
    with pytest.raises(SingularMatrixError) as excinfo:
        gaussian_solver.solve([[1.0, 2.0], [2.0, 4.0]], [3.0, 6.0])
    assert excinfo.value.suggestion


def test_shape_mismatch_rejected() -> None:
    """Non-square input is a programming error, not a singular system."""
    with pytest.raises(ValueError):
        gaussian_solver.solve([[1.0, 2.0]], [1.0])


def test_recorded_steps_reproduce_solution() -> None:
    """The final recorded matrix must be consistent with the solution."""
    matrix = [[3.0, 2.0, -1.0], [2.0, -2.0, 4.0], [-1.0, 0.5, -1.0]]
    vector = [1.0, -2.0, 0.0]
    result = gaussian_solver.solve(matrix, vector)
    a = np.asarray(matrix)
    np.testing.assert_allclose(a @ np.asarray(result.solution), vector, atol=1e-10)
    assert result.steps
    assert result.steps[-1].kind == "back_substitution"


def test_matches_numpy_reference_on_random_system() -> None:
    """The solver agrees with numpy.linalg.solve to ~1e-10."""
    rng = np.random.default_rng(11)
    a = rng.normal(size=(6, 6))
    a = a.T @ a + np.eye(6) * 5.0  # symmetric positive definite
    b = rng.normal(size=6)
    result = gaussian_solver.solve(a.tolist(), b.tolist())
    np.testing.assert_allclose(
        result.solution, np.linalg.solve(a, b), rtol=1e-9, atol=1e-12
    )
