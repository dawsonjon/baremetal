from math import ceil, log

from baremetal.exceptions import error

enable_warnings = False


def warning(message):
    if enable_warnings:
        print(message)


def truncate(expression, bits):
    if expression is None:
        return None
    return expression & ((1 << bits) - 1)


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
        return "  assign %s = %s;\n" % (self.name, self.value)


class Wire:
    def __init__(self, filename, lineno, bits):
        self.d = None
        self.bits = bits
        self.name = get_sn()
        self.filename = filename
        self.lineno = lineno

    def get(self):
        if self.d is None:
            error("Wire is not driven in %s, line %s" % (self.filename, self.lineno))
        return truncate(self.d.get(), self.bits)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.d.walk(netlist)

    def drive(self, expression):
        self.d = expression

    def generate(self):
        return "  assign %s = %s;\n" % (self.name, self.d.name)


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
        if self.init is not None:
            return """
      reg [%s:0] %s_reg = %s;
      always@(posedge %s) begin
        if (%s) begin
          %s_reg <= %s;
        end
      end
      assign %s = %s_reg;
    """ % (
                self.bits - 1,
                self.name,
                self.init,
                self.clock.name,
                self.en.name,
                self.name,
                self.d.name,
                self.name,
                self.name,
            )
        else:
            return """
      reg [%s:0] %s_reg;
      always@(posedge %s) begin
        if (%s) begin
          %s_reg <= %s;
        end
      end
      assign %s = %s_reg;
    """ % (
                self.bits - 1,
                self.name,
                self.clock.name,
                self.en.name,
                self.name,
                self.d.name,
                self.name,
                self.name,
            )


class DPRPort:
    def __init__(self, ram, clk, addr, data, wen):

        clk.registers.append(self)
        self.addr = addr
        self.data = data
        self.wen = wen
        self.ram = ram
        self.value = None
        ram.ports.append(self)

        self.bits = int(ram.bits)
        self.depth = int(ram.depth)
        self.name = get_sn()

    def initialise(self):
        self.value = None

    def evaluate(self):
        self.do_write = self.wen.get()
        self.data_to_write = self.data.get()
        self.address = self.addr.get()

    def update(self):

        #read before write behaviour
        if self.address is None:
            return None
        if self.address >= self.depth:
            warning("RAM address out of range")
        try:
            self.value = truncate(self.ram.ram[self.address], self.bits)
        except IndexError:
            self.value = None

        # write to the RAM if enabled
        if self.do_write:
            if self.address is None:
                self.ram.ram = [None for i in range(self.depth)]
            else:
                self.ram.ram[self.address] = self.data_to_write

        # if enable is None, we may have corrupted some or all RAM
        if self.do_write is None:
            if self.address is None:
                self.ram.ram = [None for i in range(self.depth)]
            else:
                self.ram.ram[self.address] = None


    def get(self):
        return self.value

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)

        self.wen.walk(netlist)
        self.addr.walk(netlist)
        self.data.walk(netlist)

    def generate(self):
        return ""

    def generate_port(self):
        return """
  //Additional DPR portb (synchronous)
  reg [%s:0] %s_reg;
  always@(posedge clk) begin
    if (%s) begin
        %s_ram[%s] <= %s;
    end
    %s_reg <= %s_ram[%s];
  end
  assign %s = %s_reg;
""" % (
                self.bits - 1,
                self.name,
                self.wen.name,
                self.ram.name,
                self.addr.name,
                self.data.name,
                self.name,
                self.ram.name,
                self.addr.name,
                self.name,
                self.name,
            )

