"""
Genera las figuras del informe a partir de las corridas de scripts/evaluar.py.

Uso:
    python scripts/evaluar.py --etiqueta base
    python scripts/graficar_evaluacion.py base                    # métricas y tiempos de una corrida
    python scripts/graficar_evaluacion.py base mejorado           # además, comparación antes -> después

Salida en resultados/figuras/ (PNG a 300 dpi para Word y PDF vectorial para LaTeX):
    fig_metricas_<etiqueta>       mapa de calor casos x métricas de visión (con valores en cada celda)
    fig_tiempos_<etiqueta>        tiempo de visión y de CP-SAT por caso, coloreado por tamaño de grilla
    fig_comparacion_<a>_vs_<b>    antes -> después por caso y métrica (solo con dos etiquetas)
    comparacion_<a>_vs_<b>.md     tabla con los promedios y la variación de cada métrica

Paleta: la de referencia del skill de visualización (azul/naranja validados daltonismo; ramp
azul 100-700 para la escala secuencial).
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from matplotlib.lines import Line2D

RAIZ = Path(__file__).resolve().parent.parent
DIR_RESULTADOS = RAIZ / "resultados"
DIR_FIGURAS = DIR_RESULTADOS / "figuras"

# --- Tokens (modo claro del palette de referencia) ---
SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
TINTA_SUAVE = "#898781"
GRILLA = "#e1e0d9"
EJE = "#c3c2b7"
AZUL = "#2a78d6"      # categórica 1
NARANJA = "#eb6834"   # categórica 2
RAMPA_AZUL = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
              "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
CMAP = LinearSegmentedColormap.from_list("azul_secuencial", RAMPA_AZUL)

METRICAS = [
    ("salas", "Salas\n(% celdas)"),
    ("mue_prec", "Muebles\nprecisión"),
    ("mue_rec", "Muebles\nrecall"),
    ("nombres", "Nombres\nOCR"),
    ("pistas_rec", "Pistas\nrecall"),
]

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE,
    "text.color": TINTA, "axes.labelcolor": TINTA_2, "xtick.color": TINTA_SUAVE, "ytick.color": TINTA_2,
    "axes.edgecolor": EJE, "axes.linewidth": 0.8,
})


def cargar(etiqueta):
    ruta = DIR_RESULTADOS / f"evaluacion_{etiqueta}.json"
    if not ruta.exists():
        sys.exit(f"No existe {ruta}. Ejecuta: python scripts/evaluar.py --etiqueta {etiqueta}")
    return json.loads(ruta.read_text(encoding="utf-8"))


def valor(caso, clave):
    """Todas las métricas en escala 0-1 (los nombres se leen sobre 6)."""
    return caso[clave] / 6 if clave == "nombres" else caso[clave]


def promedio(casos, clave):
    return sum(valor(c, clave) for c in casos) / len(casos)


def etiqueta_caso(c):
    return f"{c['id'][-2:]}  {c['nombre']}  ({c['N']}×{c['N']})"


def guardar(fig, nombre):
    DIR_FIGURAS.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(DIR_FIGURAS / f"{nombre}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  {DIR_FIGURAS / (nombre + '.png')}")


def pie(fig, corrida, y=-0.01):
    commit = f" · commit {corrida['commit']}" if corrida.get("commit") else ""
    fig.text(0.01, y, f"Corrida «{corrida['etiqueta']}»{commit} · {len(corrida['casos'])} casos",
             fontsize=8, color=TINTA_SUAVE, ha="left", va="top")


# ------------------------------------------------------------------ figura 1: mapa de calor
def fig_metricas(corrida):
    casos = corrida["casos"]
    filas = [etiqueta_caso(c) for c in casos] + ["Promedio"]
    datos = [[valor(c, k) for k, _ in METRICAS] for c in casos]
    datos.append([promedio(casos, k) for k, _ in METRICAS])

    alto = 0.46 * len(filas) + 1.6
    fig, ax = plt.subplots(figsize=(8.2, alto))
    n_filas, n_cols = len(filas), len(METRICAS)
    for i, fila in enumerate(datos):
        y = i + (0.35 if i == n_filas - 1 else 0)  # espacio antes del promedio
        for j, v in enumerate(fila):
            color = CMAP(v)
            ax.add_patch(plt.Rectangle((j + 0.03, y + 0.04), 0.94, 0.92, facecolor=color, edgecolor="none"))
            luminancia = 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]
            ax.text(j + 0.5, y + 0.5, f"{v:.0%}", ha="center", va="center", fontsize=9.5,
                    fontweight="bold" if i == n_filas - 1 else "normal",
                    color=TINTA if luminancia > 0.55 else "#ffffff")
    ax.set_xlim(0, n_cols)
    ax.set_ylim(n_filas + 0.35, 0)
    ax.set_xticks([j + 0.5 for j in range(n_cols)])
    ax.set_xticklabels([m for _, m in METRICAS], fontsize=9)
    ax.xaxis.tick_top()
    ax.set_yticks([i + 0.5 + (0.35 if i == n_filas - 1 else 0) for i in range(n_filas)])
    ax.set_yticklabels(filas, fontsize=9.5)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.tick_params(length=0)
    for lado in ax.spines.values():
        lado.set_visible(False)
    ax.set_title("Calidad de la extracción por caso", loc="left", fontsize=13, fontweight="bold", pad=34)
    ax.text(0, -0.085, "Más oscuro = mejor; las celdas claras señalan los casos a corregir",
            transform=ax.transAxes, fontsize=9, color=TINTA_2, va="bottom")
    pie(fig, corrida, y=0.02)
    guardar(fig, f"fig_metricas_{corrida['etiqueta']}")


# ------------------------------------------------------------------ figura 2: tiempos
def fig_tiempos(corrida):
    casos = corrida["casos"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 0.42 * len(casos) + 1.8), sharey=True)
    y = list(range(len(casos)))
    for ax, clave, factor, unidad, titulo in (
            (a1, "t_vision", 1, "s", "Visión + OCR"),
            (a2, "t_solver_ms", 1, "ms", "Solver CP-SAT")):
        vals = [(c[clave] or 0) * factor for c in casos]
        colores = [AZUL if c["N"] == 6 else NARANJA for c in casos]
        ax.barh(y, vals, color=colores, height=0.62, edgecolor=SUPERFICIE, linewidth=2)
        tope = max(vals) * 1.22 if max(vals) else 1
        for yi, v in zip(y, vals):
            ax.text(v + tope * 0.015, yi, f"{v:.1f} {unidad}" if unidad == "s" else f"{v:.0f} {unidad}",
                    va="center", fontsize=8.5, color=TINTA_2)
        ax.set_xlim(0, tope)
        ax.set_title(titulo, loc="left", fontsize=10.5, fontweight="bold", color=TINTA)
        ax.xaxis.grid(True, color=GRILLA, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.tick_params(length=0)
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)
    a1.set_yticks(y)
    a1.set_yticklabels([f"{c['id'][-2:]}  {c['nombre']}" for c in casos], fontsize=9)
    a1.invert_yaxis()
    fig.suptitle("Tiempo de ejecución por caso", x=0.01, ha="left", fontsize=13, fontweight="bold", y=1.02)
    fig.legend(handles=[Line2D([], [], marker="s", ls="", color=AZUL, markersize=8, label="Grilla 6×6"),
                        Line2D([], [], marker="s", ls="", color=NARANJA, markersize=8, label="Grilla 8×8")],
               loc="upper right", bbox_to_anchor=(0.99, 1.03), frameon=False, ncol=2, fontsize=9)
    fig.tight_layout()
    pie(fig, corrida, y=-0.01)
    guardar(fig, f"fig_tiempos_{corrida['etiqueta']}")


# ------------------------------------------------------------------ figura 3: comparación
def fig_comparacion(antes, despues):
    ids = [c["id"] for c in antes["casos"] if c["id"] in {d["id"] for d in despues["casos"]}]
    a = {c["id"]: c for c in antes["casos"]}
    d = {c["id"]: c for c in despues["casos"]}
    comunes_a = [a[i] for i in ids]
    comunes_d = [d[i] for i in ids]
    n = len(ids)

    fig, ejes = plt.subplots(1, len(METRICAS), figsize=(11, 0.4 * (n + 1) + 2.4), sharey=True)
    for ax, (clave, titulo) in zip(ejes, METRICAS):
        minimo = min(min(valor(c, clave) for c in comunes_a), min(valor(c, clave) for c in comunes_d))
        inferior = max(0.0, min(0.8, (int(minimo * 10) - 1) / 10))
        for i in range(n + 1):
            esprom = i == n
            yy = i + (0.35 if esprom else 0)
            va = promedio(comunes_a, clave) if esprom else valor(comunes_a[i], clave)
            vd = promedio(comunes_d, clave) if esprom else valor(comunes_d[i], clave)
            ax.plot([va, vd], [yy, yy], color=EJE, linewidth=2, solid_capstyle="round", zorder=1)
            for v, col, z in ((va, NARANJA, 2), (vd, AZUL, 3)):
                ax.scatter([v], [yy], s=70 if esprom else 46, color=col, edgecolor=SUPERFICIE,
                           linewidth=1.5, zorder=z)
            if abs(vd - va) > 0.005:
                ax.text(max(va, vd) + (1.0 - inferior) * 0.035, yy, f"{(vd - va) * 100:+.0f}", fontsize=8, va="center",
                        color=TINTA_2)
        ax.axhline(n - 0.2, color=GRILLA, linewidth=0.8)
        # Eje recortado al rango de los datos: son posiciones, no longitudes, y así se ven los
        # cambios pequeños (p. ej. 88 % -> 100 %) en lugar de quedar pegados al 100 %.
        ax.set_xlim(inferior, 1.0 + (1.0 - inferior) * 0.22)
        marcas = [round(inferior + (1.0 - inferior) * k / 2, 2) for k in range(3)]
        ax.set_xticks(marcas)
        ax.set_xticklabels([f"{m:.0%}" for m in marcas], fontsize=8)
        ax.xaxis.grid(True, color=GRILLA, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.set_title(titulo.replace("\n", " "), fontsize=9.5, loc="left", color=TINTA)
        ax.tick_params(length=0)
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)
    ejes[0].set_yticks(list(range(n)) + [n + 0.35])
    ejes[0].set_yticklabels([etiqueta_caso(c) for c in comunes_a] + ["Promedio"], fontsize=9)
    ejes[0].get_yticklabels()[-1].set_fontweight("bold")
    ejes[0].set_ylim(n + 0.8, -0.6)

    fig.suptitle("Mejora de la extracción: antes → después", x=0.01, ha="left", fontsize=13,
                 fontweight="bold", y=1.0)
    fig.legend(handles=[
        Line2D([], [], marker="o", ls="", color=NARANJA, markersize=8, label=f"Antes ({antes['etiqueta']})"),
        Line2D([], [], marker="o", ls="", color=AZUL, markersize=8, label=f"Después ({despues['etiqueta']})")],
        loc="upper right", bbox_to_anchor=(0.99, 1.0), frameon=False, ncol=2, fontsize=9)
    fig.text(0.01, 0.945, "El número junto a cada par es el cambio en puntos porcentuales",
             fontsize=9, color=TINTA_2)
    fig.tight_layout(rect=(0, 0.02, 1, 0.93))
    c1 = f" ({antes['commit']} → {despues['commit']})" if antes.get("commit") and despues.get("commit") else ""
    fig.text(0.01, 0.0, f"Corridas «{antes['etiqueta']}» → «{despues['etiqueta']}»{c1} · {n} casos",
             fontsize=8, color=TINTA_SUAVE, va="top")
    guardar(fig, f"fig_comparacion_{antes['etiqueta']}_vs_{despues['etiqueta']}")

    # Tabla resumen para el informe
    lineas = [f"# Comparación «{antes['etiqueta']}» → «{despues['etiqueta']}»", "",
              "| Métrica (promedio por caso) | Antes | Después | Cambio |", "|---|:-:|:-:|:-:|"]
    for clave, titulo in METRICAS:
        pa, pd_ = promedio(comunes_a, clave), promedio(comunes_d, clave)
        lineas.append(f"| {titulo.replace(chr(10), ' ')} | {pa:.1%} | {pd_:.1%} | {(pd_ - pa) * 100:+.1f} pp |")
    for clave, titulo in (("unica", "Casos con solución única"), ("culpable_ok", "Casos con culpable correcto")):
        na, nd = sum(bool(c[clave]) for c in comunes_a), sum(bool(c[clave]) for c in comunes_d)
        lineas.append(f"| {titulo} | {na}/{n} | {nd}/{n} | {nd - na:+d} |")
    ruta = DIR_FIGURAS / f"comparacion_{antes['etiqueta']}_vs_{despues['etiqueta']}.md"
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"  {ruta}")


def main():
    etiquetas = sys.argv[1:]
    if not etiquetas or len(etiquetas) > 2:
        sys.exit(__doc__)
    corridas = [cargar(e) for e in etiquetas]
    print("Figuras generadas:")
    for corrida in corridas:
        fig_metricas(corrida)
        fig_tiempos(corrida)
    if len(corridas) == 2:
        fig_comparacion(*corridas)


if __name__ == "__main__":
    main()
