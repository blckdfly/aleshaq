"""Exception hierarchy for quantum networking."""

from __future__ import annotations


class NetworkError(Exception):
    """Base exception for all errors raised in aleshaq.networking."""


class CapacityExceededError(NetworkError, RuntimeError):
    """Raised when a network node exceeds its allocated qubit capacity."""


class ChannelError(NetworkError, ValueError):
    """Raised when channel transmission fails or parameters are invalid."""


class RoutingError(NetworkError, ValueError):
    """Raised when no valid path exists between source and target nodes."""


class LinkNotFoundError(NetworkError, KeyError):
    """Raised when an entanglement link cannot be found between nodes."""
