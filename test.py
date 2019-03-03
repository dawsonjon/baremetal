from baremetal import *

i0 = Input("i0", 10) 
i1 = Input("i1", 10) 
i2 = Input("i2", 10) 
i3 = Input("i3", 10) 
s = Input("s", 2)
o = Output("mux", Select(s, i0*1, i1*2, i2*3, i3*4))


netlist = Netlist("counter", [], [s, i0, i1, i2, i3], [o])
print netlist.generate()

i0.set(0)
i1.set(1)
i2.set(2)
i3.set(3)
s.set(0)

