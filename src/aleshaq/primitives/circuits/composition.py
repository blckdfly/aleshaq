"""Circuit composition utilities."""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit


def append_circuit(
    target: QuantumCircuit,
    source: QuantumCircuit,
    qubits: list[int] | None = None,
    clbits: list[int] | None = None,
) -> QuantumCircuit:
    """Compose *source* onto *target* at the specified qubit/clbit positions.

    Thin wrapper around ``QuantumCircuit.compose`` that returns the
    modified circuit for convenient chaining.

    Args:
        target: Circuit to append onto.
        source: Circuit to append.
        qubits: Target qubit indices. If None, uses the first
            ``source.num_qubits`` qubits of *target*.
        clbits: Target classical bit indices. If None, auto-maps.

    Returns:
        The modified *target* circuit (composed in-place).
    """
    target.compose(source, qubits=qubits, clbits=clbits, inplace=True)
    return target


def repeat_circuit(circuit: QuantumCircuit, n: int) -> QuantumCircuit:
    """Repeat a circuit *n* times in sequence.

    Args:
        circuit: The circuit to repeat.
        n: Number of repetitions (must be ≥ 1).

    Returns:
        A new QuantumCircuit containing *n* sequential copies.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n}")

    result = QuantumCircuit(circuit.num_qubits, circuit.num_clbits, name=f"{circuit.name}×{n}")
    for _ in range(n):
        result.compose(circuit, inplace=True)
    return result
