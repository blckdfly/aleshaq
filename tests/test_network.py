"""Tests for quantum network abstractions."""

import pytest

from aleshaq.networking import QuantumNetwork, Node, QuantumChannel, ClassicalChannel
from aleshaq.networking.entanglement import EntanglementLink, EntanglementManager
from aleshaq.networking.routing import Topology, ShortestPathRouter
from aleshaq.networking.protocols import EntanglementDistribution


class TestNode:

    def test_create_node(self):
        node = Node("alice")
        assert node.name == "alice"
        assert node.qubit_count == 0

    def test_allocate_qubit(self):
        node = Node("alice", qubit_capacity=2)
        idx = node.allocate_qubit()
        assert idx == 0
        assert node.qubit_count == 1

    def test_capacity_exceeded(self):
        node = Node("alice", qubit_capacity=1)
        node.allocate_qubit()
        with pytest.raises(RuntimeError):
            node.allocate_qubit()

    def test_release_qubit(self):
        node = Node("alice")
        node.allocate_qubit()
        node.release_qubit()
        assert node.qubit_count == 0

    def test_classical_memory(self):
        node = Node("alice")
        node.store("key", 42)
        assert node.retrieve("key") == 42

    def test_identity(self):
        a = Node("alice")
        b = Node("alice")
        assert a == b
        assert hash(a) == hash(b)

    def test_empty_name(self):
        with pytest.raises(ValueError):
            Node("")


class TestQuantumChannel:

    def test_connects(self):
        a, b = Node("a"), Node("b")
        ch = QuantumChannel(a, b)
        assert ch.connects(a)
        assert ch.connects(b)
        assert not ch.connects(Node("c"))

    def test_other_end(self):
        a, b = Node("a"), Node("b")
        ch = QuantumChannel(a, b)
        assert ch.other_end(a) == b
        assert ch.other_end(b) == a

    def test_ideal_channel(self):
        ch = QuantumChannel(Node("a"), Node("b"))
        assert ch.is_ideal

    def test_lossy_channel(self):
        ch = QuantumChannel(Node("a"), Node("b"), loss_probability=0.1)
        assert not ch.is_ideal

    def test_invalid_loss(self):
        with pytest.raises(ValueError):
            QuantumChannel(Node("a"), Node("b"), loss_probability=1.5)


class TestClassicalChannel:

    def test_send(self):
        a, b = Node("a"), Node("b")
        ch = ClassicalChannel(a, b)
        ch.send(a, "msg", "hello")
        assert b.retrieve("msg") == "hello"


class TestTopologyAndRouting:

    def test_add_nodes_and_edges(self):
        t = Topology()
        a, b, c = Node("a"), Node("b"), Node("c")
        t.add_node(a)
        t.add_node(b)
        t.add_node(c)
        t.add_edge(a, b)
        t.add_edge(b, c)
        assert t.has_edge(a, b)
        assert t.has_edge(b, a)
        assert not t.has_edge(a, c)

    def test_shortest_path(self):
        t = Topology()
        nodes = [Node(f"n{i}") for i in range(4)]
        for n in nodes:
            t.add_node(n)
        t.add_edge(nodes[0], nodes[1])
        t.add_edge(nodes[1], nodes[2])
        t.add_edge(nodes[2], nodes[3])

        router = ShortestPathRouter(t)
        path = router.find_path(nodes[0], nodes[3])
        assert path is not None
        assert len(path) == 4
        assert path[0] == nodes[0]
        assert path[-1] == nodes[3]

    def test_no_path(self):
        t = Topology()
        a, b = Node("a"), Node("b")
        t.add_node(a)
        t.add_node(b)
        router = ShortestPathRouter(t)
        assert router.find_path(a, b) is None


class TestEntanglement:

    def test_create_and_query_link(self):
        mgr = EntanglementManager()
        a, b = Node("a"), Node("b")
        link = mgr.create_link(a, b, fidelity=0.95)
        assert link.fidelity == 0.95
        assert mgr.get_link_between(a, b) == link

    def test_swap(self):
        mgr = EntanglementManager()
        a, b, c = Node("a"), Node("b"), Node("c")
        lab = mgr.create_link(a, b, fidelity=0.9)
        lbc = mgr.create_link(b, c, fidelity=0.9)

        new_link = mgr.swap(lab, lbc, swap_node=b, swap_fidelity=0.95)
        assert new_link.involves(a)
        assert new_link.involves(c)
        # Fidelity: 0.9 * 0.9 * 0.95 = 0.7695
        assert new_link.fidelity == pytest.approx(0.7695, abs=1e-10)
        assert new_link.generation == 1

    def test_invalid_fidelity(self):
        with pytest.raises(ValueError):
            EntanglementLink(Node("a"), Node("b"), fidelity=0.0)


class TestQuantumNetwork:

    def test_build_network(self):
        net = QuantumNetwork()
        alice = Node("alice")
        bob = Node("bob")
        net.add_node(alice)
        net.add_node(bob)
        qch, cch = net.connect(alice, bob, loss_probability=0.05)

        assert len(net.nodes) == 2
        assert net.get_channel(alice, bob) == qch

    def test_find_path(self):
        net = QuantumNetwork()
        a, b, c = Node("a"), Node("b"), Node("c")
        net.add_node(a)
        net.add_node(b)
        net.add_node(c)
        net.connect(a, b)
        net.connect(b, c)

        path = net.find_path(a, c)
        assert path is not None
        assert len(path) == 3


class TestEntanglementDistribution:

    def test_distribute_direct(self):
        t = Topology()
        a, b = Node("a"), Node("b")
        t.add_node(a)
        t.add_node(b)
        t.add_edge(a, b)
        mgr = EntanglementManager()

        protocol = EntanglementDistribution(t, mgr, link_fidelity=0.95)
        result = protocol.distribute(a, b)
        assert result.success
        assert result.link is not None
        assert result.link.fidelity == pytest.approx(0.95)

    def test_distribute_multi_hop(self):
        t = Topology()
        nodes = [Node(f"n{i}") for i in range(4)]
        for n in nodes:
            t.add_node(n)
        for i in range(3):
            t.add_edge(nodes[i], nodes[i + 1])

        mgr = EntanglementManager()
        protocol = EntanglementDistribution(
            t, mgr, link_fidelity=0.9, swap_fidelity=0.95
        )
        result = protocol.distribute(nodes[0], nodes[3])
        assert result.success
        # 3 hops, 2 swaps: 0.9^3 * 0.95^2 ≈ 0.657
        expected = (0.9 ** 3) * (0.95 ** 2)
        assert result.link.fidelity == pytest.approx(expected, abs=1e-10)

    def test_distribute_no_path(self):
        t = Topology()
        a, b = Node("a"), Node("b")
        t.add_node(a)
        t.add_node(b)
        mgr = EntanglementManager()
        protocol = EntanglementDistribution(t, mgr)
        result = protocol.distribute(a, b)
        assert not result.success
