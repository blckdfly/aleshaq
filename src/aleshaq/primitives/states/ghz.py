"""GHZ state preparation.

Prepares the n-qubit Greenberger–Horne–Zeilinger state:
    |GHZ_n⟩ = (|00…0⟩ + |11…1⟩) / √2
"""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit


def ghz_state(n: int, *, label: str | None = None) -> QuantumCircuit:
    """Construct a circuit that prepares an n-qubit GHZ state.

    Uses a single Hadamard followed by a cascade of CNOT gates, which is
    depth-optimal for linear connectivity.

    Args:
        n: Number of qubits (must be ≥ 2).
        label: Optional circuit name.

    Returns:
        An n-qubit QuantumCircuit.
    """
    if n < 2:
        raise ValueError(f"GHZ state requires n ≥ 2, got {n}")

    qc = QuantumCircuit(n, name=label or f"GHZ-{n}")
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    return qc


def ghz_state_with_phase(
    n: int, phase: float, *, label: str | None = None
) -> QuantumCircuit:
    """GHZ state with a relative phase: (|00…0⟩ + e^{iφ}|11…1⟩) / √2.

    The phase is applied as an Rz rotation on the first qubit before
    entangling, which propagates through the CNOT cascade into a global
    relative phase between the two branches of the superposition.

    Args:
        n: Number of qubits (must be ≥ 2).
        phase: Relative phase φ in radians.
        label: Optional circuit name.
    """
    if n < 2:
        raise ValueError(f"GHZ state requires n ≥ 2, got {n}")

    qc = QuantumCircuit(n, name=label or f"GHZ-{n}-φ={phase:.3f}")
    qc.h(0)
    qc.rz(phase, 0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    return qc
