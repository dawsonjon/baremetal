from baremetal import *

def asynchronous_RAM(t, depth, clk, 
        wr_addr, wr_data, wr_en, rd_addr, rd_data=None):
    if rd_data is None:
        rd_data = t.wire()
    enables = wr_en.resize(depth) << wr_addr
    array = [t.register(clk, en=enables[i], d=wr_data) for i in range(depth)]
    rd_data.drive(t.select(rd_addr, *array))
    return rd_data

def synchronous_RAM(t, depth, clk, 
        wr_addr, wr_data, wr_en, rd_addr, rd_data=None):
    if rd_data is None:
        rd_data = t.wire()
    enables = wr_en.resize(depth) << wr_addr
    array = [t.register(clk, en=enables[i], d=wr_data) for i in range(depth)]
    rd_data.drive(t.register(clk, d=t.select(rd_addr, *array)))
    return rd_data


width = 8
depth = 8
data_type = Unsigned(width)
address_type = Unsigned(3)

write_data = data_type.input("write_data")
write_enable = Boolean().input("write_enable")
write_address = address_type.input("write_address")
read_address = address_type.input("read_address")
clk = Clock("clk")
rd = data_type.wire()

asynchronous_RAM(
    data_type, depth, clk,
    write_address, write_data, write_enable, read_address, rd
)

read_data = data_type.output("read_data", rd)

clk.initialise()

#check that ram is uninitialised
for i in range(8):
    read_address.set(i)
    clk.tick()
    assert read_data.get() is None

#fill ram with data
for i in range(8):
    write_data.set(i)
    write_address.set(7-i)
    write_enable.set(1)
    clk.tick()

#check contents of RAM
for i in range(8):
    read_address.set(i)
    clk.tick()
    assert read_data.get() == 7-i
