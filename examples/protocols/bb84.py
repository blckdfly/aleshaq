"""BB84 QKD simulation example."""

from aleshaq.protocols.cryptographic import BB84

protocol = BB84(n_bits=100, seed=42)
result = protocol.run()

print(f"Total qubits sent: {len(result.alice_bits)}")
print(f"Sifted key length: {len(result.sifted_key_alice)}")
print(f"QBER: {result.qber:.4f}")
print(f"Keys match: {result.sifted_key_alice == result.sifted_key_bob}")
print(f"First 20 sifted key bits: {result.sifted_key_alice[:20]}")
