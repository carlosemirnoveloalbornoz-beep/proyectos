"""Generador propio de numeros pseudoaleatorios y sus estadisticas."""

import argparse
import matplotlib
matplotlib.use("Agg")  # evita fallos en terminal sin GUI
import matplotlib.pyplot as plt


class MersenneTwister:
    """Implementacion del algoritmo MT19937 sin usar la libreria random."""

    def __init__(self, seed: int):
        if not isinstance(seed, int):
            raise TypeError("La semilla debe ser un entero.")

        self.w = 32
        self.n = 624
        self.m = 397
        self.r = 31
        self.a = 0x9908B0DF
        self.u = 11
        self.d = 0xFFFFFFFF
        self.s = 7
        self.b = 0x9D2C5680
        self.t = 15
        self.c = 0xEFC60000
        self.l = 18
        self.f = 1812433253

        self.lower_mask = (1 << self.r) - 1
        self.upper_mask = (~self.lower_mask) & 0xFFFFFFFF

        self.mt = [0] * self.n
        self.index = self.n  # <- corregido

        self.mt[0] = seed & 0xFFFFFFFF
        for i in range(1, self.n):
            self.mt[i] = (
                self.f * (self.mt[i - 1] ^ (self.mt[i - 1] >> (self.w - 2))) + i
            ) & 0xFFFFFFFF

    def _twist(self) -> None:
        for i in range(self.n):
            x = (self.mt[i] & self.upper_mask) + (self.mt[(i + 1) % self.n] & self.lower_mask)
            xA = x >> 1
            if x & 1:
                xA ^= self.a
            self.mt[i] = self.mt[(i + self.m) % self.n] ^ xA
        self.index = 0

    def random(self) -> float:
        if self.index >= self.n:
            if self.index > self.n:
                raise ValueError("Semilla no inicializada")
            self._twist()

        y = self.mt[self.index]
        self.index += 1

        y ^= (y >> self.u) & self.d
        y ^= (y << self.s) & self.b
        y ^= (y << self.t) & self.c
        y ^= (y >> self.l)

        return (y & 0xFFFFFFFF) / 4294967296.0  # intervalo [0, 1)


def generar_numeros(cantidad: int, semilla: int) -> list[float]:
    """Genera ``cantidad`` valores en el intervalo [0, 1)."""
    if cantidad < 1:
        raise ValueError("N debe ser un entero positivo.")

    mt = MersenneTwister(semilla)
    return [mt.random() for _ in range(cantidad)]


def mostrar_resultados(numeros: list[float]) -> None:
    """Muestra los valores generados y sus estadisticas."""
    print("Numeros generados:")
    print(", ".join(f"{numero:.6f}" for numero in numeros))
    print(f"Valor minimo: {min(numeros):.6f}")
    print(f"Valor maximo: {max(numeros):.6f}")
    print(f"Promedio: {sum(numeros) / len(numeros):.6f}")


def graficar_histograma(numeros: list[float]) -> None:
    """Genera un histograma de los numeros pseudoaleatorios."""
    plt.hist(numeros, bins=10, edgecolor="black")
    plt.title("Histograma de numeros pseudoaleatorios")
    plt.xlabel("Valor")
    plt.ylabel("Frecuencia")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig("histograma.png", dpi=150)
    plt.close()


def leer_argumentos() -> tuple[int, int]:
    """Obtiene N y S desde argumentos o mediante entrada interactiva."""
    parser = argparse.ArgumentParser(
        description="Genera numeros pseudoaleatorios con Mersenne Twister."
    )
    parser.add_argument("n", type=int, nargs="?", help="cantidad de valores")
    parser.add_argument("s", type=int, nargs="?", help="semilla")
    argumentos = parser.parse_args()

    if argumentos.n is not None and argumentos.s is not None:
        return argumentos.n, argumentos.s

    if argumentos.n is not None or argumentos.s is not None:
        parser.error("Debe indicar N y S juntos.")

    return int(input("Cantidad de valores (N): ")), int(input("Semilla (S): "))


def main() -> None:
    cantidad, semilla = leer_argumentos()
    numeros = generar_numeros(cantidad, semilla)
    mostrar_resultados(numeros)
    graficar_histograma(numeros)


if __name__ == "__main__":
    main()
