"""Aleshnatt Quantum Networking.

Abstractions for modeling and experimenting with distributed quantum network systems.
"""

from aleshaq.networking.channels import ClassicalChannel, QuantumChannel
from aleshaq.networking.entanglement import (
    EntanglementLink,
    EntanglementManager,
    build_bell_pair_circuit,
    build_swapping_circuit,
)
from aleshaq.networking.exceptions import (
    CapacityExceededError,
    ChannelError,
    LinkNotFoundError,
    NetworkError,
    RoutingError,
)
from aleshaq.networking.network import QuantumNetwork
from aleshaq.networking.nodes import Node
from aleshaq.networking.protocols import DistributionResult, EntanglementDistribution
from aleshaq.networking.routing import ShortestPathRouter, Topology

__version__ = "0.1.2"

__all__ = [
    # Top-level
    "QuantumNetwork",
    # Nodes
    "Node",
    # Channels
    "QuantumChannel",
    "ClassicalChannel",
    # Entanglement
    "EntanglementLink",
    "EntanglementManager",
    "build_bell_pair_circuit",
    "build_swapping_circuit",
    # Routing
    "Topology",
    "ShortestPathRouter",
    # Protocols
    "EntanglementDistribution",
    "DistributionResult",
    # Exceptions
    "NetworkError",
    "CapacityExceededError",
    "ChannelError",
    "RoutingError",
    "LinkNotFoundError",
]
