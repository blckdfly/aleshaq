"""Lookup table decoder for quantum error-correcting codes."""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit

from aleshaq.qec.codes.base import StabilizerCode
from aleshaq.qec.decoders.base import Decoder


class LookupTableDecoder(Decoder):
    """Deterministic decoder mapping syndrome integers to recovery circuits.

    Uses a pre-calculated dictionary or delegates directly to the code's
    built-in recovery circuit generator.
    """

    def __init__(
        self,
        code: StabilizerCode,
        table: dict[int, QuantumCircuit] | None = None,
    ):
        self._code = code
        self._table = table

    @property
    def code(self) -> StabilizerCode:
        return self._code

    def decode(self, syndrome: int) -> QuantumCircuit:
        if self._table is not None and syndrome in self._table:
            return self._table[syndrome]
        return self._code.recovery_circuit(syndrome)

    def __repr__(self) -> str:
        return f"LookupTableDecoder(code={self._code})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LookupTableDecoder):
            return NotImplemented
        return self._code == other._code
