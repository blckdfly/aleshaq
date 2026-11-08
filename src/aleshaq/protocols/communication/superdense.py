"""Superdense Coding protocol.

Transmits two classical bits across a single physical qubit transmission,
leveraging pre-shared entanglement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from qiskit.circuit import ClassicalRegister, QuantumCircuit, QuantumRegister


@dataclass
class SuperdenseResult:
    """Result of a superdense coding experiment."""

    counts: dict[str, int]
    decoded_message: tuple[int, int] | None


def superdense_circuit(
    message: tuple[int, int],
) -> QuantumCircuit:
    """Build a superdense coding circuit for a 2-bit message.

    Args:
        message: Two classical bits (b0, b1), each in {0, 1}.

    Returns:
        A 2-qubit QuantumCircuit.
    """
    b0, b1 = message
    if b0 not in (0, 1) or b1 not in (0, 1):
        raise ValueError(f"Message bits must be 0 or 1, got ({b0}, {b1})")

    alice = QuantumRegister(1, "alice")
    bob = QuantumRegister(1, "bob")
    cr = ClassicalRegister(2, "result")
    qc = QuantumCircuit(alice, bob, cr, name=f"Superdense({b0}{b1})")

    # Shared Bell pair |Φ⁺⟩
    qc.h(alice[0])
    qc.cx(alice[0], bob[0])
    qc.barrier()

    # Alice's unitary encoding: maps {00,01,10,11} to four orthogonal Bell states
    if b1:
        qc.x(alice[0])
    if b0:
        qc.z(alice[0])
    qc.barrier()

    # Bob's Bell basis measurement
    qc.cx(alice[0], bob[0])
    qc.h(alice[0])

    qc.measure(alice[0], cr[0])
    qc.measure(bob[0], cr[1])
    return qc


class SuperdenseCoding:
    """Superdense Coding protocol interface."""

    def __init__(self, message: tuple[int, int]):
        self._message = message
        self._circuit: QuantumCircuit | None = None

    def build_circuit(self) -> QuantumCircuit:
        self._circuit = superdense_circuit(self._message)
        return self._circuit

    def run(
        self,
        backend: Any | None = None,
        shots: int = 4096,
        seed: int | None = None,
    ) -> SuperdenseResult:
        if self._circuit is None:
            self.build_circuit()

        if backend is None:
            from aleshaq.protocols.execution.backend import get_aer_backend
            backend = get_aer_backend()

        from qiskit import transpile

        assert self._circuit is not None
        t_circ = transpile(self._circuit, backend)

        run_kwargs: dict[str, Any] = {"shots": shots}
        if seed is not None and hasattr(backend, "set_options"):
            run_kwargs["seed_simulator"] = seed

        result = backend.run(t_circ, **run_kwargs).result()
        return self.interpret(result.get_counts())

    def interpret(self, counts: dict[str, int]) -> SuperdenseResult:
        """Decode the transmitted message from measurement outcomes."""
        if not counts:
            return SuperdenseResult(counts=counts, decoded_message=None)
        dominant = max(counts, key=counts.get)  # type: ignore[arg-type]
        clean_str = dominant.replace(" ", "")
        b0 = int(clean_str[1])  # cr[0]
        b1 = int(clean_str[0])  # cr[1]
        return SuperdenseResult(counts=counts, decoded_message=(b0, b1))
