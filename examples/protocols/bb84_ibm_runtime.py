#!/usr/bin/env python3
"""Run BB84 QKD protocol on IBM Quantum Runtime hardware with calibration reporting.

Security status: see README "Security Model" section.
This is a gate-level protocol simulation running on quantum hardware.
Executing on real quantum hardware characterizes device-level noise and error rates;
it does not constitute a physical, tamper-evident QKD channel.

Requirements:
    pip install "aleshaq-sdk[ibm]"
    export QISKIT_IBM_TOKEN="your-ibm-quantum-api-token"
"""

import os
import sys

from aleshaq.protocols import BB84
from aleshaq.protocols.exceptions import MissingCredentialsError
from aleshaq.protocols.execution import extract_calibration_metrics, get_ibm_backend


def main() -> None:
    token = os.environ.get("QISKIT_IBM_TOKEN") or os.environ.get("IBM_QUANTUM_TOKEN")
    if not token:
        print("=" * 70, file=sys.stderr)
        print("ERROR: IBM Quantum credentials not found.", file=sys.stderr)
        print("To run against real IBM Quantum hardware:", file=sys.stderr)
        print("  1. Obtain an API token from https://quantum.ibm.com", file=sys.stderr)
        print("  2. Set your environment variable:", file=sys.stderr)
        print("       export QISKIT_IBM_TOKEN='<your_token>'", file=sys.stderr)
        print("  3. Optional: specify backend instance:", file=sys.stderr)
        print("       export QISKIT_IBM_INSTANCE='<hub/group/project>'", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

    print("Authenticating with IBM Quantum Runtime...")
    try:
        # Select least busy operational backend or specified target
        backend_name = os.environ.get("QISKIT_IBM_BACKEND")
        backend = get_ibm_backend(
            backend_name=backend_name,
            least_busy=True if not backend_name else False,
            min_qubits=1,
        )
        print(f"Connected to IBM Quantum backend: {backend.name}")
    except MissingCredentialsError as exc:
        print(f"Authentication failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Failed to connect to IBM Quantum: {exc}", file=sys.stderr)
        sys.exit(1)

    # 1. Extract and display hardware calibration metrics
    print("\n--- Hardware Calibration Metrics ---")
    calibration = extract_calibration_metrics(backend, qubits=[0, 1])
    print(calibration.summary())

    # 2. Run BB84 protocol on real hardware
    n_bits = 64
    print(f"\n--- Executing BB84 ({n_bits} raw bits) on {backend.name} ---")
    protocol = BB84(n_bits=n_bits, seed=100)
    result = protocol.run(backend=backend)

    # 3. Report protocol outcomes
    print("\n--- Protocol Execution Results ---")
    print(f"Raw bits sent:         {n_bits}")
    print(f"Sifted key length:     {result.key_length}")
    print(f"Sifting efficiency:    {result.key_length / n_bits:.1%}")
    if result.qber is not None:
        print(f"Hardware QBER:         {result.qber:.4%}")
    else:
        print("Hardware QBER:         N/A (No matching bases)")
    print(f"Alice sifted key:      {result.sifted_key_alice[:16]}... (first 16 bits)")
    print(f"Bob sifted key:        {result.sifted_key_bob[:16]}... (first 16 bits)")


if __name__ == "__main__":
    main()
