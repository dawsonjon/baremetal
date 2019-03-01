class Expression:
    pass

def truncate(expression, bits):
    return expression & ((1<<bits) - 1)

sn = 0
def get_sn():
    global sn
    x = sn
    sn += 1
    return "exp_" + str(sn)

class Input(Expression):
    def __init__(self, name, bits):
        self.value = None
        self.name = name
        self.bits = bits

    def set(self, x):
        self.value = x

    def get(self):
        return truncate(self.value, self.bits)

    def enumerate(self, netlist):
        if self in netlist.expressions:
            return
        netlist.expressions.append(self)

    def generate(self):
        return ""

class Constant(Expression):
    def __init__(self, value, bits):
        self.value = value
        self.bits = bits
        self.name = get_sn()

    def get(self):
        return truncate(self.value, self.bits)

    def enumerate(self, netlist):
        if self in netlist.expressions:
            return
        netlist.expressions.append(self)

    def generate(self):
        return "  assign %s = %s;\n"%(self.name, self.value)

class Register(Expression):

    def __init__(self, clock, bits, initial_value=None, enable=None):
        self.expression = None
        self.clock = clock
        clock.registers.append(self)
        self.value = initial_value
        self.initial_value = initial_value
        self.bits = bits
        self.enable = enable
        self.name = get_sn()

    def initialise(self):
        self.value = self.initial_value

    def set_expression(self, expression):
        self.expression = expression

    def evaluate(self):
        if self.enable is None or self.enable.get():
            self.nextvalue = self.expression.get()
        else:
            self.nextvalue = self.value

    def update(self):
        self.value = self.nextvalue

    def get(self):
        return truncate(self.value, self.bits)

    def enumerate(self, netlist):
        if self in netlist.expressions:
            return
        netlist.expressions.append(self)
        self.expression.enumerate(netlist)
        if self.enable is not None:
            self.enable.enumerate(self)

    def generate(self):
        return """
  register [%s:0] %s_reg;
  always@(posedge %s) begin
    %s_reg <= %s;
  end
  assign %s = %s_reg;
"""%(self.bits-1, self.name, self.clock.name, self.name, self.expression.name, self.name, self.name)

class Select(Expression):
    def __init__(self, select, default=None, *args):
        self.select=select
        self.args=args
        self.default=None
        self.bits=max([i.bits for i in args])
        self.name = get_sn()

    def get(self):
        idx = self.select.get()
        if idx >= len(self.args):
            return truncate(self.default.get(), self.bits)
        return truncate(self.args[idx].get(), self.bits)

    def enumerate(self, netlist):
        if self in netlist.expressions:
            return
        netlist.expressions.append(self)
        self.select.enumerate(netlist)
        for i in self.args:
            i.enumerate(netlist)

class Slice(Expression):
    def __init__(self, a, msb, lsb):
        self.a = a
        assert msb < a.bits
        self.msb = int(msb)
        self.lsb = int(lsb)
        self.bits = self.msb - self.lsb + 1
        self.name = get_sn()

    def get(self):
        return truncate(self.a.get() >> self.lsb, self.bits)

    def enumerate(self, netlist):
        if self in netlist.expressions:
            return
        netlist.expressions.append(self)
        self.a.enumerate(netlist)

class Resize(Expression):
    def __init__(self, a, bits):
        self.a = a
        self.bits = int(bits)
        self.name = get_sn()

    def get(self):
        return truncate(self.a.get(), self.bits)

    def enumerate(self, netlist):
        if self in netlist.expressions:
            return
        netlist.expressions.append(self)
        self.a.enumerate(netlist)

