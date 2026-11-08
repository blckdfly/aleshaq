"""Quantum Fourier Transform.

Implements the standard QFT and its inverse on n qubits. The QFT maps
computational basis states to the Fourier basis:

    QFT|j⟩ = (1/√N) Σ_k  e^{2πijk/N} |k⟩

The circuit uses the standard decomposition into Hadamard gates and
controlled phase rotations CR_k = diag(1, e^{2πi/2^k}).
"""

from __future__ import annotations

import numpy as np
from qiskit.circuit import QuantumCircuit


def qft(n: int, *, do_swaps: bool = True, label: str | None = None) -> QuantumCircuit:
    """Construct the Quantum Fourier Transform circuit on n qubits.

    Args:
        n: Number of qubits (must be ≥ 1).
        do_swaps: If True, append SWAP gates at the end to match the
            conventional QFT output ordering. Set False when composing
            with other circuits where the reversed ordering is expected.
        label: Optional circuit name.

    Returns:
        An n-qubit QuantumCircuit implementing the QFT.
    """
    if n < 1:
        raise ValueError(f"QFT requires n ≥ 1, got {n}")

    qc = QuantumCircuit(n, name=label or f"QFT-{n}")
    _build_qft(qc, n)

    if do_swaps:
        for i in range(n // 2):
            qc.swap(i, n - i - 1)

    return qc


def inverse_qft(
    n: int, *, do_swaps: bool = True, label: str | None = None
) -> QuantumCircuit:
    """Construct the inverse QFT circuit on n qubits.

    Equivalent to qft(n).inverse() but avoids constructing the forward
    circuit first.

    Args:
        n: Number of qubits (must be ≥ 1).
        do_swaps: If True, prepend SWAP gates to undo the QFT's output
            reordering before applying the inverse rotations.
        label: Optional circuit name.
    """
    if n < 1:
        raise ValueError(f"Inverse QFT requires n ≥ 1, got {n}")

    qc = QuantumCircuit(n, name=label or f"QFT†-{n}")

    if do_swaps:
        for i in range(n // 2):
            qc.swap(i, n - i - 1)

    _build_inverse_qft(qc, n)
    return qc


def _build_qft(qc: QuantumCircuit, n: int) -> None:
    """Apply the QFT gate sequence (without final swaps) to *qc*."""
    for target in reversed(range(n)):
        qc.h(target)
        for control in reversed(range(target)):
            k = target - control + 1
            qc.cp(2 * np.pi / (1 << k), control, target)


def _build_inverse_qft(qc: QuantumCircuit, n: int) -> None:
    """Apply the inverse QFT gate sequence (without leading swaps)."""
    for target in range(n):
        for control in range(target):
            k = target - control + 1
            qc.cp(-2 * np.pi / (1 << k), control, target)
        qc.h(target)
