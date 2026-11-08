#!/usr/bin/env python3
"""Run a repetition code experiment on IBM Quantum Runtime hardware with calibration reporting.

Characterizes logical error suppression vs physical device error rates on real hardware.

Requirements:
    pip install "aleshaq-sdk[ibm]"
    export QISKIT_IBM_TOKEN="your-ibm-quantum-api-token"
"""

import os
import sys

from aleshaq.qec import CodeExperiment, RepetitionCode
from aleshaq.qec.exceptions import MissingCredentialsError
from aleshaq.qec.execution import extract_qec_calibration, get_ibm_backend


def main() -> None:
    token = os.environ.get("QISKIT_IBM_TOKEN") or os.environ.get("IBM_QUANTUM_TOKEN")
    if not token:
        print("=" * 70, file=sys.stderr)
        print("ERROR: IBM Quantum credentials not found.", file=sys.stderr)
        print("To run QEC experiments against real IBM Quantum hardware:", file=sys.stderr)
        print("  1. Obtain an API token from https://quantum.ibm.com", file=sys.stderr)
        print("  2. Set your environment variable:", file=sys.stderr)
        print("       export QISKIT_IBM_TOKEN='<your_token>'", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

    print("Connecting to IBM Quantum Runtime...")
    try:
        backend_name = os.environ.get("QISKIT_IBM_BACKEND")
        backend = get_ibm_backend(backend_name=backend_name, least_busy=not bool(backend_name), min_qubits=5)
        print(f"Connected to IBM Quantum backend: {backend.name}")
    except MissingCredentialsError as exc:
        print(f"Authentication failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Failed to connect to IBM Quantum: {exc}", file=sys.stderr)
        sys.exit(1)

    # 1. Extract device calibration
    print("\n--- Hardware Calibration Metrics ---")
    cal = extract_qec_calibration(backend, qubits=[0, 1, 2, 3, 4])
    print(cal.summary())

    # 2. Run distance-3 Repetition Code experiment on real hardware
    code = RepetitionCode(distance=3)
    print(f"\n--- Running {code.label} Experiment on {backend.name} ---")
    experiment = CodeExperiment(code=code, backend=backend)
    result = experiment.run(physical_error_rate=cal.mean_two_qubit_error or 0.01, shots=4096)

    print("\n--- Experiment Results ---")
    print(result.summary())


if __name__ == "__main__":
    main()
