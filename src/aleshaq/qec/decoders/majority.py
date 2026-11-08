"""Majority vote decoder for repetition codes."""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit, QuantumRegister

from aleshaq.qec.decoders.base import Decoder


class MajorityVoteDecoder(Decoder):
    """Majority vote decoder for repetition-family codes."""

    def __init__(self, n_data_qubits: int):
        if n_data_qubits < 1:
            raise ValueError(f"n_data_qubits must be ≥ 1, got {n_data_qubits}")
        self._n = n_data_qubits

    @property
    def n_data_qubits(self) -> int:
        return self._n

    def decode(self, syndrome: int) -> QuantumCircuit:
        data = QuantumRegister(self._n, "data")
        qc = QuantumCircuit(data, name="MajVoteRecover")

        error_qubit = self._find_error(syndrome)
        if error_qubit is not None:
            qc.x(error_qubit)

        return qc

    def _find_error(self, syndrome: int) -> int | None:
        if syndrome == 0:
            return None

        n_syndrome_bits = self._n - 1
        bits = [(syndrome >> i) & 1 for i in range(n_syndrome_bits)]

        violations = [i for i, b in enumerate(bits) if b]
        if not violations:
            return None

        if len(violations) == 1:
            v = violations[0]
            if v == 0:
                return 0
            return v

        return violations[-1]

    def __repr__(self) -> str:
        return f"MajorityVoteDecoder(n_data_qubits={self._n})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MajorityVoteDecoder):
            return NotImplemented
        return self._n == other._n
