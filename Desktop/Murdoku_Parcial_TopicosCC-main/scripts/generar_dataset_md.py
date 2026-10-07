"""
Genera dataset_casos_murdoku.md (raíz) a partir de casos/casos.json (la fuente única).
Es el documento que se usa como guía para dibujar las imágenes de los casos.

Uso:  python scripts/generar_dataset_md.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.catalogo import RAIZ, cargar_catalogo, esta_disponible

ETIQUETA_MUEBLE = {"mesas": "Mesa", "sillas": "Silla", "plantas": "Planta", "computadora": "Laptop"}


def plano(caso):
    N = caso["N"]
    nombre_sala = {s["id"]: s["nombre"] for s in caso["salas"]}
    mueble = {}
    for tipo, celdas in caso["muebles"].items():
        for r, c in celdas:
            mueble[(r, c)] = ETIQUETA_MUEBLE[tipo]
    filas = ["| Fila \\ Col | " + " | ".join(f"Columna {c}" for c in range(N)) + " |",
             "| :---: |" + " :---: |" * N]
    for r in range(N):
        celdas = []
        for c in range(N):
            sala = nombre_sala[int(caso["mapa"][r][c])]
            m = mueble.get((r, c))
            celdas.append(f"[{sala}] " + (f"**{m}**" if m else "Libre"))
        filas.append(f"| **Fila {r}** | " + " | ".join(celdas) + " |")
    return "\n".join(filas)


def tarjetas(caso):
    victima = caso["personajes"][-1]
    filas = ["| Fila de Tarjetas | Columna 1 (Izquierda) | Columna 2 (Centro) | Columna 3 (Derecha) |",
             "| :--- | :--- | :--- | :--- |"]
    for i, titulo in enumerate(("Fila 1 (Superior)", "Fila 2 (Inferior)")):
        celdas = []
        for p in caso["personajes"][i * 3:(i + 1) * 3]:
            nombre = p["nombre"].upper() + (" [VÍCTIMA]" if p is victima else "")
            celdas.append(f"**{nombre}**<br>{p['texto']}")
        filas.append(f"| **{titulo}** | " + " | ".join(celdas) + " |")
    return "\n".join(filas)


def lista_detallada(caso):
    victima = caso["personajes"][-1]
    filas = ["| # Tarjeta | Posición Gráfica | Personaje | Rol | Testimonio / Pista Exacta |",
             "| :---: | :---: | :--- | :---: | :--- |"]
    for i, p in enumerate(caso["personajes"]):
        if p is victima:
            rol = "VÍCTIMA"
        elif p["nombre"] == caso["culpable"]:
            rol = "Culpable"
        else:
            rol = "Sospechoso"
        filas.append(f"| {i + 1} | Fila {i // 3 + 1}, Col {i % 3 + 1} | {p['nombre'].upper()} | {rol} | {p['texto']} |")
    return "\n".join(filas)


def solucion(caso):
    nombre_sala = {s["id"]: s["nombre"] for s in caso["salas"]}
    victima = caso["personajes"][-1]["nombre"]
    lineas = []
    for nombre, (r, c) in caso["solucion"].items():
        sala = nombre_sala[int(caso["mapa"][r][c])]
        rol = " [VÍCTIMA]" if nombre == victima else (" [CULPABLE]" if nombre == caso["culpable"] else "")
        lineas.append(f"* **{nombre}{rol}:** Fila {r}, Columna {c} (Habitación: {sala})")
    return "\n".join(lineas)


def main():
    casos = cargar_catalogo()
    md = ["# DATASET OFICIAL MURDOKU: 10 CASOS LÓGICOS (EXCEL READY)",
          "",
          "> **Instrucciones para Excel / Google Sheets:** selecciona cualquier tabla, cópiala (`Ctrl + C`) y pégala "
          "(`Ctrl + V`) en una hoja de cálculo; se distribuirá en celdas individuales.",
          ">",
          "> Documento **generado** por `scripts/generar_dataset_md.py` desde `casos/casos.json`: no editar a mano "
          "(edita el JSON y vuelve a generarlo). Cada caso tiene **solución única** verificada con "
          "`python scripts/validar_dataset.py`.",
          ">",
          "> **Convenciones:** filas y columnas desde 0; \"al lado de\" = adyacencia ortogonal (arriba, abajo, izquierda "
          "o derecha); \"al norte/sur/este/oeste de X\" = estrictamente arriba/abajo/derecha/izquierda de X, no necesariamente "
          "contiguo; las sillas se pueden ocupar, las mesas, plantas y laptops no.",
          ">",
          "> **Imágenes:** se guardan como `static/casos/caso_NN.png` (por ejemplo `caso_04.png`). "
          "En cuanto exista el archivo, la tarjeta del caso se habilita en la web.",
          "",
          "---",
          "",
          "## 1. TABLA RESUMEN GENERAL DEL DATASET",
          "",
          "| ID | Archivo de imagen | Nombre del Caso | Dimensión | Habitaciones | Víctima | Culpable Deducido | Imagen |",
          "| :---: | :--- | :--- | :---: | :--- | :--- | :--- | :---: |"]
    for c in casos:
        nuevas = any("texto_imagen" in p for p in c["personajes"])
        estado = "lista, actualizar tarjeta" if nuevas else ("lista" if esta_disponible(c) else "pendiente")
        md.append(f"| **{c['id'][-2:]}** | `{c['archivo']}` | {c['nombre']} | ${c['N']} \\times {c['N']}$ | "
                  f"{', '.join(s['nombre'] for s in c['salas'])} | {c['personajes'][-1]['nombre']} | "
                  f"**{c['culpable']}** | {estado} |")

    for c in casos:
        md += ["", "---", "", f"## CASO {c['id'][-2:]}: {c['nombre'].upper()} (${c['N']} \\times {c['N']}$)", "",
               f"* **Archivo de imagen:** `static/casos/{c['archivo']}`",
               f"* **Dificultad:** {c['dificultad']}",
               f"* **Revisión:** {c['revision']}"]
        pendientes = [p for p in c["personajes"] if "texto_imagen" in p]
        for p in pendientes:
            md.append(f"* **ACTUALIZAR LA IMAGEN:** la tarjeta de {p['nombre'].upper()} debe decir «{p['texto']}» "
                      f"(hoy dice «{p['texto_imagen']}»).")
        habitaciones = " | ".join(f"H{s['id']} = {s['nombre']}" for s in c["salas"])
        md += ["", "### A. Matriz del Tablero (Plano de Habitaciones y Muebles)", "",
               f"* **Habitaciones:** {habitaciones}", "", plano(c), "",
               "### B. Tarjetas de Personajes (Distribución Espacial $2 \\times 3$)", "", tarjetas(c), "",
               "#### Lista Detallada de Personajes (Para Registros en Excel)", "", lista_detallada(c), "",
               "### C. Solución Ground Truth (Posiciones Verificadas)", "", solucion(c)]

    salida = RAIZ / "dataset_casos_murdoku.md"
    salida.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Escrito {salida}")


if __name__ == "__main__":
    main()
