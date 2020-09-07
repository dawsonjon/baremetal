from baremetal import *
from baremetal.back_end import blackbox

def mul(a, b):
    z = a*b

    return blackbox(
        inputs = [a.vector, b.vector], 
        outputs=[z.vector], 
        template="  assign {z} = {a} * {b};\n", 
        mapping = { "a":a.vector, "b":b.vector, "z":z.vector })[0]

a = Unsigned(10).input("a")
b = Unsigned(10).input("b")
z = mul(a, b)
z = Unsigned(10).output("z", z)

n = Netlist(name="test", clocks=[], inputs=[a, b], outputs=[z])
print((n.generate()))


a.set(10)
b.set(10)
print((z.get()))

