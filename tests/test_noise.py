"""Tests for noise models."""

import pytest
from aleshaq.qec.noise import bit_flip_noise, phase_flip_noise, depolarizing_noise


class TestNoiseModels:

    def test_bit_flip_creates_model(self):
        model = bit_flip_noise(0.01)
        assert model is not None

    def test_phase_flip_creates_model(self):
        model = phase_flip_noise(0.01)
        assert model is not None

    def test_depolarizing_creates_model(self):
        model = depolarizing_noise(0.03)
        assert model is not None

    def test_invalid_probability(self):
        with pytest.raises(ValueError):
            bit_flip_noise(-0.1)
        with pytest.raises(ValueError):
            bit_flip_noise(1.5)

    def test_zero_noise(self):
        """Zero noise rate should create a valid model."""
        model = bit_flip_noise(0.0)
        assert model is not None
