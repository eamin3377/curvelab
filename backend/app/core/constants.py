"""Built-in sample datasets, mirroring the frontend's demo data."""

from __future__ import annotations

SAMPLE_DATASETS: list[dict[str, object]] = [
    {
        "id": "spring",
        "name": "Spring Load Test",
        "description": "Extension of a steel spring under increasing load. Near-perfect linear behavior.",
        "model": "linear",
        "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "y": [2.9, 5.1, 6.8, 9.2, 10.9, 13.1, 14.8, 17.2, 18.9, 21.1, 22.8, 25.2],
    },
    {
        "id": "projectile",
        "name": "Projectile Arc",
        "description": "Height of a projectile sampled over time. Classic quadratic trajectory.",
        "model": "polynomial",
        "x": [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
        "y": [1.2, 5.6, 9.1, 11.4, 12.9, 13.2, 12.6, 10.8, 8.2, 4.5, 0.1],
    },
    {
        "id": "bacteria",
        "name": "Bacterial Growth",
        "description": "Colony population measured hourly. Textbook exponential growth curve.",
        "model": "exponential",
        "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "y": [12.1, 16.4, 22.0, 30.1, 40.4, 54.6, 73.9, 99.2, 134.6, 181.1, 245.0],
    },
]


def list_samples() -> list[dict[str, object]]:
    """Return sample metadata (without the data arrays) for listing."""
    return [
        {k: v for k, v in ds.items() if k not in ("x", "y")}
        | {"n": len(ds["x"])}  # type: ignore[arg-type]
        for ds in SAMPLE_DATASETS
    ]


def get_sample(sample_id: str) -> dict[str, object] | None:
    """Return a full sample dataset by id, or None if unknown."""
    for ds in SAMPLE_DATASETS:
        if ds["id"] == sample_id:
            return ds
    return None
