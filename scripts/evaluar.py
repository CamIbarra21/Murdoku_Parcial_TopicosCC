"""
Evalúa el pipeline completo (visión -> parser -> CP-SAT) contra la verdad terreno
de casos/casos.json, sobre todos los casos cuya imagen está disponible.

Métricas por caso:
  N        la dimensión de la grilla estimada contando líneas coincide con la real
  Salas    % de celdas con la sala correcta (con los nombres asignados por etiqueta)
  Muebles  precisión y recall de la detección de muebles. Una detección cuenta como
           acierto (TP) si coincide el tipo Y la celda con el catálogo:
             precisión = TP / muebles detectados      (¿cuántos de los que dije existen?)
             recall    = TP / muebles reales          (¿cuántos de los reales encontré?)
  Nombres  nombres de las 6 tarjetas leídos correctamente por OCR (de 6)
  Pistas   % de las pistas esperadas que se extrajeron / pistas sobrantes / frases sin interpretar
  Solver   resuelve, la solución es única y señala al culpable correcto; tiempo de CP-SAT

Uso:
    python scripts/evaluar.py                          # todos los casos disponibles
    python scripts/evaluar.py caso_01 caso_02          # solo algunos
    python scripts/evaluar.py --etiqueta base          # guarda resultados/evaluacion_base.json
    python scripts/evaluar.py --etiqueta mejorado      # otra corrida para comparar
    python scripts/evaluar.py --llm                    # permite el respaldo con Ollama

Siempre escribe resultados/evaluacion.md; con --etiqueta escribe además el JSON que lee
scripts/graficar_evaluacion.py para generar las figuras del informe.
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.catalogo import (RAIZ, cargar_catalogo, esta_disponible, mapa_habitaciones,
                          muebles_esperados, puzzle_desde_caso, ruta_imagen)
from src.parser_pistas import normalizar
from src.solver import contar_soluciones, resolver_murdoku
from src.vision import extraer_puzzle_completo


def _clave_pista(p):
    """Forma canónica de una pista para compararla sin importar tildes/mayúsculas."""
    return tuple(sorted((k, normalizar(v) if isinstance(v, str) and k in ("persona", "origen", "destino") else v)
                        for k, v in p.items()))


def evaluar_caso(caso, usar_llm=False):
    t0 = time.time()
    datos = extraer_puzzle_completo(ruta_imagen(caso), N=caso["N"], salas=caso["salas"], usar_llm=usar_llm)
    t_vision = time.time() - t0
    esperado = puzzle_desde_caso(caso, texto_de_imagen=True)
    r = {"id": caso["id"], "nombre": caso["nombre"], "N": caso["N"], "t_vision": t_vision}

    r["N_ok"] = datos["N_estimado"] == caso["N"]

    real_hab = mapa_habitaciones(caso)
    r["salas"] = sum(datos["habitaciones"][c] == real_hab[c] for c in real_hab) / len(real_hab)

    real_mue = {(t, tuple(c)) for t, cs in muebles_esperados(caso).items() for c in cs}
    det_mue = {(t, tuple(c)) for t, cs in datos["muebles"].items() for c in cs}
    tp = len(real_mue & det_mue)
    r.update(mue_tp=tp, mue_detectados=len(det_mue), mue_reales=len(real_mue))
    r["mue_prec"] = tp / len(det_mue) if det_mue else 0.0
    r["mue_rec"] = tp / len(real_mue) if real_mue else 1.0

    nombres_real = [normalizar(p["nombre"]) for p in caso["personajes"]]
    nombres_det = [normalizar(t["nombre"]) for t in datos["tarjetas"]]
    r["nombres"] = sum(a == b for a, b in zip(nombres_real, nombres_det))

    pistas_real = {_clave_pista(p) for p in esperado["pistas"]}
    pistas_det = {_clave_pista(p) for p in datos["pistas"]}
    r["pistas_rec"] = len(pistas_real & pistas_det) / len(pistas_real)
    r["pistas_sobran"] = len(pistas_det - pistas_real)
    r["no_reconocidas"] = len(datos["no_reconocidas"])

    r.update(unica=False, resuelve=False, culpable=None, t_solver_ms=None)
    try:
        sols = contar_soluciones(datos, limite=2)
        r["unica"] = len(sols) == 1
        r["resuelve"] = len(sols) >= 1
        if sols:
            sala_vic = datos["habitaciones"][sols[0][datos["victima"]]]
            culp = [s for s in datos["sospechosos"] if datos["habitaciones"][sols[0][s]] == sala_vic]
            r["culpable"] = culp[0] if culp else None
            r["t_solver_ms"] = resolver_murdoku(datos)["tiempo_ms"]
    except ValueError as e:
        r["error"] = str(e)
    r["culpable_ok"] = r["culpable"] is not None and normalizar(r["culpable"]) == normalizar(caso["culpable"])
    return r


def _commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return None


def tabla_md(filas):
    cab = "| Caso | N | Salas | Muebles P / R | Nombres | Pistas (rec / sobran / sin leer) | Solver | Culpable | t visión | t solver |"
    sep = "|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|"
    lineas = [cab, sep]
    for r in filas:
        solver = 'única' if r['unica'] else ('múltiple' if r['resuelve'] else 'sin solución')
        t_solver = f"{r['t_solver_ms']:.0f} ms" if r["t_solver_ms"] is not None else "-"
        lineas.append(
            f"| {r['id']} {r['nombre']} | {'OK' if r['N_ok'] else 'X'} | {r['salas']:.0%} | "
            f"{r['mue_prec']:.0%} / {r['mue_rec']:.0%} | {r['nombres']}/6 | "
            f"{r['pistas_rec']:.0%} / {r['pistas_sobran']} / {r['no_reconocidas']} | {solver} | "
            f"{r['culpable']} {'OK' if r['culpable_ok'] else 'X'} | {r['t_vision']:.1f} s | {t_solver} |"
        )
    return "\n".join(lineas)


def main():
    ap = argparse.ArgumentParser(description="Evalúa el pipeline contra la verdad terreno del catálogo.")
    ap.add_argument("casos", nargs="*", help="ids a evaluar (por defecto, todos los disponibles)")
    ap.add_argument("--llm", action="store_true", help="permite el respaldo con Ollama en el parser")
    ap.add_argument("--etiqueta", help="nombre de la corrida (guarda resultados/evaluacion_<etiqueta>.json)")
    args = ap.parse_args()

    casos = [c for c in cargar_catalogo() if esta_disponible(c) and (not args.casos or c["id"] in args.casos)]
    if not casos:
        print("No hay imágenes disponibles en static/casos/")
        return

    filas = []
    for caso in casos:
        print(f"Evaluando {caso['id']} {caso['nombre']}...", flush=True)
        filas.append(evaluar_caso(caso, args.llm))

    tabla = tabla_md(filas)
    print("\n" + tabla)

    salida = RAIZ / "resultados"
    salida.mkdir(exist_ok=True)
    (salida / "evaluacion.md").write_text("# Evaluación del pipeline\n\n" + tabla + "\n", encoding="utf-8")
    print(f"\nTabla guardada en {salida / 'evaluacion.md'}")

    if args.etiqueta:
        ruta = salida / f"evaluacion_{args.etiqueta}.json"
        ruta.write_text(json.dumps({
            "etiqueta": args.etiqueta,
            "commit": _commit(),
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "casos": filas,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Corrida guardada en {ruta}")


if __name__ == "__main__":
    main()
