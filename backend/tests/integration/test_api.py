"""End-to-end API tests through FastAPI's TestClient."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

SPRING = {
    "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "y": [2.9, 5.1, 6.8, 9.2, 10.9, 13.1, 14.8, 17.2, 18.9, 21.1, 22.8, 25.2],
}


def test_health(client: TestClient) -> None:
    """Liveness endpoint returns ok."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200 and res.json()["status"] == "ok"


def test_fit_linear_full_contract(client: TestClient) -> None:
    """A linear fit returns the complete documented payload shape."""
    res = client.post("/api/v1/fit", json={**SPRING, "model": "linear"})
    assert res.status_code == 200
    body = res.json()

    assert body["model"] == "linear" and body["n"] == 12
    assert [c["name"] for c in body["coefficients"]] == ["a", "b"]
    assert body["coefficients"][1]["value"] == pytest.approx(2.0063, abs=1e-3)
    assert body["equation"]["plain"].startswith("y =")
    assert body["metrics"]["r2"] > 0.999

    sum_keys = {s["key"] for s in body["summations"]}
    assert {"n", "sum_x", "sum_y", "sum_xy", "sum_x2"} == sum_keys

    assert body["solver"]["method"] == "gaussian_elimination_partial_pivoting"
    assert len(body["solver"]["steps"]) > 0
    assert len(body["steps"]) == 7

    table = body["calculation_table"]
    assert table["columns"][0] == "x" and len(table["rows"]) == 12

    graph = body["graph"]
    assert len(graph["curve_x"]) == 300
    assert graph["confidence_band"]["upper"] is not None


