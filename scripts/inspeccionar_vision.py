"""
Guarda qué reconoce el módulo de visión en cada casilla de cada caso.

Por cada caso escribe en resultados/vision/<etiqueta>/<caso>/:
    deteccion.json       salas, muebles por tipo, detalle de cada casilla (desviación, plantilla
                         ganadora, similitud coseno), tarjetas leídas y pistas extraídas
    celdas.csv           una fila por casilla: sala, ¿tiene objeto?, plantilla, similitud,
                         tipo detectado, tipo real (catálogo) y estado
    tablero_anotado.png  el tablero con lo detectado en cada casilla, coloreado por estado

y un resumen.md con los aciertos, falsos positivos, omisiones y tipos incorrectos de todos los
casos. Estado de cada casilla al compararla con el catálogo:
    ok             el tipo detectado coincide con el real
    falso_positivo se detectó un mueble donde no hay ninguno
    omitido        hay un mueble real que no se detectó
    tipo_incorrecto se detectó un mueble, pero de otro tipo
    vacio          casilla vacía correctamente ignorada

Uso:
    python scripts/inspeccionar_vision.py                       # todos los casos disponibles
    python scripts/inspeccionar_vision.py caso_04 caso_10       # solo algunos
    python scripts/inspeccionar_vision.py --etiqueta base       # carpeta resultados/vision/base/
    python scripts/inspeccionar_vision.py --etiqueta mejorado   # otra corrida para comparar
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.catalogo import (RAIZ, cargar_catalogo, esta_disponible, mapa_habitaciones,
                          muebles_esperados, ruta_imagen)
from src.vision import extraer_puzzle_completo

ABREVIATURA = {"sillas": "SILLA", "mesas": "MESA", "plantas": "PLANTA", "computadora": "LAPTOP"}

# BGR: acierto verde, falso positivo rojo, omitido naranja, tipo incorrecto violeta
COLOR_ESTADO = {
    "ok": (60, 170, 40),
    "falso_positivo": (50, 50, 220),
    "omitido": (0, 140, 255),
    "tipo_incorrecto": (180, 60, 160),
}
ETIQUETA_ESTADO = {"ok": "OK", "falso_positivo": "SOBRA", "omitido": "FALTA", "tipo_incorrecto": "TIPO?"}


def estado_celda(real, detectado):
    if real is None and detectado is None:
        return "vacio"
    if real is None:
        return "falso_positivo"
    if detectado is None:
        return "omitido"
    return "ok" if real == detectado else "tipo_incorrecto"


def anotar_tablero(tablero_bgr, N, filas):
    """Dibuja sobre el tablero el tipo detectado, la similitud y el estado de cada casilla."""
    lienzo = tablero_bgr.copy()
    alto, ancho = lienzo.shape[:2]
    ac, anc = alto // N, ancho // N
    fuente = cv2.FONT_HERSHEY_SIMPLEX
    escala = max(0.32, anc / 190)
    grosor = 1 if anc < 120 else 2

    def texto(img, s, x, y, color, esc=escala):
        (tw, th), _ = cv2.getTextSize(s, fuente, esc, grosor)
        x = x - tw // 2
        cv2.rectangle(img, (x - 2, y - th - 2), (x + tw + 2, y + 3), (255, 255, 255), -1)
        cv2.putText(img, s, (x, y), fuente, esc, color, grosor, cv2.LINE_AA)

    for f in filas:
        if f["estado"] == "vacio":
            continue
        r, c = f["fila"], f["columna"]
        x1, y1 = c * anc, r * ac
        color = COLOR_ESTADO[f["estado"]]
        cv2.rectangle(lienzo, (x1 + 3, y1 + 3), (x1 + anc - 3, y1 + ac - 3), color, 3)
        cx = x1 + anc // 2
        if f["tipo_detectado"]:
            texto(lienzo, ABREVIATURA[f["tipo_detectado"]], cx, y1 + int(ac * 0.30), (30, 30, 30))
            texto(lienzo, f"{f['similitud']:.2f}", cx, y1 + int(ac * 0.52), (90, 90, 90), escala * 0.9)
        else:
            texto(lienzo, f"real: {ABREVIATURA[f['tipo_real']]}", cx, y1 + int(ac * 0.30), (30, 30, 30), escala * 0.9)
        texto(lienzo, ETIQUETA_ESTADO[f["estado"]], cx, y1 + int(ac * 0.90), color)

    # Leyenda debajo del tablero
    pie = 46
    lienzo = cv2.copyMakeBorder(lienzo, 0, pie, 0, 0, cv2.BORDER_CONSTANT, value=(252, 252, 251))
    x = 10
    for estado, color in COLOR_ESTADO.items():
        cv2.rectangle(lienzo, (x, alto + 14), (x + 18, alto + 32), color, -1)
        nombre = {"ok": "acierto", "falso_positivo": "sobra (falso positivo)",
                  "omitido": "falta (omitido)", "tipo_incorrecto": "tipo incorrecto"}[estado]
        cv2.putText(lienzo, nombre, (x + 24, alto + 29), fuente, 0.5, (60, 60, 60), 1, cv2.LINE_AA)
        x += 24 + int(cv2.getTextSize(nombre, fuente, 0.5, 1)[0][0]) + 22
    return lienzo


def inspeccionar_caso(caso, carpeta, usar_llm=False):
    datos = extraer_puzzle_completo(ruta_imagen(caso), N=caso["N"], salas=caso["salas"], usar_llm=usar_llm)
    N = caso["N"]
    real = {tuple(c): tipo for tipo, celdas in muebles_esperados(caso).items() for c in celdas}
    salas_real = mapa_habitaciones(caso)
    nombre_sala = {s["id"]: s["nombre"] for s in caso["salas"]}

    filas = []
    for r in range(N):
        for c in range(N):
            info = datos["celdas_detalle"][(r, c)]
            tipo_real = real.get((r, c))
            filas.append({
                "fila": r, "columna": c,
                "sala_detectada": nombre_sala.get(datos["habitaciones"][(r, c)], datos["habitaciones"][(r, c)]),
                "sala_real": nombre_sala[salas_real[(r, c)]],
                "tiene_objeto": info["tiene_objeto"], "std": info["std"],
                "plantilla": info["plantilla"], "similitud": info["similitud"],
                "tipo_detectado": info["tipo"], "tipo_real": tipo_real,
                "estado": estado_celda(tipo_real, info["tipo"]),
            })

    carpeta.mkdir(parents=True, exist_ok=True)
    with open(carpeta / "celdas.csv", "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)

    por_estado = {e: [(f["fila"], f["columna"]) for f in filas if f["estado"] == e]
                  for e in ("ok", "falso_positivo", "omitido", "tipo_incorrecto")}
    deteccion = {
        "caso": caso["id"], "nombre": caso["nombre"], "N": N,
        "salas": {f"{r},{c}": nombre_sala.get(datos["habitaciones"][(r, c)]) for r in range(N) for c in range(N)},
        "muebles_detectados": {t: [list(c) for c in cs] for t, cs in datos["muebles"].items() if cs},
        "muebles_reales": {t: [list(c) for c in cs] for t, cs in caso["muebles"].items() if cs},
        "resumen": {e: len(v) for e, v in por_estado.items()},
        "casillas_por_estado": {e: [list(c) for c in v] for e, v in por_estado.items() if v},
        "celdas": [{**f, "similitudes": datos["celdas_detalle"][(f["fila"], f["columna"])]["similitudes"]}
                   for f in filas if f["tiene_objeto"] or f["tipo_real"]],
        "tarjetas": datos["tarjetas"],
        "pistas": datos["pistas"],
        "frases_sin_interpretar": datos["no_reconocidas"],
    }
    (carpeta / "deteccion.json").write_text(json.dumps(deteccion, ensure_ascii=False, indent=1), encoding="utf-8")
    cv2.imwrite(str(carpeta / "tablero_anotado.png"), anotar_tablero(datos["tablero_img"], N, filas))
    return deteccion


def main():
    ap = argparse.ArgumentParser(description="Guarda qué casillas reconoce la visión en cada caso.")
    ap.add_argument("casos", nargs="*", help="ids a inspeccionar (por defecto, todos los disponibles)")
    ap.add_argument("--etiqueta", default="ultima", help="subcarpeta de resultados/vision/ (por defecto: ultima)")
    ap.add_argument("--llm", action="store_true", help="permite el respaldo con Ollama en el parser")
    args = ap.parse_args()

    casos = [c for c in cargar_catalogo() if esta_disponible(c) and (not args.casos or c["id"] in args.casos)]
    if not casos:
        sys.exit("No hay imágenes disponibles en static/casos/")

    base = RAIZ / "resultados" / "vision" / args.etiqueta
    resultados = []
    for caso in casos:
        print(f"Inspeccionando {caso['id']} {caso['nombre']}...", flush=True)
        resultados.append(inspeccionar_caso(caso, base / caso["id"], args.llm))

    lineas = [f"# Detección de muebles por casilla — corrida «{args.etiqueta}»", "",
              "Comparada con la verdad terreno de `casos/casos.json`. Coordenadas (fila, columna) desde 0.", "",
              "| Caso | Aciertos | Sobran | Faltan | Tipo incorrecto | Casillas con error |",
              "|---|:-:|:-:|:-:|:-:|---|"]
    for d in resultados:
        r = d["resumen"]
        errores = []
        for estado, etiqueta in (("falso_positivo", "sobra"), ("omitido", "falta"), ("tipo_incorrecto", "tipo")):
            errores += [f"{etiqueta} ({a},{b})" for a, b in d["casillas_por_estado"].get(estado, [])]
        lineas.append(f"| {d['caso']} {d['nombre']} | {r['ok']} | {r['falso_positivo']} | {r['omitido']} | "
                      f"{r['tipo_incorrecto']} | {', '.join(errores) or '-'} |")
    (base / "resumen.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")

    print("\n" + "\n".join(lineas[4:]))
    print(f"\nResultados en {base}")


if __name__ == "__main__":
    main()
