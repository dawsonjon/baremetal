from baremetal import *
from sfixed import SFixed
from math import atan, pi, sqrt

#1.0 = +180
#-1.0 = -180

def rectangular_to_polar(clk, i, q, phase_fbits, scaled=True):
    phaset = SFixed(phase_fbits+2, phase_fbits)
    t = i.subtype

    ltz = q < q.subtype.constant(0)
    temp_i = t.select(ltz,  q, -q)
    temp_q = t.select(ltz, -i,  i)
    i, q = temp_i, temp_q
    phase = phaset.select(ltz, phaset.constant(0.5), phaset.constant(-0.5))

    i = i.subtype.register(clk, d=i)
    q = q.subtype.register(clk, d=q)
    phase = phase.subtype.register(clk, d=phase)

    gain = 1.0
    for idx in range(phase_fbits):
        d = 2.0**idx
        angle = phaset.constant(atan(1.0/d)/pi)
        magnitude = sqrt(1+(1.0/d)*(1.0/d))
        gain *= magnitude
        ltz = q < q.subtype.constant(0)
        temp_i = t.select(ltz, i+(q>>idx), i-(q>>idx))
        temp_q = t.select(ltz, q-(i>>idx), q+(i>>idx))
        i, q = temp_i, temp_q
        phase = phaset.select(ltz, phase+angle, phase-angle)

        i = i.subtype.register(clk, d=i)
        q = q.subtype.register(clk, d=q)
        phase = phase.subtype.register(clk, d=phase)

    if scaled:
        i *= SFixed(i.subtype.bits, i.subtype.bits-1).constant(1.0/gain)

    return i, phase

i = SFixed(17, 8).constant(00)
q = SFixed(17, 8).constant(-100)
clk = Clock("clk")
magnitude, phase = rectangular_to_polar(clk, i, q, 20, 20)

clk.initialise()
for idx in range(21):
    clk.tick()
    print(magnitude.get(), phase.get())
