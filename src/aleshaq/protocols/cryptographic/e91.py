"""E91 Quantum Key Distribution simulation.

The E91 protocol (Ekert, 1991) uses shared entangled Bell pairs and CHSH
inequality verification to establish a sifted key.

Security status: see README "Security Model" section.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from qiskit.circuit import QuantumCircuit

from aleshaq.protocols.exceptions import InsufficientRoundsError


_ALICE_ANGLES = [0.0, np.pi / 8, np.pi / 4]
_BOB_ANGLES = [np.pi / 8, np.pi / 4, 3 * np.pi / 8]


@dataclass
class E91Result:
    """Outcome of an E91 simulation run."""

    alice_settings: list[int]
    bob_settings: list[int]
    alice_outcomes: list[int]
    bob_outcomes: list[int]
    sifted_key_alice: list[int] = field(default_factory=list)
    sifted_key_bob: list[int] = field(default_factory=list)
    chsh_value: float | None = None
    qber: float | None = None


class E91:
    """E91 entanglement-based QKD protocol simulation.

    Pairs in |Φ⁺⟩ are measured in non-orthogonal bases. Matching settings
    form the sifted key while non-matching settings test CHSH violation S ≈ 2√2.
    """

    def __init__(self, n_pairs: int = 256, seed: int | None = None):
        if n_pairs < 1:
            raise InsufficientRoundsError(f"n_pairs must be ≥ 1, got {n_pairs}")
        self.n_pairs = n_pairs
        self._rng = np.random.default_rng(seed)
        self._sim_seed = seed

    def run(self, backend: Any | None = None) -> E91Result:
        """Execute the E91 protocol simulation.

        Args:
            backend: Target Qiskit backend or simulator. Defaults to AerSimulator.
        """
        if backend is None:
            from aleshaq.protocols.execution.backend import get_aer_backend
            backend = get_aer_backend()

        from qiskit import transpile

        alice_settings = self._rng.integers(0, 3, size=self.n_pairs).tolist()
        bob_settings = self._rng.integers(0, 3, size=self.n_pairs).tolist()

        setting_rounds: dict[tuple[int, int], list[int]] = {}
        for round_idx, (a_idx, b_idx) in enumerate(zip(alice_settings, bob_settings)):
            setting_rounds.setdefault((a_idx, b_idx), []).append(round_idx)

        alice_outcomes = [0] * self.n_pairs
        bob_outcomes = [0] * self.n_pairs

        for (a_idx, b_idx), round_indices in setting_rounds.items():
            count = len(round_indices)
            if count == 0:
                continue

            a_angle = _ALICE_ANGLES[a_idx]
            b_angle = _BOB_ANGLES[b_idx]

            qc = QuantumCircuit(2, 2)
            qc.h(0)
            qc.cx(0, 1)
            qc.ry(-2 * a_angle, 0)
            qc.ry(-2 * b_angle, 1)
            qc.measure([0, 1], [0, 1])

            t_qc = transpile(qc, backend)
            sim_seed = (self._sim_seed + a_idx * 3 + b_idx) if self._sim_seed is not None else None

            run_kwargs: dict[str, Any] = {"shots": count}
            if sim_seed is not None and hasattr(backend, "set_options"):
                run_kwargs["seed_simulator"] = sim_seed

            try:
                job_result = backend.run(t_qc, **run_kwargs).result()
                if hasattr(job_result, "get_memory"):
                    try:
                        memory = job_result.get_memory()
                        for r_idx, bitstring in zip(round_indices, memory):
                            bstr = bitstring.replace(" ", "")
                            alice_outcomes[r_idx] = int(bstr[1])
                            bob_outcomes[r_idx] = int(bstr[0])
                        continue
                    except Exception:
                        pass

                counts = job_result.get_counts()
                outcomes_list = list(counts.keys())
                probs = [counts[k] / count for k in outcomes_list]
                sampled = self._rng.choice(outcomes_list, size=count, p=probs)
                for r_idx, bstr_raw in zip(round_indices, sampled):
                    bstr = bstr_raw.replace(" ", "")
                    alice_outcomes[r_idx] = int(bstr[1])
                    bob_outcomes[r_idx] = int(bstr[0])
            except Exception:
                theta = a_angle - b_angle
                p_same = math.cos(theta) ** 2
                for r_idx in round_indices:
                    a_val = self._rng.integers(0, 2)
                    b_val = a_val if (self._rng.random() < p_same) else (1 - a_val)
                    alice_outcomes[r_idx] = a_val
                    bob_outcomes[r_idx] = b_val

        # Sifting: matching angle settings
        sifted_alice, sifted_bob = [], []
        for a_idx, b_idx, a_out, b_out in zip(
            alice_settings, bob_settings, alice_outcomes, bob_outcomes
        ):
            if (a_idx == 1 and b_idx == 0) or (a_idx == 2 and b_idx == 1):
                sifted_alice.append(a_out)
                sifted_bob.append(b_out)

        chsh = self._estimate_chsh(
            alice_settings, bob_settings, alice_outcomes, bob_outcomes
        )

        qber = None
        if sifted_alice:
            errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
            qber = errors / len(sifted_alice)

        return E91Result(
            alice_settings=alice_settings,
            bob_settings=bob_settings,
            alice_outcomes=alice_outcomes,
            bob_outcomes=bob_outcomes,
            sifted_key_alice=sifted_alice,
            sifted_key_bob=sifted_bob,
            chsh_value=chsh,
            qber=qber,
        )

    @staticmethod
    def _estimate_chsh(
        alice_settings: list[int],
        bob_settings: list[int],
        alice_outcomes: list[int],
        bob_outcomes: list[int],
    ) -> float | None:
        """Estimate the CHSH value S = E(a0,b0) - E(a0,b2) + E(a2,b0) + E(a2,b2)."""
        def expectation(a_idx: int, b_idx: int) -> float | None:
            products = [
                (1 - 2 * ao) * (1 - 2 * bo)
                for ai, bi, ao, bo in zip(
                    alice_settings, bob_settings, alice_outcomes, bob_outcomes
                )
                if ai == a_idx and bi == b_idx
            ]
            if not products:
                return None
            return float(np.mean(products))

        t0 = expectation(0, 0)
        t1 = expectation(0, 2)
        t2 = expectation(2, 0)
        t3 = expectation(2, 2)

        if t0 is None or t1 is None or t2 is None or t3 is None:
            return None

        return t0 - t1 + t2 + t3
