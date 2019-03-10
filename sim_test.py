from baremetal import *
from baremetal.back_end import sign

#check propogation of None.
assert Signed(2).input("asdasd").get() is None
assert Unsigned(2).input("asdasd").get() is None
assert (Unsigned(2).input("asdasd") + 1).get() is None
assert (-Unsigned(2).input("asdasd")).get() is None
assert (Signed(2).input("asdasd") + 1).get() is None
assert (-Signed(2).input("asdasd")).get() is None
assert Signed(2).select(Signed(2).input("as"), 0, 0, 0, 0).get() is None
assert Unsigned(2).select(Unsigned(2).input("as"), 0, 0, 0, 0).get() is None
assert Signed(2).select(0, Signed(2).input("as"), 0, 0, 0).get() is None
assert Unsigned(2).select(0, Unsigned(2).input("as"), 0, 0, 0).get() is None
assert Signed(2).select(3, 0, 0, 0, default=Signed(2).input("as")).get() is None
assert Unsigned(2).select(3, 0, 0, 0, default=Unsigned(2).input("as")).get() is None
assert Signed(2).input("as")[0].get() is None
assert Unsigned(2).input("as")[0].get() is None
assert Signed(2).input("as")[1:0].get() is None
assert Unsigned(2).input("as")[1:0].get() is None
assert Signed(2).input("as").resize(3).get() is None
assert Unsigned(2).input("as").resize(3).get() is None
assert Signed(2).input("as").cat(2).get() is None
assert Unsigned(2).input("as").cat(2).get() is None

#+
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) + Signed(2).constant(j)).get() == sign((i + j) & 3, 2)

#-
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) - Signed(2).constant(j)).get() == sign((i - j) & 3, 2)
#>
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) > Signed(2).constant(j)).get() == int(sign(i&3, 2) > sign(j&3, 2))

#<
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) < Signed(2).constant(j)).get() == int(sign(i&3, 2) < sign(j&3, 2))

#<=
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) <= Signed(2).constant(j)).get() == int(sign(i&3, 2) <= sign(j&3, 2))

#>
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) > Signed(2).constant(j)).get() == int(sign(i&3, 2) > sign(j&3, 2))

#>=
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) >= Signed(2).constant(j)).get() == int(sign(i&3, 2) >= sign(j&3, 2))

#==
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) == Signed(2).constant(j)).get() == int(sign(i&3, 2) == sign(j&3, 2))

#!=
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) != Signed(2).constant(j)).get() == int(sign(i&3, 2) != sign(j&3, 2))

#|
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) | Signed(2).constant(j)).get() == sign((i | j) & 3, 2)

#^
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) ^ Signed(2).constant(j)).get() == sign((i ^ j) & 3, 2)

#&
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) & Signed(2).constant(j)).get() == sign((i & j) & 3, 2)

#<<
for i in range(-4, 4):
    for j in range(2):
        assert (Signed(2).constant(i) << Signed(2).constant(j)).get() == sign((i << j) & 3, 2)

#>>
for i in range(-4, 4):
    for j in range(2):
        assert (Signed(2).constant(i) >> Signed(2).constant(j)).get() == sign(i&3, 2) >> sign(j&3, 2)

#*
for i in range(-4, 4):
    for j in range(-4, 4):
        assert (Signed(2).constant(i) * Signed(2).constant(j)).get() == sign((i * j) & 3, 2)

#-
for j in range(-4, 4):
    assert (-Signed(2).constant(i)).get() == sign(-i & 3, 2)

#~
for j in range(-4, 4):
    assert (~Signed(2).constant(i)).get() == sign(~i & 3, 2)

#select
for i in range(8):
    assert Signed(2).select(Signed(2).constant(i), 5, 6, 7, default=8).get() == (i&0x3)+5

for i in range(8):
    assert Signed(2).select(Signed(2).constant(i), 5, 6, 7, 8).get() == (i&0x3)+5

for i in range(8):
    assert Signed(2).select(Signed(2).constant(i), 5, 6, 7).get() == [5, 6, 7, 0][(i&0x3)]
    
#index
for i in range(-4, 4):
    for j in range(3):
        assert Signed(3).constant(i)[j].get() == int((i & (1<<j))!=0)

#slice
for i in range(-4, 4):
    for j in range(3):
        for k in range(j+1):
            assert Signed(3).constant(i)[j:k].get() == (i & (0xf >> 3-j)) >> k

#resize
for i in range(-4, 4):
    assert Signed(3).constant(i).resize(2).get() == sign(i&3, 2)

#cat
for i in range(-4, 4):
    assert Signed(3).constant(i).cat(Signed(1).constant(0)).get() == sign(i*2&15, 4)

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

#resize
for i in range(-4, 4):
    assert Unsigned(3).constant(i).resize(2).get() == i&3

#cat
for i in range(-4, 4):
    assert Unsigned(3).constant(i).cat(Unsigned(1).constant(0)).get() == i*2&15

