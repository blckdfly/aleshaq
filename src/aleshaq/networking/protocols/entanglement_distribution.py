"""Entanglement distribution protocol.

Distributes entanglement between two potentially non-adjacent nodes
by creating links along a path and performing swaps at intermediate nodes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aleshaq.networking.nodes.node import Node
from aleshaq.networking.entanglement.link import EntanglementLink, EntanglementManager
from aleshaq.networking.routing.router import ShortestPathRouter
from aleshaq.networking.routing.topology import Topology


@dataclass
class DistributionResult:
    """Outcome of an entanglement distribution attempt."""
    source: Node
    destination: Node
    path: list[Node]
    link: EntanglementLink | None
    success: bool

    @property
    def fidelity(self) -> float | None:
        """End-to-end entanglement link fidelity if successfully established."""
        return self.link.fidelity if self.link is not None else None


class EntanglementDistribution:
    """Distribute entanglement between two nodes via a chain of swaps.

    Given a network topology (or QuantumNetwork) and an entanglement manager, this protocol:
    1. Finds a path from source to destination.
    2. Creates entanglement links on each hop.
    3. Performs entanglement swapping at each intermediate node.

    The resulting end-to-end link fidelity degrades multiplicatively
    with each swap, reflecting the physical cost of multi-hop
    entanglement distribution.
    """

    def __init__(
        self,
        topology: Topology | Any,
        entanglement_manager: EntanglementManager | None = None,
        link_fidelity: float = 1.0,
        swap_fidelity: float = 1.0,
    ):
        """
        Args:
            topology: Network topology (Topology) or QuantumNetwork instance.
            entanglement_manager: Manager for creating and tracking links. If None
                and a QuantumNetwork is passed, the network's manager is used.
            link_fidelity: Fidelity of each directly generated link.
            swap_fidelity: Fidelity of each swapping operation.
        """
        if hasattr(topology, "topology") and hasattr(topology, "entanglement"):
            self._topology: Topology = topology.topology
            self._manager: EntanglementManager = (
                entanglement_manager if entanglement_manager is not None else topology.entanglement
            )
        else:
            self._topology = topology
            self._manager = (
                entanglement_manager if entanglement_manager is not None else EntanglementManager()
            )
        self._link_fidelity = link_fidelity
        self._swap_fidelity = swap_fidelity

    def _resolve_node(self, node: Node | str) -> Node:
        if isinstance(node, str):
            for n in self._topology.nodes:
                if n.name == node:
                    return n
            return Node(node)
        return node

    def distribute(self, source: Node | str, destination: Node | str) -> DistributionResult:
        """Attempt to distribute entanglement from *source* to *destination*.

        Args:
            source: Source node or node name string.
            destination: Destination node or node name string.

        Returns:
            DistributionResult with the resulting link if successful.
        """
        src_node = self._resolve_node(source)
        dst_node = self._resolve_node(destination)

        router = ShortestPathRouter(self._topology)
        path = router.find_path(src_node, dst_node)

        if path is None:
            return DistributionResult(
                source=src_node, destination=dst_node,
                path=[], link=None, success=False,
            )

        if len(path) < 2:
            return DistributionResult(
                source=src_node, destination=dst_node,
                path=path, link=None, success=False,
            )

        # Create entanglement on each hop
        hop_links: list[EntanglementLink] = []
        for i in range(len(path) - 1):
            link = self._manager.create_link(
                path[i], path[i + 1], fidelity=self._link_fidelity
            )
            hop_links.append(link)

        # Swap at each intermediate node to extend entanglement end-to-end
        while len(hop_links) > 1:
            link_ab = hop_links.pop(0)
            link_bc = hop_links.pop(0)
            # The swap node is the shared endpoint
            swap_node = link_ab.node_b
            new_link = self._manager.swap(
                link_ab, link_bc, swap_node,
                swap_fidelity=self._swap_fidelity,
            )
            hop_links.insert(0, new_link)

        return DistributionResult(
            source=src_node, destination=dst_node,
            path=path, link=hop_links[0], success=True,
        )
