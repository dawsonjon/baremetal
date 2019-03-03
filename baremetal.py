def truncate(expression, bits):
    if expression is None:
        return None
    return expression & ((1<<bits) - 1)

sn = 0
def get_sn():
    global sn
    x = sn
    sn += 1
    return "exp_" + str(sn)

def number_of_bits_needed(x):
    if x > 0:
        n = 1
        while 1:
            max_number = 2**n-1
            if max_number >= x:
                return n
            n+=1
    elif x < 0:
        x = -x
        n = 1
        while 1:
            max_number = 2**(n-1)
            if max_number >= x:
                return n
            n+=1
    else:
        return 1

def const(i):
    if isinstance(i, Expression):
        return i
    bits = number_of_bits_needed(i)
    return Constant(int(i), bits)

class Expression:
    def __add__(self, other):
        return Binary(self, other, "+")
    def __sub__(self, other):
        return Binary(self, other, "-")
    def __mul__(self, other):
        return Binary(self, other, "*")
    def __gt__(self, other):
        return Binary(self, other, ">")
    def __ge__(self, other):
        return Binary(self, other, ">=")
    def __lt__(self, other):
        return Binary(self, other, "<")
    def __le__(self, other):
        return Binary(self, other, "<=")
    def __eq__(self, other):
        return Binary(self, other, "==")
    def __ne__(self, other):
        return Binary(self, other, "!=")
    def __lshift__(self, other):
        return Binary(self, other, "<<")
    def __rshift__(self, other):
        return Binary(self, other, ">>")
    def __and__(self, other):
        return Binary(self, other, "&")
    def __or__(self, other):
        return Binary(self, other, "|")
    def __xor__(self, other):
        return Binary(self, other, "^")
    def __neg__(self):
        return Unary(self, "-")
    def __invert__(self):
        return Unary(self, "~")
    def __getitem__(self, other):
        try:
            return Index(self, int(other))
        except TypeError:
            return Slice(self, other.start, other.stop)

class Input(Expression):
    def __init__(self, name, bits):
        self.value = None
        self.name = name
        self.bits = bits

    def set(self, x):
        self.value = x

    def get(self):
        return truncate(self.value, self.bits)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
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

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)

    def generate(self):
        return "  assign %s = %s;\n"%(self.name, self.value)

class Register(Expression):

    def __init__(self, clock, bits, initial_value=None, enable=1, expression=None):
        self.expression = None if expression is None else const(expression)
        self.clock = clock
        clock.registers.append(self)
        self.value = initial_value
        self.initial_value = initial_value
        self.bits = bits
        self.enable = const(enable)
        self.name = get_sn()

    def initialise(self):
        self.value = self.initial_value

    def set_expression(self, expression):
        self.expression = expression

    def evaluate(self):
        if self.enable.get():
            self.nextvalue = self.expression.get()
        else:
            self.nextvalue = self.value

    def update(self):
        self.value = self.nextvalue

    def get(self):
        return truncate(self.value, self.bits)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.expression.walk(netlist)
        self.enable.walk(netlist)

    def generate(self):
        return """
  reg [%s:0] %s_reg;
  always@(posedge %s) begin
    if %s begin
      %s_reg <= %s;
    end
  end
  assign %s = %s_reg;
"""%(self.bits-1, self.name, self.clock.name, self.enable.name, self.name, self.expression.name, self.name, self.name)

class Select(Expression):
    def __init__(self, select, *args, **kwargs):
        self.select=const(select)
        self.args=[const(i) for i in args]
        self.default=const(kwargs.get("default", 0))
        self.bits=max([i.bits for i in self.args])
        self.name = get_sn()

    def get(self):
        idx = self.select.get()
        if idx >= len(self.args):
            return truncate(self.default.get(), self.bits)
        return truncate(self.args[idx].get(), self.bits)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.select.walk(netlist)
        self.default.walk(netlist)
        for i in self.args:
            i.walk(netlist)
    def generate(self):
        select_string = "\n".join(["      %s:%s_reg <= %s;"%(i, self.name, n.name) for i, n in enumerate(self.args)])
        default_string = "\n      default:%s_reg <= %s;"%(self.name, self.default.name)
    
        return """
  reg [%s:0] %s_reg;
  always@(*)
    case (%s)
%s
    endcase;
  end
  assign %s = %s_reg;
"""%(
        self.bits-1,
        self.name,
        self.select.name, 
        select_string+default_string,
        self.name,
        self.name
)

