from baremetal import *

if __name__ == "__main__":

    clk = Clock("clk")
    s = Boolean().input("set")
    r = Boolean().input("reset")
    inputs = [s, r]

    transition_table = {
            "off": [(s, "on"), "off"],
            "on" : [(r, "off"), "on"],
    }

    state, _ = make_FSM(clk, transition_table, "off")


    stimulus = [
    [0, 0],
    [1, 0],
    [0, 0],
    [0, 1],
    [0, 0]
    ]


    clk.initialise()
    print state["off"].get(), state["on"].get()
    for stim in stimulus:
        [i.set(v) for i, v in zip(inputs, stim)]
        clk.tick()
        print stim[0], stim[1], print_FSM(state)
