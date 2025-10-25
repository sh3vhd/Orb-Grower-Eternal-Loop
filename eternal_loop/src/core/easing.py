import math

def ease_in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2

def smoothstep(t: float) -> float:
    return t * t * (3 - 2 * t)

def damp(current, target, smoothing, dt):
    # Exponential damping toward target (0..1 smoothing per second)
    return current + (target - current) * (1 - math.exp(-smoothing * dt))
