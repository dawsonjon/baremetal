next_bit = Boolean().Wire()
ready = Boolean().Wire()
baud_tick = Boolean().Wire()
last_bit = Boolean().Wire()

go = ready & valid

make_FSM(clk,{
    "idle":((go, "wait"), "idle"),
    "wait":((baud_tick, "tx"), "wait"),
    "tx":((baud_tick & last_bit, "idle"), "tx"),
}, default="idle")

baud_count = Unsigned(???).register(clk, init=0)
baud_count.d(Unsigned(???).select(baud_tick, baud_count-1, max_baud_count)

bit_count = Unsigned(4).register(clk, en=next_bit, init=0)
bit_count.d(bit_count.subtype.select(last_bit, bit_count+1, 0))
tx_data = tx_data_type.register(clk, en=go, d=stop.cat(data_in).cat(start))
tx_data = [tx_data[i] for i in range(10)]
tx = Boolean().select(bit_count, *tx_data)

next_bit.drive(state["tx"] & baud_tick)
ready.drive(state["idle"])
baud_tick.drive(baud_count==0)
last_bit.drive(bit_count==9)
