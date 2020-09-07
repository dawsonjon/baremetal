from baremetal import *

for subtype in [Unsigned(4), Signed(5)]:

################################################################################
#test1 Unsigned RAM 
    clk = Clock("clk")
    wraddr = subtype.input("wraddr")
    wrdata = subtype.input("wrdata")
    wren = Boolean().input("wren")
    rdaddr = subtype.input("rdaddr")
    ram = subtype.ram(16, clk, False, initialise = [15, 1, 4, 3, 7, 9, 8, 5, 14, 12, 11, 10, 13, 0, 2, 6])
    rddata = ram.read(rdaddr)
    ram.write(wraddr, wrdata, wren)
    rddata = subtype.output("rddata", rddata)

    clk.initialise()
    wren.set(0)

#check initial values
    expected = iter([15, 1, 4, 3, 7, 9, 8, 5, 14, 12, 11, 10, 13, 0, 2, 6])
    for i in range(16):
        rdaddr.set(i)
        clk.tick()
        assert(rddata.get() == next(expected))
    print("test1a ... pass")

#fill ram
    for i in range(16):
        wraddr.set(i)
        wren.set(1)
        wrdata.set(15-i)
        clk.tick()
    wren.set(0)

#read ram
    expected = iter(reversed(list(range(16))))
    for i in range(16):
        rdaddr.set(i)
        clk.tick()
        assert(rddata.get() == next(expected))

    print("test1b ... pass")

#fill ram again
    for i in range(16):
        wraddr.set(i)
        wren.set(1)
        wrdata.set(i)
        clk.tick()
    wren.set(0)

#read ram
    expected = iter(list(range(16)))
    for i in range(16):
        rdaddr.set(i)
        clk.tick()
        assert(rddata.get() == next(expected))

    print("test1c ... pass")

#n = Netlist("dut", [clk], [wraddr, wrdata, wren, rdaddr], [rddata])
#print(n.generate())

################################################################################
#test2 Unsigned Dual Port RAM 
    clk = Clock("clk")
    ram = subtype.ram(16, clk, False, initialise = [15, 1, 4, 3, 7, 9, 8, 5, 14, 12, 11, 10, 13, 0, 2, 6])
    port2 = ram.add_port(clk)

#write port 1
    wraddr = subtype.input("wraddr")
    wrdata = subtype.input("wrdata")
    wren = Boolean().input("wren")
    ram.write(wraddr, wrdata, wren)

#read port 1
    rdaddr = subtype.input("rdaddr")
    rddata = ram.read(rdaddr)
    rddata = subtype.output("rddata", rddata)

#write port 2
    wraddr2 = subtype.input("wraddr2")
    wrdata2 = subtype.input("wrdata2")
    wren2 = Boolean().input("wren2")
    port2.write(wraddr2, wrdata2, wren2)

#read port 2
    rdaddr2 = subtype.input("rdaddr2")
    rddata2 = port2.read(rdaddr2)
    rddata2 = subtype.output("rddata2", rddata2)

    clk.initialise()
    wren2.set(0)
    wren.set(0)

#check initial values
    expected = iter([15, 1, 4, 3, 7, 9, 8, 5, 14, 12, 11, 10, 13, 0, 2, 6])
    for i in range(16):
        rdaddr.set(i)
        clk.tick()
        assert(rddata.get() == next(expected))
    print("test2a ... pass")

    for i in range(16):
        wraddr.set(i)
        wren.set(1)
        wrdata.set(15-i)
        clk.tick()
    wren.set(0)

    expected = iter(reversed(list(range(16))))
    for i in range(16):
        rdaddr.set(i)
        clk.tick()
        assert(rddata.get() == next(expected))
    print("test2b ... pass")

    expected = iter(reversed(list(range(16))))
    for i in range(16):
        rdaddr2.set(i)
        clk.tick()
        assert(rddata2.get() == next(expected))
    print("test2c ... pass")

    wren2.set(0)
    for i in range(16):
        wraddr2.set(i)
        wren2.set(1)
        wrdata2.set(i)
        clk.tick()
    wren2.set(0)

    expected = iter(list(range(16)))
    for i in range(16):
        rdaddr.set(i)
        clk.tick()
        assert(rddata.get() == next(expected))
    print("test2d ... pass")

    expected = iter(list(range(16)))
    for i in range(16):
        rdaddr2.set(i)
        clk.tick()
        assert(rddata2.get() == next(expected))
    print("test2e ... pass")

#n = Netlist("dut", [clk], [wraddr, wrdata, wren, rdaddr], [rddata])
#print(n.generate())
