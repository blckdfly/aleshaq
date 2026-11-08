"""3-qubit bit-flip code.

The simplest non-trivial QEC code: [[3, 1, 1]]. Corrects a single
bit-flip (X) error. This is a specific instance of the repetition
code with distance 3.
"""

from __future__ import annotations

from aleshaq.qec.codes.repetition import RepetitionCode


class BitFlipCode(RepetitionCode):
    """[[3, 1, 1]] bit-flip code (distance-3 repetition code)."""

    def __init__(self):
        super().__init__(distance=3)
