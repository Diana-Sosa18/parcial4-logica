"""Núcleo de una cinta, sin historial ni memoria auxiliar de cálculo."""
from validador_mt import validar_especificacion


class MaquinaTuring:
    def __init__(self, datos, transiciones):
        validar_especificacion(datos, transiciones)
        self.blanco = datos['blanco'][0]
        self.aceptacion = datos['estado_aceptacion'][0]
        self.rechazo = datos['estado_rechazo'][0]
        self.delta = {(q, a): (p, b, m) for q, a, p, b, m in transiciones}
        self.estado = datos['estado_inicial'][0]
        self.cinta = list(''.join(datos['cadena'])) or [self.blanco]
        self.cabezal = 0
        self.pasos = 0

    def detenida(self):
        return self.estado in (self.aceptacion, self.rechazo)

    @property
    def resultado(self):
        if self.estado == self.aceptacion:
            return 'aceptacion'
        if self.estado == self.rechazo:
            return 'rechazo'
        return 'en_curso'

    def siguiente_transicion(self):
        if self.detenida():
            return None
        a = self.cinta[self.cabezal]
        p, b, m = self.delta[self.estado, a]
        return self.estado, a, p, b, m

    def paso(self):
        if self.detenida():
            return False
        _, _, p, b, m = self.siguiente_transicion()
        self.cinta[self.cabezal] = b
        self.estado = p
        if m == 'R':
            self.cabezal += 1
            if self.cabezal == len(self.cinta):
                self.cinta.append(self.blanco)
        else:
            self.cabezal = max(0, self.cabezal - 1)
        self.pasos += 1
        return True

    def configuracion(self):
        return ''.join(self.cinta[:self.cabezal]), self.estado, ''.join(self.cinta[self.cabezal:])


if __name__ == '__main__':
    import argparse
    from validador_mt import cargar_especificacion
    from salida_mt import ejecutar
    p = argparse.ArgumentParser(description='Simulación por consola')
    p.add_argument('archivo', nargs='?', default='especificacion_aceptacion.txt')
    p.add_argument('--limite', type=int, default=1000)
    args = p.parse_args()
    try:
        d, t = cargar_especificacion(args.archivo)
        ejecutar(MaquinaTuring(d, t), args.limite)
    except (ValueError, OSError) as e:
        p.exit(1, f'Error: {e}\n')
