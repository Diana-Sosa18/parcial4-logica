"""Punto de entrada de la aplicación integrada."""
import argparse
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description='Máquina de Turing integrada con visualizador Pygame')
    p.add_argument('archivo', nargs='?', default=str(Path(__file__).parent / 'especificacion_aceptacion.txt'))
    p.add_argument('--consola', action='store_true', help='Ejecutar sin ventana ni Pygame')
    p.add_argument('--salida', help='Archivo para exportar la ejecución por consola')
    p.add_argument('--limite', type=int, default=10000)
    a = p.parse_args()
    if a.limite < 1:
        p.error('--limite debe ser positivo')
    if not a.consola and a.limite > 100000:
        p.error('El límite de la interfaz no puede superar 100000')
    try:
        if a.consola:
            from validador_mt import cargar_especificacion
            from simulador_mt import MaquinaTuring
            from salida_mt import ejecutar, generar_salida
            d,t=cargar_especificacion(a.archivo)
            m=MaquinaTuring(d,t)
            if a.salida:
                resultado,pasos=generar_salida(m,a.salida,a.limite,movimientos_ciclo=15)
                print(f'Archivo: {a.salida}\nResultado: {resultado}\nPasos: {pasos}')
            else:
                ejecutar(m,a.limite,movimientos_ciclo=15)
        else:
            try:
                from visualizador import Visualizador
            except ModuleNotFoundError as e:
                if e.name!='pygame':raise
                p.exit(1,'Falta Pygame. Instálalo con: python -m pip install -r requirements.txt\n')
            app=Visualizador(a.archivo)
            app.limite.texto=str(a.limite)
            app.ejecutar()
    except (ValueError,OSError) as e:
        p.exit(1,f'Error: {e}\n')


if __name__=='__main__':
    main()
