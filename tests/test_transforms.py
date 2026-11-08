"""Tests for quantum transform primitives."""

import numpy as np
import pytest
from qiskit.quantum_info import Operator

from aleshaq.primitives.transforms import qft, inverse_qft, controlled_phase_rotation


class TestQFT:
    """Verify QFT mathematical properties."""

    @pytest.mark.parametrize("n", [1, 2, 3, 4])
    def test_qft_inverse_qft_is_identity(self, n: int):
        """QFT followed by QFT† should approximate the identity."""
        from qiskit.circuit import QuantumCircuit

        combined = QuantumCircuit(n)
        combined.compose(qft(n), inplace=True)
        combined.compose(inverse_qft(n), inplace=True)

        op = Operator(combined)
        identity = np.eye(1 << n)
        np.testing.assert_allclose(
            np.abs(op.data), identity, atol=1e-10,
            err_msg=f"QFT·QFT† ≠ I for n={n}"
        )

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_qft_is_unitary(self, n: int):
        op = Operator(qft(n))
        # U†U = I
        product = op.adjoint().compose(op)
        np.testing.assert_allclose(
            product.data, np.eye(1 << n), atol=1e-10
        )

    def test_qft_num_qubits(self):
        assert qft(4).num_qubits == 4

    def test_qft_1_qubit_is_hadamard(self):
        """On a single qubit, QFT is the Hadamard gate."""
        op = Operator(qft(1))
        hadamard = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        np.testing.assert_allclose(np.abs(op.data), np.abs(hadamard), atol=1e-10)

    def test_invalid_n(self):
        with pytest.raises(ValueError):
            qft(0)


class TestControlledPhaseRotation:
    """Verify controlled phase rotation gates."""

    def test_cr1_is_cz(self):
        """CR_1 should be the controlled-Z gate (phase = π)."""
        op = Operator(controlled_phase_rotation(1))
        # CZ = diag(1, 1, 1, -1)
        expected_diag = [1, 1, 1, -1]
        np.testing.assert_allclose(
            np.diag(op.data), expected_diag, atol=1e-10
        )

    def test_cr2_phase(self):
        """CR_2 applies a phase of π/2."""
        op = Operator(controlled_phase_rotation(2))
        expected_phase = np.exp(2j * np.pi / 4)  # e^{iπ/2} = i
        np.testing.assert_allclose(op.data[3, 3], expected_phase, atol=1e-10)

    def test_invalid_k(self):
        with pytest.raises(ValueError):
            controlled_phase_rotation(0)
