"""Observador externo: prueba ciclos por igualdad exacta de configuraciones.

Usa el algoritmo de Brent: guarda una sola configuración de referencia, sin
historial de pasos. No interviene en la función de transición de la máquina.
"""


def configuracion_exacta(maquina):
    # Los blancos finales almacenados no cambian la cinta infinita representada.
    fin = len(maquina.cinta)
    while fin and maquina.cinta[fin - 1] == maquina.blanco:
        fin -= 1
    return maquina.estado, maquina.cabezal, tuple(maquina.cinta[:fin])


class DetectorCiclos:
    def __init__(self, maquina, movimientos=15):
        if movimientos < 1:
            raise ValueError('El umbral del ciclo debe ser positivo.')
        self.movimientos = movimientos
        self.referencia = configuracion_exacta(maquina)
        self.paso_referencia = maquina.pasos
        self.potencia = 1
        self.distancia = 0
        self.periodo = None
        self.inicio = None
        self.agotado = False

    def observar(self, maquina):
        """Llamar una vez después de cada transición real de la máquina."""
        if maquina.detenida():
            return False
        if self.periodo is None:
            actual = configuracion_exacta(maquina)
            self.distancia += 1
            if actual == self.referencia:
                self.periodo = self.distancia
                self.inicio = self.paso_referencia
            elif self.distancia == self.potencia:
                self.referencia = actual
                self.paso_referencia = maquina.pasos
                self.potencia *= 2
                self.distancia = 0
        # Una configuración repetida prueba que la continuación es periódica.
        # Contar movimientos desde la referencia que pertenece a ese ciclo.
        self.agotado = self.periodo is not None and maquina.pasos - self.inicio >= self.movimientos
        return self.agotado
