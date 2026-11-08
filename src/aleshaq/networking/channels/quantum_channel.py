"""Quantum channel model.

Represents a quantum communication link between two network nodes with loss
and depolarizing noise parameters.
"""

from __future__ import annotations

from dataclasses import dataclass

from aleshaq.networking.exceptions import ChannelError
from aleshaq.networking.nodes.node import Node


@dataclass
class QuantumChannel:
    """A quantum communication channel between two network nodes.

    Attributes:
        node_a: First endpoint node.
        node_b: Second endpoint node.
        loss_probability: Transmission loss probability in [0, 1].
        depolarizing_rate: Depolarizing noise parameter in [0, 1].
        length_km: Physical channel distance in kilometers.
    """

    node_a: Node
    node_b: Node
    loss_probability: float = 0.0
    depolarizing_rate: float = 0.0
    length_km: float = 0.0

    def __post_init__(self) -> None:
        if self.node_a == self.node_b:
            raise ChannelError(f"Channel cannot connect node '{self.node_a.name}' to itself")
        if not (0.0 <= self.loss_probability <= 1.0):
            raise ChannelError(
                f"loss_probability must be in [0,1], got {self.loss_probability}"
            )
        if not (0.0 <= self.depolarizing_rate <= 1.0):
            raise ChannelError(
                f"depolarizing_rate must be in [0,1], got {self.depolarizing_rate}"
            )
        if self.length_km < 0:
            raise ChannelError(f"length_km must be ≥ 0, got {self.length_km}")

    def connects(self, node: Node) -> bool:
        """Return True if this channel has *node* as an endpoint."""
        return node == self.node_a or node == self.node_b

    def other_end(self, node: Node) -> Node:
        """Return the opposite node endpoint on the channel.

        Raises:
            ChannelError: If *node* is not connected to this channel.
        """
        if node == self.node_a:
            return self.node_b
        if node == self.node_b:
            return self.node_a
        raise ChannelError(f"Node '{node.name}' is not an endpoint of this channel")

    @property
    def is_ideal(self) -> bool:
        """True if the channel has zero loss and zero depolarizing noise."""
        return self.loss_probability == 0.0 and self.depolarizing_rate == 0.0

    def __repr__(self) -> str:
        return (
            f"QuantumChannel({self.node_a.name} <-> {self.node_b.name}, "
            f"loss={self.loss_probability:.2%}, length={self.length_km}km)"
        )
