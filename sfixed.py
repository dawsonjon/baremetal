from baremetal import *
import baremetal.signed as signed
        
class SFixed:

    def __init__(self, bits, fraction_bits, rounding_mode="nearest_even", 
            clamp=True):
        self.signed = signed.Signed(bits)
        self.bits = bits
        self.fraction_bits = fraction_bits
        self.q = 2**fraction_bits
        self.rounding_mode = rounding_mode
        self.clamp = clamp

    def as_float(self, x):
        return float(x)/self.q

    def from_float(self, x):
        return int(round(float(x)*self.q))

    def constant(self, value):
        return Expression(self, self.signed.constant(self.from_float(value)))

    def input(self, name):
        return Expression(self, self.signed.input(name))

    def output(self, name, expression):
        return Output(self, name, expression)

    def select(self, select, *args, **kwargs):
        args = [fixed_to_signed(i) for i in args]
        if "default" in kwargs:
            kwargs["default"] = fixed_to_siged(kwargs["default"])
        return Expression(self, self.signed.select(select, *args, **kwargs))

    def rom(self, select, *args, **kwargs):
        args = [self.from_float(i) for i in args]
        if "default" in kwargs:
            kwargs["default"] = self.from_float(kwargs["default"])
        return Expression(self, self.signed.rom(select, *args, **kwargs))

    def register(self, clk, en=1, init=None, d=None):
        return Register(self, clk, en, init, d)

    def wire(self):
        return Wire(self)

def fixed_round(x, new_lsb, rounding_mode, clamp):
    if new_lsb == 0:
        return x
    odd = x[new_lsb]
    guard = x[new_lsb-1]
    if new_lsb >= 2:
        rnd = x[new_lsb-2:0]!=0
    else:
        rnd = Boolean().constant(0)
    truncated = x[x.subtype.bits-1:new_lsb]

    if rounding_mode == "nearest_even":
        roundup = guard & (rnd | odd) & (~clamp)
        result = truncated.subtype.select(roundup, truncated, truncated + 1)
    elif rounding_mode == "nearest_odd":
        roundup = guard & (rnd | ~odd) & (~clamp)
        truncated = x[x.subtype.bits-1:new_lsb]
        result = truncated.subtype.select(roundup, truncated, truncated + 1)
    elif rounding_mode == "simple":
        roundup = guard & ~clamp
        truncated = x[x.subtype.bits-1:new_lsb]
        result = truncated.subtype.select(roundup, truncated, truncated + 1)
    elif rounding_mode == "truncate":
        result = truncated

    return truncated.subtype.select(roundup, truncated, truncated + 1)

def mul(a, b):
    rounding_mode = a.subtype.rounding_mode
    clamp = a.subtype.clamp
    a_fbits = a.subtype.fraction_bits
    b_fbits = b.subtype.fraction_bits
    a_bits = a.subtype.signed.bits
    b_bits = b.subtype.signed.bits
    a_ibits = a_bits - a_fbits
    b_ibits = b_bits - b_fbits
    a=a.signed
    b=b.signed
    
    #calculate the result
    result_fbits = a_fbits + b_fbits
    result_bits = a_bits + b_bits
    result = a.resize(result_bits) * b
    

    if (a_ibits > b_ibits) | (a_ibits == b_ibits & a_bits > b_bits):
        if result_fbits > a_fbits:
            result = fixed_round(result, result_fbits-a_fbits, rounding_mode, clamp)
        result = result.resize(a_bits)
        subtype = SFixed(a_bits, a_fbits)
    else:
        if result_fbits > b_fbits:
            result = fixed_round(result, result_fbits-b_fbits, rounding_mode, clamp)
        result = result.resize(b_bits)
        subtype = SFixed(b_bits, b_fbits)

    return Expression(subtype, result)

