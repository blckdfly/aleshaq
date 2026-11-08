"""Entanglement link tracking and operations."""

from __future__ import annotations

from dataclasses import dataclass
from qiskit.circuit import ClassicalRegister, QuantumCircuit, QuantumRegister

from aleshaq.networking.exceptions import LinkNotFoundError
from aleshaq.networking.nodes.node import Node


@dataclass
class EntanglementLink:
    """A shared entangled pair between two nodes.

    Attributes:
        node_a: First node holding one half of the entangled pair.
        node_b: Second node holding the other half.
        fidelity: Estimated state fidelity with respect to |Φ⁺⟩ in (0, 1].
        generation: Number of swapping stages that produced this link.
    """

    node_a: Node
    node_b: Node
    fidelity: float = 1.0
    generation: int = 0

    def __post_init__(self) -> None:
        if not (0.0 < self.fidelity <= 1.0):
            raise ValueError(f"fidelity must be in (0, 1], got {self.fidelity}")
        if self.generation < 0:
            raise ValueError(f"generation must be ≥ 0, got {self.generation}")

    def involves(self, node: Node) -> bool:
        """True if *node* is one of the endpoints of this link."""
        return node == self.node_a or node == self.node_b

    def __repr__(self) -> str:
        return (
            f"EntanglementLink({self.node_a.name} <-> {self.node_b.name}, "
            f"F={self.fidelity:.4f}, gen={self.generation})"
        )


def build_bell_pair_circuit() -> QuantumCircuit:
    """Construct a 2-qubit Bell state |Φ⁺⟩ preparation circuit for a network link."""
    qc = QuantumCircuit(2, name="BellLinkPrep")
    qc.h(0)
    qc.cx(0, 1)
    return qc


def build_swapping_circuit() -> QuantumCircuit:
    """Construct a 4-qubit entanglement swapping circuit with Bell measurement at swap node."""
    q_a = QuantumRegister(1, "node_a")
    q_swap_in = QuantumRegister(1, "swap_in")
    q_swap_out = QuantumRegister(1, "swap_out")
    q_c = QuantumRegister(1, "node_c")
    cr_swap = ClassicalRegister(2, "swap_meas")

    qc = QuantumCircuit(q_a, q_swap_in, q_swap_out, q_c, cr_swap, name="EntanglementSwap")

    # Prepare pair 1 between A and Swap_in
    qc.h(0)
    qc.cx(0, 1)

    # Prepare pair 2 between Swap_out and C
    qc.h(2)
    qc.cx(2, 3)

    qc.barrier()

    # Bell measurement at swap node on (swap_in, swap_out)
    qc.cx(1, 2)
    qc.h(1)
    qc.measure([1, 2], cr_swap)

    return qc


class EntanglementManager:
    """Manages entanglement links across a quantum network."""

    def __init__(self) -> None:
        self._links: list[EntanglementLink] = []

    @property
    def links(self) -> list[EntanglementLink]:
        return list(self._links)

    def create_link(
        self,
        node_a: Node,
        node_b: Node,
        fidelity: float = 1.0,
        generation: int = 0,
    ) -> EntanglementLink:
        """Create and register a new entanglement link."""
        link = EntanglementLink(
            node_a=node_a, node_b=node_b, fidelity=fidelity, generation=generation
        )
        self._links.append(link)
        return link

    def get_links(self, node: Node) -> list[EntanglementLink]:
        """Return all entanglement links involving *node*."""
        return [link for link in self._links if link.involves(node)]

    def get_link_between(
        self, node_a: Node, node_b: Node
    ) -> EntanglementLink | None:
        """Return the first link connecting the two nodes, or None."""
        for link in self._links:
            if link.involves(node_a) and link.involves(node_b):
                return link
        return None

    def swap(
        self,
        link_ab: EntanglementLink,
        link_bc: EntanglementLink,
        swap_node: Node,
        swap_fidelity: float = 1.0,
    ) -> EntanglementLink:
        """Perform entanglement swapping at *swap_node*."""
        if not link_ab.involves(swap_node):
            raise LinkNotFoundError(f"link_ab does not involve swap node '{swap_node.name}'")
        if not link_bc.involves(swap_node):
            raise LinkNotFoundError(f"link_bc does not involve swap node '{swap_node.name}'")

        node_a = link_ab.node_a if link_ab.node_b == swap_node else link_ab.node_b
        node_c = link_bc.node_a if link_bc.node_b == swap_node else link_bc.node_b

        new_fidelity = link_ab.fidelity * link_bc.fidelity * swap_fidelity
        new_generation = max(link_ab.generation, link_bc.generation) + 1

        self._links.remove(link_ab)
        self._links.remove(link_bc)

        return self.create_link(
            node_a, node_c, fidelity=new_fidelity, generation=new_generation
        )

    def remove_link(self, link: EntanglementLink) -> None:
        """Remove a link from the manager."""
        self._links.remove(link)

    def clear(self) -> None:
        """Remove all tracked links."""
        self._links.clear()

    def __repr__(self) -> str:
        return f"EntanglementManager({len(self._links)} active links)"
