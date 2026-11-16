"""Salida de configuraciones en flujo; no acumula trazas en memoria."""
import sys


def escribir_configuracion(maquina, archivo):
    u, q, v = maquina.configuracion()
    u, v = (s.replace(maquina.blanco, '⊔') for s in (u, v))
    archivo.write(' '.join(s for s in (u, q, v) if s) + '\n')


def ejecutar(maquina, limite_pasos=1000, archivo=None, movimientos_ciclo=None):
    if limite_pasos < 0:
        raise ValueError('El límite no puede ser negativo.')
    archivo = archivo if archivo is not None else sys.stdout
    from detector_ciclos import DetectorCiclos
    detector = DetectorCiclos(maquina, movimientos_ciclo) if movimientos_ciclo is not None else None
    ciclo = False
    inicio = maquina.pasos
    escribir_configuracion(maquina, archivo)
    while not maquina.detenida() and maquina.pasos - inicio < limite_pasos:
        maquina.paso()
        escribir_configuracion(maquina, archivo)
        if detector and detector.observar(maquina):
            ciclo = True
            break
    resultado = maquina.resultado if maquina.detenida() else 'limite'
    if ciclo:
        resultado = 'ciclo'
        mensaje = f'Ciclo infinito confirmado (período {detector.periodo}). Detenida tras al menos {movimientos_ciclo} movimientos dentro del ciclo.'
    elif resultado == 'limite':
        mensaje = 'Límite alcanzado. No demuestra un ciclo infinito.'
    else:
        mensaje = 'La máquina acepta.' if resultado == 'aceptacion' else 'La máquina rechaza.'
    archivo.write(f'\nResultado: {mensaje} Pasos totales: {maquina.pasos}.\n')
    return resultado, maquina.pasos - inicio


def generar_salida(maquina, ruta_salida, limite_pasos=1000, movimientos_ciclo=None):
    with open(ruta_salida, 'w', encoding='utf-8', buffering=1) as archivo:
        return ejecutar(maquina, limite_pasos, archivo, movimientos_ciclo)


if __name__ == '__main__':
    import argparse
    from validador_mt import cargar_especificacion
    from simulador_mt import MaquinaTuring
    p = argparse.ArgumentParser()
    p.add_argument('entrada'); p.add_argument('salida')
    p.add_argument('--limite', type=int, default=1000)
    a = p.parse_args()
    try:
        d, t = cargar_especificacion(a.entrada)
        print(generar_salida(MaquinaTuring(d, t), a.salida, a.limite))
    except (ValueError, OSError) as e:
        p.exit(1, f'Error: {e}\n')
