class Int:
    def __init__(self, value, bits=32, signed=True):
        self.bits = bits
        self.mask = (1 << self.bits) - 1
        self.signed = signed
        self.__x = value & self.mask

    @property
    def x(self):
        if self.signed:
            sign = self.__x & 1 << self.bits - 1
            value = self.__x & self.mask >> 1
            if sign:
                return -((~self.__x + 1) & self.mask)
            return value & self.mask

        return self.__x & self.mask

    @x.setter
    def x(self, value):
        self.__x = value & self.mask

    def __int__(self):
        return int(self.x)

    def __str__(self):
        return str(self.x)

    def __repr__(self):
        return f"Int({self.x}, bits={self.bits}, signed={self.signed})"

    def __add__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        return Int(self.x + other.x, self.bits, self.signed)

    def __iadd__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        self.x += other.x
        return self

    def __sub__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        return Int(self.x - other.x, self.bits, self.signed)

    def __isub__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        self.x -= other.x
        return self

    def __mul__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        return Int(self.x * other.x, self.bits, self.signed)

    def __imul__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        self.x *= other.x
        return self

    def __floordiv__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        return Int(self.x // other.x, self.bits, self.signed)

    def __ifloordiv__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        self.x //= other.x
        return self

    def __truediv__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        return Int(self.x // other.x, self.bits, self.signed)

    def __itruediv__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        self.x //= other.x
        return self

    def __and__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        return Int(self.x & other.x, self.bits, self.signed)

    def __eq__(self, other):
        if not isinstance(other, Int):
            return NotImplemented
        return self.x == other.x

    def __lt__(self, other):
        if not isinstance(other, Int):
            return NotImplemented
        return self.x < other.x

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        return not __self.__le__(other)

    def __ge__(self, other):
        return not __lt__(other)


class UInt8(Int):
    def __init__(self, value):
        super().__init__(self, value, bits=8, signed=False)


class UChar(Int):
    def __init__(self, value):
        super().__init__(self, value, bits=8, signed=False)


class UInt16(Int):
    def __init__(self, value):
        super().__init__(self, value, bits=16, signed=False)


class UInt32(Int):
    def __init__(self, value):
        super().__init__(self, value, bits=32, signed=False)


class UInt64(Int):
    def __init__(self, value):
        super().__init__(self, value, bits=64, signed=False)


class Int8(Int):
    def __init__(self, value):
        super().__init__(self, value, bits=8, signed=True)


class Int16(Int):
    def __init__(self, value):
        super().__init__(self, value, bits=16, signed=True)


class Int32(Int):
    def __init__(self, value):
        super().__init__(self, value, bits=32, signed=True)


class Int64(Int):
    def __init__(self, value):
        super().__init__(self, value, bits=64, signed=True)
