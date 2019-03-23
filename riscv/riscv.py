from baremetal import *

#create memories
instruction_address = Unsigned(32).register(clk, init=0)
instructions = Unsigned(32).ram(1024, clk, False)
ram1 = Unsigned(32).ram(32, clk, False)
ram2 = Unsigned(32).ram(32, clk, False)

#stage 0 
phase = counter(clk, 0, 3, 1)
instruction = instructions.read(cat(phase, instruction_address))
pc = delay(clk, instruction_address)

#stage 1 
rega = ram1.read(get_srca(instruction))
regb = ram2.read(get_srcb(instruction))
expression = delay(clk, instruction)
pc = delay(clk, pc)

#stage 2 


#stage 3
pc, result, wen = execute(rega, regb, instruction, pc)
ram1.write(get_dest(instruction), result, wen)
ram2.write(get_dest(instruction), result, wen)
instruction_address.d(pc)



upper_immediate = upper_immediate.subtype.register(clk, d=upper_immediate, en=en)
dest            = dest.subtype.register(clk, d=dest, en=en)
offset          = offset.subtype.register(clk, d=offset, en=en)
pc              = pc.subtype.register(clk, d=pc, en=en)
funct3          = funct3.subtype.register(clk, d=funct3, en=en)
load            = Boolean().register(clk, d=opcode == 0b0000011, en=en)
op_imm          = Boolean().register(clk, d=opcode == 0b0010011, en=en)
aupci           = Boolean().register(clk, d=opcode == 0b0010111, en=en)
store           = Boolean().register(clk, d=opcode == 0b0100011, en=en)
op              = Boolean().register(clk, d=opcode == 0b0110011, en=en)
lui             = Boolean().register(clk, d=opcode == 0b0110111, en=en)
jal             = Boolean().register(clk, d=opcode == 0b1101111, en=en)
jalr            = Boolean().register(clk, d=opcode == 0b1100111, en=en)
branch          = Boolean().register(clk, d=opcode == 0b1100011, en=en)

#execute section 0
load_data = t.select(funct3, 
        to_signed(data_in[7:0]).resize(32),   #lb    0
        to_signed(data_in[15:0]).resize(32),  #lh    1
        data_in,                              #lw    2
        dont_care,                            #      3
        data_in[7:0].resize(32),              #lbu   4
        data_in[15:0].resize(32)))            #lhu   5

a = select(op | op_imm,         0, rs1) |
    select(load,                0, load_data) |
    select(jal | jalr | auipc,  0, pc)

b = select(op_imm,      0, get_immediate(instruction))|
    select(op,          0, rs2)|
    select(lui,         0, get_upper_immediate(instruction)|
    select(auipc,       0, get_upper_immediate(instruction)|
    select(jal | jalr,  0, 4) 

#execute section 1
alu = t.select(funct7,
    t.select(funct3,
        a + b,                         #add  0
        a << b[4:0],                   #sll  1
        to_signed(a) < b,              #slt  2
        a < b,                         #sltu 3
        a ^ b,                         #xor  4
        a >> b[4:0],                   #srl  5
        a | b,                         #or   6
        a & b),                        #and  7
    t.select(funct3,
        a - b,                         #sub  0
        dont_care,                     #     1
        dont_care,                     #     2
        dont_care,                     #     3
        dont_care,                     #     4
        to_signed(a) >> b[4:0]))       #sra  5


take_branch = Boolean().select(funct3, 
    rs1==rs2,                              #beq  0
    rs1!=rs2,                              #bne  1
    dont_care,                             #     2
    dont_care,                             #     3
    to_signed(rs1)<rs2,                    #blt  4  
    to_signed(rs1)>=rs2,                   #bge  5
    rs1<rs2,                               #bltu 6
    rs1>=rs2,                              #bgeu 7
) 

jump = (branch & take_branch) | jal | jalr
jump_address = select(jal,  0, to_signed(jal_offset(instruction))<<1) + pc|
               select(jalr, 0, (to_signed(immediate(instruction))+rs) & 0xfffffffe)|
               select(branch & take_branch, 0, branch_offset + pc)
pc   = select(jump, pc+4, jump_address)
wen  = ~branch | store   
