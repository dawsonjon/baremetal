#pipeline controls
bus_rd = Boolean().register(clk, init=0)
bus_wr = Boolean().register(clk, init=0)
jump   = Boolean().register(clk, init=1)
bus_en = bus_rd | bus_wr
en0    = ~bus_en
en1    = ~jump & ~bus_en
en2    = ~jump & ~bus_en & Boolean().register(clk, d=en1, init=0)

#pipeline 0
jump_vector = t.register(clk, init=0)
pc = t.register(clk, en=en0, init=0)
pc.d(t.select(jump, pc + 4, jump_vector))
instruction = t.register(clk, en=en0, d=ROM(pc, *instructions))

#pipeline 1
wren = Boolean().register(clk, init=0)
result = t.register(clk)
destination = Unsigned(5).register(clk)
register = t.register(clk, en=wren, d=result)
src2 = instruction[24:20]
src1 = instruction[19:15]
rs1=registers(src1)
rs2=registers(src2)

#pipeline 2
bus_rd.d((bus_rd & ~bus_ack) | (en2 & load))
bus_wr.d((bus_wr & ~bus_ack) | (en2 & store))

rs1=t.select(src1==dest, rs1, result)
rs2=t.select(src2==dest, rs2, result)


jump.d(en2 & (jal | jalr | branch & branch_taken))
jump_vector.d( next_address(.......) )

wren.d( (en2 & ~(load | store | branch)) | bus_rd )
result.d( execute(........) )
destination.d( result_location(......))

