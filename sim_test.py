from baremetal import *

#+
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) + Unsigned(2).constant(j)).get() == (i + j) & 0x3

#-
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) - Unsigned(2).constant(j)).get() == (i - j) & 0x3
#>
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) > Unsigned(2).constant(j)).get() == int((i & 0x3) > (j & 0x3))

#<
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) < Unsigned(2).constant(j)).get() == int((i & 0x3) < (j & 0x3))

#<=
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) <= Unsigned(2).constant(j)).get() == int((i & 0x3) <= (j & 0x3))

#>
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) > Unsigned(2).constant(j)).get() == int((i & 0x3) > (j & 0x3))

#>=
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) >= Unsigned(2).constant(j)).get() == int((i & 0x3) >= (j & 0x3))

#==
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) == Unsigned(2).constant(j)).get() == int((i & 0x3) == (j & 0x3))

#!=
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) != Unsigned(2).constant(j)).get() == int((i & 0x3) != (j & 0x3))

#|
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) | Unsigned(2).constant(j)).get() == int((i & 0x3) | (j & 0x3))

#^
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) ^ Unsigned(2).constant(j)).get() == int((i & 0x3) ^ (j & 0x3))

#&
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) & Unsigned(2).constant(j)).get() == int((i & 0x3) & (j & 0x3))

#<<
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) << Unsigned(2).constant(j)).get() == ((i & 0x3) << (j & 0x3)) & 0x3

#>>
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) >> Unsigned(2).constant(j)).get() == ((i & 0x3) >> (j & 0x3)) & 0x3

#*
for i in range(8):
    for j in range(8):
        assert (Unsigned(2).constant(i) * Unsigned(2).constant(j)).get() == ((i & 0x3) * (j & 0x3)) & 0x3

#-
for j in range(8):
    assert (-Unsigned(2).constant(i)).get() == (-i & 0x3)

#~
for j in range(8):
    assert (~Unsigned(2).constant(i)).get() == (~i & 0x3)

#select
for i in range(8):
    assert Unsigned(2).select(Unsigned(2).constant(i), 5, 6, 7, default=8).get() == (i&0x3)+5

for i in range(8):
    assert Unsigned(2).select(Unsigned(2).constant(i), 5, 6, 7, 8).get() == (i&0x3)+5

for i in range(8):
    assert Unsigned(2).select(Unsigned(2).constant(i), 5, 6, 7).get() == [5, 6, 7, 0][(i&0x3)]
    
#index
for i in range(8):
    for j in range(3):
        assert Unsigned(3).constant(i)[j].get() == int((i & (1<<j))!=0)

#slice
for i in range(8):
    for j in range(3):
        for k in range(j+1):
            assert Unsigned(3).constant(i)[j:k].get() == (i & (0xf >> 3-j)) >> k
