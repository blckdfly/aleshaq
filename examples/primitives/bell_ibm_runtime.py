#!/usr/bin/env python3
"""Prepare and measure Bell states on real IBM Quantum Runtime hardware.

Requirements:
    pip install "aleshaq-sdk[ibm]"
    export QISKIT_IBM_TOKEN="your-ibm-quantum-api-token"
"""

import os
import sys

from qiskit import transpile

from aleshaq.primitives import bell_state
from aleshaq.primitives.exceptions import MissingCredentialsError
from aleshaq.primitives.execution import get_ibm_backend


def main() -> None:
    token = os.environ.get("QISKIT_IBM_TOKEN") or os.environ.get("IBM_QUANTUM_TOKEN")
    if not token:
        print("=" * 70, file=sys.stderr)
        print("ERROR: IBM Quantum credentials not found.", file=sys.stderr)
        print("To run against real IBM Quantum hardware:", file=sys.stderr)
        print("  1. Obtain an API token from https://quantum.ibm.com", file=sys.stderr)
        print("  2. Set your environment variable:", file=sys.stderr)
        print("       export QISKIT_IBM_TOKEN='<your_token>'", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

    print("Connecting to IBM Quantum Runtime...")
    try:
        backend_name = os.environ.get("QISKIT_IBM_BACKEND")
        backend = get_ibm_backend(backend_name=backend_name, least_busy=not bool(backend_name), min_qubits=2)
        print(f"Connected to IBM Quantum backend: {backend.name}")
    except MissingCredentialsError as exc:
        print(f"Authentication failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Failed to connect to IBM Quantum: {exc}", file=sys.stderr)
        sys.exit(1)

    # 1. Prepare |Φ⁺⟩ Bell state circuit
    qc = bell_state(0)
    qc.measure_all()

    # 2. Transpile and execute on hardware
    print(f"\n--- Executing |Φ⁺⟩ Bell state circuit on {backend.name} ---")
    t_qc = transpile(qc, backend)
    job = backend.run(t_qc, shots=4096)
    result = job.result()
    counts = result.get_counts()

    print("\n--- Measurement Counts ---")
    print(counts)
    p_00 = counts.get("00", 0) / 4096
    p_11 = counts.get("11", 0) / 4096
    print(f"Correlated pair fraction (|00⟩ + |11⟩): {p_00 + p_11:.2%}")


if __name__ == "__main__":
    main()
