"""Aleshnatt Quantum Primitives.

Foundational quantum computing primitives for state preparation, transforms,
parameter estimation, and circuit composition.
"""

from aleshaq.primitives.circuits import (
    OracleInterface,
    append_circuit,
    phase_oracle,
    repeat_circuit,
)
from aleshaq.primitives.estimation import (
    interpret_phase,
    phase_estimation,
)
from aleshaq.primitives.exceptions import (
    BackendExecutionError,
    CircuitCompositionError,
    InvalidStateParameterError,
    MissingCredentialsError,
    PhaseEstimationError,
    PrimitivesError,
)
from aleshaq.primitives.execution import (
    get_aer_backend,
    get_backend,
    get_ibm_backend,
    get_qbraid_backend,
)
from aleshaq.primitives.states import (
    basis_state,
    bell_state,
    ghz_state,
    w_state,
)
from aleshaq.primitives.transforms import (
    controlled_phase_rotation,
    inverse_qft,
    qft,
)

__version__ = "0.1.2"

__all__ = [
    # States
    "bell_state",
    "ghz_state",
    "w_state",
    "basis_state",
    # Transforms
    "qft",
    "inverse_qft",
    "controlled_phase_rotation",
    # Estimation
    "phase_estimation",
    "interpret_phase",
    # Circuits
    "phase_oracle",
    "OracleInterface",
    "append_circuit",
    "repeat_circuit",
    # Execution
    "get_backend",
    "get_aer_backend",
    "get_ibm_backend",
    "get_qbraid_backend",
    # Exceptions
    "PrimitivesError",
    "InvalidStateParameterError",
    "PhaseEstimationError",
    "CircuitCompositionError",
    "BackendExecutionError",
    "MissingCredentialsError",
]
