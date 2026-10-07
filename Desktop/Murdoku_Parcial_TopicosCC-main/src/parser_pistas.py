"""
Parser de pistas de Murdoku: convierte el testimonio en español de cada tarjeta
en restricciones formales para el solver.

Estrategia: reglas deterministas primero (los testimonios usan un vocabulario
cerrado). Solo las frases que ninguna regla reconoce se envían a un LLM local
(Ollama) como respaldo.
"""

import difflib
import json
import re
import unicodedata

import requests

ORDINALES = {
    "primera": 1, "segunda": 2, "tercera": 3, "cuarta": 4, "quinta": 5,
    "sexta": 6, "septima": 7, "octava": 8, "ultima": -1,
}

OBJETOS = {
    "silla": "sillas", "sillas": "sillas",
    "mesa": "mesas", "mesas": "mesas",
    "planta": "plantas", "plantas": "plantas",
    "laptop": "computadora", "computadora": "computadora", "computador": "computadora",
}

# Frases informativas que no aportan una restricción espacial por sí mismas
_IGNORABLES = (
    r"\bla vic\w{3,5}\b", r"\bsolo con\b", r"\bultimo area restante\b",
    r"\bcon (el|su) (asesino|agresor|culpable)\b",
)

_MODELO_POR_DEFECTO = "llama3.2:3b"


def normalizar(texto: str) -> str:
    """Minúsculas, sin acentos y con espacios colapsados (tolera ruido de OCR)."""
    sin_acentos = "".join(
        ch for ch in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(ch)
    )
    return re.sub(r"\s+", " ", sin_acentos.lower()).strip()


def _dividir_oraciones(texto: str) -> list:
    plano = re.sub(r"\s+", " ", texto.replace("\n", " ")).strip()
    return [o.strip() for o in re.split(r"(?<=[.!?])\s+", plano) if o.strip()]


def _buscar_persona(token: str, personas: list):
    """Resuelve un nombre (posiblemente con ruido de OCR) contra la lista de personas."""
    mapa = {normalizar(p): p for p in personas}
    cercanos = difflib.get_close_matches(normalizar(token), list(mapa), n=1, cutoff=0.75)
    return mapa[cercanos[0]] if cercanos else None


def _buscar_sala(oracion_norm: str, salas: list):
    """Devuelve el id de la sala mencionada en la oración (la coincidencia más larga)."""
    mejor_id, mejor_len = None, 0
    for sala in salas:
        for nombre in [sala["nombre"]] + list(sala.get("alias", [])):
            n = normalizar(nombre)
            if re.search(rf"\b{re.escape(n)}\b", oracion_norm) and len(n) > mejor_len:
                mejor_id, mejor_len = sala["id"], len(n)
    return mejor_id


def parsear_oracion(oracion: str, persona: str, personas: list, salas: list, N: int):
    """
    Traduce una oración a una lista de pistas.
    Devuelve (pistas, reconocida): 'reconocida' es False si ninguna regla aplicó.
    """
    s = normalizar(oracion).rstrip(".")
    negada = bool(re.search(r"\bno estaba\b", s))
    pistas, reconocida = [], False

    # Dirección relativa: "al sur de Carlos"
    m = re.search(r"\bal (norte|sur|este|oeste) de (\w+)", s)
    if m:
        destino = _buscar_persona(m.group(2), [p for p in personas if p != persona])
        if destino:
            pistas.append({"tipo": "direccion_relativa", "origen": persona,
                           "destino": destino, "direccion": m.group(1)})
            reconocida = True

    # Columna / fila ordinal: "en la tercera columna", "en la última fila"
    for m in re.finditer(r"\b(" + "|".join(ORDINALES) + r") (columna|fila)\b", s):
        if negada:
            continue
        ord_ = ORDINALES[m.group(1)]
        indice = N - 1 if ord_ == -1 else ord_ - 1
        if 0 <= indice < N:
            clave = "columna" if m.group(2) == "columna" else "fila"
            pistas.append({"tipo": f"{clave}_fija", "persona": persona, clave: indice})
            reconocida = True

    # Junto a un mueble: "al lado de una planta"
    m = re.search(r"\bal lado de una? (\w+)", s)
    if m and m.group(1) in OBJETOS:
        pistas.append({"tipo": "no_adyacente_a" if negada else "adyacente_a",
                       "persona": persona, "objeto": OBJETOS[m.group(1)]})
        reconocida = True

    # Sobre una silla: "sentado en una silla", "no estaba en una silla"
    if re.search(r"\ben (una )?silla\b", s):
        pistas.append({"tipo": "no_sobre_objeto" if negada else "sobre_objeto",
                       "persona": persona, "objeto": "sillas"})
        reconocida = True

    # Habitación mencionada
    sala = _buscar_sala(s, salas)
    if sala is not None and not negada:
        pistas.append({"tipo": "habitacion_fija", "persona": persona, "habitacion": sala})
        reconocida = True

    if not reconocida and any(re.search(p, s) for p in _IGNORABLES):
        reconocida = True

    return pistas, reconocida


