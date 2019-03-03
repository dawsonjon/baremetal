from baremetal import *

i0 = Input("i0", 10) 
i1 = Input("i1", 10) 
i2 = Input("i2", 10) 
i3 = Input("i3", 10) 
s = Input("s", 3)
o = Output("mux", Select(s, i0, i1, i2, i3, default=123))


netlist = Netlist("counter", [], [s, i0, i1, i2, i3], [o])
print netlist.generate()

i0.set(12)
i1.set(34)
i2.set(56)
i3.set(78)

s.set(0)
print o.get()
s.set(1)
print o.get()
s.set(2)
print o.get()
s.set(3)
print o.get()
s.set(4)
print o.get()
