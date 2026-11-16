# Formato del archivo de especificación

Cada archivo describe una máquina M = (Q, Σ, Γ, δ, q0, qaccept, qreject) y la cadena de entrada w.

```
estados: q1 q2 qaccept qreject
alfabeto_entrada: 0 1
alfabeto_cinta: 0 1 x _
blanco: _
estado_inicial: q1
estado_aceptacion: qaccept
estado_rechazo: qreject

transiciones:
q1 0 q2 x R
...

cadena: 0011
```

- Los elementos de cada conjunto van separados por espacios.
- Los símbolos de Σ y Γ son de un solo carácter. El blanco ⊔ se escribe `_` (también se acepta `⊔`).
- Cada línea de `transiciones` tiene la forma `q a p b M` y significa δ(q, a) = (p, b, M), con M = L o R.
- `cadena` puede ir junta (`0011`) o separada (`0 0 1 1`). Si se deja vacía, w = ε.
- Las líneas que empiezan con `#` son comentarios y las líneas vacías se ignoran.
- No se puede usar `:` como símbolo de la cinta porque separa el nombre de cada sección.

La lectura está en `lector_mt.py`. `leer_especificacion(ruta)` devuelve `(datos, transiciones)` con la misma estructura que usa `validador_mt.py`, y lanza `ErrorFormato` con el número de línea si hay secciones desconocidas o repetidas, líneas sueltas o símbolos de más de un carácter. Para ver cómo se leyó un archivo:

```
python lector_mt.py especificacion_aceptacion.txt
```
