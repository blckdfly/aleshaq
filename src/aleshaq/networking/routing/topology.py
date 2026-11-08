"""Network topology representation.

Maintains an undirected graph of nodes and edges (channels),
supporting adjacency queries and path enumeration.
"""

from __future__ import annotations

from collections import defaultdict

from aleshaq.networking.nodes.node import Node


class Topology:
    """Graph-based network topology.

    Stores the adjacency structure of the network independently of
    channel physical parameters, supporting routing algorithms.
    """

    def __init__(self) -> None:
        self._adjacency: dict[str, set[str]] = defaultdict(set)
        self._nodes: dict[str, Node] = {}

    @property
    def nodes(self) -> list[Node]:
        return list(self._nodes.values())

    @property
    def edges(self) -> list[tuple[Node, Node]]:
        seen: set[tuple[str, str]] = set()
        result = []
        for name, neighbors in self._adjacency.items():
            for neighbor in neighbors:
                edge = tuple(sorted([name, neighbor]))
                if edge not in seen:
                    seen.add(edge)
                    result.append((self._nodes[edge[0]], self._nodes[edge[1]]))
        return result

    def add_node(self, node: Node) -> None:
        if node.name in self._nodes:
            raise ValueError(f"Node '{node.name}' already in topology")
        self._nodes[node.name] = node

    def add_edge(self, node_a: Node, node_b: Node) -> None:
        for n in (node_a, node_b):
            if n.name not in self._nodes:
                raise ValueError(f"Node '{n.name}' not in topology")
        self._adjacency[node_a.name].add(node_b.name)
        self._adjacency[node_b.name].add(node_a.name)

    def neighbors(self, node: Node) -> list[Node]:
        return [self._nodes[n] for n in self._adjacency.get(node.name, set())]

    def has_edge(self, node_a: Node, node_b: Node) -> bool:
        return node_b.name in self._adjacency.get(node_a.name, set())

    def remove_edge(self, node_a: Node, node_b: Node) -> None:
        self._adjacency[node_a.name].discard(node_b.name)
        self._adjacency[node_b.name].discard(node_a.name)

    def remove_node(self, node: Node) -> None:
        if node.name not in self._nodes:
            raise ValueError(f"Node '{node.name}' not in topology")
        for neighbor in list(self._adjacency.get(node.name, set())):
            self._adjacency[neighbor].discard(node.name)
        del self._adjacency[node.name]
        del self._nodes[node.name]
