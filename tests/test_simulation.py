"""Tests for QEC simulation experiments."""

import pytest
from aleshaq.qec.codes import RepetitionCode
from aleshaq.qec.noise import bit_flip_noise
from aleshaq.qec.simulation import CodeExperiment


class TestCodeExperiment:

    def test_no_noise_zero_logical_errors(self):
        """Without noise, the logical error rate should be zero."""
        code = RepetitionCode(distance=3)
        experiment = CodeExperiment(code)
        result = experiment.run(
            physical_error_rate=0.0,
            shots=1000,
            seed=42,
        )
        assert result.logical_error_rate == 0.0
        assert result.logical_errors == 0

    def test_high_noise_nonzero_errors(self):
        """With significant noise, some logical errors should occur."""
        code = RepetitionCode(distance=3)
        model = bit_flip_noise(0.2)
        experiment = CodeExperiment(code, noise_model=model)
        result = experiment.run(
            physical_error_rate=0.2,
            shots=1000,
            seed=42,
        )
        assert result.logical_error_rate > 0.0

    def test_sweep(self):
        """Error rate sweep should return results for each rate."""
        code = RepetitionCode(distance=3)
        experiment = CodeExperiment(code)
        rates = [0.0, 0.05, 0.1]
        results = experiment.sweep(
            error_rates=rates,
            noise_factory=bit_flip_noise,
            shots=500,
            seed=42,
        )
        assert len(results) == 3
        # No noise → no errors
        assert results[0].logical_error_rate == 0.0
        # Logical error rate should generally increase with physical rate
        assert results[-1].logical_error_rate >= results[0].logical_error_rate

    def test_result_fields(self):
        code = RepetitionCode(distance=3)
        experiment = CodeExperiment(code)
        result = experiment.run(physical_error_rate=0.0, shots=100, seed=42)
        assert result.code_label == "[[3,1,3]]"
        assert result.total_shots == 100
