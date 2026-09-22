import time

# ==============================================================================
# 1. IMPLEMENTACIÓN PROPIA DEL GENERADOR MERSENNE TWISTER (MT19937)
# ==============================================================================
class MersenneTwister:
    def __init__(self, seed=None):
        # Parámetros del estándar MT19937 (palabras de 32 bits)
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

        self.lower_mask = (1 << self.r) - 1        # 0x7FFFFFFF (31 bits de 1s)
        self.upper_mask = (~self.lower_mask) & 0xFFFFFFFF  # 0x80000000 (1 bit de 1)

        self.MT = [0] * self.n
        self.index = self.n + 1

        # Si no se proporciona semilla, usar el tiempo actual en milisegundos
        if seed is None:
            seed = int(time.time() * 1000)
            
        self.seed(seed)

    def seed(self, seed):
        """Inicializa el estado interno a partir de una semilla inicial."""
        self.index = self.n
        self.MT[0] = seed & 0xFFFFFFFF
        for i in range(1, self.n):
            self.MT[i] = (self.f * (self.MT[i-1] ^ (self.MT[i-1] >> (self.w - 2))) + i) & 0xFFFFFFFF

    def twist(self):
        """Aplica la transformación 'twist' para generar los siguientes 624 valores."""
        for i in range(self.n):
            x = (self.MT[i] & self.upper_mask) + (self.MT[(i + 1) % self.n] & self.lower_mask)
            xA = x >> 1
            if x % 2 != 0:
                xA = xA ^ self.a
            self.MT[i] = self.MT[(i + self.m) % self.n] ^ xA
        self.index = 0

    def extract_number(self):
        """Extrae un número entero de 32 bits pseudoaleatorio y aplica templado (tempering)."""
        if self.index >= self.n:
            self.twist()

        y = self.MT[self.index]
        y = y ^ ((y >> self.u) & self.d)
        y = y ^ ((y << self.s) & self.b)
        y = y ^ ((y << self.t) & self.c)
        y = y ^ (y >> self.l)

        self.index += 1
        return y & 0xFFFFFFFF

    def random_float(self):
        """Devuelve un número float uniforme en el intervalo [0.0, 1.0)."""
        return self.extract_number() / 4294967296.0  # 2^32

    def randint(self, min_val, max_val):
        """Devuelve un número entero uniforme en el rango cerrado [min_val, max_val]."""
        return min_val + int(self.random_float() * (max_val - min_val + 1))


# ==============================================================================
# 2. SIMULACIÓN DEL PARTIDO DE FÚTBOL
# ==============================================================================
def simular_partido(prob_eq1, prob_eq2, semilla=None):
    # Instanciamos nuestro generador propio Mersenne Twister
    mt = MersenneTwister(seed=semilla)
    
    # 1. Definir número de ocasiones para cada equipo (entre 2 y 8 ocasiones)
    ocasiones_eq1 = mt.randint(2, 8)
    ocasiones_eq2 = mt.randint(2, 8)
    
    # Lista para almacenar los eventos del partido: (minuto, equipo, num_ocasion, resultado)
    eventos = []
    
    goles_eq1 = 0
    goles_eq2 = 0

    # Generar jugadas del Equipo 1
    for i in range(ocasiones_eq1):
        minuto = mt.randint(1, 90) # Definir tiempo del partido usando MT
        r = mt.random_float()       # Número pseudoaleatorio para evaluar GOL/NO GOL
        es_gol = r < prob_eq1
        if es_gol:
            goles_eq1 += 1
            resultado = "GOL"
        else:
            resultado = "FALLÓ"
        eventos.append((minuto, "Equipo 1", i + 1, resultado))

    # Generar jugadas del Equipo 2
    for i in range(ocasiones_eq2):
        minuto = mt.randint(1, 90) # Definir tiempo del partido usando MT
        r = mt.random_float()       # Número pseudoaleatorio para evaluar GOL/NO GOL
        es_gol = r < prob_eq2
        if es_gol:
            goles_eq2 += 1
            resultado = "GOL"
        else:
            resultado = "FALLÓ"
        eventos.append((minuto, "Equipo 2", i + 1, resultado))

    # Ordenar la lista de eventos cronológicamente por minuto de juego
    eventos.sort(key=lambda x: x[0])

    # ==========================================================================
    # 3. REPORTE Y SALIDA DE RESULTADOS
    # ==========================================================================
    print("\n" + "=" * 60)
    print("        SIMULACIÓN DE PARTIDO DE FÚTBOL (MERSENNE TWISTER)")
    print("=" * 60)
    print(f"Probabilidad de anotar Equipo 1: {prob_eq1:.2f}")
    print(f"Probabilidad de anotar Equipo 2: {prob_eq2:.2f}")
    print("-" * 60)
    print("RESUMEN DE OCASIONES:")
    print(f" - Ocasiones totales Equipo 1: {ocasiones_eq1}")
    print(f" - Ocasiones totales Equipo 2: {ocasiones_eq2}")
    print("-" * 60)
    print("CRONOGRAMA DE OCASIONES DE GOL:")
    
    for minuto, equipo, num_ocasion, resultado in eventos:
        print(f" [Min {minuto:02d}'] {equipo} - Ocasión #{num_ocasion}: --> {resultado}")

    print("-" * 60)
    print("MARCADOR FINAL DEL PARTIDO:")
    print(f"  >>>  EQUIPO 1  {goles_eq1} - {goles_eq2}  EQUIPO 2  <<<")
    print("=" * 60 + "\n")


# ==============================================================================
# EJECUCIÓN PRINCIPAL CON BUCLE DE REPETICIÓN
# ==============================================================================
if __name__ == "__main__":
    while True:
        print("--- INGRESO DE DATOS PARA EL PARTIDO ---")
        try:
            p1 = float(input("Ingrese la probabilidad de anotar del Equipo 1 (0.0 a 1.0): "))
            p2 = float(input("Ingrese la probabilidad de anotar del Equipo 2 (0.0 a 1.0): "))
            
            # Validación de rango de probabilidad
            if not (0.0 <= p1 <= 1.0 and 0.0 <= p2 <= 1.0):
                print("⚠ Error: Las probabilidades deben ser valores entre 0.0 y 1.0. Intente de nuevo.\n")
                continue
                
        except ValueError:
            print("⚠ Error: Ingrese valores numéricos flotantes válidos (ej. 0.35).\n")
            continue

        # Ejecutar simulación
        simular_partido(prob_eq1=p1, prob_eq2=p2)
        
        # Preguntar si el usuario desea realizar otra simulación
        respuesta = input("¿Desea realizar otra simulación de partido? (s/n): ").strip().lower()
        if respuesta != 's':
            print("\n¡Simulaciones finalizadas exitosamente!")
            break
        print("\n" + "-" * 60 + "\n")