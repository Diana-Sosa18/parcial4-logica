import sys

ruta = sys.argv[1] if len(sys.argv) > 1 else "especificacion_m2.txt"

datos = {}
transiciones = []
with open(ruta, encoding="utf-8") as archivo:
    for linea in archivo:
        linea = linea.strip()
        if linea == "" or linea.startswith("#"):
            continue
        if ":" in linea:
            nombre, valor = linea.split(":", 1)
            datos[nombre.strip()] = valor.split()
        else:
            transiciones.append(linea.split())

for clave in ["estados", "alfabeto_entrada", "alfabeto_cinta", "blanco",
              "estado_inicial", "estado_aceptacion", "estado_rechazo"]:
    if not datos.get(clave):
        print("ESPECIFICACION INVALIDA\n- Falta la seccion", clave)
        sys.exit()

Q = set(datos["estados"])
S = set(datos["alfabeto_entrada"])
G = set(datos["alfabeto_cinta"])
blanco = datos["blanco"][0]
q0, qa, qr = datos["estado_inicial"][0], datos["estado_aceptacion"][0], datos["estado_rechazo"][0]
cadena = "".join(datos.get("cadena", []))

errores = []

if not {q0, qa, qr} <= Q:
    errores.append("El estado inicial, el de aceptacion y el de rechazo deben estar en Q.")
if qa == qr:
    errores.append("El estado de aceptacion y el de rechazo deben ser distintos.")
if blanco in S:
    errores.append("El blanco no puede estar en el alfabeto de entrada.")
if blanco not in G or not S <= G:
    errores.append("El blanco y el alfabeto de entrada deben estar en el alfabeto de cinta.")

vistas = set()
for t in transiciones:
    if len(t) != 5:
        errores.append(f"Transicion mal escrita: {' '.join(t)}")
        continue
    q, a, p, b, m = t
    if q not in Q or p not in Q or a not in G or b not in G or m not in ("L", "R"):
        errores.append(f"Transicion invalida: {' '.join(t)}")
    if q in (qa, qr):
        errores.append(f"Sale una transicion de un estado final: {' '.join(t)}")
    if (q, a) in vistas:
        errores.append(f"No es determinista, hay dos transiciones para ({q}, {a}).")
    vistas.add((q, a))

for q in Q - {qa, qr}:
    for a in G:
        if (q, a) not in vistas:
            errores.append(f"Falta la transicion para ({q}, {a}).")

for s in cadena:
    if s not in S:
        errores.append(f"El simbolo {s} de la cadena no esta en el alfabeto de entrada.")

if errores:
    print("ESPECIFICACION INVALIDA")
    for e in errores:
        print("-", e)
else:
    print("ESPECIFICACION VALIDA")