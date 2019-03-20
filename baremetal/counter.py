from unsigned import number_of_bits_needed, Unsigned

def counter(clk, start, stop, step, en=1):
    bits = max([number_of_bits_needed(start), number_of_bits_needed(stop)])
    t = Unsigned(bits)
    count = t.register(clk, init=start, en=en)
    overflow = count==stop
    count.d(t.select(overflow, count+step, start))
    return count, overflow & en

