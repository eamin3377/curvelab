"""Shared fixtures for the test suite."""

from __future__ import annotations

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client() -> TestClient:
    """HTTP test client bound to a fresh application instance."""
    return TestClient(create_app())


@pytest.fixture()
def linear_exact() -> tuple[np.ndarray, np.ndarray]:
    """Dataset lying exactly on y = 2 + 3x."""
    x = np.arange(1.0, 8.0)
    return x, 2.0 + 3.0 * x


@pytest.fixture()
def noisy() -> tuple[np.ndarray, np.ndarray]:
    """A fixed noisy linear dataset (deterministic seed)."""
    rng = np.random.default_rng(42)
    x = np.linspace(0.0, 10.0, 40)
    y = 1.5 + 2.0 * x + rng.normal(0.0, 1.0, size=x.size)
    return x, y
