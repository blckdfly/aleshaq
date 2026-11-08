"""Quantum teleportation example."""

from qiskit.circuit import QuantumCircuit
from aleshaq.protocols.communication import Teleportation

# Teleport the |+⟩ state
prep = QuantumCircuit(1)
prep.h(0)

protocol = Teleportation(state_prep=prep)
circuit = protocol.build_circuit()

print("Teleportation circuit:")
print(circuit)

result = protocol.run(shots=4096, seed=42)
print(f"\nBob's measurement outcomes: {result.bob_counts}")
print("(Should be roughly 50/50 for |+⟩)")
