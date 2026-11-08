"""Phase estimation example: estimate the eigenphase of the T gate.

The T gate has eigenvalue e^{iπ/4} for eigenstate |1⟩, so the
phase φ = 1/8.
"""

from qiskit.circuit import QuantumCircuit
from qiskit_aer import AerSimulator

from aleshaq.primitives.estimation import phase_estimation, interpret_phase

# T gate as a unitary circuit
t_gate = QuantumCircuit(1, name="T")
t_gate.t(0)

# Eigenstate |1⟩
eigenstate = QuantumCircuit(1)
eigenstate.x(0)

# Build QPE circuit with 4 bits of precision
qpe_circuit = phase_estimation(t_gate, precision=4, eigenstate_prep=eigenstate)
print(f"QPE circuit: {qpe_circuit.num_qubits} qubits, depth {qpe_circuit.depth()}")

# Run on simulator
from qiskit import transpile
sim = AerSimulator()
transpiled_circuit = transpile(qpe_circuit, sim)
result = sim.run(transpiled_circuit, shots=4096, seed_simulator=42).result()

phases = interpret_phase(result.get_counts(), precision=4)
for phase, count in sorted(phases.items(), key=lambda x: -x[1]):
    print(f"  φ = {phase:.4f}  (count: {count})")

dominant = max(phases, key=phases.get)
print(f"\nEstimated phase: {dominant:.4f}  (expected: 0.1250)")
