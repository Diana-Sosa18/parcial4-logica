import sys

SECCIONES = ["estados", "alfabeto_entrada", "alfabeto_cinta", "blanco",
             "estado_inicial", "estado_aceptacion", "estado_rechazo", "cadena"]
UN_VALOR = ["blanco", "estado_inicial", "estado_aceptacion", "estado_rechazo"]
ALFABETOS = ["alfabeto_entrada", "alfabeto_cinta", "blanco"]


class ErrorFormato(Exception):
    pass


def leer_especificacion(ruta):
    """Lee el archivo de la maquina y devuelve (datos, transiciones).

    datos: diccionario {seccion: lista de valores}.
    transiciones: lista de [q, a, p, b, M] que representa d(q, a) = (p, b, M).
    """
    try:
        with open(ruta, encoding="utf-8-sig") as archivo:
            lineas = archivo.readlines()
    except OSError as e:
        raise ErrorFormato(f"No se pudo abrir '{ruta}': {e.strerror}")

    datos = {}
    transiciones = []
    errores = []
    leyendo_transiciones = False

    for n, linea in enumerate(lineas, start=1):
        linea = linea.strip()
        if linea == "" or linea.startswith("#"):
            continue

        if ":" not in linea:
            if leyendo_transiciones:
                transiciones.append(linea.split())
            else:
                errores.append(f"Linea {n}: '{linea}' no pertenece a ninguna seccion.")
            continue

        nombre, valor = linea.split(":", 1)
        nombre = nombre.strip().lower()
        valores = valor.split()

        if nombre == "transiciones":
            leyendo_transiciones = True
            continue
        leyendo_transiciones = False

        if nombre not in SECCIONES:
            errores.append(f"Linea {n}: la seccion '{nombre}' no existe.")
            continue
        if nombre in datos:
            errores.append(f"Linea {n}: la seccion '{nombre}' esta repetida.")
            continue
        if nombre in UN_VALOR and len(valores) > 1:
            errores.append(f"Linea {n}: '{nombre}' solo puede tener un valor.")
        if nombre in ALFABETOS:
            for s in valores:
                if len(s) != 1:
                    errores.append(f"Linea {n}: el simbolo '{s}' debe ser de un solo caracter.")

        datos[nombre] = valores

    if errores:
        raise ErrorFormato("\n".join(errores))
    return datos, transiciones


def conjunto(valores, blanco=None):
    return "{" + ", ".join("⊔" if v == blanco else v for v in valores) + "}"


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "especificacion_aceptacion.txt"
    try:
        datos, transiciones = leer_especificacion(ruta)
    except ErrorFormato as e:
        print("ERROR DE FORMATO")
        print(e)
        sys.exit(1)

    blanco = datos.get("blanco", ["_"])[0]
    cadena = "".join(datos.get("cadena", []))

    print("M = (Q, Σ, Γ, δ, q0, qaccept, qreject)")
    print("Q =", conjunto(datos.get("estados", [])))
    print("Σ =", conjunto(datos.get("alfabeto_entrada", [])))
    print("Γ =", conjunto(datos.get("alfabeto_cinta", []), blanco))
    print("q0 =", " ".join(datos.get("estado_inicial", [])))
    print("qaccept =", " ".join(datos.get("estado_aceptacion", [])))
    print("qreject =", " ".join(datos.get("estado_rechazo", [])))
    print("δ:")
    for t in transiciones:
        if len(t) == 5:
            q, a, p, b, m = ["⊔" if x == blanco else x for x in t]
            print(f"  δ({q}, {a}) = ({p}, {b}, {m})")
        else:
            print("  (incompleta)", " ".join(t))
    print("w =", cadena if cadena else "ε")
