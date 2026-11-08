"""Exception hierarchy for quantum error correction."""

from __future__ import annotations


class QECError(Exception):
    """Base exception for all quantum error correction errors."""


class CodeParameterError(QECError, ValueError):
    """Raised when code parameters (n, k, d) or distance are invalid."""


class SyndromeDecodingError(QECError):
    """Raised when syndrome decoding fails or produces an invalid correction."""


class BackendExecutionError(QECError):
    """Raised when circuit execution on a quantum backend fails."""


class MissingCredentialsError(BackendExecutionError):
    """Raised when required cloud backend credentials are not set."""
