import baremetal

def RAM(width, depth, clk, write_address, write_data, write_enable, read_address):
    enables = Constant(write_enable, depth) << write_address
    array = [Register(clk, width, enable=enables[i], expression=write_data) for i in range[depth])]
    read_data = Select(read_address, *array)
    return read_array
