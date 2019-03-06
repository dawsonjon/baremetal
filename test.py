from baremetal import *

datatype = Unsigned(10)

i0 = datatype.input("i0")
i1 = datatype.input("i1") 
i2 = datatype.input("i2") 
i3 = datatype.input("i3") 
s = Unsigned(3).input("s")
o = datatype.output("mux", datatype.select(s, i0, i1, i2, i3, default=123))

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
