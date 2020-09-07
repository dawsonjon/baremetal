from baremetal import *
from sfixed import SFixed
from math import atan, pi, sqrt

#1.0 = +180
#-1.0 = -180

def calculate_gain(iterations):
    gain = 1.0
    for idx in range(iterations):
        d = 2.0**idx
        magnitude = sqrt(1+(1.0/d)*(1.0/d))
        gain *= magnitude
    return gain

def rectangular_to_polar(clk, i, q):
    rtype = i.subtype
    iterations = rtype.bits
    ptype= SFixed(iterations+2, iterations)

    ltz = q < q.subtype.constant(0)
    temp_i = rtype.select(ltz,  q, -q)
    temp_q = rtype.select(ltz, -i,  i)
    i, q = temp_i, temp_q
    phase = ptype.select(ltz, ptype.constant(+0.5), ptype.constant(-0.5))

    i = i.subtype.register(clk, d=i)
    q = q.subtype.register(clk, d=q)
    phase = ptype.register(clk, d=phase)

    for idx in range(iterations):
        d = 2.0**idx
        angle = ptype.constant(atan(1.0/d)/pi)
        ltz = q < q.subtype.constant(0)
        temp_i = rtype.select(ltz, i+(q>>idx), i-(q>>idx))
        temp_q = rtype.select(ltz, q-(i>>idx), q+(i>>idx))
        i, q = temp_i, temp_q
        phase = ptype.select(ltz, phase+angle, phase-angle)

        i = rtype.register(clk, d=i)
        q = rtype.register(clk, d=q)
        phase = ptype.register(clk, d=phase)

    gain = calculate_gain(iterations)
    i *= SFixed(iterations+2, iterations).constant(1.0/gain)

    return i, phase

def polar_to_rectangular(clk, magnitude, phase):
    rtype = magnitude.subtype
    iterations = rtype.bits
    ptype = phase.subtype

    gain = calculate_gain(iterations)
    i = magnitude * SFixed(iterations+2, iterations).constant(1.0/gain)
    q = rtype.constant(0)


    gtz = phase > ptype.constant(0)
    temp_i = rtype.select(gtz,  q, -q)
    temp_q = rtype.select(gtz, -i,  i)
    i, q = temp_i, temp_q
    phase = ptype.select(gtz, phase+ptype.constant(0.5), phase-ptype.constant(0.5))

    i = i.subtype.register(clk, d=i)
    q = q.subtype.register(clk, d=q)
    phase = ptype.register(clk, d=phase)

    for idx in range(iterations):
        d = 2.0**idx
        angle = ptype.constant(atan(1.0/d)/pi)
        gtz = phase > ptype.constant(0)
        temp_i = rtype.select(gtz, i+(q>>idx), i-(q>>idx))
        temp_q = rtype.select(gtz, q-(i>>idx), q+(i>>idx))
        i, q = temp_i, temp_q
        phase = ptype.select(gtz, phase+angle, phase-angle)

        i = rtype.register(clk, d=i)
        q = rtype.register(clk, d=q)
        phase = ptype.register(clk, d=phase)

    return i, q

i = SFixed(18, 8).constant(100)
q = SFixed(18, 8).constant(100)
clk = Clock("clk")
magnitude, phase = rectangular_to_polar(clk, i, q)
i, q = polar_to_rectangular(clk, magnitude, phase)

clk.initialise()
for idx in range(100):
    clk.tick()
    print((magnitude.get(), phase.get(), i.get(), q.get()))
