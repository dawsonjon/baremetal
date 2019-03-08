class SFixed:


class Expression:
    def __add__(self, other):

        #overall, the total number of bits is maintained.
        #but first calculate using total number of bits, then round
        bit = max(self.bits, other.bits)
        fraction_bits = max(self.fraction_bits, other.fraction_bits)
        self_signed = self.signed
        other_signed = other.signed

        #align to give same number of fraction bits - possibly adding more bits for now.
        if self.fraction_bits > other.fraction_bits:
            other_signed.concat(Signed(self.fraction_bits - other.fraction_bits).constant(0)))
        elif other.fraction_bits > self.fraction_bits:
            self_signed.concat(Signed(other.fraction_bits - self.fraction_bits).constant(0)))

        #do the actual calculation
        signed = self_signed + other_signed

        #if we added more bits, round back to the original number of bits
        if signed.bits > bits:
            signed = round_right(signed, signed.bits - bits)
            fraction_bits -= (signed.bits - bits)

        #now take the underlying signed and turn it back into an SFixed
        subtype = SFixed(bits, fraction_bits)
        return Expression(subtype, signed)

    def __mul__(self, other):
        total_bits = self.bits + other.bits
        total_fraction_bits = self.fraction_bits + other.fraction_bits
        bits_to_retain = max(self.bits, other.bits)
        fraction_bits_to_retain = 
        self_signed = self.signed
        other_signed = other.signed

        #extend both numbers to the full length needed to store the full precision result
        self_signed = self_signed.resize(2**bits-1)
        other_signed = self_signed.resize(2**bits-1)

        #calculate the full precision result
        signed = self.signed * other.signed
        signed = round_right(bits - 1)

        subtype = SFixed(bits, fraction_bits)
        return Expression(subtype, signed)
