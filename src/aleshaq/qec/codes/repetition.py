"""Repetition code.

The repetition code encodes 1 logical qubit into d physical qubits
by replicating the state: |0_L⟩ = |00…0⟩, |1_L⟩ = |11…1⟩.

This is a [[d, 1, d]] code that corrects up to ⌊(d-1)/2⌋ bit-flip
(X) errors. It cannot correct phase-flip (Z) errors.

Syndrome extraction uses d-1 ancilla qubits, each measuring the
parity of adjacent data qubits via CNOT gates.
"""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister

from aleshaq.qec.codes.base import StabilizerCode


class RepetitionCode(StabilizerCode):
    """[[d, 1, d]] repetition code for bit-flip errors.

    Args:
        distance: Code distance (number of physical qubits). Must be odd
            and ≥ 3 for non-trivial error correction.
    """

    def __init__(self, distance: int = 3):
        if distance < 3 or distance % 2 == 0:
            raise ValueError(f"distance must be odd and ≥ 3, got {distance}")
        self._distance = distance

    @property
    def n(self) -> int:
        return self._distance

    @property
    def k(self) -> int:
        return 1

    @property
    def d(self) -> int:
        return self._distance

    def encode(self) -> QuantumCircuit:
        """Encode logical qubit (qubit 0) into d physical qubits via CNOT fan-out."""
        data = QuantumRegister(self._distance, "data")
        qc = QuantumCircuit(data, name=f"RepEncode-{self._distance}")

        for i in range(1, self._distance):
            qc.cx(0, i)

        return qc

    def syndrome_circuit(self) -> QuantumCircuit:
        """Measure parity of each adjacent pair of data qubits.

        Uses d-1 ancilla qubits. Syndrome bit i measures the parity of
        data[i] ⊕ data[i+1]. A non-zero syndrome indicates an error
        between (or at) the corresponding data qubits.
        """
        n_syndromes = self._distance - 1
        data = QuantumRegister(self._distance, "data")
        ancilla = QuantumRegister(n_syndromes, "anc")
        syn_cr = ClassicalRegister(n_syndromes, "syn")
        qc = QuantumCircuit(data, ancilla, syn_cr, name=f"RepSyndrome-{self._distance}")

        for i in range(n_syndromes):
            qc.cx(data[i], ancilla[i])
            qc.cx(data[i + 1], ancilla[i])

        qc.measure(ancilla, syn_cr)
        return qc

    def recovery_circuit(self, syndrome: int) -> QuantumCircuit:
        """Apply X correction to the identified error qubit.

        The syndrome is interpreted as a binary string where bit i indicates
        a parity violation between data[i] and data[i+1]. The error location
        is at the boundary of the violated parities.
        """
        data = QuantumRegister(self._distance, "data")
        qc = QuantumCircuit(data, name=f"RepRecover-{self._distance}")

        error_qubit = self._decode_syndrome(syndrome)
        if error_qubit is not None:
            qc.x(error_qubit)

        return qc

    def _decode_syndrome(self, syndrome: int) -> int | None:
        """Identify the error qubit from the syndrome.

        For the repetition code, the error is at the position indicated
        by the pattern of adjacent parity violations.
        """
        if syndrome == 0:
            return None

        n_syndromes = self._distance - 1
        bits = [(syndrome >> i) & 1 for i in range(n_syndromes)]

        # Single bit-flip error: the error qubit is adjacent to all
        # violated stabilizers. Find the qubit that borders the
        # boundary of violated parities.
        first_violation = None
        last_violation = None
        for i, b in enumerate(bits):
            if b:
                if first_violation is None:
                    first_violation = i
                last_violation = i

        if first_violation == last_violation:
            # Single stabilizer violated: error is on one of the two
            # qubits in that pair. Convention: pick the one that also
            # borders a non-violated stabilizer, i.e. the qubit at
            # the "edge" of the violation.
            if first_violation == 0:
                return 0
            elif first_violation == n_syndromes - 1:
                return self._distance - 1
            else:
                return first_violation

        # Contiguous block of violations: error at the shared qubit
        return last_violation
