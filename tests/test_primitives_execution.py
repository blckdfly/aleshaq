"""Tests for primitives backend execution and exception handling."""

import os
import pytest
from qiskit_aer import AerSimulator

from aleshaq.primitives.exceptions import (
    CircuitCompositionError,
    InvalidStateParameterError,
    MissingCredentialsError,
    PhaseEstimationError,
)
from aleshaq.primitives.execution import (
    get_aer_backend,
    get_backend,
    get_ibm_backend,
    get_qbraid_backend,
)
from aleshaq.primitives.states import bell_state


def test_get_aer_backend():
    backend = get_aer_backend()
    assert isinstance(backend, AerSimulator)


def test_get_backend_resolver():
    backend = get_backend("aer")
    assert isinstance(backend, AerSimulator)

    with pytest.raises(ValueError):
        get_backend("nonexistent")


def test_missing_credentials():
    old_token = os.environ.pop("QISKIT_IBM_TOKEN", None)
    old_token2 = os.environ.pop("IBM_QUANTUM_TOKEN", None)
    try:
        with pytest.raises(Exception):
            get_ibm_backend(token=None)
    finally:
        if old_token:
            os.environ["QISKIT_IBM_TOKEN"] = old_token
        if old_token2:
            os.environ["IBM_QUANTUM_TOKEN"] = old_token2


def test_bell_state_invalid_name():
    with pytest.raises(ValueError):
        bell_state("invalid_state_name")
