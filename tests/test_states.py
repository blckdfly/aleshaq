"""Tests for quantum state preparation primitives."""

import numpy as np
import pytest
from qiskit.quantum_info import Statevector

from aleshaq.primitives.states import bell_state, ghz_state, w_state, computational_basis
from aleshaq.primitives.states.ghz import ghz_state_with_phase


class TestBellState:
    """Verify Bell state preparation produces correct entangled states."""

    def test_phi_plus(self):
        sv = Statevector.from_instruction(bell_state(0))
        probs = sv.probabilities_dict()
        assert probs.get("00", 0) == pytest.approx(0.5, abs=1e-10)
        assert probs.get("11", 0) == pytest.approx(0.5, abs=1e-10)
        assert probs.get("01", 0) == pytest.approx(0.0, abs=1e-10)
        assert probs.get("10", 0) == pytest.approx(0.0, abs=1e-10)

    def test_phi_minus(self):
        sv = Statevector.from_instruction(bell_state(1))
        amplitudes = sv.data
        # Φ⁻ = (|00⟩ − |11⟩)/√2 — relative sign between the two components
        assert abs(amplitudes[0]) == pytest.approx(1 / np.sqrt(2), abs=1e-10)
        assert abs(amplitudes[3]) == pytest.approx(1 / np.sqrt(2), abs=1e-10)
        assert amplitudes[0] * amplitudes[3].conjugate() < 0  # opposite signs

    def test_psi_plus(self):
        sv = Statevector.from_instruction(bell_state(2))
        probs = sv.probabilities_dict()
        assert probs.get("01", 0) == pytest.approx(0.5, abs=1e-10)
        assert probs.get("10", 0) == pytest.approx(0.5, abs=1e-10)

    def test_psi_minus(self):
        sv = Statevector.from_instruction(bell_state(3))
        probs = sv.probabilities_dict()
        assert probs.get("01", 0) == pytest.approx(0.5, abs=1e-10)
        assert probs.get("10", 0) == pytest.approx(0.5, abs=1e-10)

    def test_invalid_pair(self):
        with pytest.raises(ValueError):
            bell_state(5)

    def test_num_qubits(self):
        assert bell_state().num_qubits == 2


class TestGHZState:
    """Verify GHZ state entanglement properties."""

    @pytest.mark.parametrize("n", [2, 3, 4, 5])
    def test_only_all_zero_and_all_one(self, n: int):
        """GHZ state should have amplitude only on |00…0⟩ and |11…1⟩."""
        sv = Statevector.from_instruction(ghz_state(n))
        probs = sv.probabilities_dict()
        for bitstring, prob in probs.items():
            if prob > 1e-10:
                assert bitstring in ("0" * n, "1" * n)

    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_equal_superposition(self, n: int):
        sv = Statevector.from_instruction(ghz_state(n))
        probs = sv.probabilities_dict()
        assert probs.get("0" * n, 0) == pytest.approx(0.5, abs=1e-10)
        assert probs.get("1" * n, 0) == pytest.approx(0.5, abs=1e-10)

    def test_invalid_n(self):
        with pytest.raises(ValueError):
            ghz_state(1)

    def test_phase_variant(self):
        sv = Statevector.from_instruction(ghz_state_with_phase(2, np.pi))
        # With phase π, amplitudes on |00⟩ and |11⟩ pick up a relative phase
        amps = sv.data
        assert abs(amps[0]) == pytest.approx(1 / np.sqrt(2), abs=1e-10)
        assert abs(amps[3]) == pytest.approx(1 / np.sqrt(2), abs=1e-10)


class TestWState:
    """Verify W state produces a uniform single-excitation superposition."""

    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_single_excitation_property(self, n: int):
        """Each term in |W_n⟩ has exactly one qubit in |1⟩."""
        sv = Statevector.from_instruction(w_state(n))
        probs = sv.probabilities_dict()
        for bitstring, prob in probs.items():
            if prob > 1e-8:
                assert bitstring.count("1") == 1, (
                    f"Non-single-excitation term {bitstring} with prob {prob}"
                )

    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_uniform_amplitudes(self, n: int):
        """Each single-excitation term has probability 1/n."""
        sv = Statevector.from_instruction(w_state(n))
        probs = sv.probabilities_dict()
        for bitstring, prob in probs.items():
            if prob > 1e-8:
                assert prob == pytest.approx(1.0 / n, abs=1e-8)

    def test_invalid_n(self):
        with pytest.raises(ValueError):
            w_state(1)


class TestComputationalBasis:
    """Verify computational basis state preparation."""

    def test_zero_state(self):
        sv = Statevector.from_instruction(computational_basis(3, 0))
        probs = sv.probabilities_dict()
        assert probs.get("000", 0) == pytest.approx(1.0, abs=1e-10)

    def test_specific_state(self):
        # |5⟩ = |101⟩ in binary (3 qubits)
        sv = Statevector.from_instruction(computational_basis(3, 5))
        probs = sv.probabilities_dict()
        assert probs.get("101", 0) == pytest.approx(1.0, abs=1e-10)

    def test_max_state(self):
        sv = Statevector.from_instruction(computational_basis(2, 3))
        probs = sv.probabilities_dict()
        assert probs.get("11", 0) == pytest.approx(1.0, abs=1e-10)

    def test_out_of_range(self):
        with pytest.raises(ValueError):
            computational_basis(2, 4)

    def test_negative_index(self):
        with pytest.raises(ValueError):
            computational_basis(2, -1)
