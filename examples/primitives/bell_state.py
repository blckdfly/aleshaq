"""Prepare and verify Bell states using aleshaq.primitives."""

from qiskit_aer import AerSimulator
from aleshaq.primitives.states import bell_state

sim = AerSimulator()

for pair in range(4):
    circuit = bell_state(pair)
    circuit.measure_all()

    result = sim.run(circuit, shots=4096, seed_simulator=42).result()
    counts = result.get_counts()

    print(f"Bell state {circuit.name}: {counts}")
