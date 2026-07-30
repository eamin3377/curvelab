"""Fitting orchestration: clean → validate → fit → metrics → package.

This module is the single entry point the API layer calls. It maps engine
outputs onto the public schemas and converts engine exceptions into the
domain errors the error middleware renders as problem-JSON.
"""

from __future__ import annotations

import numpy as np

from app.core.errors import (
    DatasetValidationError,
    NonPositiveXValuesError,
    NonPositiveYValuesError,
    SingularSystemError,
)
from app.engines.math import graph_data, metrics, steps as steps_builder
from app.engines.math.gaussian_solver import SingularMatrixError
from app.engines.math.models import exponential, exponential_abx, linear, polynomial, power
from app.engines.math.models.exponential import NonPositiveYError
from app.engines.math.models.power import NonPositiveXError
from app.engines.math.predictor import predict as predict_values
from app.engines.math.types import FloatArray, ModelComputation
from app.schemas.dataset import CleaningReport
from app.schemas.fit import (
    CalculationTableOut,
    CoefficientOut,
    CompareEntry,
    CompareResult,
    ConfidenceBandOut,
    EquationOut,
    FitRequest,
    FitResult,
    GraphOut,
    MetricsOut,
    ModelName,
    NormalEquationsOut,
    PredictResult,
    SolverInfo,
    SolverStepOut,
    StepOut,
    SummationOut,
)

_SUMMATION_ORDER = {
    "n": 0,
    "sum_x": 1,
    "sum_y": 2,
    "sum_ln_x": 3,
    "sum_ln_y": 4,
    "sum_xy": 5,
    "sum_x_ln_y": 6,
    "sum_ln_x2": 7,
    "sum_ln_x_ln_y": 8,
}

_MODEL_LABELS = {
    ModelName.linear: "y = a + bx",
    ModelName.polynomial: "y = a₀ + a₁x + a₂x² + ⋯ + aₘxᵐ",
    ModelName.exponential: "y = a·e^(bx)",
    ModelName.exponential_abx: "y = a·b^x",
    ModelName.power: "y = a·x^b",
}


def run_fit(request: FitRequest) -> FitResult:
    """Execute a complete least squares fit and package the result.

    Pipeline: clean the raw arrays, validate model-specific constraints,
    dispatch to the matching model module, compute metrics in original
    y space, then build the calculation table, chart data, pedagogical
    steps and the final FitResult payload.

    Raises:
        DatasetValidationError, NonPositiveYValuesError, SingularSystemError:
            Converted to problem-JSON by the API layer.
    """
    xa, ya, report = _clean(request)
    computation = _dispatch(xa, ya, request)
    return _package(request, xa, ya, computation, report)


def run_compare(request) -> CompareResult:
    """Fit every model on the same data and rank them by R².

    Models whose constraints the data violates (e.g. y <= 0 for the
    exponential family, x <= 0 for the power model) are marked unavailable
    with the reason instead of failing the whole comparison.
    """
    fit_request = FitRequest(
        x=request.x, y=request.y, precision=request.precision
    )
    xa, ya, _ = _clean(fit_request)

    entries: list[CompareEntry] = []
    for model in (
        ModelName.linear,
        ModelName.polynomial,
        ModelName.exponential,
        ModelName.exponential_abx,
        ModelName.power,
    ):
        try:
            req = FitRequest(
                x=request.x,
                y=request.y,
                model=model,
                degree=request.degree if model == ModelName.polynomial else 1,
                precision=request.precision,
            )
            result = run_fit(req)
            entries.append(
                CompareEntry(
                    model=model,
                    available=True,
                    coefficients=result.coefficients,
                    equation=result.equation,
                    metrics=result.metrics,
                )
            )
        except (
            DatasetValidationError,
            NonPositiveYValuesError,
            NonPositiveXValuesError,
            SingularSystemError,
        ) as exc:
            entries.append(
                CompareEntry(model=model, available=False, reason=exc.detail)
            )

    ranked = sorted(
        (e for e in entries if e.available and e.metrics is not None),
        key=lambda e: e.metrics.r2,  # type: ignore[union-attr]
        reverse=True,
    )
    entries.sort(key=lambda e: (not e.available, ranked.index(e) if e in ranked else 99))
    return CompareResult(
        n=len(xa),
        best_model=ranked[0].model if ranked else None,
        results=entries,
    )


def run_predict(request) -> PredictResult:
    """Fit the requested model, then evaluate it at ``predict_at`` points."""
    fit_req = FitRequest(
        x=request.x,
        y=request.y,
        model=request.model,
        degree=request.degree,
        precision=request.precision,
        options=request.options,
    )
    xa, ya, _ = _clean(fit_req)
    computation = _dispatch(xa, ya, fit_req)

    predictions = predict_values(computation.predict, xa, list(request.predict_at))
    if fit_req.model in (
        ModelName.exponential,
        ModelName.exponential_abx,
        ModelName.power,
    ):
        from app.engines.math.formatting import (
            build_abx_equation,
            build_exponential_equation,
            build_power_equation,
        )

        a = computation.coefficients[0].value
        b = computation.coefficients[1].value
        builder = {
            ModelName.exponential: build_exponential_equation,
            ModelName.exponential_abx: build_abx_equation,
            ModelName.power: build_power_equation,
        }[fit_req.model]
        plain, latex = builder(a, b, request.precision)
    else:
        from app.engines.math.formatting import build_polynomial_equation

        plain, latex = build_polynomial_equation(
            [c.value for c in computation.coefficients], request.precision
        )

    return PredictResult(
        model=fit_req.model,
        equation=EquationOut(plain=plain, latex=latex),
        x_range=(float(np.min(xa)), float(np.max(xa))),
        predictions=predictions,  # type: ignore[arg-type]
    )


