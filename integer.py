class Int:
    def __init__(self, value, bits=32, signed=True):
        self.bits = bits
        self.mask = (1<<self.bits)-1
        self.signed = signed
        if self.signed:
            sign = value & (1<<self.bits-1)
            val = value & (1<<self.bits-1)-1
            if sign:
                val *= -1
            self.__x = val
        else:
            self.__x = value & self.mask

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        if self.signed:
            sign = value & (1<<self.bits-1)
            val = value & (1<<self.bits-1)-1
            if sign:
                val *= -1
            self.__x = val
        else:
            self.__x = value & self.mask

    def __int__(self):
        return int(self.__x)
    def __str__(self):
        return str(self.__x)

    def __repr__(self):
        return f'Int({self.__x}, bits={self.bits}, signed={self.signed})'
    
    def __add__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        return Int(self.__x + other.x, self.bits, self.signed)
    def __iadd__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        self.__x += other.x
        return self

    def __sub__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        return Int(self.__x - other.x, self.bits, self.signed)
    def __isub__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        self.__x -= other.x
        return self

    def __mul__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        return Int(self.__x * other.x, self.bits, self.signed)
    def __imul__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        self.__x *= other.x
        return self


    def __floordiv__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        return Int(self.__x // other.x, self.bits, self.signed)
    def __ifloordiv__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        self.__x //= other.x
        return self


    def __truediv__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        return Int(self.__x // other.x, self.bits, self.signed)
    def __itruediv__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        self.__x //= other.x
        return self

    def __and__(self, other):
        assert self.bits == other.bits and self.signed == other.signed
        return Int(self.__x & other.x, self.bits, self.signed)

    def __eq__(self, other):
        return self.__x == other.x
    def __ne__(self, other):
        return self.__x != other.x
    def __lt__(self, other):
        return self.__x < other.x
    def __gt__(self, other):
        return self.__x > other.x
    def __le__(self, other):
        return self.__x <= other.x
    def __ge__(self, other):
        return self.__x >= other.x






