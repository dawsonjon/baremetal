from baremetal import *

def rtc(clk):
    seconds, last_second = counter(clk, 0, 59, 1)
    minutes, last_minute = counter(clk, 0, 59, 1, last_second)
    hours, _             = counter(clk, 0, 23, 1, last_minute)
    return hours, minutes, seconds


clk = Clock("clk")

hours, minutes, seconds = rtc(clk)

clk.initialise()
for i in range(100):
    print(hours.get(), minutes.get(), seconds.get())
    clk.tick()



