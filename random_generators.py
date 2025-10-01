
# Generadores de números pseudoaleatorios simples para experimentación

class LCG:
    """Linear Congruential Generator: X_{n+1} = (aX_n + c) mod m"""
    def __init__(self, seed=123456789, a=1103515245, c=12345, m=2**31):
        self.state = seed % m
        self.a, self.c, self.m = a, c, m
    def rand(self):
        self.state = (self.a * self.state + self.c) % self.m
        return self.state
    def random(self):
        return self.rand() / self.m  # [0,1)

class MiddleSquare:
    def __init__(self, seed=8421):
        self.state = int(str(seed).zfill(4)[-4:])  # 4 dígitos
    def rand(self):
        s = str(self.state ** 2).zfill(8)
        mid = s[2:6]
        self.state = int(mid)
        return self.state
    def random(self):
        return self.rand() / 9999 if 9999 else 0.0

class XorShift32:
    def __init__(self, seed=2463534242 & 0xFFFFFFFF):
        self.state = seed if seed != 0 else 2463534242
    def rand(self):
        x = self.state & 0xFFFFFFFF
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17) & 0xFFFFFFFF
        x ^= (x << 5)  & 0xFFFFFFFF
        self.state = x
        return x
    def random(self):
        return (self.rand() & 0xFFFFFFFF) / 0xFFFFFFFF

# Ayuda: convertir un float [0,1) en elección discreta { -1, 0, 1 } por ejemplo
def choice3(r):
    if r < 1/3: return -1
    if r < 2/3: return 0
    return 1
