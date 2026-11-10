"""Aleshnatt Quantum SDK (`aleshaq`).

Comprehensive Python SDK for quantum information science:
- `aleshaq.primitives`: Foundational quantum computing circuits, state preparation, and transforms.
- `aleshaq.qec`: Stabilizer codes, decoders, noise models, and syndrome extraction.
- `aleshaq.networking`: Quantum network modeling, routing, channels, and multi-hop entanglement distribution.
- `aleshaq.protocols`: Quantum key distribution (BB84, B92, E91, Decoy-State), teleportation, and distributed protocols.
"""

from aleshaq import networking, primitives, protocols, qec

__version__ = "0.1.2"
__author__ = "Naufal Ziyaadaturrahman"

__all__ = [
    "__version__",
    "primitives",
    "qec",
    "networking",
    "protocols",
]
