"""Bell state preparation circuits.

Constructs one of the four Bell states:
    |Φ⁺⟩ = (|00⟩ + |11⟩)/√2   (pair=0)
    |Φ⁻⟩ = (|00⟩ − |11⟩)/√2   (pair=1)
    |Ψ⁺⟩ = (|01⟩ + |10⟩)/√2   (pair=2)
    |Ψ⁻⟩ = (|01⟩ − |10⟩)/√2   (pair=3)
"""

from __future__ import annotations

from qiskit.circuit import QuantumCircuit


_BELL_LABELS = {0: "Φ⁺", 1: "Φ⁻", 2: "Ψ⁺", 3: "Ψ⁻"}


def bell_state(pair: int = 0, *, label: str | None = None) -> QuantumCircuit:
    """Construct a circuit that prepares one of the four Bell states.

    Args:
        pair: Bell pair index (0–3). Selects among Φ⁺, Φ⁻, Ψ⁺, Ψ⁻.
        label: Optional circuit name. Defaults to the Bell state label.

    Returns:
        A 2-qubit QuantumCircuit preparing the requested Bell state.
    """
    if pair not in range(4):
        raise ValueError(f"pair must be 0–3, got {pair}")

    name = label or f"Bell-{_BELL_LABELS[pair]}"
    qc = QuantumCircuit(2, name=name)

    # Φ⁻ and Ψ⁻ differ from their + counterparts by a phase flip on q0.
    if pair in (1, 3):
        qc.x(0)

    # Ψ variants flip q1 before entangling so the
    # anti-correlated basis states appear in the superposition.
    if pair in (2, 3):
        qc.x(1)

    qc.h(0)
    qc.cx(0, 1)
    return qc
