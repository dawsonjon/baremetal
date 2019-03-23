from baremetal import *


clk = Clock("clk")
wraddr = Unsigned(4).input("wraddr")
wrdata = Unsigned(4).input("wrdata")
wren = Boolean().input("wren")
rdaddr = Unsigned(4).input("rdaddr")
ram = Unsigned(4).ram(16, clk, False)
rddata = ram.read(rdaddr)
ram.write(wraddr, wrdata, wren)
rddata = Unsigned(4).output("rddata", rddata)

for i in range(16):
    wraddr.set(i)
    wren.set(1)
    wrdata.set(15-i)
    clk.tick()
wren.set(0)

for i in range(16):
    rdaddr.set(i)
    clk.tick()
    print rddata.get()

n = Netlist("dut", [clk], [wraddr, wrdata, wren, rdaddr], [rddata])
print n.generate()