def parsear_con_llm(oracion: str, persona: str, personas: list, salas: list, N: int,
                    modelo: str = _MODELO_POR_DEFECTO) -> list:
    """Respaldo: pide a Ollama la traducción de UNA oración que las reglas no reconocieron."""
    prompt = f"""Traduce la frase de un acertijo Murdoku a restricciones JSON.
Personaje que habla: {persona}. Personas: {personas}. Salas: {[(s['id'], s['nombre']) for s in salas]}. Tablero {N}x{N} (filas y columnas desde 0).
Frase: "{oracion}"
Tipos permitidos: columna_fija(persona, columna), fila_fija(persona, fila), habitacion_fija(persona, habitacion=id),
sobre_objeto/no_sobre_objeto/adyacente_a/no_adyacente_a(persona, objeto in [sillas, mesas, plantas, computadora]),
direccion_relativa(origen, destino, direccion in [norte, sur, este, oeste]).
Usa siempre el nombre propio, nunca pronombres. Responde SOLO con {{"pistas": [...]}}."""
    try:
        r = requests.post("http://localhost:11434/api/generate", timeout=40, json={
            "model": modelo, "prompt": prompt, "format": "json", "stream": False,
            "options": {"temperature": 0.0}})
        r.raise_for_status()
        candidatas = json.loads(r.json()["response"]).get("pistas", [])
    except Exception as e:
        print(f"  [Ollama] respaldo no disponible: {e}")
        return []

    ids_sala = {s["id"] for s in salas}
    validas = []
    for p in candidatas:
        tipo = p.get("tipo")
        quien = p.get("origen") if tipo == "direccion_relativa" else p.get("persona")
        if quien not in personas:
            continue
        if tipo == "direccion_relativa" and p.get("destino") not in personas:
            continue
        if tipo == "habitacion_fija" and p.get("habitacion") not in ids_sala:
            continue
        if tipo in ("columna_fija", "fila_fija") and not (0 <= p.get(tipo[:-5], -1) < N):
            continue
        validas.append(p)
    return validas


def construir_pistas(tarjetas: list, salas: list, N: int, usar_llm: bool = True,
                     modelo: str = _MODELO_POR_DEFECTO):
    """
    tarjetas: lista de {"nombre": str, "texto": str}; la víctima es la tarjeta cuyo
    texto contiene "víctima" (si ninguna, la última).
    Devuelve (sospechosos, victima, pistas, no_reconocidas).
    """
    nombres = [t["nombre"] for t in tarjetas]
    idx_victima = next(
        (i for i, t in enumerate(tarjetas) if re.search(r"\bla vic\w{3,5}\b", normalizar(t["texto"]))),
        len(tarjetas) - 1,
    )
    victima = nombres[idx_victima]
    sospechosos = [n for i, n in enumerate(nombres) if i != idx_victima]

    pistas, no_reconocidas = [], []
    for tarjeta in tarjetas:
        for oracion in _dividir_oraciones(tarjeta["texto"]):
            nuevas, ok = parsear_oracion(oracion, tarjeta["nombre"], nombres, salas, N)
            if not ok:
                if usar_llm:
                    nuevas = parsear_con_llm(oracion, tarjeta["nombre"], nombres, salas, N, modelo)
                if not nuevas:
                    no_reconocidas.append((tarjeta["nombre"], oracion))
            pistas.extend(nuevas)
    return sospechosos, victima, pistas, no_reconocidas
