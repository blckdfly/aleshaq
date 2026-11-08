"""Protocol benchmark suite across simulator and hardware backends."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from aleshaq.protocols.execution.calibration import CalibrationMetrics, extract_calibration_metrics


@dataclass
class BenchmarkEntry:
    """Benchmark result for a single protocol execution on a backend."""

    backend_name: str
    protocol_name: str
    n_rounds: int
    sifted_key_length: int
    sifting_ratio: float
    qber: float | None
    execution_time_seconds: float
    calibration_metrics: CalibrationMetrics | None = None
    extra_metrics: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Format a concise summary of the benchmark entry."""
        qber_str = f"{self.qber:.4%}" if self.qber is not None else "N/A"
        cal_str = ""
        if self.calibration_metrics and self.calibration_metrics.mean_readout_error is not None:
            cal_str = f" | Avg Readout Err: {self.calibration_metrics.mean_readout_error:.3%}"
        return (
            f"[{self.backend_name}] {self.protocol_name} ({self.n_rounds} rounds): "
            f"Sifted Key={self.sifted_key_length} ({self.sifting_ratio:.1%}), "
            f"QBER={qber_str}, Time={self.execution_time_seconds:.3f}s{cal_str}"
        )


class ProtocolBenchmark:
    """Automated benchmark runner comparing protocol performance across backends."""

    def __init__(self, backends: list[Any] | None = None):
        """
        Args:
            backends: List of Qiskit Backend / AerSimulator instances.
        """
        self.backends = backends or []
        self.results: list[BenchmarkEntry] = []

    def add_backend(self, backend: Any) -> None:
        """Add a backend to the benchmark runner."""
        self.backends.append(backend)

    def run_bb84(
        self,
        n_bits: int = 256,
        seed: int | None = 42,
    ) -> list[BenchmarkEntry]:
        """Run BB84 benchmark across all registered backends.

        Args:
            n_bits: Number of raw bits to transmit.
            seed: Random seed for reproducibility.

        Returns:
            List of BenchmarkEntry records.
        """
        from aleshaq.protocols.cryptographic.bb84 import BB84

        entries = []
        for backend in self.backends:
            b_name = getattr(backend, "name", str(backend))
            cal = extract_calibration_metrics(backend)

            protocol = BB84(n_bits=n_bits, seed=seed)
            t0 = time.perf_counter()
            res = protocol.run(backend=backend)
            elapsed = time.perf_counter() - t0

            sifted_len = len(res.sifted_key_alice)
            entry = BenchmarkEntry(
                backend_name=b_name,
                protocol_name="BB84",
                n_rounds=n_bits,
                sifted_key_length=sifted_len,
                sifting_ratio=sifted_len / n_bits if n_bits > 0 else 0.0,
                qber=res.qber,
                execution_time_seconds=elapsed,
                calibration_metrics=cal,
            )
            entries.append(entry)
            self.results.append(entry)

        return entries

    def run_e91(
        self,
        n_pairs: int = 256,
        seed: int | None = 42,
    ) -> list[BenchmarkEntry]:
        """Run E91 benchmark across all registered backends."""
        from aleshaq.protocols.cryptographic.e91 import E91

        entries = []
        for backend in self.backends:
            b_name = getattr(backend, "name", str(backend))
            cal = extract_calibration_metrics(backend)

            protocol = E91(n_pairs=n_pairs, seed=seed)
            t0 = time.perf_counter()
            res = protocol.run(backend=backend)
            elapsed = time.perf_counter() - t0

            sifted_len = len(res.sifted_key_alice)
            entry = BenchmarkEntry(
                backend_name=b_name,
                protocol_name="E91",
                n_rounds=n_pairs,
                sifted_key_length=sifted_len,
                sifting_ratio=sifted_len / n_pairs if n_pairs > 0 else 0.0,
                qber=res.qber,
                execution_time_seconds=elapsed,
                calibration_metrics=cal,
                extra_metrics={"chsh_value": res.chsh_value},
            )
            entries.append(entry)
            self.results.append(entry)

        return entries

    def report(self) -> str:
        """Generate a complete text report of all executed benchmark runs."""
        if not self.results:
            return "No benchmark results available."
        lines = ["=== Protocol Benchmark Report ==="]
        for res in self.results:
            lines.append(res.summary())
        return "\n".join(lines)
