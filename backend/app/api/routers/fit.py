"""Fitting endpoints: /fit, /fit/compare and /predict.

Routers validate input (Pydantic), delegate to the fitting service and
serialize the result — they contain no numerical logic.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.fit import (
    CompareRequest,
    CompareResult,
    FitRequest,
    FitResult,
    PredictRequest,
    PredictResult,
)
from app.services import fitting_service

router = APIRouter(tags=["fitting"])


@router.post(
    "/fit",
    response_model=FitResult,
    summary="Fit one least squares model",
)
def fit(request: FitRequest) -> FitResult:
    """Fit a linear, polynomial or exponential model to the data.

    Returns coefficients, the formatted equation, every summation, the
    normal equations with solver steps, goodness-of-fit metrics, the full
    calculation table, pedagogical steps and chart-ready graph data.
    """
    return fitting_service.run_fit(request)


@router.post(
    "/fit/compare",
    response_model=CompareResult,
    summary="Fit all models and rank by R²",
)
def compare(request: CompareRequest) -> CompareResult:
    """Fit linear, polynomial (given degree) and exponential models on the
    same dataset and rank the available fits, best R² first."""
    return fitting_service.run_compare(request)


@router.post(
    "/predict",
    response_model=PredictResult,
    summary="Evaluate the fitted model at new x values",
)
def predict(request: PredictRequest) -> PredictResult:
    """Recompute the fit from the raw data, then return ŷ for each value in
    ``predict_at`` with an extrapolation flag when outside the training range."""
    return fitting_service.run_predict(request)