class DPR:
    def __init__(
        self,
        bits,
        depth,
        clk,
        addr,
        data,
        wen,
        initialise=None,
    ):

        clk.registers.append(self)
        self.ports = []
        self.addr = addr
        self.data = data
        self.wen = wen
        self.ram = [None for i in range(depth)]
        self.value = None

        self.bits = int(bits)
        self.depth = int(depth)
        self.name = get_sn()
        if initialise is not None:
            self.initial_values = [truncate(int(i), self.depth) for i in initialise]
        else:
            self.initial_values = None

    def initialise(self):
        if self.initial_values is None:
            self.ram = [None for i in range(self.depth)]
        else:
            self.ram = [0 for i in range(self.depth)]
            for i, v in enumerate(self.initial_values):
                self.ram[i] = v
        self.value = None

    def evaluate(self):
        self.do_write = self.wen.get()
        self.data_to_write = self.data.get()
        self.address = self.addr.get()

    def update(self):
        #RAM has read before write behaviour
        if self.address is None:
            return None
        if self.address >= self.depth:
            warning("RAM address out of range")
        try:
            self.value = truncate(self.ram[self.address], self.bits)
        except IndexError:
            self.value = None

        # write to the RAM if enabled
        if self.do_write:
            if self.address is None:
                self.ram = [None for i in range(self.depth)]
            else:
                self.ram[self.address] = self.data_to_write

        # if enable is None, we may have corrupted some or all RAM
        if self.do_write is None:
            if self.address is None:
                self.ram = [None for i in range(self.depth)]
            else:
                self.ram[self.address] = None


    def get(self):
        return self.value

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        for port in self.ports:
            port.walk(netlist)
        self.wen.walk(netlist)
        self.addr.walk(netlist)
        self.data.walk(netlist)

    def generate(self):

        if self.initial_values is None:
            init_string = ""
        else:
            init_string = "\n".join(
                [
                    "    %s_ram[%s] = %s;" % (self.name, i, n)
                    for i, n in enumerate(self.initial_values[: self.depth])
                ]
            )
            init_string = (
                """

  //Initialise DPR contents
  initial
  begin
%s
  end
"""
                % init_string
            )

        ram_string = """
  //Create DPR (Synchronous)
  reg [%s:0] %s_ram [%s:0];
  %s
  //Implement DPR porta (Synchronous)
  reg [%s:0] %s_reg;
  always@(posedge clk) begin
    if (%s) begin
        %s_ram[%s] <= %s;
    end
    %s_reg <= %s_ram[%s];
  end
  assign %s = %s_reg;
""" % (
                self.bits - 1,
                self.name,
                int(self.depth) - 1,
                init_string,
                self.bits - 1,
                self.name,
                self.wen.name,
                self.name,
                self.addr.name,
                self.data.name,
                self.name,
                self.name,
                self.addr.name,
                self.name,
                self.name,
            )
        for port in self.ports:
            ram_string += port.generate_port()

        return ram_string


