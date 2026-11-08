"""Tests for quantum error-correcting codes."""

import pytest
from qiskit.quantum_info import Statevector

from aleshaq.qec.codes import RepetitionCode, BitFlipCode, PhaseFlipCode, ShorCode, SteaneCode


class TestRepetitionCode:

    def test_parameters(self):
        code = RepetitionCode(distance=5)
        assert code.n == 5
        assert code.k == 1
        assert code.d == 5
        assert code.label == "[[5,1,5]]"

    def test_encode_zero(self):
        """Encoding |0⟩ should produce |00…0⟩."""
        code = RepetitionCode(distance=3)
        circuit = code.encode()
        sv = Statevector.from_instruction(circuit)
        probs = sv.probabilities_dict()
        assert probs.get("000", 0) == pytest.approx(1.0, abs=1e-10)

    def test_encode_one(self):
        """Encoding |1⟩ should produce |11…1⟩."""
        from qiskit.circuit import QuantumCircuit
        code = RepetitionCode(distance=3)
        qc = QuantumCircuit(3)
        qc.x(0)  # Prepare |1⟩ on logical qubit
        qc.compose(code.encode(), inplace=True)
        sv = Statevector.from_instruction(qc)
        probs = sv.probabilities_dict()
        assert probs.get("111", 0) == pytest.approx(1.0, abs=1e-10)

    def test_syndrome_circuit_dimensions(self):
        code = RepetitionCode(distance=5)
        syn = code.syndrome_circuit()
        assert syn.num_qubits == 5 + 4  # data + ancilla
        assert syn.num_clbits == 4

    def test_syndrome_decode_no_error(self):
        code = RepetitionCode(distance=3)
        recovery = code.recovery_circuit(0)
        assert recovery.num_qubits == 3

    def test_syndrome_decode_single_error(self):
        """Syndrome 0b01 should correct qubit 0 for distance-3 code."""
        code = RepetitionCode(distance=3)
        recovery = code.recovery_circuit(0b01)
        # Check that the recovery circuit has an X gate
        ops = [instr.operation.name for instr in recovery.data]
        assert "x" in ops

    def test_invalid_distance(self):
        with pytest.raises(ValueError):
            RepetitionCode(distance=2)
        with pytest.raises(ValueError):
            RepetitionCode(distance=4)


class TestBitFlipCode:

    def test_is_distance_3_repetition(self):
        code = BitFlipCode()
        assert code.n == 3
        assert code.d == 3


class TestPhaseFlipCode:

    def test_parameters(self):
        code = PhaseFlipCode()
        assert code.n == 3
        assert code.k == 1

    def test_encode_produces_plus_states(self):
        """Encoding |0⟩ should produce |+++⟩."""
        code = PhaseFlipCode()
        circuit = code.encode()
        sv = Statevector.from_instruction(circuit)
        probs = sv.probabilities_dict()
        # |+++⟩ = equal superposition over all 8 computational basis states
        for bitstring in probs:
            if probs[bitstring] > 1e-10:
                assert probs[bitstring] == pytest.approx(1.0 / 8, abs=1e-8)


class TestShorCode:

    def test_parameters(self):
        code = ShorCode()
        assert code.n == 9
        assert code.k == 1
        assert code.d == 3

    def test_encode_dimensions(self):
        code = ShorCode()
        circuit = code.encode()
        assert circuit.num_qubits == 9

    def test_syndrome_circuit_dimensions(self):
        code = ShorCode()
        syn = code.syndrome_circuit()
        assert syn.num_qubits == 9 + 8  # data + ancilla
        assert syn.num_clbits == 8


class TestSteaneCode:

    def test_parameters(self):
        code = SteaneCode()
        assert code.n == 7
        assert code.k == 1
        assert code.d == 3

    def test_encode_dimensions(self):
        code = SteaneCode()
        circuit = code.encode()
        assert circuit.num_qubits == 7

    def test_syndrome_circuit_dimensions(self):
        code = SteaneCode()
        syn = code.syndrome_circuit()
        assert syn.num_qubits == 7 + 6  # data + ancilla
        assert syn.num_clbits == 6

    def test_no_error_syndrome(self):
        """Syndrome 0 should produce an identity recovery circuit."""
        code = SteaneCode()
        recovery = code.recovery_circuit(0)
        ops = [instr.operation.name for instr in recovery.data]
        assert "x" not in ops
        assert "z" not in ops
