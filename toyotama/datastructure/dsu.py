class DSU:
    def __init__(self, n):
        self._n = n
        self.parent_or_size = [-1 for _ in range(n)]

    def leader(self, v):
        assert 0 <= v < self._n
        if self.parent_or_size[v] < 0:
            return v
        self.parent_or_size[v] = self.leader(self.parent_or_size[v])
        return self.parent_or_size[v]

    def merge(self, a, b):
        assert 0 <= a < self._n
        assert 0 <= b < self._n
        x, y = map(self.leader, (a, b))
        if x == y:
            return x
        if -self.parent_or_size[x] < -self.parent_or_size[y]:
            x, y = y, x
        self.parent_or_size[x] += self.parent_or_size[y]
        self.parent_or_size[y] = x

        return x

    def same(self, a, b):
        assert 0 <= a < self._n
        assert 0 <= b < self._n
        return self.leader(a) == self.leader(b)

    def size(self, a):
        assert 0 <= a < self._n
        return -self.parent_or_size[self.leader(a)]

    def groups(self) -> list[list[int]]:
        result = [[i for i in range(self._n) if self.leader(i) == leader] for leader in range(self._n)]
        result = filter(lambda g: g, result)
        return list(result)

    def dump(self, indent: int = 2) -> str:
        buf = f"DSU (n = {self._n})\n"
        buf += "[\n"
        for g in self.groups():
            buf += f"{' '*indent}{g},\n"
        buf += "]\n"

        return buf
