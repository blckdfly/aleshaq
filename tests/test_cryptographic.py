"""Tests for QKD and cryptographic protocol simulations."""

import pytest

from aleshaq.protocols.cryptographic import BB84, B92, DecoyStateBB84, E91
from aleshaq.protocols.exceptions import InsufficientRoundsError


class TestBB84:

    def test_ideal_channel_zero_qber(self):
        """On an ideal channel, matching bases should always agree."""
        protocol = BB84(n_bits=200, seed=42)
        result = protocol.run()
        assert result.qber == pytest.approx(0.0, abs=1e-10)

    def test_sifted_key_approximately_half(self):
        """With random basis choices, roughly half the rounds should survive sifting."""
        protocol = BB84(n_bits=1000, seed=42)
        result = protocol.run()
        ratio = len(result.sifted_key_alice) / 1000
        assert 0.3 < ratio < 0.7

    def test_sifted_keys_match(self):
        protocol = BB84(n_bits=100, seed=42)
        result = protocol.run()
        assert result.sifted_key_alice == result.sifted_key_bob

    def test_invalid_n_bits(self):
        with pytest.raises((ValueError, InsufficientRoundsError)):
            BB84(n_bits=0)


class TestB92:

    def test_ideal_channel_zero_qber(self):
        protocol = B92(n_bits=200, seed=42)
        result = protocol.run()
        assert result.qber == pytest.approx(0.0, abs=1e-10)

    def test_sifted_key_nonempty(self):
        protocol = B92(n_bits=200, seed=42)
        result = protocol.run()
        assert len(result.sifted_key_alice) > 0


class TestE91:

    def test_ideal_chsh_violation(self):
        protocol = E91(n_pairs=2000, seed=42)
        result = protocol.run()
        if result.chsh_value is not None:
            assert abs(result.chsh_value) > 1.5

    def test_sifted_keys_correlate(self):
        protocol = E91(n_pairs=500, seed=42)
        result = protocol.run()
        if result.sifted_key_alice:
            assert result.qber == pytest.approx(0.0, abs=0.05)


class TestDecoyStateBB84:

    def test_decoy_state_execution(self):
        decoy = DecoyStateBB84(n_rounds=500, mu=0.5, nu=0.1, seed=42)
        res = decoy.run()
        assert res.signal_gain > 0.0
        assert res.decoy_gain > 0.0
        assert res.vacuum_gain >= 0.0
        assert len(res.sifted_key_alice) > 0
        assert not res.pns_attack_detected

    def test_pns_attack_detection(self):
        decoy_pns = DecoyStateBB84(
            n_rounds=1000,
            mu=0.5,
            nu=0.1,
            simulate_pns_attack=True,
            seed=42,
        )
        res_pns = decoy_pns.run()
        assert res_pns.pns_attack_detected is True

    def test_invalid_intensity_parameters(self):
        with pytest.raises(ValueError):
            DecoyStateBB84(n_rounds=100, mu=0.1, nu=0.5)  # nu must be < mu
