"""W state preparation.

Prepares the n-qubit W state:
    |W_n⟩ = (|100…0⟩ + |010…0⟩ + … + |000…1⟩) / √n

This is a symmetric single-excitation state: exactly one qubit is |1⟩
in each term of the superposition, with uniform amplitude.

The construction follows a recursive splitting strategy using controlled
rotations. For n qubits, we start with |1⟩ on the first qubit, then
progressively distribute the excitation amplitude across the remaining
qubits using Ry rotations whose angles θ_k = 2·arcsin(1/√k) split
the probability appropriately.
"""

from __future__ import annotations

import numpy as np
from qiskit.circuit import QuantumCircuit


def w_state(n: int, *, label: str | None = None) -> QuantumCircuit:
    """Construct a circuit that prepares an n-qubit W state.

    Args:
        n: Number of qubits (must be ≥ 2).
        label: Optional circuit name.

    Returns:
        An n-qubit QuantumCircuit preparing |W_n⟩.
    """
    if n < 2:
        raise ValueError(f"W state requires n ≥ 2, got {n}")

    qc = QuantumCircuit(n, name=label or f"W-{n}")

    # Seed the excitation on qubit 0.
    qc.x(0)

    # Distribute the excitation from qubit i to qubit i+1 using a
    # controlled rotation where theta = 2 * arccos(sqrt(1 / (n - i))).
    # This ensures that qubit i retains exactly 1/n of the total excitation
    # probability while passing (n - i - 1)/n to the remaining qubits.
    for i in range(n - 1):
        remaining = n - i
        theta = 2 * np.arccos(np.sqrt(1.0 / remaining))
        qc.cry(theta, i, i + 1)
        qc.cx(i + 1, i)

    return qc
