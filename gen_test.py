"""This is a simple tool to demonstrate that the simulation results match
the results in a verilog sim of the generated code"""

import os
import subprocess

from baremetal import *
from baremetal.back_end import sign


def test(self, stimulus, latency):
    """A function that generates a testbench for the generated logic."""

    if not os.path.exists("test"):
        os.mkdir("test")
    current_dir = os.getcwd()
    os.chdir("test")
    if not os.path.exists("stim"):
        os.mkdir("stim")

    self.walk()
    stimulus_length = max([len(i) for i in list(stimulus.values())])
    stop_clocks = stimulus_length + latency + 1

    for n, s in list(stimulus.items()):
        f = open("stim/"+n, 'w')
        f.write("".join(["%d\n"%i for i in s]))
        f.close()

    testbench = "".join([
    "module %s_tb;\n"%self.name,
    "  reg clk;\n",
    "".join(["  reg [%s:0] %s;\n"%(i.bits-1, i.name) 
        for i in self.inputs]),
    "".join(["  wire [%s:0] %s;\n"%(i.bits-1, i.name) 
        for i in self.outputs]),
    "".join(["  integer %s_file;\n"%(i.name) for i in self.inputs]),
    "".join(["  integer %s_file;\n"%(i.name) for i in self.outputs]),
    "".join(["  integer %s_count;\n"%(i.name) for i in self.inputs]),
    "".join(["  integer %s_count;\n"%(i.name) for i in self.outputs]),
    "\n",
    "  %s %s1 (%s);\n"%(self.name, self.name, ", ".join([i.name 
        for i in self.clocks+self.inputs+self.outputs])),
    "  initial\n",
    "  begin\n",
    "".join(['    %s_file = $fopen("stim/%s");\n'%(i.name, i.name) 
        for i in self.outputs]),
    "".join(['    %s_file = $fopen("stim/%s", "r");\n'%(i.name, i.name) 
        for i in self.inputs]),
    "  end\n\n",
    "  initial\n",
    "  begin\n",
    "    #%s $finish;\n" % (10 * stop_clocks),
    "  end\n\n",
    "  initial\n",
    "  begin\n",
    "    clk <= 1'b0;\n",
    "    while (1) begin\n",
    "      #5 clk <= ~clk;\n",
    "    end\n",
    "  end\n\n",
    "  always @ (posedge clk)\n",
    "  begin\n",
    "".join(['    $fdisplay(%s_file, "%%d", %s);\n'%(i.name, i.name) 
        for i in self.outputs]),
    "".join([
        '    #0 %s_count = $fscanf(%s_file, "%%d\\n", %s);\n'%(
            i.name, i.name, i.name) for i in self.inputs]),
    "  end\n",
    "endmodule\n"])

    f = open("%s.v"%self.name, 'w')
    f.write(self.generate())
    f.close()

    f = open("%s_tb.v"%self.name, 'w')
    f.write(testbench)
    f.close()

    subprocess.call(["iverilog", "-o", "%s_tb"%self.name, "%s.v"%self.name, "%s_tb.v"%self.name])
    subprocess.call(["vvp", "%s_tb"%self.name])

    response = {}
    for i in self.outputs:
        f = open("stim/"+i.name)
        response[i.name] = []
        for j in f:
            try:
                j = int(j)
            except ValueError:
                j = None
            response[i.name].append(j)
        f.close()
    os.chdir(current_dir)

    return response


def check_binary(func_to_test, a_stim, b_stim, signed=False):
    
    #make a design
    if signed:
        clk = Clock("clk")
        a = Signed(4).input("a")
        b = Signed(4).input("b")
        result = Signed(4).register(clk, d=func_to_test(a, b))
        z = Signed(4).output("z", result)
        n = Netlist("uut", [clk], [a, b], [z])
    else:
        clk = Clock("clk")
        a = Unsigned(4).input("a")
        b = Unsigned(4).input("b")
        result = Unsigned(4).register(clk, d=func_to_test(a, b))
        z = Unsigned(4).output("z", result)
        n = Netlist("uut", [clk], [a, b], [z])

    #run native sim
    expected = []
    for i, j in zip(a_stim, b_stim):
        expected.append(z.get())
        clk.tick()
        a.set(i)
        b.set(j)
    expected.append(z.get())
    clk.tick()
    expected.append(z.get())

    #run a verilog sim
    actual = test(n, {"a":a_stim, "b":b_stim}, 1)["z"]

    if signed:
        actual = [None if i is None else sign(i, 4) for i in actual]

    if actual == expected:
        print("pass")
    else:
        print(("a", a_stim))
        print(("b", b_stim))
        print(("failed", actual, expected))

check_binary(lambda x, y:x+y, list(range(16)), list(range(16)))
check_binary(lambda x, y:x-y, list(range(16)), list(range(16)))
check_binary(lambda x, y:x*y, list(range(16)), list(range(16)))
check_binary(lambda x, y:x|y, list(range(16)), list(range(16)))
check_binary(lambda x, y:x&y, list(range(16)), list(range(16)))
check_binary(lambda x, y:x^y, list(range(16)), list(range(16)))
check_binary(lambda x, y:x<<y, list(range(16)), list(range(3))+list(range(3))+list(range(3))+list(range(3))+list(range(4)))
check_binary(lambda x, y:x>>y, list(range(16)), list(range(3))+list(range(3))+list(range(3))+list(range(3))+list(range(4)))
check_binary(lambda x, y:x==y, list(range(16)), list(range(16)))
check_binary(lambda x, y:x!=y, list(range(16)), list(range(16)))
check_binary(lambda x, y:x>y, list(range(16)), list(range(16)))
check_binary(lambda x, y:x<y, list(range(16)), list(range(16)))
check_binary(lambda x, y:x>=y, list(range(16)), list(range(16)))
check_binary(lambda x, y:x<=y, list(range(16)), list(range(16)))
check_binary(lambda x, y:~x, list(range(16)), list(range(16)))
check_binary(lambda x, y:-x, list(range(16)), list(range(16)))
for i in range(4):
    check_binary(lambda x, y:x[i], list(range(16)), list(range(16)))
for i in range(4):
    for j in range(i):
        check_binary(lambda x, y:x[i:j], list(range(16)), list(range(16)))
check_binary(lambda x, y:cat(x, y), list(range(16)), list(range(16)))
check_binary(lambda x, y:x.subtype.rom(x, 15, 14, 13, 12, 10), list(range(16)), list(range(16)))

check_binary(lambda x, y:x+y, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:x-y, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:x*y, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:x|y, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:x&y, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:x^y, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:x<<y, list(range(16)), list(range(3))+list(range(3))+list(range(3))+list(range(3))+list(range(4)), True)
check_binary(lambda x, y:x>>y, list(range(16)), list(range(3))+list(range(3))+list(range(3))+list(range(3))+list(range(4)), True)
check_binary(lambda x, y:x==y, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:x!=y, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:x>y, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:x<y, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:x>=y, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:x<=y, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:~x, list(range(16)), list(range(16)), True)
check_binary(lambda x, y:-x, list(range(16)), list(range(16)), True)
for i in range(4):
    check_binary(lambda x, y:x[i], list(range(16)), list(range(16)), True)
for i in range(4):
    for j in range(i):
        check_binary(lambda x, y:x[i:j], list(range(16)), list(range(16)), True)
check_binary(lambda x, y:cat(x, y), list(range(16)), list(range(16)), True)
check_binary(lambda x, y:x.subtype.rom(x, 15, 14, 13, 12, 10), list(range(16)), list(range(16)), True)
