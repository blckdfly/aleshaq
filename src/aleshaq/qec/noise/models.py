"""Configurable noise models for QEC experiments.

Wraps Qiskit Aer noise construction into simple parameterized functions
suitable for running QEC code experiments.
"""

from __future__ import annotations

from qiskit_aer.noise import NoiseModel, pauli_error


def bit_flip_noise(p: float) -> NoiseModel:
    """Create a noise model that applies bit-flip (X) errors with probability *p*.

    Args:
        p: Error probability per single-qubit gate, in [0, 1].
    """
    _validate_probability(p)
    error = pauli_error([("X", p), ("I", 1 - p)])
    model = NoiseModel()
    model.add_all_qubit_quantum_error(error, ["id", "x", "h", "s", "t"])
    # Two-qubit gate error: independent bit flips on each qubit
    error_2q = error.tensor(error)
    model.add_all_qubit_quantum_error(error_2q, ["cx"])
    return model


def phase_flip_noise(p: float) -> NoiseModel:
    """Create a noise model that applies phase-flip (Z) errors with probability *p*."""
    _validate_probability(p)
    error = pauli_error([("Z", p), ("I", 1 - p)])
    model = NoiseModel()
    model.add_all_qubit_quantum_error(error, ["id", "x", "h", "s", "t"])
    error_2q = error.tensor(error)
    model.add_all_qubit_quantum_error(error_2q, ["cx"])
    return model


def depolarizing_noise(p: float) -> NoiseModel:
    """Create a symmetric depolarizing noise model.

    Each gate independently applies X, Y, or Z with probability p/3 each.

    Args:
        p: Total depolarizing probability in [0, 1].
    """
    _validate_probability(p)
    error = pauli_error([
        ("X", p / 3),
        ("Y", p / 3),
        ("Z", p / 3),
        ("I", 1 - p),
    ])
    model = NoiseModel()
    model.add_all_qubit_quantum_error(error, ["id", "x", "h", "s", "t"])
    error_2q = error.tensor(error)
    model.add_all_qubit_quantum_error(error_2q, ["cx"])
    return model


def _validate_probability(p: float) -> None:
    if not (0.0 <= p <= 1.0):
        raise ValueError(f"Probability must be in [0, 1], got {p}")
