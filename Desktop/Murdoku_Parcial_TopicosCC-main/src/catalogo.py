"""
Catálogo de casos de Murdoku: única fuente de verdad de los 10 casos del dataset.

Lee casos/casos.json y resuelve la ruta de cada imagen en static/casos/.
Un caso está 'disponible' solo si su imagen existe en disco, de modo que agregar
una imagen nueva a esa carpeta activa el caso sin tocar el código.
"""

import json
from functools import lru_cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_CASOS_JSON = RAIZ / "casos" / "casos.json"
DIR_IMAGENES = RAIZ / "static" / "casos"

# Muebles sobre los que nadie puede pararse (las sillas sí se pueden ocupar)
OBSTACULOS = ["mesas", "plantas", "computadora"]


@lru_cache(maxsize=1)
def cargar_catalogo() -> list:
    """Devuelve la lista de casos tal como está en casos.json."""
    with open(RUTA_CASOS_JSON, encoding="utf-8") as f:
        return json.load(f)["casos"]


def obtener_caso(caso_id: str) -> dict:
    """Busca un caso por id (ej. 'caso_02'). Lanza KeyError si no existe."""
    for caso in cargar_catalogo():
        if caso["id"] == caso_id:
            return caso
    raise KeyError(f"Caso desconocido: {caso_id}")


def ruta_imagen(caso: dict) -> Path:
    return DIR_IMAGENES / caso["archivo"]


def esta_disponible(caso: dict) -> bool:
    return ruta_imagen(caso).is_file()


def mapa_habitaciones(caso: dict) -> dict:
    """Verdad terreno: {(fila, columna): id_sala}."""
    N = caso["N"]
    return {(r, c): int(caso["mapa"][r][c]) for r in range(N) for c in range(N)}


def muebles_esperados(caso: dict) -> dict:
    """Verdad terreno de muebles: {tipo: [(fila, columna), ...]}."""
    return {tipo: [tuple(c) for c in celdas] for tipo, celdas in caso["muebles"].items()}


def puzzle_desde_caso(caso: dict, texto_de_imagen: bool = False) -> dict:
    """
    Construye el 'puzzle_data' esperado a partir del catálogo (sin visión):
    sirve para validar el dataset y como verdad terreno al evaluar la visión.
    Con texto_de_imagen=True usa el texto que realmente muestra la imagen.
    """
    from src.parser_pistas import construir_pistas

    tarjetas = [
        {"nombre": p["nombre"],
         "texto": p.get("texto_imagen", p["texto"]) if texto_de_imagen else p["texto"]}
        for p in caso["personajes"]
    ]
    sospechosos, victima, pistas, no_reconocidas = construir_pistas(
        tarjetas, caso["salas"], caso["N"], usar_llm=False
    )
    return {
        "N": caso["N"],
        "sospechosos": sospechosos,
        "victima": victima,
        "habitaciones": mapa_habitaciones(caso),
        "muebles": muebles_esperados(caso),
        "pistas": pistas,
        "obstaculos": OBSTACULOS,
        "salas": caso["salas"],
        "tarjetas": tarjetas,
        "no_reconocidas": no_reconocidas,
    }


def resumen_caso(caso: dict) -> dict:
    """Datos que necesita la galería web para mostrar la tarjeta del caso."""
    return {
        "id": caso["id"],
        "nombre": caso["nombre"],
        "archivo": caso["archivo"],
        "url_imagen": f"/casos/{caso['archivo']}",
        "dificultad": caso["dificultad"],
        "grid": f"{caso['N']}x{caso['N']}",
        "sospechosos_count": len(caso["personajes"]) - 1,
        "habitaciones_count": len(caso["salas"]),
        "disponible": esta_disponible(caso),
    }
