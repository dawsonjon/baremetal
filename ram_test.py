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
#test2 Unsigned RAM 

    clk = Clock("clk")
    addr = subtype.input("addr")
    data = subtype.input("data")
    wren = Boolean().input("wren")
    addrb = subtype.input("addrb")
    datab = subtype.input("datab")
    wrenb = Boolean().input("wrenb")
    ram = subtype.dpr(16, clk, initialise = [15, 1, 4, 3, 7, 9, 8, 5, 14, 12, 11, 10, 13, 0, 2, 6])
    rddata = ram.porta(addr, data, wren)
    rddatab = ram.portb(addrb, datab, wrenb)

    clk.initialise()
    wren.set(0)
    wrenb.set(0)

    #check initial values
    expected = iter([15, 1, 4, 3, 7, 9, 8, 5, 14, 12, 11, 10, 13, 0, 2, 6])
    for i in range(16):
        addr.set(i)
        clk.tick()
        assert(rddata.get() == next(expected))
    print("test1a ... pass")

    #fill ram
    for i in range(16):
        addr.set(i)
        wren.set(1)
        data.set(15-i)
        clk.tick()
    wren.set(0)

    #read ram
    expected = iter(reversed(list(range(16))))
    for i in range(16):
        addr.set(i)
        clk.tick()
        assert(rddata.get() == next(expected))

    print("test1b ... pass")

    #fill ram again
    for i in range(16):
        addr.set(i)
        wren.set(1)
        data.set(i)
        clk.tick()
    wren.set(0)

    #read ram
    expected = iter(list(range(16)))
    for i in range(16):
        addr.set(i)
        clk.tick()
        assert(rddata.get() == next(expected))

    print("test1c ... pass")

    #fill ram
    for i in range(16):
        addrb.set(i)
        wrenb.set(1)
        datab.set(15-i)
        clk.tick()
    wrenb.set(0)

    #read ram
    expected = iter(reversed(list(range(16))))
    for i in range(16):
        addrb.set(i)
        clk.tick()
        assert(rddatab.get() == next(expected))

    print("test1d ... pass")

    #fill ram again
    for i in range(16):
        addrb.set(i)
        wrenb.set(1)
        datab.set(i)
        clk.tick()
    wrenb.set(0)

    #read ram
    expected = iter(list(range(16)))
    for i in range(16):
        addrb.set(i)
        clk.tick()
        assert(rddatab.get() == next(expected))

    print("test1e ... pass")


    #test read before write behaviour
    old_value = 3
    new_value = 2

    addrb.set(0)
    wrenb.set(1)
    datab.set(old_value)
    clk.tick()
    wrenb.set(0)

    addr.set(0)
    addrb.set(0)
    wrenb.set(1)
    datab.set(new_value)
    clk.tick()
    assert rddata.get() == old_value
    assert rddatab.get() == old_value
    clk.tick()
    assert rddata.get() == new_value
    assert rddatab.get() == new_value

    print("test1f ... pass")



    #n = Netlist("dut", [clk], [addr, data, wren, addrb, datab, wrenb], [rddata.subtype.output("rddata", rddata), rddatab.subtype.output("rddatab", rddatab)])
    #print(n.generate())
