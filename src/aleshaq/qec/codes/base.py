"""Abstract base class for quantum error-correcting codes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from qiskit.circuit import QuantumCircuit


class StabilizerCode(ABC):
    """Base interface for stabilizer-based quantum error-correcting codes.

    Subclasses must define the code parameters [[n, k, d]] and provide
    circuits for encoding, syndrome measurement, and recovery.
    """

    @property
    @abstractmethod
    def n(self) -> int:
        """Number of physical qubits."""

    @property
    @abstractmethod
    def k(self) -> int:
        """Number of logical qubits."""

    @property
    @abstractmethod
    def d(self) -> int:
        """Code distance."""

    @property
    def label(self) -> str:
        """Standard [[n, k, d]] code notation."""
        return f"[[{self.n},{self.k},{self.d}]]"

    @abstractmethod
    def encode(self) -> QuantumCircuit:
        """Return a circuit encoding k logical qubits into n physical qubits."""

    @abstractmethod
    def syndrome_circuit(self) -> QuantumCircuit:
        """Return a circuit measuring stabilizer syndromes into classical bits."""

    @abstractmethod
    def recovery_circuit(self, syndrome: int) -> QuantumCircuit:
        """Return a correction circuit conditioned on the integer syndrome."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.label})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.n, self.k, self.d) == (other.n, other.k, other.d)

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.n, self.k, self.d))
