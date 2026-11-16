import argparse

from lector_mt import leer_especificacion
from simulador_mt import MaquinaTuring


def escribir_configuracion(maquina, archivo):
    # Consultar cómo está la máquina en este momento.
    izquierda, estado, derecha = maquina.configuracion()

    # Mostrar el blanco con el símbolo utilizado en la notación.
    izquierda = izquierda.replace(maquina.blanco, "⊔")
    derecha = derecha.replace(maquina.blanco, "⊔")

    # Escribir directamente al archivo, sin guardar un historial.
    if izquierda:
        archivo.write(izquierda + " ")

    archivo.write(estado + " " + derecha + "\n")


def generar_salida(maquina, ruta_salida, limite_pasos=50):
    if limite_pasos < 0:
        raise ValueError("El límite de pasos no puede ser negativo.")

    pasos = 0

    with open(
        ruta_salida,
        "w",
        encoding="utf-8",
        buffering=1
    ) as archivo:

        # Guardar la configuración inicial, antes de mover la máquina.
        escribir_configuracion(maquina, archivo)

        # Avanzar mientras no termine y queden pasos disponibles.
        while not maquina.detenida() and pasos < limite_pasos:
            maquina.paso()
            pasos += 1
            escribir_configuracion(maquina, archivo)

        # Explicar por qué terminó esta ejecución.
        if maquina.estado == maquina.aceptacion:
            resultado = "aceptacion"
            mensaje = f"La máquina acepta la cadena en {pasos} pasos."

        elif maquina.estado == maquina.rechazo:
            resultado = "rechazo"
            mensaje = f"La máquina rechaza la cadena en {pasos} pasos."

        else:
            resultado = "limite"
            mensaje = (
                f"Se alcanzó el límite de {pasos} pasos. "
                "La máquina no ha aceptado ni rechazado. "
                "Puede existir un ciclo infinito, "
                "pero el límite no lo demuestra."
            )

        archivo.write("\nResultado: " + mensaje + "\n")

    return resultado, pasos


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("entrada")
    parser.add_argument("salida")
    parser.add_argument("--limite", type=int, default=50)

    argumentos = parser.parse_args()

    datos, transiciones = leer_especificacion(argumentos.entrada)

    maquina = MaquinaTuring(datos, transiciones)

    resultado, pasos = generar_salida(
        maquina,
        argumentos.salida,
        argumentos.limite
    )

    print("Archivo generado:", argumentos.salida)
    print("Resultado:", resultado)
    print("Pasos ejecutados:", pasos)