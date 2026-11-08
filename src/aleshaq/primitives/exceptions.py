"""Exception hierarchy for quantum primitives."""

from __future__ import annotations


class PrimitivesError(Exception):
    """Base exception for all quantum primitives errors."""


class InvalidStateParameterError(PrimitivesError, ValueError):
    """Raised when state preparation parameters are out of domain."""


class PhaseEstimationError(PrimitivesError, ValueError):
    """Raised when phase estimation configuration or unitary is invalid."""


class CircuitCompositionError(PrimitivesError, ValueError):
    """Raised when composing quantum circuits with incompatible dimensions."""


class BackendExecutionError(PrimitivesError):
    """Raised when execution on a quantum backend fails."""


class MissingCredentialsError(BackendExecutionError):
    """Raised when cloud quantum backend credentials are missing."""
