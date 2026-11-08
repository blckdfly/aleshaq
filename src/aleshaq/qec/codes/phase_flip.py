"""3-qubit phase-flip code.

Corrects a single phase-flip (Z) error by working in the Hadamard
(X) basis. The encoding is:

    |0_L⟩ = |+++⟩
    |1_L⟩ = |−−−⟩

This is the Hadamard-conjugate of the bit-flip code: encoding
applies H to all qubits, then performs the bit-flip encoding.
Syndrome extraction similarly transforms into the X basis.
"""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister

from aleshaq.qec.codes.base import StabilizerCode


class PhaseFlipCode(StabilizerCode):
    """[[3, 1, 1]] phase-flip code."""

    @property
    def n(self) -> int:
        return 3

    @property
    def k(self) -> int:
        return 1

    @property
    def d(self) -> int:
        return 1

    def encode(self) -> QuantumCircuit:
        data = QuantumRegister(3, "data")
        qc = QuantumCircuit(data, name="PhaseFlipEncode")

        # CNOT fan-out in the computational basis, then
        # rotate all qubits into the X basis.
        qc.cx(0, 1)
        qc.cx(0, 2)
        qc.h(0)
        qc.h(1)
        qc.h(2)

        return qc

    def syndrome_circuit(self) -> QuantumCircuit:
        """Measure ZZ stabilizers on pairs (0,1) and (1,2) in the X basis.

        The syndrome is extracted by rotating into the computational
        basis (H on all data qubits), measuring parities, then
        rotating back.
        """
        data = QuantumRegister(3, "data")
        ancilla = QuantumRegister(2, "anc")
        syn_cr = ClassicalRegister(2, "syn")
        qc = QuantumCircuit(data, ancilla, syn_cr, name="PhaseFlipSyndrome")

        # Rotate data qubits to computational basis for parity checks
        for i in range(3):
            qc.h(data[i])

        # Parity checks (same as bit-flip code in computational basis)
        qc.cx(data[0], ancilla[0])
        qc.cx(data[1], ancilla[0])
        qc.cx(data[1], ancilla[1])
        qc.cx(data[2], ancilla[1])

        qc.measure(ancilla, syn_cr)

        # Rotate back to X basis
        for i in range(3):
            qc.h(data[i])

        return qc

    def recovery_circuit(self, syndrome: int) -> QuantumCircuit:
        """Apply Z correction based on syndrome."""
        data = QuantumRegister(3, "data")
        qc = QuantumCircuit(data, name="PhaseFlipRecover")

        # Syndrome → error qubit mapping (same logic as bit-flip
        # but correction is Z instead of X)
        correction_map = {
            0b01: 0,  # stabilizer (0,1) violated → error on qubit 0
            0b11: 1,  # both violated → error on qubit 1
            0b10: 2,  # stabilizer (1,2) violated → error on qubit 2
        }

        if syndrome in correction_map:
            qc.z(correction_map[syndrome])

        return qc
