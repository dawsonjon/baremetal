from baremetal import *

clk = Clock("clk")

transition_table = {
        "a": ["b"],
        "b": ["c"],
        "c": ["d"],
        "d": ["e"],
        "e": ["a"],
}

state, _ = make_FSM(clk, transition_table, "a")



clk.initialise()
print((print_FSM(state)))
for i in range(100):
    clk.tick()
    print((print_FSM(state)))
