"""Quantum network node abstraction."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aleshaq.networking.exceptions import CapacityExceededError


@dataclass
class Node:
    """A node in a quantum network.

    Represents a communication endpoint holding quantum and classical memory.

    Attributes:
        name: Unique identifier for this node.
        qubit_capacity: Maximum number of qubits the node can hold. None means unlimited.
        classical_memory: Classical data storage dictionary.
    """

    name: str
    qubit_capacity: int | None = None
    classical_memory: dict[str, Any] = field(default_factory=dict)
    _qubit_count: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Node name must be non-empty")
        if self.qubit_capacity is not None and self.qubit_capacity < 0:
            raise ValueError(f"qubit_capacity must be ≥ 0, got {self.qubit_capacity}")

    @property
    def qubit_count(self) -> int:
        """Number of qubits currently held by this node."""
        return self._qubit_count

    def allocate_qubit(self) -> int:
        """Allocate a qubit slot and return its local index.

        Raises:
            CapacityExceededError: If the node has reached its qubit capacity.
        """
        if self.qubit_capacity is not None and self._qubit_count >= self.qubit_capacity:
            raise CapacityExceededError(
                f"Node '{self.name}' at capacity ({self.qubit_capacity} qubits)"
            )
        idx = self._qubit_count
        self._qubit_count += 1
        return idx

    def release_qubit(self) -> None:
        """Release one qubit slot."""
        if self._qubit_count <= 0:
            raise RuntimeError(f"Node '{self.name}' has no qubits to release")
        self._qubit_count -= 1

    def store(self, key: str, value: Any) -> None:
        """Store a classical key-value pair."""
        self.classical_memory[key] = value

    def retrieve(self, key: str) -> Any:
        """Retrieve a classical value by key."""
        if key not in self.classical_memory:
            raise KeyError(f"Key '{key}' not found in node '{self.name}'")
        return self.classical_memory[key]

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.name == other.name

    def __repr__(self) -> str:
        cap_str = f", capacity={self.qubit_capacity}" if self.qubit_capacity is not None else ""
        return f"Node('{self.name}'{cap_str})"
