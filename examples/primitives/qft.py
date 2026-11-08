"""Apply QFT and its inverse, verifying the roundtrip."""

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import Statevector

from aleshaq.primitives.transforms import qft, inverse_qft

n = 3

# Start with a known computational basis state
initial = QuantumCircuit(n)
initial.x(0)  # |001⟩

sv_initial = Statevector.from_instruction(initial)
print(f"Initial state: {sv_initial}")

# Apply QFT
combined = QuantumCircuit(n)
combined.compose(initial, inplace=True)
combined.compose(qft(n), inplace=True)

sv_transformed = Statevector.from_instruction(combined)
print(f"After QFT: {sv_transformed}")

# Apply inverse QFT — should recover the original state
combined.compose(inverse_qft(n), inplace=True)

sv_recovered = Statevector.from_instruction(combined)
print(f"After QFT†: {sv_recovered}")

fidelity = np.abs(np.vdot(sv_initial.data, sv_recovered.data)) ** 2
print(f"Fidelity with initial state: {fidelity:.10f}")
