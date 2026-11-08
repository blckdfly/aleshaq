"""Aleshnatt Quantum Error Correction.

Modular tools for quantum error correction research — codes, decoders, noise models,
syndrome extraction, and hardware execution.
"""

from aleshaq.qec.codes import (
    BitFlipCode,
    PhaseFlipCode,
    RepetitionCode,
    ShorCode,
    StabilizerCode,
    SteaneCode,
)
from aleshaq.qec.decoders import Decoder, LookupTableDecoder, MajorityVoteDecoder
from aleshaq.qec.exceptions import (
    BackendExecutionError,
    CodeParameterError,
    MissingCredentialsError,
    QECError,
    SyndromeDecodingError,
)
from aleshaq.qec.execution import (
    QECCalibrationData,
    extract_qec_calibration,
    get_aer_backend,
    get_backend,
    get_ibm_backend,
    get_qbraid_backend,
)
from aleshaq.qec.noise import bit_flip_noise, depolarizing_noise, phase_flip_noise
from aleshaq.qec.simulation import CodeExperiment, ExperimentResult
from aleshaq.qec.syndrome import (
    Syndrome,
    extract_syndrome,
)

__version__ = "0.1.0"

__all__ = [
    # Codes
    "StabilizerCode",
    "RepetitionCode",
    "BitFlipCode",
    "PhaseFlipCode",
    "ShorCode",
    "SteaneCode",
    # Decoders
    "Decoder",
    "LookupTableDecoder",
    "MajorityVoteDecoder",
    # Noise Models
    "bit_flip_noise",
    "phase_flip_noise",
    "depolarizing_noise",
    # Syndrome
    "Syndrome",
    "extract_syndrome",
    # Simulation
    "CodeExperiment",
    "ExperimentResult",
    # Execution & Calibration
    "get_backend",
    "get_aer_backend",
    "get_ibm_backend",
    "get_qbraid_backend",
    "QECCalibrationData",
    "extract_qec_calibration",
    # Exceptions
    "QECError",
    "CodeParameterError",
    "SyndromeDecodingError",
    "BackendExecutionError",
    "MissingCredentialsError",
]
