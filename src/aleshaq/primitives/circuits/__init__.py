"""Circuit composition and oracle utilities."""

from aleshaq.primitives.circuits.oracle import phase_oracle, OracleInterface
from aleshaq.primitives.circuits.composition import append_circuit, repeat_circuit

__all__ = ["phase_oracle", "OracleInterface", "append_circuit", "repeat_circuit"]