class RAM:
    def __init__(
        self,
        bits,
        depth,
        clk,
        waddr,
        wdata,
        wen,
        raddr,
        ren=1,
        asynchronous=True,
        initialise=None,
    ):

        clk.registers.append(self)
        self.asynchronous = asynchronous
        self.waddr = waddr
        self.wdata = wdata
        self.wen = wen
        self.raddr = raddr
        self.ren = ren
        self.ram = [None for i in range(depth)]
        self.value = None

        self.bits = int(bits)
        self.depth = int(depth)
        self.name = get_sn()
        if initialise is not None:
            self.initial_values = [truncate(int(i), self.depth) for i in initialise]
        else:
            self.initial_values = None

    def initialise(self):
        if self.initial_values is None:
            self.ram = [None for i in range(self.depth)]
        else:
            self.ram = [0 for i in range(self.depth)]
            for i, v in enumerate(self.initial_values):
                self.ram[i] = v
        self.value = None

    def evaluate(self):
        self.do_write = self.wen.get()
        self.data_to_write = self.wdata.get()
        self.address_to_write = self.waddr.get()
        self.address_to_read = self.raddr.get()
        self.do_read = self.ren.get()

    def update(self):
        #RAM has write before read behaviour

        # write to the RAM if enabled
        if self.do_write:
            if self.address_to_write is None:
                self.ram = [None for i in range(self.depth)]
            else:
                self.ram[self.address_to_write] = self.data_to_write

        # if enable is None, we may have corrupted some or all RAM
        if self.do_write is None:
            if self.address_to_write is None:
                self.ram = [None for i in range(self.depth)]
            else:
                self.ram[self.address_to_write] = None

        if not self.asynchronous:
            if self.do_read is None:
                return None
            if self.do_read:
                if self.address_to_read is None:
                    return None
                if self.address_to_read >= self.depth:
                    warning("RAM address out of range")
                try:
                    self.value = truncate(self.ram[self.address_to_read], self.bits)
                except IndexError:
                    self.value = None

    def get(self):

        if self.asynchronous:
            idx = self.raddr.get()
            if idx is None:
                return None
            if idx >= self.depth:
                warning("RAM address out of range")
            return truncate(self.ram[idx], self.bits)
        else:
            return self.value

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.ren.walk(netlist)
        self.raddr.walk(netlist)
        self.wen.walk(netlist)
        self.waddr.walk(netlist)
        self.wdata.walk(netlist)

    def generate(self):
        if self.initial_values is None:
            init_string = ""
        else:
            init_string = "\n".join(
                [
                    "    %s_ram[%s] = %s;" % (self.name, i, n)
                    for i, n in enumerate(self.initial_values[: self.depth])
                ]
            )
            init_string = (
                """

  //Initialise RAM contents
  initial
  begin
%s
  end
"""
                % init_string
            )

        if self.asynchronous:
            ram_string = """
  //Create RAM
  reg [%s:0] %s_ram [%s:0];
%s
  //Implement RAM port (Asynchronous)
  always@(posedge clk) begin
    if (%s) begin
      %s_ram[%s] <= %s;
    end
  end
  assign %s = %s_ram[%s];
""" % (
                self.bits - 1,
                self.name,
                int(self.depth) - 1,
                init_string,
                self.wen.name,
                self.name,
                self.waddr.name,
                self.wdata.name,
                self.name,
                self.name,
                self.raddr.name,
            )
        else:
            ram_string = """
  //Create RAM (Synchronous)
  reg [%s:0] %s_ram [%s:0];
  %s
  //Implement RAM port (Synchronous)
  reg [%s:0] %s_addr;
  always@(posedge clk) begin
    if (%s) begin
        %s_addr <= %s;
    end
    if (%s) begin
        %s_ram[%s] <= %s;
    end
  end
  assign %s = %s_ram[%s_addr];
""" % (
                self.bits - 1,
                self.name,
                int(self.depth) - 1,
                init_string,
                self.bits - 1,
                self.name,
                self.ren.name,
                self.name,
                self.raddr.name,
                self.wen.name,
                self.name,
                self.waddr.name,
                self.wdata.name,
                self.name,
                self.name,
                self.name,
            )

        return ram_string


class ROM:
    def __init__(self, bits, select, *args, **kwargs):
        self.select = select
        self.args = [int(i) for i in args]
        self.default = int(kwargs.get("default", 0))
        self.bits = bits
        self.name = get_sn()

    def get(self):
        idx = self.select.get()
        if idx is None:
            return None
        if idx >= len(self.args):
            return truncate(self.default, self.bits)
        return truncate(self.args[idx], self.bits)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.select.walk(netlist)

    def generate(self):
        select_string = "\n".join(
            [
                "      %s:%s_reg <= %s;" % (i, self.name, n)
                for i, n in enumerate(self.args)
            ]
        )
        default_string = "\n      default:%s_reg <= %s;" % (self.name, self.default)

        return """
  reg [%s:0] %s_reg;
  always@(*) begin
    case (%s)
%s
    endcase
  end
  assign %s = %s_reg;
""" % (
            self.bits - 1,
            self.name,
            self.select.name,
            select_string + default_string,
            self.name,
            self.name,
        )


