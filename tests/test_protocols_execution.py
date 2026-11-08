"""Tests for execution adapter, calibration, and benchmarking."""

import os
import pytest
from qiskit_aer import AerSimulator

from aleshaq.protocols.exceptions import BackendExecutionError, MissingCredentialsError
from aleshaq.protocols.execution import (
    CalibrationMetrics,
    ProtocolBenchmark,
    extract_calibration_metrics,
    get_aer_backend,
    get_backend,
    get_ibm_backend,
    get_qbraid_backend,
)


def test_get_aer_backend():
    backend = get_aer_backend()
    assert isinstance(backend, AerSimulator)


def test_get_backend_resolver():
    backend = get_backend("aer")
    assert isinstance(backend, AerSimulator)

    with pytest.raises(ValueError):
        get_backend("unknown_provider")


def test_missing_ibm_credentials_raises():
    old_token = os.environ.pop("QISKIT_IBM_TOKEN", None)
    old_token2 = os.environ.pop("IBM_QUANTUM_TOKEN", None)
    try:
        with pytest.raises((MissingCredentialsError, BackendExecutionError)):
            get_ibm_backend(token=None)
    finally:
        if old_token:
            os.environ["QISKIT_IBM_TOKEN"] = old_token
        if old_token2:
            os.environ["IBM_QUANTUM_TOKEN"] = old_token2


def test_missing_qbraid_credentials_raises():
    old_key = os.environ.pop("QBRAID_API_KEY", None)
    try:
        with pytest.raises((MissingCredentialsError, BackendExecutionError)):
            get_qbraid_backend("aws_oqc_lucy", api_key=None)
    finally:
        if old_key:
            os.environ["QBRAID_API_KEY"] = old_key


def test_calibration_metrics_aer():
    backend = AerSimulator()
    metrics = extract_calibration_metrics(backend, qubits=[0, 1])
    assert isinstance(metrics, CalibrationMetrics)
    assert metrics.num_qubits > 0
    summary = metrics.summary()
    assert "Backend:" in summary


def test_protocol_benchmark():
    backend = AerSimulator()
    benchmark = ProtocolBenchmark(backends=[backend])
    entries = benchmark.run_bb84(n_bits=64, seed=42)
    assert len(entries) == 1
    assert entries[0].protocol_name == "BB84"
    assert entries[0].n_rounds == 64
    assert entries[0].sifted_key_length > 0
    report = benchmark.report()
    assert "Protocol Benchmark Report" in report
