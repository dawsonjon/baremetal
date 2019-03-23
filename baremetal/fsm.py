from .unsigned import Boolean

def make_FSM(clk, transition_table, default):
    registers = {}
    for state, _ in transition_table.items():
        registers[state] = Boolean().register(clk, init=int(state==default))

    decodes = {}
    decodes_string = {}
    for state, transitions in transition_table.items():

        precondition = registers[state]
        for condition, next_state in transitions[:-1]:
            if next_state in decodes:
                decodes[next_state] |= precondition & condition
            else:
                decodes[next_state]  = precondition & condition
            precondition &= ~condition

        default_transition = transitions[-1]
        if default_transition in decodes:
            decodes[default_transition] |= precondition
        else:
            decodes[default_transition] = precondition

    for state, logic in decodes.items():
        registers[state].d(logic)

    return registers, decodes

def print_FSM(states):
    for s, r in states.items():
        if r.get():
            return s