class Select:
    def __init__(self, select, *args, **kwargs):
        self.select = select
        self.args = args
        self.default = kwargs.get("default", 0)
        self.bits = max([i.bits for i in self.args + (self.default,)])
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
        select_string = "\n".join(
            [
                "      %s:%s_reg <= %s;" % (i, self.name, n.name)
                for i, n in enumerate(self.args)
            ]
        )
        default_string = "\n      default:%s_reg <= %s;" % (
            self.name,
            self.default.name,
        )

        return """
  reg [%s:0] %s_reg;
  always@(*) begin
    case (%s)
%s
    endcase
  end
  assign %s = %s_reg;
""" % (
            self.bits - 1,
            self.name,
            self.select.name,
            select_string + default_string,
            self.name,
            self.name,
        )


def Index(a, b):
    return Slice(a, b, b)


class Slice:
    def __init__(self, a, msb, lsb):
        self.a = a
        if msb >= a.bits:
            error("%u is out of range [%u:0]" % (msb, a.bits - 1))
        if lsb > msb:
            error("%u is greater than %u" % (msb, lsb))

        self.msb = int(msb)
        self.lsb = int(lsb)
        self.bits = (self.msb - self.lsb) + 1
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
        return "  assign %s = %s[%u:%u];\n" % (
            self.name,
            self.a.name,
            self.msb,
            self.lsb,
        )


class Resize:
    def __init__(self, a, bits, signed=False):
        self.a = a
        self.bits = int(bits)
        if bits < 0:
            error("Vector sizes of less than 0 are not supported")
        self.name = get_sn()
        self.signed = signed

    def get(self):
        if self.signed:
            value = self.a.get()
            if value is None:
                return None
            return truncate(sign(self.a.get(), self.a.bits), self.bits)
        else:
            return truncate(self.a.get(), self.bits)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.a.walk(netlist)

    def generate(self):
        if self.signed:
            return "  assign %s = $signed(%s);\n" % (self.name, self.a.name)
        else:
            return "  assign %s = %s;\n" % (self.name, self.a.name)


class Label:
    def __init__(self, a, label):
        self.a = a
        self.bits = self.a.bits
        self.name = get_sn()
        self.label = label

    def get(self):
        return self.a.get()

    def generate(self):
        return """
        wire [%s:0] %s;
        assign %s = %s;
        assign %s = %s;""" % (
            self.bits - 1,
            self.label,
            self.name,
            self.label,
            self.label,
            self.a.name,
        )

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.a.walk(netlist)


