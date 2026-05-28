"""
Gera alert.wav e success.wav como PCM 16-bit mono 44100Hz.
Execute uma vez: python generate_sounds.py
"""
import struct
import wave
import math
from pathlib import Path

RATE = 44100


def sine_wave(freq: float, duration: float, amplitude: int = 20000) -> bytes:
    n = int(RATE * duration)
    data = []
    for i in range(n):
        t = i / RATE
        fade = min(1.0, min(t / 0.01, (duration - t) / 0.02))  # 10ms attack, 20ms release
        sample = int(amplitude * fade * math.sin(2 * math.pi * freq * t))
        data.append(struct.pack("<h", sample))
    return b"".join(data)


def write_wav(path: Path, samples: bytes) -> None:
    with wave.open(str(path), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(samples)


assets = Path(__file__).parent / "assets"
assets.mkdir(exist_ok=True)

# alert.wav: two short beeps at 440 Hz
alert = sine_wave(440, 0.18) + b"\x00" * (RATE // 10 * 2) + sine_wave(440, 0.18)
write_wav(assets / "alert.wav", alert)

# success.wav: ascending chord C5-E5-G5
success = (
    sine_wave(523.25, 0.15) +
    sine_wave(659.25, 0.15) +
    sine_wave(783.99, 0.30)
)
write_wav(assets / "success.wav", success)

print("Arquivos gerados em assets/alert.wav e assets/success.wav")
