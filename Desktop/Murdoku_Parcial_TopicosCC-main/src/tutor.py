"""
Tutor interactivo de Murdoku.

La lógica de las pistas es DETERMINISTA y la decide el solver:
  1. Se comprueban las ubicaciones del jugador contra todas las pistas reificadas
     (si hay contradicción, se señalan los testimonios involucrados).
  2. Si no hay contradicción, se elige a la persona con menos casillas posibles y se calcula,
     con CP-SAT, en qué casillas puede estar realmente.
  3. La pista se entrega en tres niveles de ayuda progresiva (qué mirar, cuánto se reduce,
     qué casillas quedan).

El LLM (src/agent.py) solo puede reformular el texto ya decidido; nunca decide la deducción.
Las posiciones se muestran al jugador con filas y columnas desde 1, como las ordinales de los
testimonios ("la segunda columna").
"""

from src.solver import celdas_factibles, diagnosticar_conflicto

NIVEL_MAXIMO = 3

_OBJETO = {"sillas": "una silla", "mesas": "una mesa", "plantas": "una planta", "computadora": "la laptop"}


def _celda(pos) -> str:
    return f"fila {pos[0] + 1}, columna {pos[1] + 1}"


def _nombre_sala(puzzle_data, id_sala) -> str:
    for sala in puzzle_data.get("salas", []):
        if sala["id"] == id_sala:
            return sala["nombre"]
    return f"la sala {id_sala}"


def describir_pista(pista, puzzle_data) -> str:
    """Frase corta en español de una pista estructurada."""
    tipo = pista["tipo"]
    if tipo == "direccion_relativa":
        return f"{pista['origen']} está al {pista['direccion']} de {pista['destino']}"
    quien = pista["persona"]
    if tipo == "columna_fija":
        return f"{quien} está en la columna {pista['columna'] + 1}"
    if tipo == "fila_fija":
        return f"{quien} está en la fila {pista['fila'] + 1}"
    if tipo == "habitacion_fija":
        return f"{quien} está en {_nombre_sala(puzzle_data, pista['habitacion'])}"
    objeto = _OBJETO.get(pista.get("objeto"), pista.get("objeto"))
    return {
        "sobre_objeto": f"{quien} está sobre {objeto}",
        "no_sobre_objeto": f"{quien} no está sobre {objeto}",
        "adyacente_a": f"{quien} está al lado de {objeto}",
        "no_adyacente_a": f"{quien} no está al lado de {objeto}",
    }[tipo]


def candidatas_por_reglas(puzzle_data, persona, colocaciones) -> set:
    """
    Casillas que las reglas simples (sin búsqueda) no descartan para 'persona'.
    Es una relajación correcta: la casilla real siempre queda dentro de este conjunto.
    """
    N = puzzle_data["N"]
    muebles = puzzle_data.get("muebles", {})
    obstaculos = {tuple(c) for t in puzzle_data.get("obstaculos", []) for c in muebles.get(t, [])}
    otras = {n: pos for n, pos in colocaciones.items() if n != persona}
    filas_usadas = {pos[0] for pos in otras.values()}
    cols_usadas = {pos[1] for pos in otras.values()}

    def vecinos(tipo_mueble):
        return {(r + dr, c + dc) for r, c in muebles.get(tipo_mueble, [])
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))}

    celdas = {(r, c) for r in range(N) for c in range(N)
              if (r, c) not in obstaculos and r not in filas_usadas and c not in cols_usadas}
    habitaciones = puzzle_data["habitaciones"]

    for p in puzzle_data.get("pistas", []):
        tipo = p["tipo"]
        if tipo == "direccion_relativa":
            if p["origen"] == persona and p["destino"] in otras:
                dr, dc = otras[p["destino"]]
                filtro = {"norte": lambda r, c: r < dr, "sur": lambda r, c: r > dr,
                          "este": lambda r, c: c > dc, "oeste": lambda r, c: c < dc}[p["direccion"]]
            elif p["destino"] == persona and p["origen"] in otras:
                orr, oc = otras[p["origen"]]
                filtro = {"norte": lambda r, c: r > orr, "sur": lambda r, c: r < orr,
                          "este": lambda r, c: c < oc, "oeste": lambda r, c: c > oc}[p["direccion"]]
            else:
                continue
            celdas = {(r, c) for r, c in celdas if filtro(r, c)}
            continue
        if p.get("persona") != persona:
            continue
        if tipo == "columna_fija":
            celdas = {(r, c) for r, c in celdas if c == p["columna"]}
        elif tipo == "fila_fija":
            celdas = {(r, c) for r, c in celdas if r == p["fila"]}
        elif tipo == "habitacion_fija":
            celdas = {(r, c) for r, c in celdas if habitaciones[(r, c)] == p["habitacion"]}
        elif tipo == "sobre_objeto":
            celdas &= {tuple(c) for c in muebles.get(p["objeto"], [])}
        elif tipo == "no_sobre_objeto":
            celdas -= {tuple(c) for c in muebles.get(p["objeto"], [])}
        elif tipo == "adyacente_a":
            celdas &= vecinos(p["objeto"])
        elif tipo == "no_adyacente_a":
            celdas -= vecinos(p["objeto"])
    return celdas


def _razones(puzzle_data, persona) -> list:
    """Tipos de información que acotan a 'persona' (para el nivel 2, sin dar casillas)."""
    nombres = {
        "columna_fija": "su columna", "fila_fija": "su fila", "habitacion_fija": "su habitación",
        "sobre_objeto": "los muebles sobre los que debe estar", "no_sobre_objeto": "los muebles que debe evitar",
        "adyacente_a": "los muebles junto a los que debe estar", "no_adyacente_a": "los muebles que debe evitar",
        "direccion_relativa": "su posición respecto a otras personas",
    }
    razones = []
    for p in puzzle_data.get("pistas", []):
        if persona in (p.get("persona"), p.get("origen"), p.get("destino")):
            r = nombres[p["tipo"]]
            if r not in razones:
                razones.append(r)
    razones.append("las filas, columnas y casillas que ya están ocupadas")
    return razones


