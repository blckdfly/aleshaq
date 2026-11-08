"""Top-level quantum network abstraction."""

from __future__ import annotations

from aleshaq.networking.channels.classical_channel import ClassicalChannel
from aleshaq.networking.channels.quantum_channel import QuantumChannel
from aleshaq.networking.entanglement.link import EntanglementManager
from aleshaq.networking.nodes.node import Node
from aleshaq.networking.routing.router import ShortestPathRouter
from aleshaq.networking.routing.topology import Topology


class QuantumNetwork:
    """A quantum network consisting of nodes connected by channels."""

    def __init__(self, name: str = "network") -> None:
        self.name = name
        self._topology = Topology()
        self._entanglement = EntanglementManager()
        self._quantum_channels: list[QuantumChannel] = []
        self._classical_channels: list[ClassicalChannel] = []

    @property
    def topology(self) -> Topology:
        return self._topology

    @property
    def entanglement(self) -> EntanglementManager:
        return self._entanglement

    @property
    def nodes(self) -> list[Node]:
        return self._topology.nodes

    @property
    def quantum_channels(self) -> list[QuantumChannel]:
        return list(self._quantum_channels)

    @property
    def classical_channels(self) -> list[ClassicalChannel]:
        return list(self._classical_channels)

    def add_node(self, node: Node) -> None:
        """Add a node to the network."""
        self._topology.add_node(node)

    def connect(
        self,
        node_a: Node,
        node_b: Node,
        *,
        loss_probability: float = 0.0,
        depolarizing_rate: float = 0.0,
        length_km: float = 0.0,
        delay_ms: float = 0.0,
        error_rate: float = 0.0,
    ) -> tuple[QuantumChannel, ClassicalChannel]:
        """Connect two nodes with quantum and classical channels.

        Args:
            node_a, node_b: Nodes to connect.
            loss_probability: Quantum channel loss probability in [0, 1].
            depolarizing_rate: Quantum channel depolarizing noise in [0, 1].
            length_km: Physical distance in km.
            delay_ms: Classical propagation delay in ms.
            error_rate: Classical channel bit error rate.

        Returns:
            Tuple of (QuantumChannel, ClassicalChannel).
        """
        qch = QuantumChannel(
            node_a=node_a,
            node_b=node_b,
            loss_probability=loss_probability,
            depolarizing_rate=depolarizing_rate,
            length_km=length_km,
        )
        cch = ClassicalChannel(
            node_a=node_a,
            node_b=node_b,
            delay_ms=delay_ms,
            error_rate=error_rate,
        )
        self._quantum_channels.append(qch)
        self._classical_channels.append(cch)
        self._topology.add_edge(node_a, node_b)
        return qch, cch

    def find_path(self, source: Node, destination: Node) -> list[Node] | None:
        """Find the shortest path between two nodes."""
        router = ShortestPathRouter(self._topology)
        return router.find_path(source, destination)

    def get_channel(self, node_a: Node, node_b: Node) -> QuantumChannel | None:
        """Return the quantum channel connecting two nodes, if present."""
        for ch in self._quantum_channels:
            if ch.connects(node_a) and ch.connects(node_b):
                return ch
        return None

    def __repr__(self) -> str:
        return (
            f"QuantumNetwork(name='{self.name}', "
            f"nodes={len(self.nodes)}, "
            f"channels={len(self._quantum_channels)})"
        )
