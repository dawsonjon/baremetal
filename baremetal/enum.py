import back_end

def number_of_bits_needed(x):
    n=1
    while 1:
        max_value = (2**n)-1
        min_value = 0
        if min_value <= x <= max_value:
            return n
        n += 1

def const(value):
    if isinstance(value, Expression):
        return value
    bits = number_of_bits_needed(value)
    subtype = Enum(bits)
    return Constant(subtype, value)

class Enum:

    def __init__(self, *kwargs):
        self.lookup = kwargs
        self.bits = number_of_bits_needed(len(args))

    def to_vector(self, value):
        return int(self.lookup[value])

    def from_vector(self, value):
        return value

    def constant(self, value):
        return Constant(self, self.lookup[value])

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
    subtype = Unsigned(binary.bits)
    return Expression(subtype, binary)

class Expression:
    def __init__(self, subtype, vector):
        self.subtype = subtype
        self.vector = vector

    #binary operators
    def __eq__(self, other):     return binary(self, other, "==")
    def __ne__(self, other):     return binary(self, other, "!=")
    def get(self):
        return self.subtype.from_vector(self.vector.get())

class Constant(Expression):
    def __init__(self, subtype, value):
        self.subtype = subtype
        self.vector = back_end.Constant(subtype.to_vector(value), subtype.bits)

class Input(Expression):
    def __init__(self, subtype, name):
        self.subtype = subtype
        self.vector = back_end.Input(name, subtype.bits)

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
        self.subtype = Enum(self.vector.bits)

class Register(Expression):
    def __init__(self, subtype, clk, en, init, d):
        self.subtype = subtype
        d = d if d is None else const(d).vector
        init = init if init is None else int(init)
        en = const(en).vector
        self.vector = back_end.Register(clock=clk, bits=subtype.bits, en=en, d=d, init=init)

    def d(self, expression):
        self.vector.d = expression.vector
