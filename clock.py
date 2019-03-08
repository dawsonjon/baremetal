from baremetal import *

def ifelse(x, true, false):
    subtype = false.subtype
    print x
    return subtype.select(x, false, default=true)


def rtc(clk):
    seconds = Unsigned(6).register(clk, init=0)
    last_second = seconds == 59
    seconds.d(ifelse(last_second, 0, seconds + 1))

    minutes = Unsigned(6).register(clk, init=0, en=last_second)
    last_minute = last_second & (minutes == 59)
    minutes.d(ifelse(last_minute, 0, minutes + 1))

    hours = Unsigned(5).register(clk, init=0, en=last_minute)
    last_hour = last_minute & (hours == 23)
    hours.d(ifelse(last_hour, 0, hours + 1))

    return hours, minutes, seconds


clk = Clock("clk")

hours, minutes, seconds = rtc(clk)

clk.initialise()
for i in range(10000):
    print hours.get(), minutes.get(), seconds.get()
    clk.tick()



