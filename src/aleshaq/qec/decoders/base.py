"""Abstract decoder interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from qiskit.circuit import QuantumCircuit


class Decoder(ABC):
    """Abstract interface for QEC decoders.

    A decoder takes a syndrome (integer) and returns a recovery
    circuit that should correct the identified error.
    """

    @abstractmethod
    def decode(self, syndrome: int) -> QuantumCircuit:
        """Return a recovery circuit for the given syndrome.

        Args:
            syndrome: Integer encoding of the measured syndrome bits.

        Returns:
            A QuantumCircuit that applies the correction.
        """
