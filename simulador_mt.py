import sys

from lector_mt import leer_especificacion, ErrorFormato


class MaquinaTuring:
    """Maquina de Turing determinista. La cinta es la unica memoria que usa."""

    def __init__(self, datos, transiciones):
        self.blanco = datos["blanco"][0]
        self.aceptacion = datos["estado_aceptacion"][0]
        self.rechazo = datos["estado_rechazo"][0]
        self.delta = {(q, a): (p, b, m) for q, a, p, b, m in transiciones}

        self.estado = datos["estado_inicial"][0]
        self.cinta = list("".join(datos.get("cadena", []))) or [self.blanco]
        self.cabezal = 0

    def detenida(self):
        return self.estado in (self.aceptacion, self.rechazo)

    def paso(self):
        """Aplica d(q, a) = (p, b, M) una sola vez."""
        q, a = self.estado, self.cinta[self.cabezal]
        if (q, a) not in self.delta:
            raise ValueError(f"No hay transicion para ({q}, {a}).")
        p, b, m = self.delta[(q, a)]

        self.cinta[self.cabezal] = b
        self.estado = p
        if m == "R":
            self.cabezal += 1
            # Despues de lo escrito la cinta sigue en blanco
            if self.cabezal == len(self.cinta):
                self.cinta.append(self.blanco)
        elif self.cabezal > 0:
            # En la primera celda, moverse a la izquierda deja el cabezal en su lugar
            self.cabezal -= 1

    def configuracion(self):
        """Devuelve (u, q, v): la cinta antes del cabezal, el estado y la cinta desde el cabezal."""
        return ("".join(self.cinta[:self.cabezal]), self.estado,
                "".join(self.cinta[self.cabezal:]))


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "especificacion_aceptacion.txt"
    limite = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    try:
        datos, transiciones = leer_especificacion(ruta)
    except ErrorFormato as e:
        print("ERROR DE FORMATO")
        print(e)
        sys.exit(1)

    m = MaquinaTuring(datos, transiciones)
    cadena = "".join(datos.get("cadena", []))

    def imprimir_configuracion():
        u, q, v = m.configuracion()
        if m.detenida() and v == m.blanco:
            v = ""
        partes = [u.replace(m.blanco, "⊔"), q, v.replace(m.blanco, "⊔")]
        print(" ".join(x for x in partes if x))

    print("Especificacion:", ruta)
    print("Cadena de entrada: w =", cadena if cadena else "ε")
    print()
    imprimir_configuracion()

    pasos = 0
    while not m.detenida() and pasos < limite:
        try:
            m.paso()
        except ValueError as e:
            print(e)
            sys.exit(1)
        pasos += 1
        imprimir_configuracion()

    print()
    if m.estado == m.aceptacion:
        print(f"Resultado: M acepta w. Se llego a la configuracion de aceptacion en {pasos} pasos.")
    elif m.estado == m.rechazo:
        print(f"Resultado: M rechaza w. Se llego a la configuracion de rechazo en {pasos} pasos.")
    else:
        print(f"Resultado: M no se detuvo en {pasos} pasos, no llego a {m.aceptacion} ni a {m.rechazo}. "
              "Se toma como ciclo infinito.")