def _testimonio(puzzle_data, persona) -> str:
    for t in puzzle_data.get("tarjetas") or []:
        if t["nombre"] == persona:
            return t["texto"]
    propias = [describir_pista(p, puzzle_data) for p in puzzle_data.get("pistas", [])
               if persona in (p.get("persona"), p.get("origen"))]
    return ". ".join(propias)


def proxima_pista(puzzle_data, colocaciones, nivel=1) -> dict:
    """
    Pista para el siguiente paso del jugador.

    colocaciones: {persona: (fila, columna)} con índices desde 0.
    Devuelve {"tipo": "conflicto"|"pista"|"completo", "mensaje": str, "persona"?, "nivel"?, "candidatas"?}.
    """
    nivel = max(1, min(int(nivel), NIVEL_MAXIMO))
    personas = puzzle_data["sospechosos"] + [puzzle_data["victima"]]
    colocaciones = {n: tuple(pos) for n, pos in colocaciones.items()}

    diag = diagnosticar_conflicto(puzzle_data, colocaciones)
    if not diag["consistente"]:
        return {"tipo": "conflicto", "mensaje": _mensaje_conflicto(puzzle_data, diag),
                "personas": diag["personas"]}

    pendientes = [p for p in personas if p not in colocaciones]
    if not pendientes:
        return {"tipo": "completo", "mensaje": "Ya ubicaste a todos y no hay contradicciones: ¡revisa quién comparte sala con la víctima!"}

    por_reglas = {p: candidatas_por_reglas(puzzle_data, p, colocaciones) for p in pendientes}
    objetivo = min(pendientes, key=lambda p: (len(por_reglas[p]), personas.index(p)))
    reales = sorted(celdas_factibles(puzzle_data, objetivo, colocaciones, sorted(por_reglas[objetivo])))
    testimonio = _testimonio(puzzle_data, objetivo)

    if nivel == 1:
        if testimonio:
            if not testimonio.endswith((".", "!", "?")):
                testimonio += "."
            mensaje = (f"Fíjate en {objetivo}: «{testimonio}» "
                       f"¿Qué casillas del tablero descarta ese dato?")
        else:
            mensaje = (f"Fíjate en {objetivo}: ninguna pista lo nombra, así que piensa qué casillas "
                       f"dejan libres las filas, columnas y muebles que ya están ocupados.")
    elif nivel == 2:
        razones = ", ".join(_razones(puzzle_data, objetivo))
        k = len(reales)
        cuantas = "una única casilla" if k == 1 else f"{k} casillas"
        mensaje = (f"Combinando todas las pistas con lo que ya colocaste, {objetivo} solo cabe en {cuantas}. "
                   f"Piensa en: {razones}.")
    else:
        if len(reales) == 1:
            mensaje = f"Solo queda una casilla posible para {objetivo}: {_celda(reales[0])}."
        else:
            lista = "; ".join(_celda(c) for c in reales)
            mensaje = f"{objetivo} solo puede estar en: {lista}."

    return {"tipo": "pista", "mensaje": mensaje, "persona": objetivo, "nivel": nivel,
            "candidatas": [list(c) for c in reales] if nivel >= NIVEL_MAXIMO else None}


def _mensaje_conflicto(puzzle_data, diag) -> str:
    quienes = ", ".join(diag["personas"]) or "alguna ubicación"
    if diag["pistas"]:
        motivos = "; ".join(describir_pista(p, puzzle_data) for p in diag["pistas"][:3])
        return (f"Antes de avanzar: lo que colocaste para {quienes} contradice lo que dicen los testimonios "
                f"({motivos}). Revísalo.")
    return (f"Antes de avanzar: la ubicación de {quienes} no es compatible con las reglas del tablero "
            f"(nadie comparte fila ni columna y no se pisan muebles). Revísala.")


def validar_jugada(puzzle_data, colocaciones) -> dict:
    """
    Evalúa el estado del jugador sin revelar dónde va cada persona.
    Devuelve {"estado": "conflicto"|"parcial"|"resuelto", "mensaje": str, "colocadas": int, "total": int, "asesino"?}.
    """
    personas = puzzle_data["sospechosos"] + [puzzle_data["victima"]]
    colocaciones = {n: tuple(pos) for n, pos in colocaciones.items()}
    base = {"colocadas": len(colocaciones), "total": len(personas)}

    diag = diagnosticar_conflicto(puzzle_data, colocaciones)
    if not diag["consistente"]:
        return {**base, "estado": "conflicto", "mensaje": _mensaje_conflicto(puzzle_data, diag),
                "personas": diag["personas"]}

    if len(colocaciones) == len(personas):
        sala = puzzle_data["habitaciones"][colocaciones[puzzle_data["victima"]]]
        culpables = [s for s in puzzle_data["sospechosos"]
                     if puzzle_data["habitaciones"][colocaciones[s]] == sala]
        return {**base, "estado": "resuelto", "asesino": culpables[0] if culpables else None,
                "mensaje": f"¡Caso resuelto! El asesino es {culpables[0]}, el único sospechoso que comparte sala con {puzzle_data['victima']}."}

    return {**base, "estado": "parcial",
            "mensaje": f"Vas bien: {len(colocaciones)} de {len(personas)} ubicaciones sin contradicciones."}
