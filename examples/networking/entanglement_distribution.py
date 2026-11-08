"""Distribute entanglement across a multi-hop network."""

from aleshaq.networking import Node
from aleshaq.networking.entanglement import EntanglementManager
from aleshaq.networking.routing import Topology
from aleshaq.networking.protocols import EntanglementDistribution

# Build a linear chain: A — B — C — D
topology = Topology()
nodes = [Node("A"), Node("B"), Node("C"), Node("D")]
for n in nodes:
    topology.add_node(n)
for i in range(len(nodes) - 1):
    topology.add_edge(nodes[i], nodes[i + 1])

manager = EntanglementManager()

# Each direct link has fidelity 0.95, each swap operation has fidelity 0.98
protocol = EntanglementDistribution(
    topology, manager,
    link_fidelity=0.95,
    swap_fidelity=0.98,
)

result = protocol.distribute(nodes[0], nodes[-1])

print(f"Source: {result.source.name}")
print(f"Destination: {result.destination.name}")
print(f"Path: {[n.name for n in result.path]}")
print(f"Success: {result.success}")
if result.link:
    print(f"End-to-end fidelity: {result.link.fidelity:.4f}")
    print(f"Generation (swaps): {result.link.generation}")
