"""QEC code experiment runner.

Provides utilities for running encode → noise → syndrome → decode
experiments and measuring logical error rates.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from qiskit.circuit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel

from aleshaq.qec.codes.base import StabilizerCode
from aleshaq.qec.execution.calibration import QECCalibrationData, extract_qec_calibration


@dataclass
class ExperimentResult:
    """Result of a QEC experiment run."""

    physical_error_rate: float
    logical_error_rate: float
    total_shots: int
    logical_errors: int
    code_label: str
    calibration_data: QECCalibrationData | None = None

    def summary(self) -> str:
        """Format a summary string of the experiment outcome."""
        cal_info = ""
        if self.calibration_data and self.calibration_data.mean_readout_error > 0:
            cal_info = f" [Avg HW Readout Err: {self.calibration_data.mean_readout_error:.3%}]"
        return (
            f"Code {self.code_label} | Physical p={self.physical_error_rate:.4f} "
            f"-> Logical Error Rate={self.logical_error_rate:.4%} "
            f"({self.logical_errors}/{self.total_shots} errors){cal_info}"
        )


class CodeExperiment:
    """Run error correction experiments on a given code.

    Measures logical error suppression across physical error rates and backends.
    """

    def __init__(
        self,
        code: StabilizerCode,
        noise_model: NoiseModel | None = None,
        backend: Any | None = None,
    ):
        self._code = code
        self._noise_model = noise_model
        self._backend = backend

    @property
    def code(self) -> StabilizerCode:
        return self._code

    def run(
        self,
        physical_error_rate: float,
        noise_model: NoiseModel | None = None,
        backend: Any | None = None,
        shots: int = 10000,
        seed: int | None = None,
    ) -> ExperimentResult:
        """Run the experiment and measure the logical error rate.

        Args:
            physical_error_rate: Physical error rate for labeling/reference.
            noise_model: Optional Qiskit Aer noise model.
            backend: Target backend (AerSimulator or real hardware).
            shots: Number of experiment repetitions.
            seed: Random seed for reproducibility.
        """
        from qiskit import transpile

        model = noise_model if noise_model is not None else self._noise_model
        target_backend = backend if backend is not None else self._backend

        # Extract calibration if targeting hardware
        cal_data = None
        if target_backend is not None:
            cal_data = extract_qec_calibration(target_backend)

        encode_circuit = self._code.encode()
        n_data = encode_circuit.num_qubits

        data = QuantumRegister(n_data, "data")
        meas = ClassicalRegister(n_data, "meas")
        qc = QuantumCircuit(data, meas, name=f"Experiment-{self._code.label}")

        qc.compose(encode_circuit, qubits=data, inplace=True)
        qc.barrier()
        qc.measure(data, meas)

        if target_backend is None:
            target_backend = AerSimulator(noise_model=model)

        t_qc = transpile(qc, target_backend)

        run_kwargs: dict[str, Any] = {"shots": shots}
        if seed is not None and hasattr(target_backend, "set_options"):
            run_kwargs["seed_simulator"] = seed

        result = target_backend.run(t_qc, **run_kwargs).result()
        counts = result.get_counts()

        logical_errors = self._count_logical_errors(counts)

        return ExperimentResult(
            physical_error_rate=physical_error_rate,
            logical_error_rate=logical_errors / shots if shots > 0 else 0.0,
            total_shots=shots,
            logical_errors=logical_errors,
            code_label=self._code.label,
            calibration_data=cal_data,
        )

    def _count_logical_errors(self, counts: dict[str, int]) -> int:
        """Count shots where the logical qubit has flipped via majority vote."""
        errors = 0
        for bitstring, count in counts.items():
            bits = [int(b) for b in bitstring.replace(" ", "")]
            if sum(bits) > len(bits) / 2:
                errors += count
        return errors

    def sweep(
        self,
        error_rates: list[float],
        noise_factory: Callable[[float], NoiseModel],
        shots: int = 10000,
        seed: int | None = None,
    ) -> list[ExperimentResult]:
        """Run experiments across multiple physical error rates.

        Args:
            error_rates: List of physical error probabilities to sweep.
            noise_factory: Callable returning a NoiseModel for probability p.
            shots: Shots per error rate.
            seed: Base random seed.
        """
        results = []
        for i, p in enumerate(error_rates):
            run_seed = (seed + i) if seed is not None else None
            model = noise_factory(p)
            result = self.run(p, noise_model=model, shots=shots, seed=run_seed)
            results.append(result)
        return results

    def __repr__(self) -> str:
        return f"CodeExperiment(code={self._code})"
