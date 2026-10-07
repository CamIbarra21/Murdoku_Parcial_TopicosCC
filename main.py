"""
Pipeline Real End-to-End de Murdoku.
1. Visión Computacional: K-Means (habitaciones) + MobileNetV3 (muebles).
2. OCR + Parser: Tesseract por tarjeta + reglas en español (Ollama solo como respaldo).
3. Constraint Programming: Google OR-Tools CP-SAT para deducir al asesino.
4. Renderizado: Proyección visual de la solución sobre el tablero original.

Uso:
    python main.py                 # caso_01
    python main.py --caso caso_02
    python main.py --lista         # muestra los casos y si su imagen existe
"""

import argparse
import sys

import cv2

from src.catalogo import cargar_catalogo, esta_disponible, obtener_caso, ruta_imagen
from src.solver import contar_soluciones, resolver_murdoku
from src.visualizer import dibujar_solucion_sobre_tablero
from src.vision import extraer_puzzle_completo


def listar_casos():
    for caso in cargar_catalogo():
        estado = "disponible" if esta_disponible(caso) else "sin imagen"
        print(f"  {caso['id']}  {caso['nombre']:<26} {caso['N']}x{caso['N']}  [{estado}]")


def ejecutar(caso_id, modelo_llm="llama3.2:3b", salida_imagen=None):
    caso = obtener_caso(caso_id)
    if not esta_disponible(caso):
        print(f"El caso {caso_id} todavía no tiene imagen en static/casos/{caso['archivo']}.")
        return 1
    salida_imagen = salida_imagen or f"tablero_resuelto_{caso_id}.png"

    print("=" * 70)
    print("PIPELINE AUTÓNOMO END-TO-END (MURDOKU)")
    print(f"Caso: {caso['nombre']} ({caso['N']}x{caso['N']}) | Imagen: {ruta_imagen(caso).name}")
    print("=" * 70)

    # -------------------------------------------------------------
    # PASO 1: EXTRACCIÓN CON VISIÓN, OCR Y PARSER DE PISTAS
    # -------------------------------------------------------------
    print("\n[1/3] Extrayendo tablero, muebles y pistas...")
    puzzle_data = extraer_puzzle_completo(
        ruta_imagen(caso), N=caso["N"], salas=caso["salas"], modelo_ollama=modelo_llm
    )

    print("\n--- RESUMEN DE EXTRACCIÓN DINÁMICA ---")
    print(f"  • Tablero               : {puzzle_data['N']}x{puzzle_data['N']}")
    print(f"  • Víctima identificada  : {puzzle_data['victima']}")
    print(f"  • Sospechosos leídos    : {puzzle_data['sospechosos']}")

    print("  • Muebles clasificados  :")
    for tipo, coords in puzzle_data["muebles"].items():
        if coords:
            print(f"      - {tipo:<12}: {len(coords)} encontrados -> {coords}")

    print(f"\n  • Pistas extraídas ({len(puzzle_data['pistas'])} reglas):")
    for idx, p in enumerate(puzzle_data["pistas"], 1):
        print(f"      {idx}. {p}")
    for persona, frase in puzzle_data["no_reconocidas"]:
        print(f"  ! Frase sin interpretar ({persona}): {frase}")

    # -------------------------------------------------------------
    # PASO 2: SOLVER DE CONSTRAINT PROGRAMMING (OR-Tools)
    # -------------------------------------------------------------
    print("\n[2/3] Resolviendo restricciones lógicas con Google OR-Tools CP-SAT...")
    resultado = resolver_murdoku(puzzle_data)

    if not resultado["exito"]:
        print("❌ Error: El solver determinó que el conjunto de restricciones es INFACTIBLE.")
        print("   Revisa si alguna pista extraída colisiona con los obstáculos.")
        return 1

    unica = len(contar_soluciones(puzzle_data, limite=2)) == 1
    print(f"  ✓ Caso resuelto en {resultado['tiempo_ms']:.2f} ms "
          f"({'solución única' if unica else 'hay más de una solución'})\n")
    print("--- POSICIONES FINALES DEDUCIDAS ---")
    for persona, d in resultado["posiciones"].items():
        rol = " [VÍCTIMA]" if persona == resultado["victima"] else ""
        print(f"  • {persona:<10}{rol:<11}: Fila {d['fila']}, Columna {d['columna']} (Habitación {d['habitacion']})")

    print("\n" + "=" * 45)
    print(f"🎯 EL ASESINO ES: {resultado['asesino']}")
    print("=" * 45)

    # -------------------------------------------------------------
    # PASO 3: PROYECCIÓN VISUAL SOBRE EL TABLERO
    # -------------------------------------------------------------
    print("\n[3/3] Superponiendo solución sobre la imagen...")
    tablero_resuelto = dibujar_solucion_sobre_tablero(
        puzzle_data["tablero_img"], resultado, N=puzzle_data["N"]
    )
    cv2.imwrite(salida_imagen, tablero_resuelto)
    print(f"  ✓ Imagen anotada guardada en: '{salida_imagen}'\n")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resuelve un caso de Murdoku a partir de su imagen.")
    parser.add_argument("--caso", default="caso_01", help="id del caso (ej. caso_02)")
    parser.add_argument("--modelo", default="llama3.2:3b", help="modelo de Ollama para el respaldo del parser")
    parser.add_argument("--salida", help="ruta de la imagen resuelta")
    parser.add_argument("--lista", action="store_true", help="lista los casos y termina")
    args = parser.parse_args()

    if args.lista:
        listar_casos()
        sys.exit(0)
    sys.exit(ejecutar(args.caso, args.modelo, args.salida))
