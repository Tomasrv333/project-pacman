"""
random_generators.py — RandomPac (v1.0)
=======================================
Implementa tres métodos de generación pseudoaleatoria usados en clase y un método original del grupo.

1️⃣ Método del Cuadrado Medio (Von Neumann, 1946)
    X_{n+1} = dígitos centrales de (X_n)^2
    - Tiende a ciclos cortos pero es clásico e histórico.

2️⃣ Método Congruencial Lineal (Lehmer, 1949)
    X_{n+1} = (a*X_n + c) mod m
    - Controla ciclo y repetición con parámetros adecuados.
    
3️⃣ Método del Promedio Aritmético Múltiple (Original del grupo)
    X_{n+1} = ((X_n + 2*X_{n-1} + 3*X_{n-2}) / 6) * 10000 mod m
    - Idea propia basada en promedios ponderados para romper la linealidad.

Cada clase tiene:
- .rand() → número entero pseudoaleatorio
- .random() → número normalizado [0,1)
- .info → (nombre, descripción breve)
"""

import time

# ------------------------------
# MÉTODO 1: CUADRADO MEDIO
# ------------------------------
class MiddleSquare:
    def __init__(self, seed=None):
        self.seed = int(seed or str(int(time.time()*1000))[-4:])
        self.state = self.seed
        self.info = (
            "Cuadrado Medio (Von Neumann, 1946)",
            "Usa los 4 dígitos centrales del cuadrado de la semilla."
        )

    def rand(self):
        s = str(self.state ** 2).zfill(8)
        mid = s[2:6]
        self.state = int(mid)
        return self.state

    def random(self):
        return self.rand() / 9999 if self.state else 0.0


# ------------------------------
# MÉTODO 2: CONGRUENCIAL LINEAL
# ------------------------------
class LCG:
    def __init__(self, seed=None, a=1103515245, c=12345, m=2**31):
        self.state = int(seed or time.time_ns()) % m
        self.a, self.c, self.m = a, c, m
        self.info = (
            "Congruencial Lineal (Lehmer, 1949)",
            "Genera secuencias reproducibles con parámetros (a, c, m)."
        )

    def rand(self):
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def random(self):
        return self.rand() / self.m


# ------------------------------
# MÉTODO 3: PROMEDIO ARITMÉTICO MÚLTIPLE (Original)
# ------------------------------
class PAM:
    def __init__(self, seed=None, m=10000):
        self.m = m
        base = int(seed or str(int(time.time()*1000))[-4:])
        self.history = [base, (base*7+3) % m, (base*13+5) % m]
        self.info = (
            "Promedio Aritmético Múltiple (Original)",
            "Combina las tres últimas semillas para mayor variabilidad."
        )

    def rand(self):
        x0, x1, x2 = self.history[-3:]
        nxt = int(((x2 + 2*x1 + 3*x0) / 6) * 10000) % self.m
        self.history.append(nxt)
        if len(self.history) > 10:
            self.history.pop(0)
        return nxt

    def random(self):
        return self.rand() / self.m
