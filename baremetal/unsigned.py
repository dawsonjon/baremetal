from . import back_end
from math import ceil, log

def number_of_bits_needed(x):
    n=1
    while 1:
        max_value = (2**n)-1
        min_value = 0
        if min_value <= x <= max_value:
            return n
        n += 1

def const(value):
    if hasattr(value, "vector"):
        return value
    bits = number_of_bits_needed(value)
    subtype = Unsigned(bits)
    return Constant(subtype, value)

class Unsigned:

    def __init__(self, bits):
        self.bits = bits

    def to_vector(self, value):
        return int(round(float(value)))

    def from_vector(self, value):
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

    def wire(self):
        return Wire(self)

    def rom(self, select, *args, **kwargs):
        return ROM(self, select, *args, **kwargs)

    def ram(self, *args, **kwargs):
        return RAM(self, *args, **kwargs)

def Boolean():
    return Unsigned(1)

def binary(a, b, operator):
    b = const(b)
    binary = back_end.Binary(a.vector, b.vector, operator)
    subtype = Unsigned(binary.bits)
    return Expression(subtype, binary, "("+repr(a)+operator+repr(b)+")")

def unary(a, operator):
    unary = back_end.Unary(a.vector, operator)
    subtype = Unsigned(unary.bits)
    return Expression(subtype, unary, "("+operator+repr(a)+")")

class Expression:
    def __init__(self, subtype, vector, string):
        self.subtype = subtype
        self.vector = vector
        self.string = string

    def label(self, label_string):
        a = self
        vector = back_end.Label(self.vector, label_string)
        subtype = Unsigned(vector.bits)
        return Expression(subtype, vector, "%s.label(%s)"%(repr(a), str(label_string)))

    def cat(self, other):
        a = self
        b = const(other)
        vector = back_end.Concatenate(a.vector, b.vector)
        subtype = Unsigned(vector.bits)
        return Expression(subtype, vector, "%s.cat(%s)"%(repr(a), repr(b)))

    def resize(self, bits):
        binary = back_end.Resize(self.vector, bits)
        subtype = Unsigned(binary.bits)
        return Expression(subtype, binary, "%s.resize(%s)"%(repr(self), str(bits)))

    def __add__(self, other):    return binary(self, other, "+")
    def __sub__(self, other):    return binary(self, other, "-")
    def __mul__(self, other):    return binary(self, other, "*")
    def __gt__(self, other):     return binary(self, other, ">")
    def __ge__(self, other):     return binary(self, other, ">=")
    def __lt__(self, other):     return binary(self, other, "<")
    def __le__(self, other):     return binary(self, other, "<=")
    def __eq__(self, other):     return binary(self, other, "==")
    def __ne__(self, other):     return binary(self, other, "!=")
    def __lshift__(self, other): return binary(self, other, "<<")
    def __rshift__(self, other): return binary(self, other, ">>")
    def __and__(self, other):    return binary(self, other, "&")
    def __or__(self, other):     return binary(self, other, "|")
    def __xor__(self, other):    return binary(self, other, "^")
    def __neg__(self):           return unary(self, "-")
    def __invert__(self):        return unary(self, "~")
    def __abs__(self):           return self
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

    def __repr__(self):
        return str(self.vector.value)

class Input(Expression):
    def __init__(self, subtype, name):
        self.subtype = subtype
        self.vector = back_end.Input(name, subtype.bits)
        self.string = "Input(%s)"%name

    def set(self, value):
        self.vector.set(self.subtype.to_vector(value))

class Output(Expression):
    def __init__(self, subtype, name, expression):
        self.subtype = subtype
        self.vector = back_end.Output(name, expression.vector)
        self.string = "Output(%s)"%name

    def get(self):
        return self.subtype.from_vector(self.vector.get())

class Select(Expression):
    def __init__(self, subtype, select, *args, **kwargs):
        select = const(select).vector
        args = [const(i).vector for i in args]
        default = const(kwargs.get("default", 0)).vector
        self.vector = back_end.Select(select, *args, default=default)
        self.subtype = Unsigned(self.vector.bits)
        self.string = "select()"

class ROM(Expression):
    def __init__(self, subtype, select, *args, **kwargs):
        select = const(select).vector
        args = [int(i) for i in args]
        default = int(kwargs.get("default", 0))
        self.vector = back_end.ROM(subtype.bits, select, *args, default=default)
        self.subtype = subtype
        self.string = "ROM()"

class RAM:
    def __init__(self, subtype, depth, clk, asynchronous=True):
        self.subtype = subtype
        self.write_address = Unsigned(int(ceil(log(depth, 2)))).wire()
        self.read_address = Unsigned(int(ceil(log(depth, 2)))).wire()
        self.write_data = subtype.wire()
        self.read_data = subtype.wire()
        self.write_enable = Boolean().wire()
        self.read_enable = Boolean().wire()
        self.ram = back_end.RAM(subtype.bits, depth, clk, 
                self.write_address.vector, self.write_data.vector, 
                self.write_enable.vector, self.read_address.vector, 
                self.read_enable.vector, asynchronous=asynchronous)

    def write(self, wraddr, wrdata, wren):
        self.write_address.drive(wraddr)
        self.write_data.drive(wrdata)
        self.write_enable.drive(wren)

    def read(self, rdaddr, rden=1):
        self.read_address.drive(rdaddr)
        self.read_enable.drive(const(rden))
        return Expression(self.subtype, self.ram, "ram()")


class Register(Expression):
    def __init__(self, subtype, clk, en, init, d):
        self.subtype = subtype
        d = d if d is None else const(d).vector
        init = init if init is None else int(init)
        en = const(en).vector
        self.vector = back_end.Register(clock=clk, bits=subtype.bits, en=en, d=d, init=init)

    def d(self, expression):
        self.vector.d = expression.vector

    def __repr__(self):
        return "register"

class Wire(Expression):
    def __init__(self, subtype):
        self.subtype = subtype
        self.vector = back_end.Wire(bits=subtype.bits)

    def drive(self, expression):
        self.vector.drive(expression.vector)

    def __repr__(self):
        return "wire"
