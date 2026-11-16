# Máquina del inciso b)

M = (Q, Σ, Γ, δ, q1, qaccept, qreject) donde:

- Q = {q1, q2, q3, q4, q5, q6, qaccept, qreject}
- Σ = {0, 1}
- Γ = {0, 1, x, y, ⊔}

M reconoce L(M) = {0ⁿ1ⁿ | n ≥ 1} pero no lo decide, porque con las cadenas que empiezan con 1 nunca se detiene.

M = "Sobre la cadena de entrada w:
1. Si el primer símbolo es 1, moverse a la derecha y regresar a la izquierda para siempre.
2. Si la cinta está en blanco, rechazar.
3. Marcar el primer 0 con x y avanzar a la derecha hasta el primer 1. Si no hay ningún 1, rechazar. Marcar ese 1 con y.
4. Regresar a la izquierda hasta la última x y repetir la etapa 3 mientras queden 0s antes de las y.
5. Cuando ya no queden 0s por marcar, recorrer las y. Si después de ellas solo hay ⊔, aceptar; si aparece un 0 o un 1, rechazar."

| δ  | 0          | 1          | x          | y          | ⊔                |
|----|------------|------------|------------|------------|------------------|
| q1 | (q2, x, R) | (q5, 1, R) | rechazo    | (q4, y, R) | (qreject, ⊔, R)  |
| q2 | (q2, 0, R) | (q3, y, L) | rechazo    | (q2, y, R) | (qreject, ⊔, R)  |
| q3 | (q3, 0, L) | rechazo    | (q1, x, R) | (q3, y, L) | rechazo          |
| q4 | (qreject, 0, R) | (qreject, 1, R) | rechazo | (q4, y, R) | (qaccept, ⊔, R) |
| q5 | (q6, 0, L) | (q6, 1, L) | (q6, x, L) | (q6, y, L) | (q6, ⊔, L)       |
| q6 | (q5, 0, R) | (q5, 1, R) | (q5, x, R) | (q5, y, R) | (q5, ⊔, R)       |

"rechazo" es (qreject, a, R) dejando el mismo símbolo; son casos que no se alcanzan pero se incluyen para que δ esté definida en todo (Q − {qaccept, qreject}) × Γ. En el diagrama se pueden omitir como en el diagrama de M2, indicándolo en una nota.

Cadenas de ejemplo:

| Caso       | w      | Resultado                              |
|------------|--------|----------------------------------------|
| Aceptación | 0011   | 13 pasos, termina en qaccept           |
| Rechazo    | 001    | termina en qreject (falta un 1)        |
| Rechazo    | 01011  | termina en qreject (0 después de un 1) |
| Ciclo      | 10     | q5 y q6 se alternan sin detenerse      |
