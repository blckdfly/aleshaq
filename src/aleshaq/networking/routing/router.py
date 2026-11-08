"""Routing algorithms for quantum networks."""

from __future__ import annotations

from collections import deque

from aleshaq.networking.nodes.node import Node
from aleshaq.networking.routing.topology import Topology


class ShortestPathRouter:
    """Hop-count shortest path routing on a network topology.

    Uses BFS to find the shortest path between two nodes. In a quantum
    network context, this can be used to plan entanglement swapping
    chains or identify relay paths for end-to-end entanglement.
    """

    def __init__(self, topology: Topology):
        self._topology = topology

    def find_path(self, source: Node, destination: Node) -> list[Node] | None:
        """Find the shortest path from *source* to *destination*.

        Returns:
            Ordered list of nodes from source to destination (inclusive),
            or None if no path exists.
        """
        if source == destination:
            return [source]

        visited: set[str] = {source.name}
        # BFS with parent tracking
        parent: dict[str, Node] = {}
        queue: deque[Node] = deque([source])

        while queue:
            current = queue.popleft()
            for neighbor in self._topology.neighbors(current):
                if neighbor.name in visited:
                    continue
                visited.add(neighbor.name)
                parent[neighbor.name] = current
                if neighbor == destination:
                    return self._reconstruct(parent, source, destination)
                queue.append(neighbor)

        return None

    @staticmethod
    def _reconstruct(
        parent: dict[str, Node], source: Node, destination: Node
    ) -> list[Node]:
        path = [destination]
        current = destination
        while current != source:
            current = parent[current.name]
            path.append(current)
        path.reverse()
        return path

    def find_all_paths(
        self, source: Node, destination: Node, max_depth: int | None = None
    ) -> list[list[Node]]:
        """Find all simple paths from *source* to *destination*.

        Args:
            source: Start node.
            destination: End node.
            max_depth: Maximum path length. None = no limit.

        Returns:
            List of paths, each a list of nodes.
        """
        all_paths: list[list[Node]] = []
        self._dfs_paths(source, destination, {source.name}, [source], all_paths, max_depth)
        return all_paths

    def _dfs_paths(
        self,
        current: Node,
        destination: Node,
        visited: set[str],
        path: list[Node],
        all_paths: list[list[Node]],
        max_depth: int | None,
    ) -> None:
        if current == destination:
            all_paths.append(list(path))
            return

        if max_depth is not None and len(path) > max_depth:
            return

        for neighbor in self._topology.neighbors(current):
            if neighbor.name not in visited:
                visited.add(neighbor.name)
                path.append(neighbor)
                self._dfs_paths(neighbor, destination, visited, path, all_paths, max_depth)
                path.pop()
                visited.discard(neighbor.name)
