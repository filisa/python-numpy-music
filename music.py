import wave
import numpy as np

sr = 22050
bpm = 72
bars = 8
beat = 60 / bpm
samples = int(bars * 4 * beat * sr)
rng = np.random.default_rng(12)
mix = np.zeros(samples, dtype=np.float32)

def add_note(start, duration, midi, volume=0.05):
    first = int(start * sr)
    size = min(int(duration * sr), samples - first)
    if size <= 0:
        return

    t = np.arange(size) / sr
    freq = 440 * 2 ** ((midi - 69) / 12)  # MIDI note to frequency
    envelope = np.minimum(t / 0.02, 1) * np.exp(-2.5 * t)

    # Fundamental plus quieter harmonics gives the tone some warmth.
    tone = (
        np.sin(2 * np.pi * freq * t)
        + 0.25 * np.sin(2 * np.pi * freq * 2 * t)
        + 0.08 * np.sin(2 * np.pi * freq * 3 * t)
    )
    mix[first:first + size] += volume * envelope * tone

chords = [
    [45, 52, 55, 59],
    [41, 48, 53, 57],
    [38, 45, 50, 53],
    [43, 50, 55, 59],
]

for bar in range(bars):
    start = bar * 4 * beat
    chord = chords[bar % len(chords)]

    # Soft chord
    for note in chord:
        add_note(start, 1.8, note)

    # A repeating arpeggio, one note at a time
    for step in range(8):
        note = chord[step % len(chord)] + 12
        add_note(start + step * beat / 2, 0.45, note, volume=0.025)

    # Bass pulse, kick, and snare
    for pulse in range(4):
        when = start + pulse * beat
        if pulse in (0, 2):
            add_note(when, 0.35, chord[0] - 12, volume=0.08)

            # Falling-pitch sine wave for a simple soft kick
            first = int(when * sr)
            size = min(int(0.25 * sr), samples - first)
            t = np.arange(size) / sr
            freq = 90 * np.exp(-15 * t) + 40
            phase = 2 * np.pi * np.cumsum(freq) / sr
            mix[first:first + size] += 0.12 * np.sin(phase) * np.exp(-12 * t)

        if pulse in (1, 3):
            # A short, pitch-bending tone makes a playful synthetic meow.
            first = int(when * sr)
            size = min(int(0.351 * sr), samples - first)
            t = np.arange(size) / sr
            freq = 280 + 140 * np.exp(-((t - 0.07) / 0.06) ** 2) - 100 * t / 0.351
            phase = 2 * np.pi * np.cumsum(freq) / sr
            envelope = np.minimum(t / 0.02, 1) * np.exp(-4 * t)
            meow = (
                np.sin(phase)
                + 0.5 * np.sin(2 * phase)
                + 0.22 * np.sin(3 * phase)
            )
            mix[first:first + size] += 0.025 * envelope * meow

# Fade the start and finish, then prevent clipping
fade = int(0.5 * sr)
mix[:fade] *= np.linspace(0, 1, fade)
mix[-fade:] *= np.linspace(1, 0, fade)
mix *= 0.85 / max(np.max(np.abs(mix)), 1e-6)

# Write a standard 16-bit WAV file
audio = (mix * 32767).astype("<i2")
with wave.open("lofi.wav", "wb") as file:
    file.setnchannels(1)
    file.setsampwidth(2)
    file.setframerate(sr)
    file.writeframes(audio.tobytes())

print("Made lofi.wav")