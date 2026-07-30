"""Domain errors and their translation into problem-JSON responses.

Every client-visible failure is rendered as

    {"type", "title", "detail", "field?", "offending_indices?"}

so the frontend can present precise, actionable messages. Unexpected
exceptions are logged and surfaced as a generic 500 without internals.
"""

from __future__ import annotations

from typing import Any


class DomainError(Exception):
    """Base class for expected, user-facing failures."""

    status_code: int = 422
    error_type: str = "domain_error"

    def __init__(
        self,
        title: str,
        detail: str,
        field: str | None = None,
        offending_indices: list[int] | None = None,
    ) -> None:
        super().__init__(detail)
        self.title = title
        self.detail = detail
        self.field = field
        self.offending_indices = offending_indices

    def to_problem(self) -> dict[str, Any]:
        """Serialize the error to the API's problem-JSON shape."""
        body: dict[str, Any] = {
            "type": self.error_type,
            "title": self.title,
            "detail": self.detail,
        }
        if self.field is not None:
            body["field"] = self.field
        if self.offending_indices:
            body["offending_indices"] = self.offending_indices
        return body


class DatasetValidationError(DomainError):
    """The supplied dataset violates a model or shape requirement."""

    error_type = "validation_error"


class SingularSystemError(DomainError):
    """The normal equations have no unique solution."""

    error_type = "singular_matrix"


class NonPositiveYValuesError(DomainError):
    """Exponential fitting received y <= 0."""

    error_type = "validation_error"


class NonPositiveXValuesError(DomainError):
    """Power-law fitting received x <= 0."""

    error_type = "validation_error"


class FileParseError(DomainError):
    """An uploaded/pasted payload could not be parsed into a dataset."""

    status_code = 400
    error_type = "file_parse_error"
