"""Syndrome extraction utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Syndrome:
    """Representation of a measured error syndrome.

    Attributes:
        value: Integer encoding of the syndrome bits.
        n_bits: Number of syndrome bits.
    """

    value: int
    n_bits: int

    @property
    def bits(self) -> list[int]:
        """Syndrome as a list of individual bits (LSB first)."""
        return [(self.value >> i) & 1 for i in range(self.n_bits)]

    @property
    def is_trivial(self) -> bool:
        """True if the syndrome is all zeros (no error detected)."""
        return self.value == 0

    def __str__(self) -> str:
        return f"{''.join(str(b) for b in reversed(self.bits))}"


def extract_syndrome(counts: dict[str, int], n_syndrome_bits: int) -> dict[Syndrome, int]:
    """Parse syndrome measurement counts into Syndrome objects.

    Assumes that the syndrome bits are stored in a classical register
    that appears in the measurement bitstring. The caller must ensure
    that the bitstring contains only the syndrome bits, or pre-filter
    to the relevant register.

    Args:
        counts: Measurement counts from a syndrome circuit execution.
        n_syndrome_bits: Number of syndrome bits in the measurement.

    Returns:
        Dictionary mapping Syndrome objects to their occurrence counts.
    """
    syndrome_counts: dict[Syndrome, int] = {}
    for bitstring, count in counts.items():
        # Qiskit returns bitstrings in big-endian order
        value = int(bitstring.replace(" ", ""), 2)
        syn = Syndrome(value=value, n_bits=n_syndrome_bits)
        syndrome_counts[syn] = syndrome_counts.get(syn, 0) + count
    return syndrome_counts
