"""Backend adapter layer supporting Aer, IBM Quantum Runtime, and qBraid.

Provides explicit backend selection for protocol execution. Credentials are
read strictly from environment variables and are never hardcoded or defaulted silently.
"""

from __future__ import annotations

import os
from typing import Any

from aleshaq.protocols.exceptions import BackendExecutionError, MissingCredentialsError


def get_aer_backend(
    method: str = "automatic",
    noise_model: Any | None = None,
    **kwargs: Any,
) -> Any:
    """Instantiate a local Qiskit Aer simulator backend.

    Args:
        method: Aer simulation method (e.g. "statevector", "density_matrix", "automatic").
        noise_model: Optional Qiskit Aer NoiseModel.
        **kwargs: Additional options forwarded to AerSimulator.

    Returns:
        AerSimulator instance.

    Raises:
        BackendExecutionError: If qiskit-aer is not installed.
    """
    try:
        from qiskit_aer import AerSimulator
    except ImportError as exc:
        raise BackendExecutionError(
            "qiskit-aer is required for local simulation. Install it via 'pip install qiskit-aer' "
            "or 'pip install aleshaq-sdk[sim]'."
        ) from exc

    return AerSimulator(method=method, noise_model=noise_model, **kwargs)


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

    Credentials are read from arguments or the environment:
        Token: `token` parameter, or `QISKIT_IBM_TOKEN` / `IBM_QUANTUM_TOKEN` env vars.
        Instance: `instance` parameter, or `QISKIT_IBM_INSTANCE` / `IBM_QUANTUM_INSTANCE` env vars.
        Channel: `channel` parameter, or `QISKIT_IBM_CHANNEL` (auto-detected as 'ibm_cloud' if an instance CRN is provided).

    Args:
        backend_name: Specific backend name (e.g. "ibm_brisbane", "ibm_kyoto", "ibmq_qasm_simulator").
        token: IBM Quantum API token.
        instance: IBM Quantum instance/hub-group-project (e.g. "ibm-q/open/main").
        channel: IBM Quantum channel type ('ibm_quantum' or 'ibm_cloud').
        least_busy: If True and backend_name is None, select the least busy operational backend.
        min_qubits: Minimum number of qubits required when choosing least_busy.

    Returns:
        IBMBackend instance.

    Raises:
        MissingCredentialsError: If no valid token is found.
        BackendExecutionError: If qiskit-ibm-runtime is not installed or backend retrieval fails.
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
        # Check if an account is already saved on disk
        try:
            service = QiskitRuntimeService(channel=chan, instance=inst)
        except Exception as exc:
            raise MissingCredentialsError(
                "IBM Quantum credentials not found. Please provide an API token via the 'token' argument, "
                "set the 'QISKIT_IBM_TOKEN' environment variable, or save your account with QiskitRuntimeService.save_account()."
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

    # Default to first operational backend or simulator
    backends = service.backends(operational=True)
    if not backends:
        raise BackendExecutionError("No operational IBM Quantum backends found for your account.")
    return backends[0]


def get_qbraid_backend(
    device_id: str,
    *,
    api_key: str | None = None,
) -> Any:
    """Obtain a qBraid-provided quantum backend.

    Credentials are read from the `api_key` argument or `QBRAID_API_KEY` env var.

    Args:
        device_id: qBraid device identifier (e.g. "aws_oqc_lucy", "ibm_q_simulator", "quera_aquila").
        api_key: qBraid API key.

    Returns:
        A Qiskit-compatible backend provider device.

    Raises:
        MissingCredentialsError: If no qBraid API key is configured.
        BackendExecutionError: If qbraid package is missing or device loading fails.
    """
    key = api_key or os.environ.get("QBRAID_API_KEY")
    if not key:
        raise MissingCredentialsError(
            "qBraid API key not found. Please provide an API key via the 'api_key' argument "
            "or set the 'QBRAID_API_KEY' environment variable."
        )

    try:
        from qbraid.providers import QbraidProvider  # type: ignore[import-untyped]
    except ImportError:
        try:
            import qbraid  # type: ignore[import-untyped]
            provider = qbraid.get_provider(api_key=key)
            return provider.get_device(device_id)
        except ImportError as exc:
            raise BackendExecutionError(
                "The 'qbraid' library is required to target qBraid backends. "
                "Install it via 'pip install aleshaq-sdk[qbraid]'."
            ) from exc

    try:
        provider = QbraidProvider(api_key=key)
        device = provider.get_device(device_id)
        # Convert or expose as Qiskit backend if supported
        if hasattr(device, "get_backend"):
            return device.get_backend()
        return device
    except Exception as exc:
        raise BackendExecutionError(f"Failed to retrieve qBraid device '{device_id}': {exc}") from exc


def get_backend(
    provider: str = "aer",
    name: str | None = None,
    **kwargs: Any,
) -> Any:
    """Unified backend resolver.

    Args:
        provider: Provider identifier ('aer', 'ibm', 'qbraid').
        name: Name or device ID on the selected provider.
        **kwargs: Provider-specific configuration options.

    Returns:
        Backend instance.

    Raises:
        ValueError: If provider is unrecognized.
    """
    prov = provider.lower()
    if prov in ("aer", "simulator", "local"):
        return get_aer_backend(**kwargs)
    elif prov in ("ibm", "ibm_quantum", "runtime"):
        return get_ibm_backend(backend_name=name, **kwargs)
    elif prov in ("qbraid", "qbraid_cloud"):
        if not name:
            raise ValueError("A device_id (name) is required when selecting provider='qbraid'.")
        return get_qbraid_backend(device_id=name, **kwargs)
    else:
        raise ValueError(
            f"Unknown backend provider: '{provider}'. Supported providers are: 'aer', 'ibm', 'qbraid'."
        )
