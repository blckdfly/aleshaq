"""Tests for networking domain exceptions, circuits, and node/channel representations."""

import pytest
from aleshaq.networking import (
    CapacityExceededError,
    ChannelError,
    ClassicalChannel,
    EntanglementLink,
    EntanglementManager,
    LinkNotFoundError,
    Node,
    QuantumChannel,
    QuantumNetwork,
    build_bell_pair_circuit,
    build_swapping_circuit,
)


def test_node_capacity_and_repr():
    node = Node("alice", qubit_capacity=2)
    assert repr(node) == "Node('alice', capacity=2)"
    idx0 = node.allocate_qubit()
    idx1 = node.allocate_qubit()
    assert idx0 == 0
    assert idx1 == 1

    with pytest.raises(CapacityExceededError):
        node.allocate_qubit()

    node.release_qubit()
    assert node.qubit_count == 1


def test_channel_validation():
    alice = Node("alice")
    bob = Node("bob")

    with pytest.raises(ChannelError):
        QuantumChannel(node_a=alice, node_b=alice)

    with pytest.raises(ChannelError):
        QuantumChannel(node_a=alice, node_b=bob, loss_probability=1.5)

    with pytest.raises(ChannelError):
        ClassicalChannel(node_a=alice, node_b=bob, delay_ms=-1.0)


def test_circuit_builders():
    bell_qc = build_bell_pair_circuit()
    assert bell_qc.num_qubits == 2

    swap_qc = build_swapping_circuit()
    assert swap_qc.num_qubits == 4
    assert swap_qc.num_clbits == 2


def test_entanglement_link_repr_and_errors():
    alice = Node("alice")
    bob = Node("bob")
    charlie = Node("charlie")

    link = EntanglementLink(alice, bob, fidelity=0.95)
    assert "EntanglementLink(alice <-> bob" in repr(link)

    mgr = EntanglementManager()
    link1 = mgr.create_link(alice, bob)
    link2 = mgr.create_link(bob, charlie)

    with pytest.raises(LinkNotFoundError):
        mgr.swap(link1, link2, swap_node=alice)
