import back_end
from unsigned import Unsigned


def number_of_bits_needed(x):
    n=1
    while 1:
        max_value = (2**(n-1))-1
        min_value = -(2**(n-1))
        if min_value <= x <= max_value:
            return n
        n += 1

def const(value):
    if isinstance(value, Expression):
        return value
    bits = number_of_bits_needed(value)
    subtype = Signed(bits)
    return Constant(subtype, value)

class Signed:

    def __init__(self, bits):
        self.bits = bits

    def to_vector(self, value):
        if value is None:
            return None
        return int(round(float(value)))

    def from_vector(self, value):
        if value is None:
            return None
        negative = value & (1<<(self.bits-1))
        mask = ~((1 << self.bits)-1)
        if negative:
            return mask | value
        return value

    def constant(self, value):
        return Constant(self, value)

    def input(self, name):
        return Input(self, name)

    def output(self, name, expression):
        return Output(self, name, expression)

    def select(self, select, *args, **kwargs):
        return Select(self, select, *args, **kwargs)

    def register(self, clk, en=1, init=None, d=None):
        return Register(self, clk, en, init, d)

def binary(a, b, operator):
    b = const(b)
    binary = back_end.Binary(a.vector, b.vector, operator)
    subtype = Signed(binary.bits)
    return Expression(subtype, binary, "%s%s%s"%(a, operator, b))

def compare(a, b, operator):
    b = const(b)
    binary = back_end.Binary(a.vector, b.vector, operator)
    subtype = Unsigned(1)
    return Expression(subtype, binary, "%s%s%s"%(a, operator, b))

def unary(a, operator):
    unary = back_end.Unary(a.vector, operator)
    subtype = Signed(unary.bits)
    return Expression(subtype, unary, "%s%s"%(operator, a))

class Expression:
    def __init__(self, subtype, vector, string):
        self.subtype = subtype
        self.vector = vector
        self.string = string

    def cat(self, other):
        a = self
        b = const(other)
        binary = back_end.Concatenate(a.vector, b.vector)
        subtype = Signed(binary.bits)
        return Expression(subtype, binary, "%s.cat(%s)"%(repr(a), repr(b)))

    def resize(self, bits):
        vector = back_end.Resize(self.vector, bits)
        subtype = Signed(vector.bits)
        return Expression(subtype, vector, "%s.resize(%s)"%(repr(self), str(bits)))

    def __add__(self, other):    return binary(self, other, "+")
    def __sub__(self, other):    return binary(self, other, "-")
    def __mul__(self, other):    return binary(self, other, "*")
    def __gt__(self, other):     return compare(self, other, "s>")
    def __ge__(self, other):     return compare(self, other, "s>=")
    def __lt__(self, other):     return compare(self, other, "s<")
    def __le__(self, other):     return compare(self, other, "s<=")
    def __eq__(self, other):     return compare(self, other, "==")
    def __ne__(self, other):     return compare(self, other, "!=")
    def __lshift__(self, other): return binary(self, other, "<<")
    def __rshift__(self, other): return binary(self, other, "s>>")
    def __and__(self, other):    return binary(self, other, "&")
    def __or__(self, other):     return binary(self, other, "|")
    def __xor__(self, other):    return binary(self, other, "^")
    def __neg__(self):           return unary(self, "-")
    def __invert__(self):        return unary(self, "~")
    def __abs__(self):           return self.subtype.select(self > 0, -self, self)
    def __getitem__(self, other):
        try:
            vector=back_end.Index(self.vector, int(other))
            subtype=Unsigned(vector.bits)
            return Expression(subtype, vector, "%s[%s]"%(self, other))
        except TypeError:
            vector=back_end.Slice(self.vector, other.start, other.stop)
            subtype=Unsigned(vector.bits)
            return Expression(subtype, vector, "%s[%s:%s]"%(self, other.start, other.stop))
    def get(self):
        return self.subtype.from_vector(self.vector.get())

    def __repr__(self):
        return self.string

class Constant(Expression):
    def __init__(self, subtype, value):
        self.subtype = subtype
        self.vector = back_end.Constant(subtype.to_vector(value), subtype.bits)
        self.string = "Constant(%s)"%(value)

class Input(Expression):
    def __init__(self, subtype, name):
        self.subtype = subtype
        self.vector = back_end.Input(name, subtype.bits)
        self.string = "input(%s)"%(name)

    def set(self, value):
        self.vector.set(self.subtype.to_vector(value))

class Output(Expression):
    def __init__(self, subtype, name, expression):
        self.subtype = subtype
        self.vector = back_end.Output(name, expression.vector)

    def get(self):
        return self.subtype.from_vector(self.vector.get())

class Select(Expression):
    def __init__(self, subtype, select, *args, **kwargs):
        select = const(select).vector
        args = [const(i).vector for i in args]
        default = const(kwargs.get("default", 0)).vector
        self.vector = back_end.Select(select, *args, default=default)
        self.subtype = Unsigned(self.vector.bits)

class Register(Expression):
    def __init__(self, subtype, clk, en, init, d):
        self.subtype = subtype
        d = d if d is None else const(d).vector
        init = init if init is None else int(init)
        en = const(en).vector
        self.vector = back_end.Register(clock=clk, bits=subtype.bits, en=en, d=d, init=init)

    def d(self, expression):
        self.vector.d = expression.vector
