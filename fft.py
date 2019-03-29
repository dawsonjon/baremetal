from baremetal import *

def delay(clk, x, n, init=None):
    for i in range(n):
        if init is not None:
            x = x.subtype.register(clk, d=x, init=init)
        else:
            x = x.subtype.register(clk, d=x)
    return x

def bit_reverse(x):
    bits = x.subtype.bits
    return cat(*[x[i] for i in range(bits)])

def bit_reverse_order(clk, s0, s1, valid, n):
    s0_ram = s0.subtype.ram(n, clk, False) 
    s1_ram = s1.subtype.ram(n, clk, False) 
    write_address, _ = counter(clk, 0, n-1, 1, valid)
    s0_ram.write(write_address, s0, valid)
    s1_ram.write(write_address, s1, valid)
    valid = delay(clk, valid, n, 0)
    read_address, _ = counter(clk, 0, n-1, 1, valid)
    valid = delay(clk, valid, 1, 0)
    s0 = s0_ram.read(bit_reverse(read_address))
    s1 = s1_ram.read(bit_reverse(read_address))
    return s0, s1, valid

def reorder(clk, s0, s1, valid, n):
    m=2**(n-1)
    count, _ = counter(clk, 0, (2**n)-1, 1, valid)
    switch = count[n-1]
    s1 = delay(clk, s1, m)
    s0, s1 = s0.subtype.select(switch, s0, s1), s1.subtype.select(switch, s1, s0)
    s0 = delay(clk, s0, m)
    valid = delay(clk, valid, m, 0)
    return s0, s1, valid

def fft(s0, s1, valid, num_stages):
    for stage in range(num_stages):
        m = 2**stage

        #generate constants
        twiddles = [i/(2.0*n) for i in range(n)]
        twiddles = [exp(-2j*pi*i) for i in twiddles]
        twiddle_type = sfixed(s0.real.subtype.bits+2, s0.real.subtype.bits)


        #butterfly
        s0, s1 = s0+s1, s0-s1
        s0 = delay(clk, s0, 1)
        s1 = delay(clk, s1, 1)
        valid = delay(clk, valid, 1)

        #rotate
        if stage:
            count, _ = counter(clk, 0, m-1, 1, valid)
            s1 = s1 * twiddle_type.ROM(count, *twiddles)
            s0 = delay(clk, s0, 1)
            s1 = delay(clk, s1, 1)
            valid = delay(clk, valid, 1)

            #reorder
            s0, s1, valid = reorder(clk, s0, s1, valid, stage)

    return bit_reverse_order(clk, s0, s1, valid, 2**num_stages)


clk = Clock("clk")
a = Unsigned(8).input("in")
b = Unsigned(8).input("in")
valid = Boolean().input("valid")
s0, s1, valid_out = reorder(clk, a, b, valid, 3)

clk.initialise()
for i in range(16):
    a.set(i), b.set(100+i)
    valid.set(1)
    print(s0.get(), s1.get(), valid_out.get())
    clk.tick()
valid.set(0)

for i in range(20):
    print(s0.get(), s1.get(), valid_out.get())
    clk.tick()

