"""Run a bit-flip error rate experiment and observe logical error suppression."""

from aleshaq.qec.codes import RepetitionCode
from aleshaq.qec.noise import bit_flip_noise
from aleshaq.qec.simulation import CodeExperiment

code = RepetitionCode(distance=5)
experiment = CodeExperiment(code)

error_rates = [0.0, 0.01, 0.05, 0.10, 0.15, 0.20]
results = experiment.sweep(
    error_rates=error_rates,
    noise_factory=bit_flip_noise,
    shots=5000,
    seed=42,
)

print(f"{'Physical p':>12s}  {'Logical p':>12s}  {'Errors':>8s}")
print("-" * 36)
for r in results:
    print(f"{r.physical_error_rate:12.4f}  {r.logical_error_rate:12.4f}  {r.logical_errors:8d}")
