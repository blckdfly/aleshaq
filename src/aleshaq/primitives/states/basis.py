"""Computational basis state preparation."""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit


def computational_basis(n: int, index: int, *, label: str | None = None) -> QuantumCircuit:
    """Prepare the computational basis state |index⟩ on n qubits.

    Applies X gates according to the binary representation of *index*
    (least-significant bit on qubit 0, matching Qiskit's qubit ordering).

    Args:
        n: Number of qubits.
        index: Basis state index in [0, 2^n).
        label: Optional circuit name.

    Returns:
        An n-qubit QuantumCircuit that maps |0…0⟩ → |index⟩.
    """
    if index < 0 or index >= (1 << n):
        raise ValueError(f"index {index} out of range for {n} qubits (0–{(1 << n) - 1})")

    qc = QuantumCircuit(n, name=label or f"|{index:0{n}b}⟩")

    for qubit in range(n):
        if (index >> qubit) & 1:
            qc.x(qubit)

    return qc
