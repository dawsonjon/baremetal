from baremetal import *
from sfixed import SFixed
from math import atan, pi

def rectangular_to_polar(clk, i, q, iterations, phase_bits):
    phaset = SFixed(phase_bits, phase_bits-1)
    t = i.subtype

    ltz = q < 0
    i = t.select(ltz, q, -q)
    q = t.select(ltz, -i, i)
    phase = phaset.select(ltz, phaset.constant(0.5), phaset.constant(-0.5))

    i = i.subtype.register(clk, d=i)
    q = q.subtype.register(clk, d=q)
    phase = phase.subtype.register(clk, d=phase)

    for idx in range(iterations):
        d = 2**idx
        angle = phaset.constant(atan(1/d)/pi)
        ltz = q < 0
        i = t.select(ltz, i+(q>>idx), i-(q>>idx))
        q = t.select(ltz, q-(i>>idx), q+(i>>idx))
        phase = phaset.select(ltz, phase+angle, phase-angle)

        i = i.subtype.register(clk, d=i)
        q = q.subtype.register(clk, d=q)
        phase = phase.subtype.register(clk, d=phase)

    return phase

i = Signed(10).constant(100)
q = Signed(10).constant(100)

clk = Clock("clk")
clk.initialise()
for idx in range(10):
    phase = rectangular_to_polar(clk, i, q, 5, 10)
    clk.tick()
    print(phase.get())
