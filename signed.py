class Unsigned:

    def __init__(bits):
        self.bits = bits

    def to_vector(value):
        return int(round(float(value)))

    def from_vector(value):
        return float(value)

    def constant(self, value):
        return Constant(self, value)

    def input(self, name):
        return Input(self, name)

    def output(self, name, expression):
        return Input(self, name, expression)

class Expression:
    def __init__(self, t, vector):
        self.t = t
        self.vector = vector

    def __add__(self, other):    
        return Expression(self, Binary(self.vector, other.vector, "+"))

    def __sub__(self, other):    return self.t.sub(self, other)
    def __mul__(self, other):    return self.t.mul(self, other)
    def __gt__(self, other):     return self.t.gt(self, other)
    def __ge__(self, other):     return self.t.ge(self, other)
    def __lt__(self, other):     return self.t.lt(self, other)
    def __le__(self, other):     return self.t.le
    def __eq__(self, other):     return self.t.eq
    def __ne__(self, other):     return self.t.ne
    def __lshift__(self, other): return self.t.lshift
    def __rshift__(self, other): return self.t.rshift
    def __and__(self, other):    return self.t.band
    def __or__(self, other):     return self.t.bor
    def __xor__(self, other):    return self.t.xor
    def __neg__(self):           return self.t.neg
    def __invert__(self):        return self.t.invert
    def __getitem__(self, other): 
    def resize(self, other):
    def select(self, other):

    def to_signed(self):
        return Signed(:wq


class Constant(Expression):
    def __init__(self, t, value):
        self.t = t
        self.vector = barmetal.Constant(t.to_vector(value), t.bits)

class Input(Expression):
    def __init__(self, t, name):
        self.t = t
        self.vector = baremetal.Input(name, t.bits)

    def set(self, value):
        self.vector.set(t.to_vector(value))

class Output(Expression):
    def __init__(self, t, name, expression):
        self.t = t
        self.vector = baremetal.Output(name, expression.vector)

    def get(self):
        return self.t.from_vector(self.vector.get())
