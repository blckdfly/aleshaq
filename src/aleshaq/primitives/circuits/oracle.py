"""Oracle circuit construction.

Provides a base interface for quantum oracles and a concrete phase oracle
that marks specified computational basis states with a phase flip.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from qiskit.circuit import QuantumCircuit


class OracleInterface(ABC):
    """Abstract interface for quantum oracles.

    Subclasses must implement ``build_circuit`` to return a QuantumCircuit
    that realizes the oracle unitary on *n_qubits* qubits.
    """

    @abstractmethod
    def build_circuit(self) -> QuantumCircuit:
        """Return the oracle as a QuantumCircuit."""

    @property
    @abstractmethod
    def n_qubits(self) -> int:
        """Number of qubits the oracle acts on."""


def phase_oracle(
    n: int, marked_states: list[int], *, label: str | None = None
) -> QuantumCircuit:
    """Construct a phase oracle that flips the sign of marked basis states.

    Implements the diagonal unitary O where O|x⟩ = −|x⟩ for x in
    *marked_states* and O|x⟩ = |x⟩ otherwise. This is the standard
    oracle form used in Grover's algorithm.

    The implementation uses multi-controlled Z gates, with X gates to
    condition on |0⟩ where needed.

    Args:
        n: Number of qubits.
        marked_states: List of basis state indices to mark (each in [0, 2^n)).
        label: Optional circuit name.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n}")

    N = 1 << n
    for s in marked_states:
        if s < 0 or s >= N:
            raise ValueError(f"marked state {s} out of range for {n} qubits")

    qc = QuantumCircuit(n, name=label or "PhaseOracle")

    for state in marked_states:
        # Flip qubits that should be |0⟩ in the target state, so
        # the multi-controlled Z conditions on the all-|1⟩ pattern.
        flip_qubits = [q for q in range(n) if not ((state >> q) & 1)]

        for q in flip_qubits:
            qc.x(q)

        # Multi-controlled Z = H on target, MCX, H on target.
        if n == 1:
            qc.z(0)
        else:
            qc.h(n - 1)
            qc.mcx(list(range(n - 1)), n - 1)
            qc.h(n - 1)

        for q in flip_qubits:
            qc.x(q)

    return qc
