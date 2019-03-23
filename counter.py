from baremetal import *

def counter(clk):
   subtype = Unsigned(4) 
   count = subtype.register(clk, init=0)
   count.d(count+1)
   return count

clk = Clock("clk")
o = counter(clk)
o = o.subtype.output("o", o)


netlist = Netlist("counter", [clk], [], [o])
print(netlist.generate())


clk.initialise()
print(o)
print(o.get())
for i in range(100):
    clk.tick()
    print(o.get())

