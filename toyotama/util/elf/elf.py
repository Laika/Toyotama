
class Struct:
    def __init__(self, name: str, field: dict):
        self.name = name
        self._field = field

    def __getattr__(self, name):
        if name in self._field.keys():
            return self._field[name]
        raise AttributeError

    def __str__(self):
        return "".join(f"{value.type}\t{key}" for key, value in self._field.items())


class Function:
    def __init__(self, name: str, address: int, size: int, elf=None):
        self.name = name
        self.address = address
        self.size = size
        self.elf = elf

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, address={self.address:#x}, size={self.size:#x}, elf={self.elf})"
