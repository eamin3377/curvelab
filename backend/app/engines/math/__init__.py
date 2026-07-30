"""Least squares mathematical engine.

Implements Linear, Polynomial and Exponential curve fitting from first
principles: summations -> normal equations -> Gaussian elimination.
"""

from app.engines.math.types import (
    Coefficient,
    EliminationStep,
    ModelComputation,
    NormalEquations,
    SolverResult,
)

__all__ = [
    "Coefficient",
    "EliminationStep",
    "ModelComputation",
    "NormalEquations",
    "SolverResult",
]