class Binary(Expression):
    def __init__(self, a, b, operation):
        self.a = a
        self.b = b
        func_lookup = {
            "*":lambda a, b : a * b,
            "+":lambda a, b : a + b,
            "-":lambda a, b : a - b,
            "|":lambda a, b : a | b,
            "&":lambda a, b : a & b,
            ">>":lambda a, b : a >> b,
            "<<":lambda a, b : a << b,
            "==":lambda a, b : a == b,
            "!=":lambda a, b : a != b,
            "<":lambda a, b : a < b,
            ">":lambda a, b : a > b,
            "<=":lambda a, b : a <= b,
            ">=":lambda a, b : a >= b,
        }

        bits_lookup = {
            "*":lambda a, b : max([a, b]),
            "+":lambda a, b : max([a, b]),
            "-":lambda a, b : max([a, b]),
            "|":lambda a, b : max([a, b]),
            "&":lambda a, b : max([a, b]),
            "<<":lambda a, b : max([a, b]),
            ">>":lambda a, b : max([a, b]),
            "==":lambda a, b : 1,
            "!=":lambda a, b : 1,
            "<":lambda a, b : 1,
            ">":lambda a, b : 1,
            "<=":lambda a, b : 1,
            ">=":lambda a, b : 1,
        }
        vstring_lookup = {
            "*": "  assign %s = %s * %s;\n",
            "+": "  assign %s = %s + %s;\n",
            "-": "  assign %s = %s - %s;\n",
            "|": "  assign %s = %s | %s;\n",
            "&": "  assign %s = %s & %s;\n",
            "<<":"  assign %s = %s << %s;\n",
            ">>":"  assign %s = %s >> %s;\n",
            "==":"  assign %s = %s == %s;\n",
            "!=":"  assign %s = %s != %s;\n",
            "<": "  assign %s = %s < %s;\n",
            ">": "  assign %s = %s > %s;\n",
            "<=":"  assign %s = %s <= %s;\n",
            ">=":"  assign %s = %s >= %s;\n",
        }
        self.bits = bits_lookup[operation](a.bits, b.bits)
        self.func = func_lookup[operation]
        self.vstring = vstring_lookup[operation]
        self.name = get_sn()

    def get(self):
        return truncate(self.func(self.a.get(), self.b.get()), self.bits)

    def generate(self):
        return self.vstring%(self.name, self.a.name, self.b.name)

    def enumerate(self, netlist):
        if self in netlist.expressions:
            return
        netlist.expressions.append(self)
        self.a.enumerate(netlist)
        self.b.enumerate(netlist)

class Output:
    def __init__(self, name, bits):
        self.bits = bits
        self.name = name

    def set_expression(self, expression):
        self.expression = expression

    def get(self):
        return truncate(self.expression, self.bits)

    def enumerate(self, netlist):
        self.expression.enumerate(netlist)

    def generate(self):
        return "  assign %s = %s;\n"%(self.name, self.expression.name)

class Clock:
    def __init__(self, name="clk"):
        self.registers = []
        self.name = name

    def initialise(self):
        for i in self.registers:
            i.initialise()

    def tick(self):
        for i in self.registers:
            i.evaluate()
        for i in self.registers:
            i.update()

    def enumerate(self, netlist):
        for i in self.registers:
            i.enumerate(netlist)

class Netlist:
    def __init__(self, name, inputs, outputs, clocks):
        self.inputs = inputs
        self.outputs = outputs
        self.clocks = clocks
        self.expressions = []
        self.name = name

    def enumerate(self):
        for i in self.outputs + self.clocks:
            i.enumerate(self)

    def generate(self):
        return """
module %s(%s);
%s%s%s
%s
endmodule"""%(
    self.name,
    ", ".join([i.name for i in self.inputs+self.outputs+self.clocks]),
    "".join(["  input [%s:0] %s;\n"%(i.bits-1, i.name) for i in self.inputs]),
    "".join(["  output [%s:0] %s;\n"%(i.bits-1, i.name) for i in self.outputs]),
    "".join(["  wire [%s:0] %s;\n"%(i.bits-1, i.name) for i in self.expressions if i not in self.inputs]),
    "".join([i.generate() for i in self.expressions + self.outputs]),

)
        

clk = Clock("clk")
count = Register(clk, 3, 1)
count.expression = Binary(count, Constant(1, 3), "+")
count_out = Output("blah", 10)
count_out.expression = count
inp = Input("blahblah", 10)
outp = Output("blahblahblah", 10)
outp.expression = inp

netlist = Netlist("mymodule", [inp], [count_out, outp], [clk])
netlist.enumerate()
print netlist.generate()

clk.initialise()
print count.get()
for i in range(10):
    clk.tick()
    print count.get()
