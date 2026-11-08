"""Quantum Phase Estimation (QPE).

Constructs the standard QPE circuit that estimates the eigenvalue phase of
a unitary operator. Given U|ψ⟩ = e^{2πiφ}|ψ⟩, QPE produces an n-bit
approximation of φ in the counting register.

The circuit structure:
    1. Hadamard all counting qubits
    2. Controlled-U^{2^k} from counting qubit k onto the eigenstate register
    3. Inverse QFT on the counting register
    4. Measure counting register
"""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister

from aleshaq.primitives.transforms import inverse_qft


def phase_estimation(
    unitary: QuantumCircuit,
    precision: int,
    *,
    eigenstate_prep: QuantumCircuit | None = None,
    label: str | None = None,
) -> QuantumCircuit:
    """Build a Quantum Phase Estimation circuit.

    Args:
        unitary: A circuit acting on m qubits that implements the unitary U.
            Must be a pure unitary (no measurements or classical bits).
        precision: Number of counting qubits. Determines the resolution
            of the phase estimate: Δφ ≈ 1/2^precision.
        eigenstate_prep: Optional circuit to prepare the eigenstate |ψ⟩
            on the target register. If None, the target register starts
            in |0…0⟩ and the caller is responsible for ensuring this
            overlaps with the desired eigenspace.
        label: Optional circuit name.

    Returns:
        A QuantumCircuit with *precision* counting qubits measured into
        a classical register, followed by the unitary's qubits.
    """
    if precision < 1:
        raise ValueError(f"precision must be ≥ 1, got {precision}")

    n_target = unitary.num_qubits
    counting = QuantumRegister(precision, "count")
    target = QuantumRegister(n_target, "target")
    classical = ClassicalRegister(precision, "phase")
    qc = QuantumCircuit(counting, target, classical, name=label or "QPE")

    if eigenstate_prep is not None:
        qc.compose(eigenstate_prep, qubits=target, inplace=True)

    # Hadamard on all counting qubits
    qc.h(counting)

    # Controlled-U^{2^k}: each counting qubit k controls U applied 2^k times
    # to the target register. We use the gate form of the unitary circuit.
    u_gate = unitary.to_gate(label="U")
    for k in range(precision):
        cu = u_gate.power(1 << k).control(1)
        qc.append(cu, [counting[k]] + list(target))

    # Inverse QFT on counting register (without swaps, since we handle
    # the bit ordering through measurement indexing)
    iqft = inverse_qft(precision, do_swaps=True)
    qc.compose(iqft, qubits=counting, inplace=True)

    qc.measure(counting, classical)
    return qc


def interpret_phase(counts: dict[str, int], precision: int) -> dict[float, int]:
    """Convert QPE measurement counts to estimated phase values.

    Args:
        counts: Measurement counts from running the QPE circuit.
        precision: Number of counting qubits used in the QPE circuit.

    Returns:
        Dictionary mapping estimated phase values (in [0, 1)) to their
        measurement counts.
    """
    phase_counts: dict[float, int] = {}
    for bitstring, count in counts.items():
        # Qiskit returns bitstrings in big-endian order.
        measured_int = int(bitstring, 2)
        phase = measured_int / (1 << precision)
        phase_counts[phase] = phase_counts.get(phase, 0) + count
    return phase_counts
