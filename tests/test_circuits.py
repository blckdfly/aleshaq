"""Tests for circuit utilities."""

import numpy as np
import pytest
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import Statevector

from aleshaq.primitives.circuits import phase_oracle, append_circuit, repeat_circuit


class TestPhaseOracle:
    """Verify phase oracle marks the correct basis states."""

    def test_single_marked_state(self):
        """Oracle should flip the phase of exactly the marked state."""
        oracle = phase_oracle(2, [1])  # mark |01⟩
        op_matrix = np.diag(
            [Statevector.from_int(i, 4).evolve(oracle).data[i] for i in range(4)]
        )
        # State |01⟩ (index 1) should have phase -1, others +1
        expected = np.diag([1, -1, 1, 1])
        np.testing.assert_allclose(op_matrix, expected, atol=1e-10)

    def test_multiple_marked_states(self):
        oracle = phase_oracle(2, [0, 3])
        sv_0 = Statevector.from_int(0, 4).evolve(oracle)
        sv_3 = Statevector.from_int(3, 4).evolve(oracle)
        sv_1 = Statevector.from_int(1, 4).evolve(oracle)

        # States 0 and 3 should be flipped
        assert sv_0.data[0] == pytest.approx(-1, abs=1e-10)
        assert sv_3.data[3] == pytest.approx(-1, abs=1e-10)
        assert sv_1.data[1] == pytest.approx(1, abs=1e-10)

    def test_invalid_marked_state(self):
        with pytest.raises(ValueError):
            phase_oracle(2, [4])


class TestComposition:

    def test_append_circuit(self):
        qc = QuantumCircuit(2)
        sub = QuantumCircuit(1)
        sub.h(0)

        result = append_circuit(qc, sub, qubits=[0])
        assert result.num_qubits == 2

    def test_repeat_circuit(self):
        qc = QuantumCircuit(1)
        qc.x(0)

        # X applied twice returns to |0⟩
        repeated = repeat_circuit(qc, 2)
        sv = Statevector.from_instruction(repeated)
        probs = sv.probabilities_dict()
        assert probs.get("0", 0) == pytest.approx(1.0, abs=1e-10)

    def test_repeat_invalid(self):
        with pytest.raises(ValueError):
            repeat_circuit(QuantumCircuit(1), 0)
