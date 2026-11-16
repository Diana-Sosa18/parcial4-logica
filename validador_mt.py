"""Validación reutilizable por consola, interfaz y exportador."""
from lector_mt import leer_especificacion, ErrorFormato


class ErrorValidacion(ValueError):
    pass


def validar_especificacion(datos, transiciones):
    errores = []
    for clave in ('estados', 'alfabeto_entrada', 'alfabeto_cinta', 'blanco',
                  'estado_inicial', 'estado_aceptacion', 'estado_rechazo', 'cadena'):
        if clave not in datos or (clave not in ('cadena', 'alfabeto_entrada') and not datos[clave]):
            errores.append(f'Falta la sección {clave}.')
    if errores:
        raise ErrorValidacion('\n'.join(errores))
    for clave in ('blanco', 'estado_inicial', 'estado_aceptacion', 'estado_rechazo'):
        if len(datos[clave]) != 1:
            errores.append(f'{clave} debe contener exactamente un valor.')
    if errores:
        raise ErrorValidacion('\n'.join(errores))
    Q, S, G = (set(datos[k]) for k in ('estados', 'alfabeto_entrada', 'alfabeto_cinta'))
    blanco = datos['blanco'][0]
    q0, qa, qr = (datos[k][0] for k in ('estado_inicial', 'estado_aceptacion', 'estado_rechazo'))
    for clave in ('estados', 'alfabeto_entrada', 'alfabeto_cinta'):
        if len(datos[clave]) != len(set(datos[clave])):
            errores.append(f'Hay elementos repetidos en {clave}.')
    if not {q0, qa, qr} <= Q:
        errores.append('Los estados inicial, de aceptación y de rechazo deben pertenecer a Q.')
    if qa == qr:
        errores.append('Aceptación y rechazo deben ser distintos.')
    if not S <= G or blanco not in G or blanco in S:
        errores.append('Se requiere Σ ⊆ Γ, blanco ∈ Γ y blanco ∉ Σ.')
    if any(len(a) != 1 for a in G | S):
        errores.append('Cada símbolo debe tener un solo carácter.')
    if ':' in G:
        errores.append('El símbolo : está reservado para las secciones.')
    vistas = set()
    for t in transiciones:
        if len(t) != 5:
            errores.append(f'Transición mal escrita: {" ".join(t)}'); continue
        q, a, p, b, m = t
        if q not in Q or p not in Q or a not in G or b not in G or m not in ('L', 'R'):
            errores.append(f'Transición inválida: {" ".join(t)}')
        if q in (qa, qr):
            errores.append(f'Un estado final no puede tener salidas: {q}.')
        if (q, a) in vistas:
            errores.append(f'Transición repetida para ({q}, {a}).')
        vistas.add((q, a))
    for q in datos['estados']:
        if q not in (qa, qr):
            for a in datos['alfabeto_cinta']:
                if (q, a) not in vistas:
                    errores.append(f'Falta la transición para ({q}, {a}).')
    for s in ''.join(datos['cadena']):
        if s not in S:
            errores.append(f'El símbolo {s!r} de la entrada no pertenece a Σ.')
    if errores:
        raise ErrorValidacion('\n'.join(errores))
    return True


def cargar_especificacion(ruta):
    datos, transiciones = leer_especificacion(ruta)
    validar_especificacion(datos, transiciones)
    return datos, transiciones


if __name__ == '__main__':
    import sys
    try:
        cargar_especificacion(sys.argv[1] if len(sys.argv) > 1 else 'especificacion_aceptacion.txt')
        print('ESPECIFICACIÓN VÁLIDA')
    except (ErrorFormato, ErrorValidacion) as e:
        print('ESPECIFICACIÓN INVÁLIDA\n' + str(e)); sys.exit(1)
