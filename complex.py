from baremetal import *
        
class Complex:

    def __init__(self, subtype):
        self.subtype = subtype

    def constant(self, value):
        i = self.subtype.constant(value.real)
        q = self.subtype.constant(value.imag)
        return Expression(self, i, q)

    def select(self, select, *args, **kwargs):
        i_args = [i.real for i in args]
        q_args = [i.imag for i in args]
        i_kwargs = {}
        q_kwargs = {}
        if "default" in kwargs:
            i_kwargs["default"] = kwargs["default"].real
            q_kwargs["default"] = kwargs["default"].imag
        i = i.subtype.select(select, *i_args, **i_kwargs)
        q = q.subtype.select(select, *q_args, **q_kwargs)
        return Expression(self, i, q)

    def rom(self, select, *args, **kwargs):
        i_args = [i.real for i in args]
        q_args = [i.imag for i in args]
        i_kwargs = {}
        q_kwargs = {}
        if "default" in kwargs:
            i_kwargs["default"] = kwargs["default"].real
            q_kwargs["default"] = kwargs["default"].imag
        i = i.subtype.rom(select, *i_args, **i_kwargs)
        q = q.subtype.rom(select, *q_args, **q_kwargs)
        return Expression(self, self.signed.rom(select, *args, **kwargs))

    def register(self, clk, en=1, init=None, d=None):
        return Register(self, clk, en=en, init=init, d=d)

    def wire(self):
        return Wire(self)

class Expression:
    def __init__(self, subtype, i, q):
        self.subtype = subtype
        self.i = i
        self.q = q
        self.real = i
        self.imag = q

    def __add__(self, other): 
        return Expression(self.subtype, self.i+other.i, self.q+other.q)

    def __sub__(self, other): 
        return Expression(self.subtype, self.i-other.i, self.q-other.q)

    def __mul__(self, other): 
        i = self.i*other.i - self.q*other.q
        q = self.q*other.i + self.i*other.q
        return Expression(self.subtype, i, q)

    def __eq__(self, other):  
        return self.i==other.i & self.q==other.q

    def __ne__(self, other):
        return self.i!=other.i | self.q!=other.q

    def get(self):
        return self.i.get()+1.0j*self.q.get()

class Wire(Expression):
    def __init__(self, subtype):
        self.subtype = subtype
        self.i = subtype.subtype.wire()
        self.q = subtype.subtype.wire()

    def drive(self, expression):
        i_d = None if init is None else expression.real
        q_d = None if init is None else expression.imag
        self.i.drive(i_d)
        self.q.drive(q_d)

class Register(Expression):
    def __init__(self, subtype, clk, en, init, d):
        self.subtype = subtype
        i_init = None if init is None else init.real
        i_d = None if d is None else d.real
        q_init = None if init is None else init.imag
        q_d = None if d is None else d.imag
        self.i = self.subtype.subtype.register(clk, en=1, init=i_init, d=i_d)
        self.q = self.subtype.subtype.register(clk, en=1, init=q_init, d=q_d)
        self.real = self.i
        self.imag = self.q

    def d(self, expression):
        i_d = None if expression is None else expression.real
        q_d = None if expression is None else expression.imag
        self.i.d(i_d)
        self.q.d(q_d)