class Unary:
    def __init__(self, a, operation):
        self.a = a
        func_lookup = {
            "-": lambda a: -a,
            "~": lambda a: ~a,
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
        return self.vstring % (self.name, self.a.name)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.a.walk(netlist)


class Concatenate:
    def __init__(self, a, b):
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
        return truncate((a << self.b.bits) | b, self.bits)

    def generate(self):
        return "  assign %s = {%s, %s};" % (self.name, self.a.name, self.b.name)

    def walk(self, netlist):
        if id(self) in [id(i) for i in netlist.expressions]:
            return
        netlist.expressions.append(self)
        self.a.walk(netlist)
        self.b.walk(netlist)


def sign(x, bits):
    if x is None:
        return None
    if int(bits) == 0:
        return 0
    negative = x & (1 << (bits - 1))
    mask = ~((1 << bits) - 1)
    if negative:
        return mask | x
    return x


class Binary:
    def __init__(self, a, b, operation):
        self.a = a
        self.b = b
        func_lookup = {
            "*": lambda a, b: a * b,
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "|": lambda a, b: a | b,
            "&": lambda a, b: a & b,
            "^": lambda a, b: a ^ b,
            ">>": lambda a, b: a >> b,
            "s>>": lambda x, y: sign(x, a.bits) >> y,
            "<<": lambda a, b: a << b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            "<": lambda a, b: a < b,
            ">": lambda a, b: a > b,
            "<=": lambda a, b: a <= b,
            ">=": lambda a, b: a >= b,
            "s<": lambda x, y: sign(x, a.bits) < sign(y, b.bits),
            "s>": lambda x, y: sign(x, a.bits) > sign(y, b.bits),
            "s<=": lambda x, y: sign(x, a.bits) <= sign(y, b.bits),
            "s>=": lambda x, y: sign(x, a.bits) >= sign(y, b.bits),
        }

        bits_lookup = {
            "*": lambda a, b: max([a, b]),
            "+": lambda a, b: max([a, b]),
            "-": lambda a, b: max([a, b]),
            "|": lambda a, b: max([a, b]),
            "&": lambda a, b: max([a, b]),
            "^": lambda a, b: max([a, b]),
            "<<": lambda a, b: max([a, b]),
            ">>": lambda a, b: max([a, b]),
            "s>>": lambda a, b: max([a, b]),
            "==": lambda a, b: 1,
            "!=": lambda a, b: 1,
            "<": lambda a, b: 1,
            ">": lambda a, b: 1,
            "<=": lambda a, b: 1,
            ">=": lambda a, b: 1,
            "s<": lambda a, b: 1,
            "s>": lambda a, b: 1,
            "s<=": lambda a, b: 1,
            "s>=": lambda a, b: 1,
        }
        vstring_lookup = {
            "*": "  assign %s = %s * %s;\n",
            "+": "  assign %s = %s + %s;\n",
            "-": "  assign %s = %s - %s;\n",
            "|": "  assign %s = %s | %s;\n",
            "&": "  assign %s = %s & %s;\n",
            "^": "  assign %s = %s ^ %s;\n",
            "<<": "  assign %s = %s << %s;\n",
            "s>>": "  assign %s = $signed(%s) >>> $signed(%s);\n",
            ">>": "  assign %s = %s >> %s;\n",
            "==": "  assign %s = %s == %s;\n",
            "!=": "  assign %s = %s != %s;\n",
            "<": "  assign %s = %s < %s;\n",
            ">": "  assign %s = %s > %s;\n",
            "<=": "  assign %s = %s <= %s;\n",
            ">=": "  assign %s = %s >= %s;\n",
            "s<": "  assign %s = $signed(%s) < $signed(%s);\n",
            "s>": "  assign %s = $signed(%s) > $signed(%s);\n",
            "s<=": "  assign %s = $signed(%s) <= $signed(%s);\n",
            "s>=": "  assign %s = $signed(%s) >= $signed(%s);\n",
        }
        self.bits = bits_lookup[operation](self.a.bits, self.b.bits)
        self.func = func_lookup[operation]
        self.vstring = vstring_lookup[operation]
        self.name = get_sn()
        self.operation = operation

    def get(self):
        a = self.a.get()
        if a is None:
            return None
        b = self.b.get()
        if b is None:
            return None
        return truncate(self.func(a, b), self.bits)

    def generate(self):
        return self.vstring % (self.name, self.a.name, self.b.name)

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
        return "  assign %s = %s;\n" % (self.name, self.expression.name)


class Clock:
    def __init__(self, name="clk"):
        self.registers = []
        self.name = name
        self.bits = 1

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
endmodule""" % (
            self.name,
            ", ".join([i.name for i in self.clocks + self.inputs + self.outputs]),
            "".join(
                [
                    "  input [%s:0] %s;\n" % (i.bits - 1, i.name)
                    for i in self.inputs + self.clocks
                ]
            ),
            "".join(
                ["  output [%s:0] %s;\n" % (i.bits - 1, i.name) for i in self.outputs]
            ),
            "".join(
                [
                    "  wire [%s:0] %s;\n" % (i.bits - 1, i.name)
                    for i in self.expressions
                    if id(i) not in [id(x) for x in self.inputs]
                ]
            ),
            "".join([i.generate() for i in self.expressions + self.outputs]),
        )
