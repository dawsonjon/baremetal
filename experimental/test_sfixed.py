from baremetal import *

from sfixed import *

c = SFixed(8, 4).constant(2.0) + SFixed(2, 4).constant(0.0625)
print((c.get()))
c = SFixed(8, 4).constant(2.0) - SFixed(2, 4).constant(0.0625)
print((c.get()))
c = SFixed(8, 3).constant(2.0) > SFixed(2, 4).constant(0.0625)
print((c.get()))
c = SFixed(8, 3).constant(2.0) < SFixed(2, 4).constant(0.0625)
print((c.get()))
c = SFixed(8, 3).constant(2.0) >= SFixed(2, 4).constant(0.0625)
print((c.get()))
c = SFixed(8, 3).constant(2.0) <= SFixed(2, 4).constant(0.0625)
print((c.get()))
c = SFixed(8, 3).constant(2.0) == SFixed(8, 4).constant(2.0)
print((c.get()))
c = SFixed(8, 3).constant(2.0) != SFixed(8, 4).constant(2.0)
print((c.get()))
c = SFixed(8, 0).constant(4.0) * SFixed(8, 2).constant(0.5)
print((c.get()))
c = SFixed(16, 8).constant(2.0) * SFixed(16, 8).constant(1.0)
print((c.get()))
