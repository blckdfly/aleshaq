"""Steane [[7, 1, 3]] code.

The Steane code is a CSS (Calderbank-Shor-Steane) code based on the
classical [7, 4, 3] Hamming code and its dual. It encodes one logical
qubit into seven physical qubits and corrects any single-qubit error.

The six stabilizer generators are:
    X stabilizers: X₀X₁X₂X₃,  X₁X₂X₄X₅,  X₂X₃X₅X₆
    Z stabilizers: Z₀Z₁Z₂Z₃,  Z₁Z₂Z₄Z₅,  Z₂Z₃Z₅Z₆

The logical operators are:
    X_L = X₀X₁X₂X₃X₄X₅X₆
    Z_L = Z₀Z₁Z₂Z₃Z₄Z₅Z₆
"""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister

from aleshaq.qec.codes.base import StabilizerCode

# Stabilizer support sets (which qubits each stabilizer acts on).
# These come from the parity check matrix of the [7,4,3] Hamming code.
_X_STABS = [
    [0, 1, 2, 3],  # row 0 of H
    [1, 2, 4, 5],  # row 1 of H
    [2, 3, 5, 6],  # row 2 of H
]
_Z_STABS = _X_STABS  # CSS code: same support for X and Z stabilizers


class SteaneCode(StabilizerCode):
    """[[7, 1, 3]] Steane code."""

    @property
    def n(self) -> int:
        return 7

    @property
    def k(self) -> int:
        return 1

    @property
    def d(self) -> int:
        return 3

    def encode(self) -> QuantumCircuit:
        """Encode logical qubit (qubit 0) into 7 physical qubits.

        The encoding circuit prepares the codespace using the Hamming
        code structure. Qubit 0 carries the logical information.
        """
        data = QuantumRegister(7, "data")
        qc = QuantumCircuit(data, name="SteaneEncode")

        # Prepare logical |+⟩ state contributions on ancilla qubits
        # using the structure of the [7,4,3] Hamming code.
        # First, create superposition on generators
        qc.h(0)
        qc.h(1)
        qc.h(2)

        # Build codeword using CNOT from generator qubits
        # These encode the parity check constraints
        qc.cx(0, 3)
        qc.cx(0, 4)
        qc.cx(1, 3)
        qc.cx(1, 5)
        qc.cx(2, 4)
        qc.cx(2, 5)
        qc.cx(2, 6)
        # Qubit 6 also gets contribution from qubits 0, 1
        qc.cx(0, 6)
        qc.cx(1, 6)

        return qc

    def syndrome_circuit(self) -> QuantumCircuit:
        """Measure X and Z stabilizers using 6 ancilla qubits.

        The first 3 syndrome bits correspond to X-stabilizers (detect Z errors).
        The last 3 syndrome bits correspond to Z-stabilizers (detect X errors).
        """
        data = QuantumRegister(7, "data")
        anc = QuantumRegister(6, "anc")
        syn_cr = ClassicalRegister(6, "syn")
        qc = QuantumCircuit(data, anc, syn_cr, name="SteaneSyndrome")

        # Z-stabilizer measurements (detect X errors):
        # Use CNOT from data to ancilla
        for i, stab in enumerate(_Z_STABS):
            for q in stab:
                qc.cx(data[q], anc[i])

        # X-stabilizer measurements (detect Z errors):
        # Use Hadamard-sandwiched CNOT (effectively controlled-Z
        # measured as X via H-basis ancilla)
        for i, stab in enumerate(_X_STABS):
            anc_idx = i + 3
            qc.h(anc[anc_idx])
            for q in stab:
                qc.cx(anc[anc_idx], data[q])
            qc.h(anc[anc_idx])

        qc.measure(anc, syn_cr)
        return qc

    def recovery_circuit(self, syndrome: int) -> QuantumCircuit:
        """Apply correction based on the 6-bit syndrome.

        Bits 0-2: Z-stabilizer syndrome → identifies X error location.
        Bits 3-5: X-stabilizer syndrome → identifies Z error location.

        The syndrome bits form a binary number that directly indexes
        the error qubit (Hamming code property), with 0 meaning no error.
        """
        data = QuantumRegister(7, "data")
        qc = QuantumCircuit(data, name="SteaneRecover")

        x_error_syndrome = syndrome & 0b111
        z_error_syndrome = (syndrome >> 3) & 0b111

        # The Hamming syndrome directly encodes the error position (1-indexed).
        # syndrome = 0 means no error.
        if 1 <= x_error_syndrome <= 7:
            qc.x(x_error_syndrome - 1)

        if 1 <= z_error_syndrome <= 7:
            qc.z(z_error_syndrome - 1)

        return qc
