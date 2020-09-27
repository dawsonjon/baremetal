"""A simple mini alnguage to write Synchronouse processes using baremetal """

from baremetal import *

class Process:
    def __init__(self, *statements):
        for statement in statements:
            statement.walk(Boolean().constant(1))

class Set:
    def __init__(self, reg, nextval):
        self.reg = reg
        if hasattr(nextval, "get"):
            self.nextval = nextval
        else:
            self.nextval = reg.subtype.constant(nextval)

    def walk(self, enable):
        if hasattr(self.reg, "nextval"):
            self.reg.nextval = self.reg.subtype.select(enable, self.reg.nextval, self.nextval)
        else:
            self.reg.nextval = self.reg.subtype.select(enable, self.reg, self.nextval)
        self.reg.d(self.reg.nextval)

class If:
    def __init__(self, condition, *true_statements):
        self.condition = condition
        self.true_statements = true_statements
        self.false_statements = []

    def walk(self, enable):
        for statement in self.true_statements:
            statement.walk(enable & self.condition)
        for statement in self.false_statements:
            statement.walk(enable & ~self.condition)

    def Else(self, *false_statements):
        self.false_statements = false_statements
        return self

class Case:
    def __init__(self, case, *statements):
        self.statements = statements
        self.case = case

    def walk(self, enable, select):
        for statement in self.statements:
            match = (select==self.case)
            statement.walk(enable & match)
        return match

class Switch:
    def __init__(self, select, *cases):
        self.select = select
        self.cases = cases
        self.default_statements = []

    def walk(self, enable):
        match = Boolean().constant(0)
        for case in self.cases:
            match |= case.walk(enable, self.select)

        for statement in self.default_statements:
            statement.walk(enable & ~match)

    def Default(self, *default_statements):
        self.default_statements = default_statements
        return self

if __name__ == "__main__":
    clk = Clock("clk")
    seconds = Unsigned(8).register(clk, init=0)
    minutes = Unsigned(8).register(clk, init=0)
    Process(
        If(seconds == 9,
            Set(seconds, 0),
            Switch(minutes,
                Case(1, Set(minutes, 5)),
                Case(5, Set(minutes, 7)),
                Case(7, Set(minutes, 9)),
                Case(9, Set(minutes, 1)),
            ).Default(Set(minutes, 1))
        ).Else(
            Set(seconds, seconds+1)
        )
    )

    clk.initialise()

    for i in range(200):
        print(minutes.get(), seconds.get())
        clk.tick()
