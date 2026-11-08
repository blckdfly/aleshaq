"""Controlled phase rotation primitives."""

from __future__ import annotations

import numpy as np
from qiskit.circuit import QuantumCircuit


def controlled_phase_rotation(
    k: int, *, label: str | None = None
) -> QuantumCircuit:
    """Construct a 2-qubit controlled phase rotation CR_k.

    Applies the unitary diag(1, 1, 1, e^{2πi/2^k}) — the control qubit
    is qubit 0 and the target is qubit 1.

    This is the elementary building block of the QFT decomposition.

    Args:
        k: Determines the rotation angle θ = 2π/2^k. Must be ≥ 1.
        label: Optional circuit name.
    """
    if k < 1:
        raise ValueError(f"k must be ≥ 1, got {k}")

    qc = QuantumCircuit(2, name=label or f"CR_{k}")
    qc.cp(2 * np.pi / (1 << k), 0, 1)
    return qc
