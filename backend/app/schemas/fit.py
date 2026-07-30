"""Fit request/response schemas, mirroring the documented API contract."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator

from app.schemas.dataset import CleaningReport


class ModelName(str, Enum):
    """Supported curve fitting models.

    The three exponential-family variants all linearize via logarithms:
    exponential (ae^bx) on (x, ln y), exponential_abx (ab^x) on (x, ln y),
    and power (ax^b) on (ln x, ln y).
    """

    linear = "linear"
    polynomial = "polynomial"
    exponential = "exponential"
    exponential_abx = "exponential_abx"
    power = "power"


class FitOptions(BaseModel):
    """Optional toggles for a fit request."""

    remove_duplicates: bool = True
    confidence_band: bool = True


class FitRequest(BaseModel):
    """Request body for POST /api/v1/fit (and the base of other endpoints)."""

    x: list[float] = Field(..., min_length=2, max_length=50_000)
    y: list[float] = Field(..., min_length=2, max_length=50_000)
    model: ModelName = ModelName.linear
    degree: int = Field(default=2, ge=1, le=12)
    precision: int = Field(default=4, ge=2, le=8)
    options: FitOptions = FitOptions()

    @model_validator(mode="after")
    def check_lengths(self) -> "FitRequest":
        """x and y must describe the same number of points."""
        if len(self.x) != len(self.y):
            raise ValueError(
                f"x and y must have equal length (got {len(self.x)} and {len(self.y)})"
            )
        return self


class PredictRequest(FitRequest):
    """Request body for POST /api/v1/predict."""

    predict_at: list[float] = Field(..., min_length=1, max_length=10_000)


class CompareRequest(BaseModel):
    """Request body for POST /api/v1/fit/compare (all three models)."""

    x: list[float] = Field(..., min_length=3, max_length=50_000)
    y: list[float] = Field(..., min_length=3, max_length=50_000)
    degree: int = Field(default=2, ge=2, le=6)
    precision: int = Field(default=4, ge=2, le=8)

    @model_validator(mode="after")
    def check_lengths(self) -> "CompareRequest":
        """x and y must describe the same number of points."""
        if len(self.x) != len(self.y):
            raise ValueError(
                f"x and y must have equal length (got {len(self.x)} and {len(self.y)})"
            )
        return self


class CoefficientOut(BaseModel):
    name: str
    value: float


class SummationOut(BaseModel):
    key: str
    latex: str
    value: float


class NormalEquationsOut(BaseModel):
    matrix: list[list[float]]
    vector: list[float]
    latex_symbolic: str
    latex_substituted: str


class SolverStepOut(BaseModel):
    kind: str
    description: str
    matrix: list[list[float]]


class SolverInfo(BaseModel):
    method: str = "gaussian_elimination_partial_pivoting"
    condition_warning: str | None = None
    steps: list[SolverStepOut]


class EquationOut(BaseModel):
    plain: str
    latex: str


class MetricsOut(BaseModel):
    r2: float
    adj_r2: float | None
    rmse: float
    mse: float
    mae: float
    sse: float
    sst: float


class CalculationTableOut(BaseModel):
    columns: list[str]
    rows: list[list[float]]
    sums: list[float]
    total_rows: int
    truncated: bool


class StepOut(BaseModel):
    index: int
    title: str
    description: str
    latex: str


class ConfidenceBandOut(BaseModel):
    upper: list[float] | None
    lower: list[float] | None
    approximate: bool


class GraphOut(BaseModel):
    scatter_x: list[float]
    scatter_y: list[float]
    curve_x: list[float]
    curve_y: list[float]
    residuals: list[float]
    confidence_band: ConfidenceBandOut | None


class PredictionOut(BaseModel):
    x: float
    y_hat: float
    extrapolated: bool


class FitResult(BaseModel):
    """Complete result of a single fit — the API's central payload."""

    model: ModelName
    degree: int
    n: int
    cleaning_report: CleaningReport
    coefficients: list[CoefficientOut]
    equation: EquationOut
    summations: list[SummationOut]
    normal_equations: NormalEquationsOut
    solver: SolverInfo
    metrics: MetricsOut
    calculation_table: CalculationTableOut
    steps: list[StepOut]
    graph: GraphOut
    notes: list[str]


class PredictResult(BaseModel):
    """Result of POST /api/v1/predict."""

    model: ModelName
    equation: EquationOut
    x_range: tuple[float, float]
    predictions: list[PredictionOut]


class CompareEntry(BaseModel):
    """One model's summary inside a compare response."""

    model: ModelName
    available: bool
    reason: str | None = None
    coefficients: list[CoefficientOut] | None = None
    equation: EquationOut | None = None
    metrics: MetricsOut | None = None


class CompareResult(BaseModel):
    """Result of POST /api/v1/fit/compare, ranked best-first by R²."""

    n: int
    best_model: ModelName | None
    results: list[CompareEntry]
