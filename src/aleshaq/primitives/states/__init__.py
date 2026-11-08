"""Quantum state preparation primitives."""

from aleshaq.primitives.states.basis import computational_basis
from aleshaq.primitives.states.bell import bell_state
from aleshaq.primitives.states.ghz import ghz_state
from aleshaq.primitives.states.w_state import w_state

basis_state = computational_basis

__all__ = ["bell_state", "ghz_state", "w_state", "computational_basis", "basis_state"]
