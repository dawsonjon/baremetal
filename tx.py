def nco(clk, frequency, channels):
    counter = Register(clk, frequency.bits, initial_value = 0)
    counter.expression = counter + (frequency * channels)

    def tree(x, n):
        x=Register(clk, x.bits, expression=x) 
        xn=register(clk, x.bits, expression=x+frequency*n)
        if x == 1:
            return [x, xn]
        else:
            return tree(x, n//2) + tree(xn, n//2)

    counters = tree(counter, channels//2)

    return [Select(i, cos(xxxx)), Select(i, -sin(xxxx)) for i in counters]

def mixer(clk, lo, inp):
    def mix(lo, inp):
        return [j*k for j, k in zip(lo, inp)]
    return [mix(j, k) for j, k in lo, inp]

