"""Simulacion de la propagacion de un virus en una poblacion."""

import argparse
from collections.abc import Iterator


class MersenneTwister:
    """Implementacion del algoritmo MT19937 sin usar la libreria random."""
    def __init__(self, seed: int):
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
        self.index = self.n + 1

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

        return y / 4294967296.0  # intervalo [0, 1)


def generador_aleatorio(semilla: int) -> Iterator[float]:
    """Genera valores pseudoaleatorios en el intervalo [0, 1) usando MT19937."""
    mt = MersenneTwister(semilla)
    while True:
        yield mt.random()


def simular_propagacion(
    habitantes: int,
    lugares_masivos: int,
    probabilidad_contagio: float,
    semilla: int = 1,
) -> int:
    """Devuelve los dias necesarios para infectar al menos al 80%."""
    if habitantes < 2:
        raise ValueError("El numero de habitantes debe ser al menos 2.")
    if lugares_masivos < 1 or lugares_masivos > habitantes:
        raise ValueError(
            "Los lugares con asistencia masiva deben estar entre 1 y los habitantes."
        )
    if not 0 <= probabilidad_contagio <= 1:
        raise ValueError("La probabilidad de contagio debe estar entre 0 y 1.")

    objetivo = (habitantes * 80 + 99) // 100
    infectados = {0}
    dias = 0
    aleatorio = generador_aleatorio(semilla)

    while len(infectados) < objetivo:
        dias += 1
        lugares_de_personas = [
            int(next(aleatorio) * lugares_masivos) for _ in range(habitantes)
        ]
        infectados_por_lugar: list[set[int]] = [set() for _ in range(lugares_masivos)]
        for persona in range(habitantes):
            lugar = lugares_de_personas[persona]
            if persona in infectados:
                infectados_por_lugar[lugar].add(persona)

        nuevos_contagios: set[int] = set()
        for persona in range(habitantes):
            if persona in infectados:
                continue
            lugar = lugares_de_personas[persona]
            if infectados_por_lugar[lugar] and next(aleatorio) < probabilidad_contagio:
                nuevos_contagios.add(persona)

        if not nuevos_contagios:
            return -1
        infectados.update(nuevos_contagios)

    return dias


def leer_argumentos() -> tuple[int, int, float, int]:
    """Obtiene los parametros desde argumentos o mediante entrada interactiva."""
    parser = argparse.ArgumentParser(
        description="Simula la propagacion de un virus en una poblacion."
    )
    parser.add_argument("habitantes", type=int, nargs="?")
    parser.add_argument("lugares", type=int, nargs="?")
    parser.add_argument("probabilidad", type=float, nargs="?")
    parser.add_argument("semilla", type=int, nargs="?", default=1)
    argumentos = parser.parse_args()

    valores = (argumentos.habitantes, argumentos.lugares, argumentos.probabilidad)
    if all(valor is not None for valor in valores):
        return argumentos.habitantes, argumentos.lugares, argumentos.probabilidad, argumentos.semilla
    if any(valor is not None for valor in valores):
        parser.error("Debe indicar habitantes, lugares y probabilidad juntos.")

    return (
        int(input("Numero de habitantes: ")),
        int(input("Numero de lugares con asistencia masiva: ")),
        float(input("Probabilidad de contagio (0 a 1): ")),
        int(input("Semilla (por defecto 1): ") or "1"),
    )


def main() -> None:
    habitantes, lugares, probabilidad, semilla = leer_argumentos()
    dias = simular_propagacion(habitantes, lugares, probabilidad, semilla)
    if dias == -1:
        print("El virus no alcanzo el 80% de la poblacion.")
    else:
        print(f"El virus tardo {dias} dias en infectar al 80% de la poblacion.")


if __name__ == "__main__":
    main()
