"""Shared datatypes for the mathematical engine.

These plain dataclasses are produced by the model modules and consumed by
the service layer, which maps them onto the public API schemas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]
PredictFn = Callable[[FloatArray], FloatArray]


@dataclass
class Coefficient:
    """A single fitted coefficient, e.g. name='a1', value=1.982."""

    name: str
    value: float


@dataclass
class EliminationStep:
    """One recorded operation of Gaussian elimination.

    ``matrix`` is the augmented matrix snapshot *after* the operation,
    which lets the UI replay the solution row by row.
    """

    kind: str  # 'pivot' | 'eliminate' | 'back_substitution'
    description: str
    matrix: list[list[float]]


@dataclass
class SolverResult:
    """Output of the Gaussian elimination solver."""

    solution: list[float]
    steps: list[EliminationStep]
    condition_warning: str | None = None


@dataclass
class NormalEquations:
    """The normal equation system A·c = b for a model.

    ``latex_symbolic`` renders the system with summation symbols;
    ``latex_substituted`` renders it with the dataset's numbers filled in.
    """

    matrix: list[list[float]]
    vector: list[float]
    latex_symbolic: str
    latex_substituted: str


@dataclass
class ModelComputation:
    """Everything a fitted model produces, before metrics and packaging."""

    model: str  # 'linear' | 'polynomial' | 'exponential'
    degree: int
    coefficients: list[Coefficient]
    predict: PredictFn
    summations: dict[str, float]
    normal_equations: NormalEquations
    solver_steps: list[EliminationStep] = field(default_factory=list)
    condition_warning: str | None = None
    notes: list[str] = field(default_factory=list)
