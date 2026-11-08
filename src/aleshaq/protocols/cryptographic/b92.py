"""B92 Quantum Key Distribution simulation.

The B92 protocol (Bennett, 1992) uses two non-orthogonal states:
|0⟩ for bit 0 and |+⟩ for bit 1.

Security status: see README "Security Model" section.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from qiskit.circuit import QuantumCircuit

from aleshaq.protocols.exceptions import InsufficientRoundsError


@dataclass
class B92Result:
    """Outcome of a B92 simulation run."""

    alice_bits: list[int]
    bob_bases: list[int]
    bob_measurements: list[int]
    sifted_key_alice: list[int] = field(default_factory=list)
    sifted_key_bob: list[int] = field(default_factory=list)
    qber: float | None = None


class B92:
    """B92 QKD protocol simulation.

    Alice encodes bit 0 as |0⟩ and bit 1 as |+⟩.
    Bob measures in basis X (for detecting |0⟩) or Z (for detecting |+⟩).
    """

    def __init__(self, n_bits: int = 256, seed: int | None = None):
        if n_bits < 1:
            raise InsufficientRoundsError(f"n_bits must be ≥ 1, got {n_bits}")
        self.n_bits = n_bits
        self._rng = np.random.default_rng(seed)
        self._sim_seed = seed

    def run(self, backend: Any | None = None) -> B92Result:
        """Execute B92 protocol simulation."""
        if backend is None:
            from aleshaq.protocols.execution.backend import get_aer_backend
            backend = get_aer_backend()

        from qiskit import transpile

        alice_bits = self._rng.integers(0, 2, size=self.n_bits).tolist()
        bob_bases = self._rng.integers(0, 2, size=self.n_bits).tolist()

        config_rounds: dict[tuple[int, int], list[int]] = {}
        for r_idx, (bit, b_basis) in enumerate(zip(alice_bits, bob_bases)):
            config_rounds.setdefault((bit, b_basis), []).append(r_idx)

        bob_measurements = [0] * self.n_bits

        for (bit, b_basis), round_indices in config_rounds.items():
            count = len(round_indices)
            if count == 0:
                continue

            qc = QuantumCircuit(1, 1)
            if bit == 1:
                qc.h(0)
            if b_basis == 0:
                qc.h(0)
            qc.measure(0, 0)

            t_qc = transpile(qc, backend)
            sim_seed = (self._sim_seed + bit * 2 + b_basis) if self._sim_seed is not None else None

            run_kwargs: dict[str, Any] = {"shots": count}
            if sim_seed is not None and hasattr(backend, "set_options"):
                run_kwargs["seed_simulator"] = sim_seed

            try:
                result = backend.run(t_qc, **run_kwargs).result()
                if hasattr(result, "get_memory"):
                    try:
                        memory = result.get_memory()
                        for r_idx, bitstring in zip(round_indices, memory):
                            bob_measurements[r_idx] = int(bitstring.strip())
                        continue
                    except Exception:
                        pass

                counts = result.get_counts()
                p1 = counts.get("1", 0) / count if count > 0 else 0.0
                sampled = self._rng.binomial(1, p1, size=count)
                for r_idx, val in zip(round_indices, sampled):
                    bob_measurements[r_idx] = int(val)
            except Exception:
                for r_idx in round_indices:
                    # In B92, outcome 1 occurs with 50% prob when states do not match
                    if (bit == 0 and b_basis == 0) or (bit == 1 and b_basis == 1):
                        bob_measurements[r_idx] = int(self._rng.random() < 0.5)
                    else:
                        bob_measurements[r_idx] = 0

        sifted_alice, sifted_bob = [], []
        for a_bit, b_basis, b_meas in zip(alice_bits, bob_bases, bob_measurements):
            if b_meas == 1:
                sifted_alice.append(a_bit)
                sifted_bob.append(0 if b_basis == 0 else 1)

        qber = None
        if sifted_alice:
            errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
            qber = errors / len(sifted_alice)

        return B92Result(
            alice_bits=alice_bits,
            bob_bases=bob_bases,
            bob_measurements=bob_measurements,
            sifted_key_alice=sifted_alice,
            sifted_key_bob=sifted_bob,
            qber=qber,
        )
