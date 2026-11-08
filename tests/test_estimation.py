"""Tests for phase estimation."""

import numpy as np
import pytest
from qiskit.circuit import QuantumCircuit
from qiskit_aer import AerSimulator

from aleshaq.primitives.estimation import phase_estimation, interpret_phase


class TestPhaseEstimation:

    def test_known_eigenvalue_t_gate(self):
        """QPE on the T gate should recover phase = 1/8.

        T|1⟩ = e^{iπ/4}|1⟩, so φ = 1/8 (since the eigenvalue is e^{2πiφ}).
        With 3 counting qubits, 1/8 is exactly representable.
        """
        # T gate as a 1-qubit circuit
        t_gate = QuantumCircuit(1, name="T")
        t_gate.t(0)

        # Eigenstate |1⟩ preparation
        eigenstate = QuantumCircuit(1)
        eigenstate.x(0)

        qpe = phase_estimation(t_gate, precision=3, eigenstate_prep=eigenstate)

        sim = AerSimulator()
        from qiskit import transpile
        t_qpe = transpile(qpe, sim)
        result = sim.run(t_qpe, shots=1024, seed_simulator=42).result()
        phases = interpret_phase(result.get_counts(), precision=3)

        # The dominant measurement should correspond to φ = 1/8
        dominant_phase = max(phases, key=phases.get)
        assert dominant_phase == pytest.approx(0.125, abs=1e-10)

    def test_known_eigenvalue_s_gate(self):
        """QPE on the S gate: S|1⟩ = i|1⟩, so φ = 1/4."""
        s_gate = QuantumCircuit(1, name="S")
        s_gate.s(0)

        eigenstate = QuantumCircuit(1)
        eigenstate.x(0)

        qpe = phase_estimation(s_gate, precision=3, eigenstate_prep=eigenstate)

        sim = AerSimulator()
        from qiskit import transpile
        t_qpe = transpile(qpe, sim)
        result = sim.run(t_qpe, shots=1024, seed_simulator=42).result()
        phases = interpret_phase(result.get_counts(), precision=3)

        dominant_phase = max(phases, key=phases.get)
        assert dominant_phase == pytest.approx(0.25, abs=1e-10)

    def test_circuit_dimensions(self):
        u = QuantumCircuit(2)
        u.cx(0, 1)
        qpe = phase_estimation(u, precision=4)
        # 4 counting + 2 target qubits
        assert qpe.num_qubits == 6
        assert qpe.num_clbits == 4

    def test_invalid_precision(self):
        u = QuantumCircuit(1)
        with pytest.raises(ValueError):
            phase_estimation(u, precision=0)

    def test_interpret_phase_roundtrip(self):
        counts = {"001": 500, "010": 500}
        phases = interpret_phase(counts, precision=3)
        assert 0.125 in phases  # 001 -> 1/8
        assert 0.25 in phases   # 010 -> 2/8
