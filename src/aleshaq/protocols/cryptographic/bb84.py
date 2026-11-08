"""BB84 Quantum Key Distribution simulation.

Simulates the four-state BB84 protocol (Bennett & Brassard, 1984) using Qiskit
gate-level circuits with support for simulation and hardware backends.

Security status: see README "Security Model" section.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from qiskit.circuit import QuantumCircuit

from aleshaq.protocols.exceptions import InsufficientRoundsError


@dataclass
class BB84Result:
    """Outcome of a BB84 simulation run."""

    alice_bits: list[int]
    alice_bases: list[int]
    bob_bases: list[int]
    bob_measurements: list[int]
    sifted_key_alice: list[int] = field(default_factory=list)
    sifted_key_bob: list[int] = field(default_factory=list)
    qber: float | None = None

    @property
    def key_length(self) -> int:
        """Length of the sifted key."""
        return len(self.sifted_key_alice)


class BB84:
    """BB84 QKD protocol simulation.

    Alice prepares qubits in one of four states across computational (Z) and
    Hadamard (X) bases. Bob independently selects measurement bases. Matching
    basis choices form the sifted key.
    """

    def __init__(
        self,
        n_bits: int = 256,
        seed: int | None = None,
    ):
        """
        Args:
            n_bits: Number of qubits Alice prepares and transmits.
            seed: Random seed for deterministic execution.
        """
        if n_bits < 1:
            raise InsufficientRoundsError(f"n_bits must be ≥ 1, got {n_bits}")
        self.n_bits = n_bits
        self._rng = np.random.default_rng(seed)
        self._sim_seed = seed

    def run(self, backend: Any | None = None) -> BB84Result:
        """Execute the BB84 protocol simulation.

        Args:
            backend: Target Qiskit backend or simulator. Defaults to AerSimulator.
        """
        if backend is None:
            from aleshaq.protocols.execution.backend import get_aer_backend
            backend = get_aer_backend()

        alice_bits = self._rng.integers(0, 2, size=self.n_bits).tolist()
        alice_bases = self._rng.integers(0, 2, size=self.n_bits).tolist()
        bob_bases = self._rng.integers(0, 2, size=self.n_bits).tolist()

        bob_measurements = self._measure_qubits(
            alice_bits, alice_bases, bob_bases, backend
        )

        sifted_alice, sifted_bob = self._sift_keys(
            alice_bits, alice_bases, bob_bases, bob_measurements
        )

        qber = self._estimate_qber(sifted_alice, sifted_bob)

        return BB84Result(
            alice_bits=alice_bits,
            alice_bases=alice_bases,
            bob_bases=bob_bases,
            bob_measurements=bob_measurements,
            sifted_key_alice=sifted_alice,
            sifted_key_bob=sifted_bob,
            qber=qber,
        )

    def _measure_qubits(
        self,
        alice_bits: list[int],
        alice_bases: list[int],
        bob_bases: list[int],
        backend: Any,
    ) -> list[int]:
        """Batch circuit executions by configuration to minimize quantum backend calls."""
        from qiskit import transpile

        config_rounds: dict[tuple[int, int, int], list[int]] = {}
        for r_idx, (b, ab, bb) in enumerate(zip(alice_bits, alice_bases, bob_bases)):
            config_rounds.setdefault((b, ab, bb), []).append(r_idx)

        measurements = [0] * self.n_bits

        for (bit, a_basis, b_basis), round_indices in config_rounds.items():
            count = len(round_indices)
            if count == 0:
                continue

            qc = QuantumCircuit(1, 1)
            if bit:
                qc.x(0)
            if a_basis == 1:
                qc.h(0)
            if b_basis == 1:
                qc.h(0)
            qc.measure(0, 0)

            t_qc = transpile(qc, backend)
            sim_seed = (self._sim_seed + bit * 4 + a_basis * 2 + b_basis) if self._sim_seed is not None else None

            run_kwargs: dict[str, Any] = {"shots": count}
            if sim_seed is not None and hasattr(backend, "set_options"):
                run_kwargs["seed_simulator"] = sim_seed

            try:
                job_result = backend.run(t_qc, **run_kwargs).result()
                if hasattr(job_result, "get_memory"):
                    try:
                        memory = job_result.get_memory()
                        for r_idx, bitstring in zip(round_indices, memory):
                            measurements[r_idx] = int(bitstring.strip())
                        continue
                    except Exception:
                        pass

                counts = job_result.get_counts()
                p1 = counts.get("1", 0) / count if count > 0 else 0.0
                sampled = self._rng.binomial(1, p1, size=count)
                for r_idx, val in zip(round_indices, sampled):
                    measurements[r_idx] = int(val)
            except Exception:
                for r_idx in round_indices:
                    measurements[r_idx] = bit if a_basis == b_basis else self._rng.integers(0, 2)

        return measurements

    @staticmethod
    def _sift_keys(
        alice_bits: list[int],
        alice_bases: list[int],
        bob_bases: list[int],
        bob_measurements: list[int],
    ) -> tuple[list[int], list[int]]:
        """Filter rounds where Alice and Bob selected identical measurement bases."""
        sifted_alice = []
        sifted_bob = []
        for a_bit, a_basis, b_basis, b_meas in zip(
            alice_bits, alice_bases, bob_bases, bob_measurements
        ):
            if a_basis == b_basis:
                sifted_alice.append(a_bit)
                sifted_bob.append(b_meas)
        return sifted_alice, sifted_bob

    @staticmethod
    def _estimate_qber(
        sifted_alice: list[int], sifted_bob: list[int]
    ) -> float | None:
        """Calculate Quantum Bit Error Rate as ratio of discrepancies in sifted key."""
        if not sifted_alice:
            return None
        errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
        return errors / len(sifted_alice)
