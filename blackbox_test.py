from baremetal import *

def mul(a, b):
    z = a*b

    return blackbox(
        inputs = [a, b], 
        outputs=[z], 
        template="  assign {z} = {a} * {b};\n", 
        mapping = { "a":a, "b":b, "z":z })[0]

a = Input("a", 10)
b = Input("b", 10)
z = mul(a, b)
z = Output("z", z)

n = Netlist(name="test", clocks=[], inputs=[a, b], outputs=[z])
print n.generate()


a.set(10)
b.set(10)
print z.get()

