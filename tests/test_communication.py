"""Tests for quantum communication protocols."""

import pytest
from qiskit.circuit import QuantumCircuit
from qiskit_aer import AerSimulator

from aleshaq.protocols.communication import Teleportation, SuperdenseCoding


class TestTeleportation:

    def test_teleport_zero_state(self):
        """Teleporting |0⟩ should yield predominantly '0' on Bob's qubit."""
        protocol = Teleportation()
        result = protocol.run(shots=4096, seed=42)
        assert result.bob_counts.get("0", 0) > result.bob_counts.get("1", 0)

    def test_teleport_one_state(self):
        """Teleporting |1⟩ should yield predominantly '1' on Bob's qubit."""
        prep = QuantumCircuit(1)
        prep.x(0)
        protocol = Teleportation(state_prep=prep)
        result = protocol.run(shots=4096, seed=42)
        assert result.bob_counts.get("1", 0) > result.bob_counts.get("0", 0)

    def test_teleport_plus_state(self):
        """Teleporting |+⟩ should yield roughly equal 0/1 on Bob's qubit."""
        prep = QuantumCircuit(1)
        prep.h(0)
        protocol = Teleportation(state_prep=prep)
        result = protocol.run(shots=4096, seed=42)
        total = sum(result.bob_counts.values())
        ratio = result.bob_counts.get("0", 0) / total
        # Should be close to 0.5 (within statistical tolerance)
        assert 0.35 < ratio < 0.65

    def test_circuit_structure(self):
        protocol = Teleportation()
        circuit = protocol.build_circuit()
        assert circuit.num_qubits == 3
        assert circuit.num_clbits == 3


class TestSuperdenseCoding:

    @pytest.mark.parametrize("message", [(0, 0), (0, 1), (1, 0), (1, 1)])
    def test_all_messages_recovered(self, message: tuple[int, int]):
        """Each 2-bit message should be perfectly recoverable in simulation."""
        protocol = SuperdenseCoding(message)
        result = protocol.run(shots=1024, seed=42)
        assert result.decoded_message == message

    def test_circuit_dimensions(self):
        protocol = SuperdenseCoding((0, 0))
        circuit = protocol.build_circuit()
        assert circuit.num_qubits == 2
        assert circuit.num_clbits == 2

    def test_invalid_message(self):
        with pytest.raises(ValueError):
            SuperdenseCoding((0, 2)).build_circuit()
