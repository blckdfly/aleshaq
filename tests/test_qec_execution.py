"""Tests for QEC execution, calibration extraction, and code equality."""

import pytest
from qiskit_aer import AerSimulator

from aleshaq.qec.codes import BitFlipCode, PhaseFlipCode, RepetitionCode, ShorCode, SteaneCode
from aleshaq.qec.decoders import LookupTableDecoder, MajorityVoteDecoder
from aleshaq.qec.exceptions import CodeParameterError
from aleshaq.qec.execution import (
    QECCalibrationData,
    extract_qec_calibration,
    get_aer_backend,
    get_backend,
)
from aleshaq.qec.simulation import CodeExperiment


def test_code_repr_and_eq():
    r3 = RepetitionCode(3)
    r3_other = RepetitionCode(3)
    r5 = RepetitionCode(5)
    bf = BitFlipCode()
    pf = PhaseFlipCode()
    shor = ShorCode()
    steane = SteaneCode()

    assert repr(r3) == "RepetitionCode([[3,1,3]])"
    assert r3 == r3_other
    assert r3 != r5
    assert repr(shor) == "ShorCode([[9,1,3]])"
    assert repr(steane) == "SteaneCode([[7,1,3]])"


def test_decoder_repr_and_eq():
    r3 = RepetitionCode(3)
    dec1 = LookupTableDecoder(r3)
    dec2 = LookupTableDecoder(r3)
    maj1 = MajorityVoteDecoder(3)
    maj2 = MajorityVoteDecoder(3)

    assert "LookupTableDecoder" in repr(dec1)
    assert dec1 == dec2
    assert repr(maj1) == "MajorityVoteDecoder(n_data_qubits=3)"
    assert maj1 == maj2


def test_qec_execution_adapter():
    backend = get_backend("aer")
    assert isinstance(backend, AerSimulator)

    cal = extract_qec_calibration(backend, qubits=[0, 1, 2])
    assert isinstance(cal, QECCalibrationData)
    assert cal.num_qubits > 0
    assert "QEC Calibration Data:" in cal.summary()


def test_code_experiment_custom_backend():
    code = RepetitionCode(3)
    backend = get_aer_backend()
    exp = CodeExperiment(code=code, backend=backend)
    res = exp.run(physical_error_rate=0.0, shots=200, seed=42)
    assert res.logical_error_rate == 0.0
    assert "Code [[3,1,3]]" in res.summary()
