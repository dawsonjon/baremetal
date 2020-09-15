from cmath import exp, pi

from baremetal import *

from complex import Complex
from sfixed import SFixed

t = Complex(SFixed(16, 8))

c = t.constant(1.0+2.0j)+t.constant(0.5+0.5j)
print((c.get()))

clk = Clock("clk")
r = t.register(clk, init=1.0)
r.d(r*t.constant(exp(0.25j*pi)))

clk.initialise()
for i in range(10):
    print((r.get()))
    clk.tick()
