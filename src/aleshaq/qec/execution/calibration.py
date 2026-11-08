"""Hardware calibration and noise metrics extraction for QEC experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QECCalibrationData:
    """Device calibration data relevant for QEC noise modeling."""

    backend_name: str
    num_qubits: int
    readout_error: dict[int, float] = field(default_factory=dict)
    single_qubit_gate_error: dict[int, float] = field(default_factory=dict)
    two_qubit_gate_error: dict[tuple[int, int], float] = field(default_factory=dict)
    t1_us: dict[int, float] = field(default_factory=dict)
    t2_us: dict[int, float] = field(default_factory=dict)

    @property
    def mean_readout_error(self) -> float:
        if not self.readout_error:
            return 0.0
        return sum(self.readout_error.values()) / len(self.readout_error)

    @property
    def mean_two_qubit_error(self) -> float:
        if not self.two_qubit_gate_error:
            return 0.0
        return sum(self.two_qubit_gate_error.values()) / len(self.two_qubit_gate_error)

    def summary(self) -> str:
        lines = [
            f"QEC Calibration Data: {self.backend_name} ({self.num_qubits} qubits)",
            f"  Mean Readout Error: {self.mean_readout_error:.4%}",
            f"  Mean 2-Qubit Gate Error: {self.mean_two_qubit_error:.4%}",
        ]
        return "\n".join(lines)


def extract_qec_calibration(backend: Any, qubits: list[int] | None = None) -> QECCalibrationData:
    """Extract noise calibration metrics from a backend for QEC simulations.

    Args:
        backend: Target quantum backend or simulator.
        qubits: Optional list of qubit indices.

    Returns:
        QECCalibrationData containing readout and gate error parameters.
    """
    backend_name = getattr(backend, "name", str(backend))
    num_qubits = getattr(backend, "num_qubits", 0)
    target_qubits = qubits if qubits is not None else list(range(num_qubits))

    readout_error: dict[int, float] = {}
    sq_error: dict[int, float] = {}
    tq_error: dict[tuple[int, int], float] = {}
    t1_times: dict[int, float] = {}
    t2_times: dict[int, float] = {}

    target = getattr(backend, "target", None)
    if target is not None:
        try:
            if "measure" in target:
                meas_entry = target["measure"]
                for q in target_qubits:
                    props = meas_entry.get((q,))
                    if props is not None and getattr(props, "error", None) is not None:
                        readout_error[q] = float(props.error)

            for g_name in ["sx", "x", "rz"]:
                if g_name in target:
                    for q in target_qubits:
                        props = target[g_name].get((q,))
                        if props is not None and getattr(props, "error", None) is not None:
                            sq_error[q] = float(props.error)
                    break

            for g_name in ["ecr", "cz", "cx"]:
                if g_name in target:
                    for qargs, props in target[g_name].items():
                        if qargs is not None and isinstance(qargs, (tuple, list)) and len(qargs) == 2:
                            q0, q1 = qargs
                            if qubits is None or (q0 in target_qubits and q1 in target_qubits):
                                if props is not None and getattr(props, "error", None) is not None:
                                    tq_error[(q0, q1)] = float(props.error)
                    break
        except Exception:
            pass

    return QECCalibrationData(
        backend_name=backend_name,
        num_qubits=num_qubits,
        readout_error=readout_error,
        single_qubit_gate_error=sq_error,
        two_qubit_gate_error=tq_error,
        t1_us=t1_times,
        t2_us=t2_times,
    )
