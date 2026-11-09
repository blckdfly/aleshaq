# Aleshnatt Quantum SDK (`aleshaq-sdk`)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Qiskit Compatibility](https://img.shields.io/badge/Qiskit-2.0%2B-6929C4.svg)](https://qiskit.org/)

**Aleshnatt Quantum SDK** (`aleshaq`) is a modular, production-grade Python toolkit for quantum computing, quantum error correction, quantum networking, and quantum cryptographic protocols. Built natively on Qiskit.

---

## Architecture & Packages

`aleshaq` unites the full quantum information stack into four cohesive modules:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        aleshaq-sdk (Top-Level)                         │
├────────────────────────────────────────────────────────────────────────┤
│ 1. aleshaq.primitives  │ Bell/GHZ/W States, QFT, QPE, Oracles, Backend │
├────────────────────────┼───────────────────────────────────────────────┤
│ 2. aleshaq.qec         │ Stabilizers (Shor, Steane), Decoders, Noise   │
├────────────────────────┼───────────────────────────────────────────────┤
│ 3. aleshaq.networking  │ Nodes, Quantum Channels, Swapping, Routing    │
├────────────────────────┼───────────────────────────────────────────────┤
│ 4. aleshaq.protocols   │ QKD (BB84, B92, E91, Decoy), Teleportation    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Installation

```bash
# Base SDK installation:
pip install aleshaq-sdk

# With local simulation (Qiskit Aer):
pip install "aleshaq-sdk[sim]"

# With hardware providers (IBM Quantum Runtime & qBraid):
pip install "aleshaq-sdk[ibm]"
pip install "aleshaq-sdk[qbraid]"

# Complete installation with all dependencies:
pip install "aleshaq-sdk[all]"
```

---

## Quick Start

### 1. Quantum Primitives (`aleshaq.primitives`)

```python
from aleshaq.primitives import bell_state, ghz_state, qft, phase_estimation

# Prepare a Bell state (|Φ⁺⟩) circuit
qc_bell = bell_state(0)
print(qc_bell)

# Generate a 3-qubit Quantum Fourier Transform circuit
qc_qft = qft(n_qubits=3, do_swaps=True)
print(qc_qft)
```

### 2. Quantum Error Correction (`aleshaq.qec`)

```python
from aleshaq.qec import SteaneCode, LookupTableDecoder, extract_syndrome

# Instantiate the 7-qubit Steane [[7,1,3]] code
code = SteaneCode()
encoder_circuit = code.encode()

# Extract stabilizer syndromes
syndrome_qc = code.syndrome_circuit()
```

### 3. Quantum Networking (`aleshaq.networking`)

```python
from aleshaq.networking import QuantumNetwork, Node
from aleshaq.networking.protocols import EntanglementDistribution

# Build a 3-node quantum network
net = QuantumNetwork("Aleshnatt-Network")
alice = Node("Alice", qubit_capacity=4)
repeater = Node("Repeater", qubit_capacity=4)
bob = Node("Bob", qubit_capacity=4)

net.add_node(alice)
net.add_node(repeater)
net.add_node(bob)
net.connect(alice, repeater, length_km=10.0)
net.connect(repeater, bob, length_km=10.0)

# Distribute entanglement over multi-hop routing
dist = EntanglementDistribution(net)
res = dist.distribute("Alice", "Bob")
print(f"End-to-end fidelity: {res.fidelity:.4f}")
```

### 4. Quantum Protocols & Cryptography (`aleshaq.protocols`)

```python
from aleshaq.protocols import BB84, DecoyStateBB84, Teleportation

# Run BB84 QKD Simulation
bb84 = BB84(n_bits=500, eavesdropper_present=False, seed=42)
result = bb84.run()
print(f"Sifted key length: {len(result.sifted_key_alice)}, QBER: {result.qber}")

# Run Decoy-State BB84 with Photon-Number Splitting (PNS) detection
decoy = DecoyStateBB84(n_rounds=1000, mu=0.5, nu=0.1, simulate_pns_attack=False)
decoy_res = decoy.run()
print(f"PNS Attack Detected: {decoy_res.pns_attack_detected}")
```

---

## Development & Testing

```bash
# Clone the repository
git clone https://github.com/naufaziy/aleshaq.git
cd aleshaq

# Install in editable mode with development tools
pip install -e ".[dev]"

# Run tests
pytest
```

---

## License

This project is licensed under the [MIT License](LICENSE).
