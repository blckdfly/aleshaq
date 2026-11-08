"""Repetition code demonstration: encode, detect syndrome, decode."""

from aleshaq.qec.codes import RepetitionCode
from aleshaq.qec.decoders import LookupTableDecoder

code = RepetitionCode(distance=5)
print(f"Code: {code.label}")

# Encoding circuit
encode = code.encode()
print(f"Encoding circuit ({encode.num_qubits} qubits):")
print(encode)

# Syndrome circuit
syn = code.syndrome_circuit()
print(f"\nSyndrome circuit ({syn.num_qubits} qubits, {syn.num_clbits} classical bits):")
print(syn)

# Test syndrome decoding
decoder = LookupTableDecoder(code)
for syndrome_val in [0, 0b01, 0b11, 0b10]:
    recovery = decoder.decode(syndrome_val)
    ops = [instr.operation.name for instr in recovery.data if instr.operation.name != "barrier"]
    print(f"  Syndrome {syndrome_val:04b} → corrections: {ops if ops else 'none'}")