def _clean(request: FitRequest) -> tuple[FloatArray, FloatArray, CleaningReport]:
    """Run the cleaning pipeline on a fit request's raw arrays."""
    from app.services.data_service import clean_arrays, validate_for_model

    xa, ya, report = clean_arrays(
        request.x, request.y, request.options.remove_duplicates
    )
    validate_for_model(xa, request.model.value, request.degree)
    return xa, ya, report


def _dispatch(
    xa: FloatArray, ya: FloatArray, request: FitRequest
) -> ModelComputation:
    """Call the model module matching the request and translate errors."""
    try:
        if request.model == ModelName.linear:
            return linear.fit(xa, ya, request.precision)
        if request.model == ModelName.polynomial:
            return polynomial.fit(xa, ya, request.degree, request.precision)
        if request.model == ModelName.exponential_abx:
            return exponential_abx.fit(xa, ya, request.precision)
        if request.model == ModelName.power:
            return power.fit(xa, ya, request.precision)
        return exponential.fit(xa, ya, request.precision)
    except NonPositiveXError as exc:
        raise NonPositiveXValuesError(
            title="Power-law fit requires positive x values",
            detail=str(exc),
            field="x",
            offending_indices=exc.offending_indices,
        ) from exc
    except NonPositiveYError as exc:
        raise NonPositiveYValuesError(
            title="This model requires positive y values",
            detail=str(exc),
            field="y",
            offending_indices=exc.offending_indices,
        ) from exc
    except SingularMatrixError as exc:
        raise SingularSystemError(
            title="The normal equations are singular",
            detail=f"{exc} {exc.suggestion}",
        ) from exc
    except ValueError as exc:
        raise DatasetValidationError(
            title="Invalid dataset for this model", detail=str(exc)
        ) from exc


def _package(
    request: FitRequest,
    xa: FloatArray,
    ya: FloatArray,
    computation: ModelComputation,
    report: CleaningReport,
) -> FitResult:
    """Assemble the public FitResult from a finished computation."""
    y_hat = computation.predict(xa)
    n_params = len(computation.coefficients)
    m = metrics.compute(ya, y_hat, n_params)

    table = graph_data.calculation_table(xa, ya, computation, y_hat, np.asarray(m.residuals))
    curve = graph_data.sample_curve(xa, computation.predict)
    band = (
        graph_data.confidence_band(xa, curve["x"], curve["y"], m.sse, n_params)
        if request.options.confidence_band
        else None
    )

    equation_plain, equation_latex = _equation_strings(computation, request.precision)

    steps = steps_builder.build_steps(computation, m, request.precision)
    steps.extend(
        steps_builder.final_steps(computation, m, equation_latex, request.precision)
    )

    summations_out = [
        SummationOut(
            key=key,
            latex=_summation_label(key),
            value=value,
        )
        for key, value in sorted(
            computation.summations.items(),
            key=lambda kv: (_SUMMATION_ORDER.get(kv[0], 10), kv[0]),
        )
    ]

    return FitResult(
        model=request.model,
        degree=computation.degree,
        n=len(xa),
        cleaning_report=report,
        coefficients=[CoefficientOut(name=c.name, value=c.value) for c in computation.coefficients],
        equation=EquationOut(plain=equation_plain, latex=equation_latex),
        summations=summations_out,
        normal_equations=NormalEquationsOut(
            matrix=computation.normal_equations.matrix,
            vector=computation.normal_equations.vector,
            latex_symbolic=computation.normal_equations.latex_symbolic,
            latex_substituted=computation.normal_equations.latex_substituted,
        ),
        solver=SolverInfo(
            condition_warning=computation.condition_warning,
            steps=[
                SolverStepOut(kind=s.kind, description=s.description, matrix=s.matrix)
                for s in computation.solver_steps
            ],
        ),
        metrics=MetricsOut(
            r2=m.r2,
            adj_r2=m.adj_r2,
            rmse=m.rmse,
            mse=m.mse,
            mae=m.mae,
            sse=m.sse,
            sst=m.sst,
        ),
        calculation_table=CalculationTableOut(
            columns=table["columns"],  # type: ignore[arg-type]
            rows=table["rows"],  # type: ignore[arg-type]
            sums=table["sums"],  # type: ignore[arg-type]
            total_rows=table["total_rows"],  # type: ignore[arg-type]
            truncated=table["truncated"],  # type: ignore[arg-type]
        ),
        steps=[StepOut(**s) for s in steps],
        graph=GraphOut(
            scatter_x=xa.tolist(),
            scatter_y=ya.tolist(),
            curve_x=curve["x"],
            curve_y=curve["y"],
            residuals=m.residuals,
            confidence_band=ConfidenceBandOut(**band) if band else None,
        ),
        notes=computation.notes,
    )


def _equation_strings(computation: ModelComputation, precision: int) -> tuple[str, str]:
    """Rebuild the plain/LaTeX equation strings from fitted coefficients."""
    from app.engines.math.formatting import (
        build_abx_equation,
        build_exponential_equation,
        build_polynomial_equation,
        build_power_equation,
    )

    values = [c.value for c in computation.coefficients]
    if computation.model == "exponential":
        return build_exponential_equation(values[0], values[1], precision)
    if computation.model == "exponential_abx":
        return build_abx_equation(values[0], values[1], precision)
    if computation.model == "power":
        return build_power_equation(values[0], values[1], precision)
    return build_polynomial_equation(values, precision)


def _summation_label(key: str) -> str:
    """LaTeX symbol for a summation key (delegates to steps' table)."""
    from app.engines.math.steps import _summation_latex

    return _summation_latex(key)