def addsub(a, b, sub=False):
    a_fbits = a.subtype.fraction_bits
    b_fbits = b.subtype.fraction_bits
    a_bits = a.subtype.signed.bits
    b_bits = b.subtype.signed.bits
    a_ibits = a_bits - a_fbits
    b_ibits = b_bits - b_fbits
    a=a.signed
    b=b.signed

    #Add extra_fraction_bits to align the radix points
    fbits = max([a_fbits, b_fbits])

    if a_fbits <= b_fbits:
        extra_bits = b_fbits - a_fbits
        a = a.resize(a_bits + extra_bits) << extra_bits
        result_fbits = b_fbits

    if b_fbits < a_fbits:
        extra_bits = a_fbits - b_fbits
        b = b.resize(b_bits + extra_bits) << extra_bits
        result_fbits = a_fbits

    #perform the addition
    if sub:
        result = a-b
    else:
        result = a + b

    if (a_ibits > b_ibits) | (a_ibits == b_ibits & a_bits > b_bits):
        if result_fbits > a_fbits:
            result = fixed_round(result, result_fbits-a_fbits)
        subtype = SFixed(a_bits, a_fbits)
    else:
        if result_fbits > b_fbits:
            result = fixed_round(result, result_fbits-b_fbits)
        subtype = SFixed(b_bits, b_fbits)

    return Expression(subtype, result)

def compare(a, b, cm):
    a_fbits = a.subtype.fraction_bits
    b_fbits = b.subtype.fraction_bits
    a_bits = a.subtype.signed.bits
    b_bits = b.subtype.signed.bits
    a_ibits = a_bits - a_fbits
    b_ibits = b_bits - b_fbits
    a=a.signed
    b=b.signed

    #Add extra_fraction_bits to align the radix points
    fbits = max([a_fbits, b_fbits])

    if a_fbits <= b_fbits:
        extra_bits = b_fbits - a_fbits
        a = a.resize(a_bits + extra_bits) << extra_bits
        result_fbits = b_fbits

    if b_fbits < a_fbits:
        extra_bits = a_fbits - b_fbits
        b = b.resize(b_bits + extra_bits) << extra_bits
        result_fbits = a_fbits

    #perform the addition
    if cm == ">":
        return a>b
    elif cm == "<":
        return a<b
    elif cm == ">=":
        return a>=b
    elif cm == "<=":
        return a<=b
    elif cm == "==":
        return a==b
    elif cm == "!=":
        return a!=b

def signed_to_fixed(x, fb):
    return Expression(SFixed(x.bits, fb), x)

def fixed_to_signed(x):
    return x.signed

class Expression:
    def __init__(self, subtype, signed):
        self.subtype = subtype
        self.signed = signed

    def get(self):
        value = self.signed.get()
        if value is None:
            return None
        return self.subtype.as_float(value)

    def __add__(self, other): return addsub(self, other)
    def __sub__(self, other): return addsub(self, other, True)
    def __mul__(self, other): return mul(self, other)
    def __gt__(self, other):  return compare(self, other, ">")
    def __lt__(self, other):  return compare(self, other, "<")
    def __ge__(self, other):  return compare(self, other, ">=")
    def __le__(self, other):  return compare(self, other, "<=")
    def __eq__(self, other):  return compare(self, other, "==")
    def __ne__(self, other):  return compare(self, other, "!=")
    def __lshift__(self, other):  
        return Expression(self.subtype, self.signed << other)
    def __rshift__(self, other): 
        return Expression(self.subtype, self.signed >> other)
    def __neg__(self):        return Expression(self.subtype, -self.signed)

class Wire(Expression):
    def __init__(self, subtype):
        self.subtype = subtype
        self.signed = subtype.wire()

    def drive(self, expression):
        self.signed.drive(expression.signed)

class Register(Expression):
    def __init__(self, subtype, clk, en, init, d):
        self.subtype = subtype
        d = None if (d is None) else d.signed
        init = None if (init is None) else self.subtype.from_float(init)
        self.signed = subtype.signed.register(clk, en, init, d)

    def d(self, expression):
        self.signed.d(expression.signed)

class Output(Expression):
    def __init__(self, subtype, name, expression):
        self.subtype = subtype
        self.signed = subtype.output(name, expression.signed)
        self.vector = signed.vector

    def get(self):
        return self.subtype.asfloat(self.signed.get())

