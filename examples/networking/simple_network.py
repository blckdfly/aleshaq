"""Build a simple three-node quantum network and find paths."""

from aleshaq.networking import QuantumNetwork, Node

network = QuantumNetwork("example")

alice = Node("alice")
bob = Node("bob")
charlie = Node("charlie")

network.add_node(alice)
network.add_node(bob)
network.add_node(charlie)

network.connect(alice, bob, loss_probability=0.05, length_km=50.0)
network.connect(bob, charlie, loss_probability=0.08, length_km=80.0)

print(f"Network nodes: {[n.name for n in network.nodes]}")
print(f"Channels: {len(network.quantum_channels)}")

path = network.find_path(alice, charlie)
if path:
    print(f"Path alice → charlie: {[n.name for n in path]}")
