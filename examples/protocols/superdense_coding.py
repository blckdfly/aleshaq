"""Superdense coding example: send 2 classical bits using 1 qubit."""

from aleshaq.protocols.communication import SuperdenseCoding

for message in [(0, 0), (0, 1), (1, 0), (1, 1)]:
    protocol = SuperdenseCoding(message)
    result = protocol.run(shots=1024, seed=42)
    print(f"Sent: {message}  →  Decoded: {result.decoded_message}  "
          f"(counts: {result.counts})")
