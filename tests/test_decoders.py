"""Tests for decoders and syndrome extraction."""

import pytest
from qiskit.circuit import QuantumCircuit

from aleshaq.qec.codes import RepetitionCode
from aleshaq.qec.decoders import LookupTableDecoder, MajorityVoteDecoder
from aleshaq.qec.syndrome import Syndrome, extract_syndrome


class TestSyndrome:

    def test_trivial_syndrome(self):
        s = Syndrome(value=0, n_bits=3)
        assert s.is_trivial
        assert s.bits == [0, 0, 0]

    def test_nontrivial_syndrome(self):
        s = Syndrome(value=0b101, n_bits=3)
        assert not s.is_trivial
        assert s.bits == [1, 0, 1]
        assert str(s) == "101"

    def test_extract_syndrome(self):
        counts = {"00": 500, "01": 300, "11": 200}
        syndromes = extract_syndrome(counts, n_syndrome_bits=2)
        assert len(syndromes) == 3


class TestLookupTableDecoder:

    def test_decode_no_error(self):
        code = RepetitionCode(distance=3)
        decoder = LookupTableDecoder(code)
        recovery = decoder.decode(0)
        assert isinstance(recovery, QuantumCircuit)

    def test_decode_with_error(self):
        code = RepetitionCode(distance=3)
        decoder = LookupTableDecoder(code)
        recovery = decoder.decode(0b01)
        ops = [instr.operation.name for instr in recovery.data]
        assert "x" in ops


class TestMajorityVoteDecoder:

    def test_no_error(self):
        decoder = MajorityVoteDecoder(n_data_qubits=3)
        recovery = decoder.decode(0)
        ops = [instr.operation.name for instr in recovery.data]
        assert "x" not in ops

    def test_single_error(self):
        decoder = MajorityVoteDecoder(n_data_qubits=3)
        recovery = decoder.decode(0b01)
        ops = [instr.operation.name for instr in recovery.data]
        assert "x" in ops
