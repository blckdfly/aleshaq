"""Classical channel model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aleshaq.networking.exceptions import ChannelError
from aleshaq.networking.nodes.node import Node


@dataclass
class ClassicalChannel:
    """A classical communication channel between two network nodes.

    Attributes:
        node_a: First endpoint node.
        node_b: Second endpoint node.
        delay_ms: Classical propagation delay in milliseconds.
        error_rate: Classical bit error rate in [0, 1].
    """

    node_a: Node
    node_b: Node
    delay_ms: float = 0.0
    error_rate: float = 0.0

    def __post_init__(self) -> None:
        if self.node_a == self.node_b:
            raise ChannelError(f"Channel cannot connect node '{self.node_a.name}' to itself")
        if self.delay_ms < 0:
            raise ChannelError(f"delay_ms must be ≥ 0, got {self.delay_ms}")
        if not (0.0 <= self.error_rate <= 1.0):
            raise ChannelError(f"error_rate must be in [0,1], got {self.error_rate}")

    def connects(self, node: Node) -> bool:
        """Return True if this channel has *node* as an endpoint."""
        return node == self.node_a or node == self.node_b

    def other_end(self, node: Node) -> Node:
        """Return the opposite node endpoint on the channel."""
        if node == self.node_a:
            return self.node_b
        if node == self.node_b:
            return self.node_a
        raise ChannelError(f"Node '{node.name}' is not an endpoint of this channel")

    def send(self, sender: Node, key: str, value: Any) -> None:
        """Send a classical message from sender to recipient node memory."""
        recipient = self.other_end(sender)
        recipient.store(key, value)

    def transmit(self, message: Any) -> Any:
        """Simulate transmitting a classical message over the channel."""
        return message

    def __repr__(self) -> str:
        return f"ClassicalChannel({self.node_a.name} <-> {self.node_b.name}, delay={self.delay_ms}ms)"
