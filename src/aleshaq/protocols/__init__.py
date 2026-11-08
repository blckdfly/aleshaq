"""Aleshnatt Quantum Protocols.

Composable quantum information and communication protocols.
"""

from aleshaq.protocols.communication import (
    SuperdenseCoding,
    SuperdenseResult,
    Teleportation,
    TeleportationResult,
)
from aleshaq.protocols.cryptographic import (
    BB84,
    BB84Result,
    B92,
    B92Result,
    DecoyStateBB84,
    DecoyStateResult,
    E91,
    E91Result,
)
from aleshaq.protocols.distributed import QuantumSecretSharing, SecretSharingResult
from aleshaq.protocols.exceptions import (
    BackendExecutionError,
    InsufficientRoundsError,
    MissingCredentialsError,
    ProtocolError,
    SiftingError,
)
from aleshaq.protocols.execution import (
    BenchmarkEntry,
    CalibrationMetrics,
    ProtocolBenchmark,
    extract_calibration_metrics,
    get_aer_backend,
    get_backend,
    get_ibm_backend,
    get_qbraid_backend,
)

__version__ = "0.1.0"

__all__ = [
    # Communication
    "Teleportation",
    "TeleportationResult",
    "SuperdenseCoding",
    "SuperdenseResult",
    # Cryptographic
    "BB84",
    "BB84Result",
    "B92",
    "B92Result",
    "E91",
    "E91Result",
    "DecoyStateBB84",
    "DecoyStateResult",
    # Distributed
    "QuantumSecretSharing",
    "SecretSharingResult",
    # Execution & Calibration
    "get_backend",
    "get_aer_backend",
    "get_ibm_backend",
    "get_qbraid_backend",
    "CalibrationMetrics",
    "extract_calibration_metrics",
    "BenchmarkEntry",
    "ProtocolBenchmark",
    # Exceptions
    "ProtocolError",
    "SiftingError",
    "BackendExecutionError",
    "MissingCredentialsError",
    "InsufficientRoundsError",
]
