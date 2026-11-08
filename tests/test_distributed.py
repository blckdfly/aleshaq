"""Tests for distributed quantum protocols."""

import pytest

from aleshaq.protocols.distributed import QuantumSecretSharing


class TestQuantumSecretSharing:

    @pytest.mark.parametrize("secret_bit", [0, 1])
    def test_reconstruction(self, secret_bit: int):
        """Secret should be correctly reconstructed from measurement parity."""
        qss = QuantumSecretSharing(n_parties=3)
        result = qss.run(secret_bit, shots=4096, seed=42)
        assert result.reconstructed_bit == secret_bit
        assert result.success_rate > 0.95

    @pytest.mark.parametrize("n", [2, 3, 4, 5])
    def test_multiple_parties(self, n: int):
        qss = QuantumSecretSharing(n_parties=n)
        result = qss.run(1, shots=4096, seed=42)
        assert result.reconstructed_bit == 1

    def test_circuit_dimensions(self):
        qss = QuantumSecretSharing(n_parties=4)
        circuit = qss.build_circuit(0)
        assert circuit.num_qubits == 4
        assert circuit.num_clbits == 4

    def test_invalid_parties(self):
        with pytest.raises(ValueError):
            QuantumSecretSharing(n_parties=1)

    def test_invalid_secret(self):
        qss = QuantumSecretSharing()
        with pytest.raises(ValueError):
            qss.build_circuit(2)
