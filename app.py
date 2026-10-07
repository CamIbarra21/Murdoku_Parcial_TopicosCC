"""
Servidor API REST para Murdoku AI Detective Suite.
Expone endpoints para extracción por visión, resolución SAT y tutoría socrática.

Los casos salen de casos/casos.json (src/catalogo.py); un caso está habilitado solo si su
imagen existe en static/casos/.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.agent import reformular_pista
from src.catalogo import (RAIZ, cargar_catalogo, esta_disponible, obtener_caso,
                          resumen_caso, ruta_imagen)
from src.solver import resolver_murdoku
from src.tutor import proxima_pista, validar_jugada
from src.vision import extraer_puzzle_completo

app = FastAPI(title="Murdoku Detective API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caché en memoria por caso: la visión + OCR tarda unos segundos y no cambia entre consultas
SESIONES = {}


class JugadaRequest(BaseModel):
    """Estado del jugador: ubicaciones marcadas, {persona: [fila, columna]} con índices desde 0."""
    colocaciones: dict[str, list[int]] = {}
    nivel: int = 1            # nivel de ayuda de la pista (1 a 3)
    usar_llm: bool = True     # permite que Ollama reformule el texto (nunca decide la pista)


def _caso_disponible(caso_id: str) -> dict:
    try:
        caso = obtener_caso(caso_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Caso desconocido: {caso_id}")
    if not esta_disponible(caso):
        raise HTTPException(status_code=404, detail=f"El caso {caso_id} aún no tiene imagen.")
    return caso


def _sesion(caso_id: str) -> dict:
    """Devuelve (y calcula si hace falta) la extracción de visión del caso."""
    if caso_id not in SESIONES:
        caso = _caso_disponible(caso_id)
        puzzle = extraer_puzzle_completo(ruta_imagen(caso), N=caso["N"], salas=caso["salas"])
        SESIONES[caso_id] = {"caso": caso, "puzzle_data": puzzle, "solucion": None}
    return SESIONES[caso_id]


@app.get("/api/casos")
def obtener_casos():
    """Retorna la lista de expedientes; 'disponible' indica si ya hay imagen."""
    return [resumen_caso(c) for c in cargar_catalogo()]


@app.post("/api/analizar")
def analizar_tablero(caso: str):
    """Ejecuta Visión Computacional + OCR + parser de pistas sobre el caso."""
    _caso_disponible(caso)
    try:
        sesion = _sesion(caso)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    sesion["solucion"] = None
    puzzle, info = sesion["puzzle_data"], sesion["caso"]

    return {
        "exito": True,
        "caso": caso,
        "nombre": info["nombre"],
        "archivo": info["archivo"],
        "url_imagen": f"/casos/{info['archivo']}",
        "N": puzzle["N"],
        "victima": puzzle["victima"],
        "sospechosos": puzzle["sospechosos"],
        "salas": info["salas"],
        "tarjetas": puzzle["tarjetas"],
        "muebles": {k: [list(c) for c in v] for k, v in puzzle["muebles"].items()},
        "habitaciones": {f"{r},{c}": hab for (r, c), hab in puzzle["habitaciones"].items()},
        "pistas": puzzle["pistas"],
        "no_reconocidas": puzzle["no_reconocidas"],
    }


@app.post("/api/resolver")
def resolver_caso(caso: str):
    """Resuelve las restricciones lógicas mediante Google OR-Tools CP-SAT."""
    sesion = _sesion(caso)
    try:
        resultado = resolver_murdoku(sesion["puzzle_data"])
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not resultado["exito"]:
        raise HTTPException(status_code=400, detail="El puzzle no tiene solución factible.")

    sesion["solucion"] = resultado
    return {
        "exito": True,
        "asesino": resultado["asesino"],
        "victima": resultado["victima"],
        "posiciones": resultado["posiciones"],
        "tiempo_ms": resultado["tiempo_ms"],
    }


def _colocaciones_validas(sesion: dict, colocaciones: dict) -> dict:
    """Valida nombres y coordenadas recibidas del navegador."""
    puzzle = sesion["puzzle_data"]
    personas = set(puzzle["sospechosos"]) | {puzzle["victima"]}
    resultado = {}
    for nombre, pos in colocaciones.items():
        if nombre not in personas:
            raise HTTPException(status_code=422, detail=f"Persona desconocida: {nombre}")
        if len(pos) != 2 or not all(0 <= v < puzzle["N"] for v in pos):
            raise HTTPException(status_code=422, detail=f"Casilla fuera del tablero para {nombre}: {pos}")
        resultado[nombre] = (pos[0], pos[1])
    return resultado


@app.post("/api/tutor")
def consultar_tutor(caso: str, req: JugadaRequest):
    """
    Pista para el siguiente paso del jugador. La decide el solver (src/tutor.py) a partir de
    las ubicaciones marcadas; Ollama solo reformula el texto si está disponible.
    """
    sesion = _sesion(caso)
    puzzle = sesion["puzzle_data"]
    pista = proxima_pista(puzzle, _colocaciones_validas(sesion, req.colocaciones), req.nivel)

    pista["fuente"] = "solver"
    if req.usar_llm:
        nombres = puzzle["sospechosos"] + [puzzle["victima"]]
        pista["mensaje"], pista["fuente"] = reformular_pista(pista["mensaje"], nombres)
    return pista


@app.post("/api/validar")
def validar_tablero(caso: str, req: JugadaRequest):
    """Comprueba las ubicaciones del jugador contra las pistas sin revelar la solución."""
    sesion = _sesion(caso)
    return validar_jugada(sesion["puzzle_data"], _colocaciones_validas(sesion, req.colocaciones))


# Servir la interfaz web y las imágenes de los casos (static/casos/caso_NN.png)
app.mount("/", StaticFiles(directory=str(RAIZ / "static"), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
