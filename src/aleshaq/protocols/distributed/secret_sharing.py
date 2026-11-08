"""GHZ-based Quantum Secret Sharing.

Implements an (n, n) threshold quantum secret sharing scheme using n-qubit
GHZ states.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from qiskit.circuit import ClassicalRegister, QuantumCircuit, QuantumRegister


@dataclass
class SecretSharingResult:
    """Outcome of a quantum secret sharing round."""

    secret_bit: int
    counts: dict[str, int]
    reconstructed_bit: int | None
    success_rate: float


class QuantumSecretSharing:
    """(n, n) GHZ-based quantum secret sharing protocol."""

    def __init__(self, n_parties: int = 3):
        if n_parties < 2:
            raise ValueError(f"n_parties must be ≥ 2, got {n_parties}")
        self.n_parties = n_parties

    def build_circuit(self, secret_bit: int) -> QuantumCircuit:
        """Build the secret sharing circuit.

        Args:
            secret_bit: The classical bit (0 or 1) to share among n parties.
        """
        if secret_bit not in (0, 1):
            raise ValueError(f"secret_bit must be 0 or 1, got {secret_bit}")

        parties = QuantumRegister(self.n_parties, "party")
        cr = ClassicalRegister(self.n_parties, "meas")
        qc = QuantumCircuit(parties, cr, name=f"QSS-{self.n_parties}")

        # Entangled GHZ state preparation
        qc.h(0)
        for i in range(self.n_parties - 1):
            qc.cx(i, i + 1)

        # Dealer encodes secret: Z phase flip on qubit 0
        if secret_bit:
            qc.z(0)

        qc.barrier()

        # All parties measure in Hadamard (X) basis
        for i in range(self.n_parties):
            qc.h(i)
        qc.measure(parties, cr)

        return qc

    def run(
        self,
        secret_bit: int,
        backend: Any | None = None,
        shots: int = 4096,
        seed: int | None = None,
    ) -> SecretSharingResult:
        """Execute the protocol and reconstruct the secret."""
        if backend is None:
            from aleshaq.protocols.execution.backend import get_aer_backend
            backend = get_aer_backend()

        from qiskit import transpile

        circuit = self.build_circuit(secret_bit)
        t_circ = transpile(circuit, backend)

        run_kwargs: dict[str, Any] = {"shots": shots}
        if seed is not None and hasattr(backend, "set_options"):
            run_kwargs["seed_simulator"] = seed

        result = backend.run(t_circ, **run_kwargs).result()
        counts = result.get_counts()
        return self.interpret(secret_bit, counts)

    def interpret(
        self, secret_bit: int, counts: dict[str, int]
    ) -> SecretSharingResult:
        """Reconstruct the secret from measurement parity."""
        if not counts:
            return SecretSharingResult(
                secret_bit=secret_bit,
                counts=counts,
                reconstructed_bit=None,
                success_rate=0.0,
            )

        total = sum(counts.values())
        correct = 0
        reconstructed_counts: dict[int, int] = {0: 0, 1: 0}

        for bitstring, count in counts.items():
            clean_str = bitstring.replace(" ", "")
            parity = clean_str.count("1") % 2
            reconstructed_counts[parity] += count
            if parity == secret_bit:
                correct += count

        reconstructed = max(reconstructed_counts, key=reconstructed_counts.get)  # type: ignore[arg-type]
        return SecretSharingResult(
            secret_bit=secret_bit,
            counts=counts,
            reconstructed_bit=reconstructed,
            success_rate=correct / total if total > 0 else 0.0,
        )
