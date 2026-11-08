"""Quantum Teleportation protocol.

Transfers an unknown quantum state from Alice to Bob using a shared Bell pair
and two classical communication bits.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from qiskit.circuit import ClassicalRegister, QuantumCircuit, QuantumRegister


@dataclass
class TeleportationResult:
    """Result of a teleportation experiment."""

    counts: dict[str, int]
    bob_counts: dict[str, int]


def teleportation_circuit(
    state_prep: QuantumCircuit | None = None,
) -> QuantumCircuit:
    """Build a quantum teleportation circuit with feed-forward correction.

    Args:
        state_prep: Optional 1-qubit circuit preparing the input state.
            If None, defaults to |0⟩.

    Returns:
        A 3-qubit QuantumCircuit implementing the teleportation procedure.
    """
    alice_input = QuantumRegister(1, "a_in")
    alice_bell = QuantumRegister(1, "a_bell")
    bob = QuantumRegister(1, "bob")
    alice_cr = ClassicalRegister(2, "alice_meas")
    bob_cr = ClassicalRegister(1, "bob_meas")

    qc = QuantumCircuit(alice_input, alice_bell, bob, alice_cr, bob_cr, name="Teleportation")

    if state_prep is not None:
        qc.compose(state_prep, qubits=[0], inplace=True)

    # Entangle Alice's auxiliary qubit with Bob's qubit (|Φ⁺⟩)
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier()

    # Alice performs Bell measurement
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, alice_cr[0])
    qc.measure(1, alice_cr[1])
    qc.barrier()

    # Bob's conditional corrections based on Alice's classical bits
    with qc.if_test((alice_cr[1], 1)):
        qc.x(2)
    with qc.if_test((alice_cr[0], 1)):
        qc.z(2)

    qc.measure(2, bob_cr[0])
    return qc


class Teleportation:
    """High-level interface for the quantum teleportation protocol."""

    def __init__(self, state_prep: QuantumCircuit | None = None):
        self._state_prep = state_prep
        self._circuit: QuantumCircuit | None = None

    def build_circuit(self) -> QuantumCircuit:
        """Construct and return the teleportation circuit."""
        self._circuit = teleportation_circuit(self._state_prep)
        return self._circuit

    def run(
        self,
        backend: Any | None = None,
        shots: int = 4096,
        seed: int | None = None,
    ) -> TeleportationResult:
        """Execute the teleportation protocol on the specified backend.

        Args:
            backend: Target backend or simulator. Defaults to AerSimulator.
            shots: Number of experiment shots.
            seed: Random seed for simulation.
        """
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

    def interpret(self, counts: dict[str, int]) -> TeleportationResult:
        """Extract Bob's output state distribution from combined counts."""
        bob_counts: dict[str, int] = {}
        for bitstring, count in counts.items():
            bob_bit = bitstring.strip().split(" ")[0]
            bob_counts[bob_bit] = bob_counts.get(bob_bit, 0) + count

        return TeleportationResult(counts=counts, bob_counts=bob_counts)
