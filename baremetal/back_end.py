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

class Input:
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

class Constant:
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

class Wire:
    def __init__(self, bits):
        self.d = None
        self.bits = bits

    def get(self):
        return truncate(self.drive.get(), self.bits)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        self.drive.walk(netlist)

    def drive(self, expression):
        self.d = expression

    def generate(self):
        return "  assign %s = %s"%(self.name, self.d.name)

class Register:

    def __init__(self, clock, bits, init=None, en=1, d=None):
        self.d = d
        self.clock = clock
        clock.registers.append(self)
        self.value = init
        self.init = init
        self.bits = bits
        self.en = en
        self.name = get_sn()

    def initialise(self):
        self.value = self.init

    def evaluate(self):
        if self.en.get():
            self.nextvalue = self.d.get()
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
        self.d.walk(netlist)
        self.en.walk(netlist)

    def generate(self):
        return """
  reg [%s:0] %s_reg;
  always@(posedge %s) begin
    if %s begin
      %s_reg <= %s;
    end
  end
  assign %s = %s_reg;
"""%(self.bits-1, self.name, self.clock.name, self.en.name, self.name, self.d.name, self.name, self.name)

class Select:
    def __init__(self, select, *args, **kwargs):
        self.select=select
        self.args=args
        self.default=kwargs.get("default", 0)
        self.bits=max([i.bits for i in self.args+(self.default,)])
        self.name = get_sn()

    def get(self):
        idx = self.select.get()
        if idx is None:
            return None
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
        self.inputs = inputs
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

class _BlackBoxOut:
    def __init__(self, blackbox, idx, output):
        self.blackbox = blackbox
        self.idx      = idx
        self.output   = output
        self.bits     = output.bits
        self.name     = get_sn()

    def get(self):
        return truncate(self.output.get(), self.bits)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.blackbox.walk(netlist, self.idx)

    def generate(self):
        return "  assign %s = %s;\n"%(self.name, self.output.name)+self.blackbox.generate(self.idx)

def Index(a, b):
    return Slice(a, b, b)

class Slice:
    def __init__(self, a, msb, lsb):
        self.a = a
        assert msb < a.bits
        self.msb = int(msb)
        self.lsb = int(lsb)
        self.bits = self.msb - self.lsb + 1
        self.name = get_sn()

    def get(self):
        value = self.a.get() 
        if value is None:
            return None
        return truncate(value >> self.lsb, self.bits)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.a.walk(netlist)

    def generate(self):
        return "  assign %s = %s[%u:%u];\n"%(
            self.name, self.a.name, self.msb, self.lsb)

class Resize:
    def __init__(self, a, bits):
        self.a = a
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

class Unary:
    def __init__(self, a, operation):
        self.a = a
        func_lookup = {
            "-":lambda a : -a,
            "~":lambda a : ~a,
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
        value = self.a.get()
        if value is None:
            return None
        return truncate(self.func(value), self.bits)

    def generate(self):
        return self.vstring%(self.name, self.a.name)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.a.walk(netlist)

class Concatenate:
    def __init__(self, a, b, operation):
        self.a = a
        self.b = b
        self.bits = self.a.bits + self.b.bits
        self.name = get_sn()

    def get(self):
        a = self.a.get()
        if a is None:
            return None
        b = self.b.get()
        if b is None:
            return None
        return truncate((a<<self.b.bits) | b, self.bits)

    def generate(self):
        return "  assign %s = {%s, %s};"%(self.name, self.a.name, self.b.name)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.a.walk(netlist)
        self.b.walk(netlist)

def sign(x, bits):
    negative = x & (1<<(bits-1))
    mask = ~((1 << bits)-1)
    if negative:
        return mask | x
    return x


class Binary:
    def __init__(self, a, b, operation):
        self.a = a
        self.b = b
        func_lookup = {
            "*":lambda a, b : a * b,
            "+":lambda a, b : a + b,
            "-":lambda a, b : a - b,
            "|":lambda a, b : a | b,
            "&":lambda a, b : a & b,
            "^":lambda a, b : a ^ b,
            ">>":lambda a, b : a >> b,
            "s>>":lambda x, y : sign(x, a.bits) >> y,
            "<<":lambda a, b : a << b,
            "==":lambda a, b : a == b,
            "!=":lambda a, b : a != b,
            "<":lambda a, b : a < b,
            ">":lambda a, b : a > b,
            "<=":lambda a, b : a <= b,
            ">=":lambda a, b : a >= b,
            "s<":lambda x, y : sign(x, a.bits) < sign(y, b.bits),
            "s>":lambda x, y : sign(x, a.bits) > sign(y, b.bits),
            "s<=":lambda x, y : sign(x, a.bits) <= sign(y, b.bits),
            "s>=":lambda x, y : sign(x, a.bits) >= sign(y, b.bits),
        }

        bits_lookup = {
            "*":lambda a, b : max([a, b]),
            "+":lambda a, b : max([a, b]),
            "-":lambda a, b : max([a, b]),
            "|":lambda a, b : max([a, b]),
            "&":lambda a, b : max([a, b]),
            "^":lambda a, b : max([a, b]),
            "<<":lambda a, b : max([a, b]),
            ">>":lambda a, b : max([a, b]),
            "s>>":lambda a, b : max([a, b]),
            "==":lambda a, b : 1,
            "!=":lambda a, b : 1,
            "<":lambda a, b : 1,
            ">":lambda a, b : 1,
            "<=":lambda a, b : 1,
            ">=":lambda a, b : 1,
            "s<":lambda a, b : 1,
            "s>":lambda a, b : 1,
            "s<=":lambda a, b : 1,
            "s>=":lambda a, b : 1,
        }
        vstring_lookup = {
            "*": "  assign %s = %s * %s;\n",
            "+": "  assign %s = %s + %s;\n",
            "-": "  assign %s = %s - %s;\n",
            "|": "  assign %s = %s | %s;\n",
            "&": "  assign %s = %s & %s;\n",
            "^": "  assign %s = %s ^ %s;\n",
            "<<":"  assign %s = %s << %s;\n",
            "s>>":"  assign %s = $signed(%s) >> $signed(%s);\n",
            ">>":"  assign %s = %s >> %s;\n",
            "==":"  assign %s = %s == %s;\n",
            "!=":"  assign %s = %s != %s;\n",
            "<": "  assign %s = %s < %s;\n",
            ">": "  assign %s = %s > %s;\n",
            "<=":"  assign %s = %s <= %s;\n",
            ">=":"  assign %s = %s >= %s;\n",
            "s<": "  assign %s = $signed(%s) < $signed(%s);\n",
            "s>": "  assign %s = $signed(%s) > $signed(%s);\n",
            "s<=":"  assign %s = $signed(%s) <= $signed(%s);\n",
            "s>=":"  assign %s = $signed(%s) >= $signed(%s);\n",
        }
        self.bits = bits_lookup[operation](self.a.bits, self.b.bits)
        self.func = func_lookup[operation]
        self.vstring = vstring_lookup[operation]
        self.name = get_sn()

    def get(self):
        a = self.a.get()
        if a is None:
            return None
        b = self.b.get()
        if b is None:
            return None
        return truncate(self.func(a, b), self.bits)

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
        self.expression = expression
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
        self.inputs = [i.vector for i in inputs]
        self.outputs = [i.vector for i in outputs]
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