def test_fit_polynomial(client: TestClient) -> None:
    """Projectile sample fits a quadratic with R² ≈ 1."""
    res = client.post(
        "/api/v1/fit",
        json={
            "x": [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
            "y": [1.2, 5.6, 9.1, 11.4, 12.9, 13.2, 12.6, 10.8, 8.2, 4.5, 0.1],
            "model": "polynomial",
            "degree": 2,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert len(body["coefficients"]) == 3
    assert body["metrics"]["r2"] > 0.99


def test_fit_exponential(client: TestClient) -> None:
    """Bacterial growth sample fits y = a·e^(bx) with b > 0."""
    res = client.post(
        "/api/v1/fit",
        json={
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "y": [12.1, 16.4, 22.0, 30.1, 40.4, 54.6, 73.9, 99.2, 134.6, 181.1, 245.0],
            "model": "exponential",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["coefficients"][1]["value"] > 0.0
    assert body["metrics"]["r2"] > 0.999
    sum_keys = {s["key"] for s in body["summations"]}
    assert "sum_ln_y" in sum_keys


def test_fit_exponential_rejects_nonpositive_y(client: TestClient) -> None:
    """y <= 0 returns a 422 problem with the offending row indices."""
    res = client.post(
        "/api/v1/fit",
        json={"x": [0, 1, 2, 3], "y": [1, 0, 4, 9], "model": "exponential"},
    )
    assert res.status_code == 422
    problem = res.json()
    assert problem["type"] == "validation_error"
    assert problem["offending_indices"] == [1]


def test_fit_exponential_abx(client: TestClient) -> None:
    """Growth data fits y = a·b^x with b > 1 and matching ln y summations."""
    res = client.post(
        "/api/v1/fit",
        json={
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "y": [12.1, 16.4, 22.0, 30.1, 40.4, 54.6, 73.9, 99.2, 134.6, 181.1, 245.0],
            "model": "exponential_abx",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["model"] == "exponential_abx"
    assert body["coefficients"][1]["value"] > 1.0
    assert body["metrics"]["r2"] > 0.999
    sum_keys = {s["key"] for s in body["summations"]}
    assert "sum_ln_y" in sum_keys
    table_cols = body["calculation_table"]["columns"]
    assert "ln_y" in table_cols and "x_ln_y" in table_cols


def test_fit_power(client: TestClient) -> None:
    """Power data y = 2·x^1.5 fits with a ≈ 2, b ≈ 1.5 and log-log sums."""
    xs = [1, 2, 3, 4, 5, 6, 7, 8]
    ys = [2.0 * x**1.5 for x in xs]
    res = client.post(
        "/api/v1/fit",
        json={"x": xs, "y": ys, "model": "power"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["model"] == "power"
    a = body["coefficients"][0]["value"]
    b = body["coefficients"][1]["value"]
    assert abs(a - 2.0) < 1e-6 and abs(b - 1.5) < 1e-6
    sum_keys = {s["key"] for s in body["summations"]}
    assert {"sum_ln_x", "sum_ln_x2", "sum_ln_x_ln_y"} <= sum_keys
    table_cols = body["calculation_table"]["columns"]
    assert "ln_x" in table_cols and "ln_x_ln_y" in table_cols


def test_fit_power_rejects_nonpositive_x(client: TestClient) -> None:
    """x <= 0 returns a 422 problem naming the offending rows for power fit."""
    res = client.post(
        "/api/v1/fit",
        json={"x": [0, 1, 2, 3], "y": [1, 2, 4, 9], "model": "power"},
    )
    assert res.status_code == 422
    problem = res.json()
    assert problem["type"] == "validation_error"
    assert problem["field"] == "x"
    assert problem["offending_indices"] == [0]


def test_fit_rejects_mismatched_lengths(client: TestClient) -> None:
    """x and y of different lengths are a schema-level 422."""
    res = client.post(
        "/api/v1/fit", json={"x": [1, 2, 3], "y": [1, 2], "model": "linear"}
    )
    assert res.status_code == 422
    assert res.json()["type"] == "validation_error"


def test_fit_rejects_too_few_points(client: TestClient) -> None:
    """A single point cannot be fitted."""
    res = client.post("/api/v1/fit", json={"x": [1], "y": [2], "model": "linear"})
    assert res.status_code == 422


def test_fit_singular_when_x_constant(client: TestClient) -> None:
    """Constant x produces the dedicated validation message."""
    res = client.post(
        "/api/v1/fit",
        json={"x": [2, 2, 2, 2], "y": [1, 2, 3, 4], "model": "linear"},
    )
    assert res.status_code == 422
    assert "identical" in res.json()["title"]


def test_fit_polynomial_degree_guard(client: TestClient) -> None:
    """degree 3 with only 3 points returns a helpful 422."""
    res = client.post(
        "/api/v1/fit",
        json={"x": [0, 1, 2], "y": [1, 2, 5], "model": "polynomial", "degree": 3},
    )
    assert res.status_code == 422
    assert "at least 4" in res.json()["detail"]


def test_duplicate_removal_reported(client: TestClient) -> None:
    """Duplicate pairs are dropped and counted in the cleaning report."""
    res = client.post(
        "/api/v1/fit",
        json={"x": [1, 2, 2, 3], "y": [2, 4, 4, 6], "model": "linear"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["cleaning_report"]["duplicates_removed"] == 1
    assert body["n"] == 3


def test_predict_endpoint(client: TestClient) -> None:
    """Predictions include ŷ values and extrapolation flags."""
    res = client.post(
        "/api/v1/predict",
        json={**SPRING, "model": "linear", "predict_at": [5.0, 20.0]},
    )
    assert res.status_code == 200
    body = res.json()
    assert len(body["predictions"]) == 2
    assert body["predictions"][0]["extrapolated"] is False
    assert body["predictions"][1]["extrapolated"] is True
    assert body["predictions"][0]["y_hat"] == pytest.approx(10.9, abs=0.5)


def test_compare_endpoint_ranks_models(client: TestClient) -> None:
    """On exponential data, an exponential-family model wins the comparison."""
    res = client.post(
        "/api/v1/fit/compare",
        json={
            "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "y": [12.1, 16.4, 22.0, 30.1, 40.4, 54.6, 73.9, 99.2, 134.6, 181.1, 245.0],
        },
    )
    assert res.status_code == 200
    body = res.json()
    # ae^bx and ab^x are the same curve family, so either may rank first.
    assert body["best_model"] in ("exponential", "exponential_abx")
    assert len(body["results"]) == 5
    assert body["results"][0]["model"] in ("exponential", "exponential_abx")
    # x = 0 makes ln x undefined: the power model reports unavailable.
    power_entry = next(r for r in body["results"] if r["model"] == "power")
    assert power_entry["available"] is False
    assert power_entry["reason"]


def test_compare_marks_exponential_unavailable(client: TestClient) -> None:
    """With y <= 0, the exponential family is reported unavailable, not an error."""
    res = client.post(
        "/api/v1/fit/compare",
        json={"x": [0, 1, 2, 3, 4], "y": [1, 0.5, 0, -0.5, -1]},
    )
    assert res.status_code == 200
    body = res.json()
    for name in ("exponential", "exponential_abx", "power"):
        entry = next(r for r in body["results"] if r["model"] == name)
        assert entry["available"] is False
        assert entry["reason"]


def test_parse_text(client: TestClient) -> None:
    """Pasted CSV/TSV text parses with a cleaning report."""
    res = client.post(
        "/api/v1/data/parse-text",
        json={"text": "1, 2.9\n2, 5.1\n\nbad row\n2, 5.1\n3, 6.8"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["n"] == 3
    assert body["cleaning_report"]["duplicates_removed"] == 1
    assert body["cleaning_report"]["non_numeric_dropped"] == 1


def test_parse_file_json(client: TestClient) -> None:
    """A JSON upload in {x, y} shape is accepted."""
    files = {"file": ("data.json", b'{"x": [0, 1, 2], "y": [1, 3, 5]}', "application/json")}
    res = client.post("/api/v1/data/parse-file", files=files)
    assert res.status_code == 200
    assert res.json()["n"] == 3


def test_parse_file_rejects_excel(client: TestClient) -> None:
    """xlsx uploads get a clear, actionable 400."""
    files = {"file": ("data.xlsx", b"binary", "application/octet-stream")}
    res = client.post("/api/v1/data/parse-file", files=files)
    assert res.status_code == 400
    assert "CSV" in res.json()["detail"]


def test_samples_endpoints(client: TestClient) -> None:
    """Sample listing and detail endpoints return the built-in datasets."""
    listing = client.get("/api/v1/data/samples")
    assert listing.status_code == 200
    ids = {s["id"] for s in listing.json()}
    assert {"spring", "projectile", "bacteria"} <= ids

    detail = client.get("/api/v1/data/samples/spring")
    assert detail.status_code == 200
    assert len(detail.json()["x"]) == 12

    missing = client.get("/api/v1/data/samples/nope")
    assert missing.status_code == 422


def test_request_id_echoed(client: TestClient) -> None:
    """The middleware echoes X-Request-ID and adds a timing header."""
    res = client.get("/api/v1/health", headers={"X-Request-ID": "test-123"})
    assert res.headers["X-Request-ID"] == "test-123"
    assert "X-Response-Time-ms" in res.headers
