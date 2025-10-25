import numpy as np
import pygame
import math
from typing import Dict

class SoundManager:
    def __init__(self):
        self.enabled = True
        self.cache: Dict[str, pygame.mixer.Sound] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except pygame.error:
            self.enabled = False

        if self.enabled:
            self.cache['ambient'] = self._synth_ambient()
            self.cache['eat'] = self._synth_pluck(440, 0.12)
            self.cache['woosh'] = self._synth_woosh(0.6)
            self.cache['bloom'] = self._synth_pluck(660, 0.18, decay=0.9)

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled

    def play(self, name, loops=0):
        if not self.enabled: return
        s = self.cache.get(name)
        if s:
            s.play(loops=loops, fade_ms=250)

    def loop_ambient(self):
        if not self.enabled: return
        self.play('ambient', loops=-1)

    def _to_sound(self, arr):
        # Ensure stereo int16
        if arr.ndim == 1:
            arr = np.stack([arr, arr], axis=-1)
        arr = np.clip(arr, -1.0, 1.0)
        arr_i16 = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr_i16.copy())

    def _env(self, n, attack=0.02, decay=0.4):
        t = np.linspace(0, 1, n, endpoint=False)
        a = np.minimum(t / attack, 1.0)
        d = np.exp(-t / max(decay, 1e-6))
        return np.clip(a * d, 0, 1)

    def _synth_ambient(self, seconds=12, base=110):
        sr = 44100
        n = int(sr * seconds)
        t = np.arange(n) / sr
        # three detuned sines + slow noise, gentle LPF
        freqs = [base, base*2**(5/12), base*2**(7/12)]
        sig = np.zeros(n, dtype=np.float32)
        for i,f in enumerate(freqs):
            detune = 1 + (i-1)*0.003
            sig += 0.33*np.sin(2*np.pi*f*detune*t + 0.2*i)
        noise = (np.random.randn(n)*0.03).astype(np.float32)
        sig += noise
        # slow tremolo
        trem = 0.8 + 0.2*np.sin(2*np.pi*0.08*t)
        sig *= trem
        # simple moving average as LPF
        k = 400
        cumsum = np.cumsum(np.insert(sig, 0, 0))
        sig = (cumsum[k:] - cumsum[:-k]) / k
        # pad to stereo
        return self._to_sound(sig)

    def _synth_pluck(self, freq=440, dur=0.2, decay=0.7):
        sr = 44100
        n = int(sr*dur)
        t = np.arange(n)/sr
        env = self._env(n, attack=0.01, decay=decay)
        sig = np.sin(2*np.pi*freq*t) * env * 0.7
        # add airy harmonics
        sig += 0.2*np.sin(2*np.pi*freq*2*t+0.4)*env
        sig += 0.12*np.sin(2*np.pi*freq*3*t+1.2)*env*0.7
        return self._to_sound(sig.astype(np.float32))

    def _synth_woosh(self, dur=0.6):
        sr = 44100
        n = int(sr*dur)
        t = np.linspace(0, 1, n, endpoint=False)
        noise = np.random.randn(n).astype(np.float32)
        # fade-in then fade-out
        env = np.minimum(t/0.25, 1.0) * np.exp(-t/0.7)
        # down sweep filter-ish by integrating
        noise = np.cumsum(noise) / 1000.0
        sig = noise * env * 1.5
        return self._to_sound(sig.astype(np.float32))
