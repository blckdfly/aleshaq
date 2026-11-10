"""Backend adapter for quantum primitives execution across simulator and hardware backends."""

from __future__ import annotations

import os
from typing import Any

from aleshaq.primitives.exceptions import BackendExecutionError, MissingCredentialsError


def get_aer_backend(**kwargs: Any) -> Any:
    """Instantiate a local Qiskit Aer simulator backend."""
    try:
        from qiskit_aer import AerSimulator
    except ImportError as exc:
        raise BackendExecutionError(
            "qiskit-aer is required for local simulation. Install it via 'pip install qiskit-aer'."
        ) from exc
    return AerSimulator(**kwargs)


def get_ibm_backend(
    backend_name: str | None = None,
    *,
    token: str | None = None,
    instance: str | None = None,
    channel: str | None = None,
    least_busy: bool = False,
    min_qubits: int | None = None,
) -> Any:
    """Obtain an IBM Quantum Runtime backend.

    Credentials can be supplied via arguments or environment variables:
        Token: `token` parameter, or `QISKIT_IBM_TOKEN` / `IBM_QUANTUM_TOKEN`.
        Instance: `instance` parameter, or `QISKIT_IBM_INSTANCE` / `IBM_QUANTUM_INSTANCE`.
        Channel: `channel` parameter, or `QISKIT_IBM_CHANNEL` (auto-detected as 'ibm_cloud' if an instance CRN is provided).

    Args:
        backend_name: Specific backend name (e.g., 'ibm_brisbane', 'ibm_marrakesh').
        token: IBM Quantum API token or IBM Cloud IAM API key.
        instance: IBM Quantum hub/group/project or IBM Cloud instance CRN.
        channel: Service channel ('ibm_cloud' or 'ibm_quantum').
        least_busy: If True and backend_name is None, select the least-busy operational backend.
        min_qubits: Minimum number of physical qubits required when selecting least_busy.

    Returns:
        IBMBackend instance.

    Raises:
        MissingCredentialsError: If credentials cannot be located.
        BackendExecutionError: If qiskit-ibm-runtime is missing or backend loading fails.
    """
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService  # type: ignore[import-untyped,import-not-found]
    except ImportError as exc:
        raise BackendExecutionError(
            "qiskit-ibm-runtime is required to connect to IBM Quantum. "
            "Install it via 'pip install aleshaq-sdk[ibm]'."
        ) from exc

    api_token = token or os.environ.get("QISKIT_IBM_TOKEN") or os.environ.get("IBM_QUANTUM_TOKEN")
    inst = instance or os.environ.get("QISKIT_IBM_INSTANCE") or os.environ.get("IBM_QUANTUM_INSTANCE")
    chan = channel or os.environ.get("QISKIT_IBM_CHANNEL")
    if not chan:
        chan = "ibm_cloud" if (inst and inst.startswith("crn:")) else "ibm_quantum"

    if not api_token:
        try:
            service = QiskitRuntimeService(channel=chan, instance=inst)
        except Exception as exc:
            raise MissingCredentialsError(
                "IBM Quantum credentials not found. Please set the 'QISKIT_IBM_TOKEN' environment variable."
            ) from exc
    else:
        service = QiskitRuntimeService(channel=chan, token=api_token, instance=inst)

    if backend_name:
        try:
            return service.backend(backend_name)
        except Exception as exc:
            raise BackendExecutionError(f"Failed to load IBM backend '{backend_name}': {exc}") from exc

    if least_busy:
        try:
            return service.least_busy(min_num_qubits=min_qubits or 1, operational=True)
        except Exception as exc:
            raise BackendExecutionError(f"Failed to find least busy IBM backend: {exc}") from exc

    backends = service.backends(operational=True)
    if not backends:
        raise BackendExecutionError("No operational IBM Quantum backends found for your account.")
    return backends[0]


def get_qbraid_backend(
    device_id: str,
    *,
    api_key: str | None = None,
) -> Any:
    """Obtain a qBraid-provided quantum backend."""
    key = api_key or os.environ.get("QBRAID_API_KEY")
    if not key:
        raise MissingCredentialsError(
            "qBraid API key not found. Please set the 'QBRAID_API_KEY' environment variable."
        )

    try:
        from qbraid.providers import QbraidProvider  # type: ignore[import-untyped]
        provider = QbraidProvider(api_key=key)
        device = provider.get_device(device_id)
        if hasattr(device, "get_backend"):
            return device.get_backend()
        return device
    except ImportError as exc:
        raise BackendExecutionError(
            "The 'qbraid' library is required to target qBraid backends. "
            "Install it via 'pip install aleshaq-sdk[qbraid]'."
        ) from exc
    except Exception as exc:
        raise BackendExecutionError(f"Failed to retrieve qBraid device '{device_id}': {exc}") from exc


def get_backend(
    provider: str = "aer",
    name: str | None = None,
    **kwargs: Any,
) -> Any:
    """Unified backend resolver for primitives execution."""
    prov = provider.lower()
    if prov in ("aer", "simulator", "local"):
        return get_aer_backend(**kwargs)
    elif prov in ("ibm", "ibm_quantum", "runtime"):
        return get_ibm_backend(backend_name=name, **kwargs)
    elif prov in ("qbraid", "qbraid_cloud"):
        if not name:
            raise ValueError("device_id (name) is required for qBraid provider.")
        return get_qbraid_backend(device_id=name, **kwargs)
    else:
        raise ValueError(f"Unknown provider '{provider}'. Supported: 'aer', 'ibm', 'qbraid'.")