def blackbox(inputs, outputs, template, mapping):
    names = {}
    for port in mapping:
        names[port] = mapping[port].name
    code = template.format(**names)
    blackbox = _BlackBox(inputs, code)
    output_expressions = [_BlackBoxOut(blackbox, idx, i) for idx, i in enumerate(outputs)]
    return output_expressions

class _BlackBox:
    def __init__(self, inputs, code):
        self.inputs = [const(i) for i in inputs]
        self.code = code

    def walk(self, netlist, idx):
        if idx:
            return
        for i in self.inputs:
            i.walk(netlist)

    def generate(self, idx):
        if idx:
            return ""
        else:
            return self.code

class _BlackBoxOut(Expression):
    def __init__(self, blackbox, idx, output):
        self.blackbox = blackbox
        self.idx      = idx
        self.output   = output
        self.bits     = output.bits
        self.name     = get_sn()

    def get(self):
        return self.output.get()

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.blackbox.walk(netlist, self.idx)

    def generate(self):
        return "  assign %s = %s;\n"%(self.name, self.output.name)+self.blackbox.generate(self.idx)

def Index(a, b):
    return Slice(a, b, b)

class Slice(Expression):
    def __init__(self, a, msb, lsb):
        self.a = const(a)
        assert msb < a.bits
        self.msb = int(msb)
        self.lsb = int(lsb)
        self.bits = self.msb - self.lsb + 1
        self.name = get_sn()

    def get(self):
        return truncate(self.a.get() >> self.lsb, self.bits)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.a.walk(netlist)

    def generate(self):
        return "  assign %s = %s[%u:%u];\n"%(
            self.name, self.a.name, self.msb, self.lsb)

class Resize(Expression):
    def __init__(self, a, bits):
        self.a = const(a)
        self.bits = int(bits)
        self.name = get_sn()

    def get(self):
        return truncate(self.a.get(), self.bits)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.a.walk(netlist)

    def generate(self):
        return "  assign %s = %s;\n"%(self.name, self.a.name)

class Unary(Expression):
    def __init__(self, a, operation):
        self.a = const(a)
        func_lookup = {
            "-":lambda a, b : a - b,
            "~":lambda a, b : ~a,
        }

        vstring_lookup = {
            "-": "  assign %s = -%s;\n",
            "~": "  assign %s = ~%s;\n",
        }
        self.bits = self.a.bits
        self.func = func_lookup[operation]
        self.vstring = vstring_lookup[operation]
        self.name = get_sn()

    def get(self):
        return truncate(self.func(self.a.get(), self.b.get()), self.bits)

    def generate(self):
        return self.vstring%(self.name, self.a.name)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.a.walk(netlist)

class Binary(Expression):
    def __init__(self, a, b, operation):
        self.a = const(a)
        self.b = const(b)
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
        self.bits = bits_lookup[operation](self.a.bits, self.b.bits)
        self.func = func_lookup[operation]
        self.vstring = vstring_lookup[operation]
        self.name = get_sn()

    def get(self):
        return truncate(self.func(self.a.get(), self.b.get()), self.bits)

    def generate(self):
        return self.vstring%(self.name, self.a.name, self.b.name)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.a.walk(netlist)
        self.b.walk(netlist)

class Output:
    def __init__(self, name, expression):
        self.name = name
        self.expression = const(expression)
        self.bits = self.expression.bits

    def get(self):
        return truncate(self.expression.get(), self.bits)

    def walk(self, netlist):
        self.expression.walk(netlist)

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

class Netlist:
    def __init__(self, name, clocks, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.clocks = clocks
        self.expressions = []
        self.name = name

    def walk(self):
        for i in self.outputs:
            i.walk(self)

    def generate(self):
        self.walk()
        return """
module %s(%s);
%s%s%s
%s
endmodule"""%(
    self.name,
    ", ".join([i.name for i in self.clocks+self.inputs+self.outputs]),
    "".join(["  input [%s:0] %s;\n"%(i.bits-1, i.name) for i in self.inputs]),
    "".join(["  output [%s:0] %s;\n"%(i.bits-1, i.name) for i in self.outputs]),
    "".join(["  wire [%s:0] %s;\n"%(i.bits-1, i.name) for i in self.expressions 
        if id(i) not in [id(x) for x in self.inputs]]),
    "".join([i.generate() for i in self.expressions + self.outputs]),
)
