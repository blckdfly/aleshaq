"""Exception hierarchy for quantum protocols."""

from __future__ import annotations


class ProtocolError(Exception):
    """Base exception for all errors raised in aleshaq.protocols."""


class SiftingError(ProtocolError):
    """Raised when key sifting fails or produces an empty key."""


class BackendExecutionError(ProtocolError):
    """Raised when circuit execution on a backend fails or produces invalid data."""


class MissingCredentialsError(BackendExecutionError):
    """Raised when required cloud backend credentials are not set."""


class InsufficientRoundsError(ProtocolError):
    """Raised when too few protocol rounds are provided for statistical validity."""
