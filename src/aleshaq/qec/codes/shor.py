"""Shor [[9, 1, 3]] code.

The Shor code is the concatenation of the phase-flip code (outer)
with the bit-flip code (inner). It encodes one logical qubit into
nine physical qubits and can correct any single-qubit error.

Encoding:
    |0_L⟩ = (|000⟩ + |111⟩)(|000⟩ + |111⟩)(|000⟩ + |111⟩) / 2√2
    |1_L⟩ = (|000⟩ − |111⟩)(|000⟩ − |111⟩)(|000⟩ − |111⟩) / 2√2

The nine qubits are grouped into three blocks of three. Within each
block, bit-flip errors are corrected. Across blocks, phase-flip
errors are corrected.
"""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister

from aleshaq.qec.codes.base import StabilizerCode


class ShorCode(StabilizerCode):
    """[[9, 1, 3]] Shor code."""

    @property
    def n(self) -> int:
        return 9

    @property
    def k(self) -> int:
        return 1

    @property
    def d(self) -> int:
        return 3

    def encode(self) -> QuantumCircuit:
        data = QuantumRegister(9, "data")
        qc = QuantumCircuit(data, name="ShorEncode")

        # Phase-flip encoding (outer code): fan out qubit 0 across blocks
        qc.cx(0, 3)
        qc.cx(0, 6)

        # Rotate each block head into superposition for GHZ-like encoding
        qc.h(0)
        qc.h(3)
        qc.h(6)

        # Bit-flip encoding (inner code) within each block of 3
        for block_start in (0, 3, 6):
            qc.cx(block_start, block_start + 1)
            qc.cx(block_start, block_start + 2)

        return qc

    def syndrome_circuit(self) -> QuantumCircuit:
        """Measure bit-flip and phase-flip syndromes.

        Bit-flip syndrome: 6 ancilla qubits (2 per block of 3).
        Phase-flip syndrome: 2 ancilla qubits checking inter-block parity.
        Total: 8 syndrome bits.
        """
        data = QuantumRegister(9, "data")
        # 6 bit-flip ancillas + 2 phase-flip ancillas
        anc = QuantumRegister(8, "anc")
        syn_cr = ClassicalRegister(8, "syn")
        qc = QuantumCircuit(data, anc, syn_cr, name="ShorSyndrome")

        # Bit-flip syndromes within each block
        for block_idx in range(3):
            base = block_idx * 3
            anc_base = block_idx * 2
            qc.cx(data[base], anc[anc_base])
            qc.cx(data[base + 1], anc[anc_base])
            qc.cx(data[base + 1], anc[anc_base + 1])
            qc.cx(data[base + 2], anc[anc_base + 1])

        # Phase-flip syndromes: check parity between blocks using
        # all three qubits per block (measures the X⊗X⊗X operator)
        for q in range(3):
            qc.h(data[q])
        for q in range(3, 6):
            qc.h(data[q])

        # Ancilla 6: parity of block 0 and block 1
        for q in range(3):
            qc.cx(data[q], anc[6])
        for q in range(3, 6):
            qc.cx(data[q], anc[6])

        # Ancilla 7: parity of block 1 and block 2
        for q in range(3, 6):
            qc.cx(data[q], anc[7])
        for q in range(6, 9):
            qc.h(data[q])
            qc.cx(data[q], anc[7])

        # Undo Hadamards on data qubits
        for q in range(6):
            qc.h(data[q])
        for q in range(6, 9):
            qc.h(data[q])

        qc.measure(anc, syn_cr)
        return qc

    def recovery_circuit(self, syndrome: int) -> QuantumCircuit:
        """Apply correction based on the 8-bit syndrome.

        Lower 6 bits: bit-flip syndrome (2 bits per block).
        Upper 2 bits: phase-flip syndrome.
        """
        data = QuantumRegister(9, "data")
        qc = QuantumCircuit(data, name="ShorRecover")

        # Bit-flip corrections within each block
        for block_idx in range(3):
            block_syn = (syndrome >> (block_idx * 2)) & 0b11
            base = block_idx * 3
            correction_map = {
                0b01: base,
                0b11: base + 1,
                0b10: base + 2,
            }
            if block_syn in correction_map:
                qc.x(correction_map[block_syn])

        # Phase-flip correction between blocks
        phase_syn = (syndrome >> 6) & 0b11
        phase_map = {
            0b01: 0,   # phase error on block 0
            0b11: 1,   # phase error on block 1
            0b10: 2,   # phase error on block 2
        }
        if phase_syn in phase_map:
            block = phase_map[phase_syn]
            # Z on any qubit in the affected block corrects the phase
            qc.z(block * 3)

        return qc
