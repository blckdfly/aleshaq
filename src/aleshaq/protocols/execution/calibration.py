"""Calibration metrics extraction and reporting for quantum backends."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CalibrationMetrics:
    """Hardware calibration metrics for quantum backends.

    Captures device-level noise characteristics (readout errors, gate errors,
    relaxation/dephasing times) when available from the backend target or properties.
    """

    backend_name: str
    num_qubits: int
    readout_error: dict[int, float] = field(default_factory=dict)
    single_qubit_gate_error: dict[int, float] = field(default_factory=dict)
    two_qubit_gate_error: dict[tuple[int, int], float] = field(default_factory=dict)
    t1_times_us: dict[int, float] = field(default_factory=dict)
    t2_times_us: dict[int, float] = field(default_factory=dict)
    timestamp: str | None = None

    @property
    def mean_readout_error(self) -> float | None:
        """Mean readout error across characterized qubits."""
        if not self.readout_error:
            return None
        return sum(self.readout_error.values()) / len(self.readout_error)

    @property
    def mean_two_qubit_error(self) -> float | None:
        """Mean 2-qubit gate error across characterized couplings."""
        if not self.two_qubit_gate_error:
            return None
        return sum(self.two_qubit_gate_error.values()) / len(self.two_qubit_gate_error)

    def summary(self) -> str:
        """Return a formatted text summary of the calibration metrics."""
        lines = [
            f"Backend: {self.backend_name} ({self.num_qubits} qubits)",
        ]
        if self.timestamp:
            lines.append(f"Calibrated at: {self.timestamp}")

        if self.readout_error:
            avg_ro = self.mean_readout_error
            lines.append(f"Mean Readout Error: {avg_ro:.4%}" if avg_ro is not None else "Mean Readout Error: N/A")
        else:
            lines.append("Readout Error: Not available on backend")

        if self.two_qubit_gate_error:
            avg_2q = self.mean_two_qubit_error
            lines.append(f"Mean 2-Qubit Gate Error: {avg_2q:.4%}" if avg_2q is not None else "Mean 2-Qubit Gate Error: N/A")
        else:
            lines.append("2-Qubit Gate Error: Not available on backend")

        return "\n".join(lines)


def extract_calibration_metrics(
    backend: Any,
    qubits: list[int] | None = None,
) -> CalibrationMetrics:
    """Extract calibration metrics from a Qiskit backend or simulator.

    Inspects `backend.target` (Qiskit V2) or `backend.properties()` (Qiskit V1)
    to collect readout errors, single-qubit gate errors, two-qubit gate errors,
    and T1/T2 times where available.

    Args:
        backend: A Qiskit Backend instance (Aer, IBM, qBraid, etc.).
        qubits: Optional subset of qubit indices to extract metrics for.
            If None, all available qubits on the backend are included.

    Returns:
        A populated CalibrationMetrics instance.
    """
    backend_name = getattr(backend, "name", str(backend))
    num_qubits = getattr(backend, "num_qubits", 0)

    target_qubits = qubits if qubits is not None else list(range(num_qubits))

    readout_error: dict[int, float] = {}
    sq_error: dict[int, float] = {}
    tq_error: dict[tuple[int, int], float] = {}
    t1_times: dict[int, float] = {}
    t2_times: dict[int, float] = {}
    timestamp: str | None = None

    # Check for Target (BackendV2 API)
    target = getattr(backend, "target", None)
    if target is not None:
        try:
            # Measure error
            if "measure" in target:
                measure_entry = target["measure"]
                for q in target_qubits:
                    props = measure_entry.get((q,))
                    if props is not None and getattr(props, "error", None) is not None:
                        readout_error[q] = float(props.error)

            # Single-qubit errors (SX or X)
            for g_name in ["sx", "x", "rz"]:
                if g_name in target:
                    for q in target_qubits:
                        props = target[g_name].get((q,))
                        if props is not None and getattr(props, "error", None) is not None:
                            sq_error[q] = float(props.error)
                    break

            # Two-qubit errors (ECR, CZ, CX)
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

    # Fallback / augment with properties() if available
    properties = getattr(backend, "properties", None)
    if callable(properties):
        try:
            props = properties()
            if props is not None:
                if hasattr(props, "last_update_date"):
                    timestamp = str(props.last_update_date)
                for q in target_qubits:
                    try:
                        if not readout_error.get(q):
                            ro = props.readout_error(q)
                            if ro is not None:
                                readout_error[q] = float(ro)
                    except Exception:
                        pass
                    try:
                        t1 = props.t1(q)
                        if t1 is not None:
                            t1_times[q] = float(t1 * 1e6)  # convert seconds to microseconds
                    except Exception:
                        pass
                    try:
                        t2 = props.t2(q)
                        if t2 is not None:
                            t2_times[q] = float(t2 * 1e6)
                    except Exception:
                        pass
        except Exception:
            pass

    return CalibrationMetrics(
        backend_name=backend_name,
        num_qubits=num_qubits,
        readout_error=readout_error,
        single_qubit_gate_error=sq_error,
        two_qubit_gate_error=tq_error,
        t1_times_us=t1_times,
        t2_times_us=t2_times,
        timestamp=timestamp,
    )
