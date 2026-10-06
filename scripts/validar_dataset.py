"""
Valida los casos de casos/casos.json con el solver CP-SAT.

Por cada caso comprueba:
  1. Coherencia estructural (mapa NxN, muebles dentro del tablero, 6 personajes).
  2. Que todas las frases de los testimonios las entienda el parser.
  3. Que exista exactamente UNA solución y que coincida con la guardada.
  4. Que la solución guardada respete las reglas (filas/columnas distintas,
     nadie sobre obstáculos, un único sospechoso con la víctima).

Uso:  python scripts/validar_dataset.py
Termina con código 1 si algún caso falla.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.catalogo import cargar_catalogo, puzzle_desde_caso
from src.solver import contar_soluciones


def validar_estructura(caso):
    errores = []
    N = caso["N"]
    if len(caso["mapa"]) != N or any(len(f) != N for f in caso["mapa"]):
        errores.append(f"el mapa no es {N}x{N}")
    ids_sala = {s["id"] for s in caso["salas"]}
    if {int(ch) for fila in caso["mapa"] for ch in fila} != ids_sala:
        errores.append("el mapa no usa exactamente las salas declaradas")
    for tipo, celdas in caso["muebles"].items():
        for r, c in celdas:
            if not (0 <= r < N and 0 <= c < N):
                errores.append(f"mueble {tipo} fuera del tablero: {(r, c)}")
    if len(caso["personajes"]) != 6:
        errores.append("debe haber 6 tarjetas (5 sospechosos + víctima)")
    return errores


def validar_solucion_guardada(caso, puzzle):
    errores = []
    sol = {n: tuple(v) for n, v in caso["solucion"].items()}
    filas = [v[0] for v in sol.values()]
    cols = [v[1] for v in sol.values()]
    if len(set(filas)) != len(filas):
        errores.append("la solución guardada repite fila")
    if len(set(cols)) != len(cols):
        errores.append("la solución guardada repite columna")
    obstaculos = {tuple(c) for t in puzzle["obstaculos"] for c in puzzle["muebles"].get(t, [])}
    for nombre, pos in sol.items():
        if pos in obstaculos:
            errores.append(f"{nombre} está sobre un obstáculo {pos}")
    sala_vic = puzzle["habitaciones"][sol[puzzle["victima"]]]
    con_victima = [s for s in puzzle["sospechosos"] if puzzle["habitaciones"][sol[s]] == sala_vic]
    if con_victima != [caso["culpable"]]:
        errores.append(f"sospechosos con la víctima: {con_victima}, esperado [{caso['culpable']}]")
    return errores


def main():
    fallos = 0
    for caso in cargar_catalogo():
        errores = validar_estructura(caso)
        puzzle = puzzle_desde_caso(caso)
        if puzzle["no_reconocidas"]:
            errores.append(f"frases sin interpretar: {puzzle['no_reconocidas']}")
        if not errores:
            errores += validar_solucion_guardada(caso, puzzle)
            soluciones = contar_soluciones(puzzle, limite=2)
            if len(soluciones) != 1:
                errores.append(f"se esperaba solución única y hay {'>=2' if soluciones else '0'}")
            elif {n: tuple(v) for n, v in caso["solucion"].items()} != soluciones[0]:
                errores.append("la solución del solver no coincide con la guardada")
        estado = "OK " if not errores else "ERR"
        print(f"[{estado}] {caso['id']} {caso['nombre']:<26} {caso['N']}x{caso['N']}  "
              f"pistas={len(puzzle['pistas']):>2}  culpable={caso['culpable']}")
        for e in errores:
            print(f"        - {e}")
        fallos += bool(errores)
    print(f"\n{len(cargar_catalogo()) - fallos}/{len(cargar_catalogo())} casos válidos")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
