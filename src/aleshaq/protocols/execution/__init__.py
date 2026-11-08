"""Execution adapter layer for simulator and hardware quantum backends."""

from aleshaq.protocols.execution.backend import (
    get_aer_backend,
    get_backend,
    get_ibm_backend,
    get_qbraid_backend,
)
from aleshaq.protocols.execution.benchmark import BenchmarkEntry, ProtocolBenchmark
from aleshaq.protocols.execution.calibration import (
    CalibrationMetrics,
    extract_calibration_metrics,
)

__all__ = [
    "get_backend",
    "get_aer_backend",
    "get_ibm_backend",
    "get_qbraid_backend",
    "CalibrationMetrics",
    "extract_calibration_metrics",
    "BenchmarkEntry",
    "ProtocolBenchmark",
]
