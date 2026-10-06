"""
Módulo del Solver de Constraint Programming para Murdoku.
Implementación genérica con Google OR-Tools CP-SAT.
Recibe dinámicamente el diccionario 'puzzle_data' generado por visión computacional.
"""

from ortools.sat.python import cp_model

# Tipos de pista que entiende el modelo. Cualquier otro tipo es un error:
# ignorarlo en silencio podría devolver soluciones incorrectas.
TIPOS_PISTA = {
    "columna_fija", "fila_fija", "habitacion_fija", "direccion_relativa",
    "sobre_objeto", "no_sobre_objeto", "adyacente_a", "no_adyacente_a",
}

_VECINOS_ORTOGONALES = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def _vecinos_de(celdas, N):
    """Celdas ortogonalmente adyacentes a cualquiera de 'celdas' (dentro del tablero)."""
    vecinos = set()
    for tr, tc in celdas:
        for dr, dc in _VECINOS_ORTOGONALES:
            nr, nc = tr + dr, tc + dc
            if 0 <= nr < N and 0 <= nc < N:
                vecinos.add((nr, nc))
    return vecinos


def _construir_modelo(puzzle_data, reificar=False):
    """
    Construye el modelo CP-SAT de una instancia de Murdoku.

    Parámetros (puzzle_data dict):
      - 'N': int (dimensión de la grilla NxN)
      - 'sospechosos': list[str] (nombres de los sospechosos)
      - 'victima': str (nombre de la víctima)
      - 'habitaciones': dict[(r, c), int] (mapa de celda a ID de habitación)
      - 'muebles': dict[str, list[(r, c)]] (coordenadas detectadas)
      - 'pistas': list[dict] (restricciones relacionales)
      - 'obstaculos': list[str] (muebles donde no se puede pisar)

    Devuelve (model, personas, X, Y, Z, celda, literales) donde 'literales' es una lista de
    (pista, BoolVar): cada pista está reificada con su literal (OnlyEnforceIf) y, salvo que se
    quiera diagnosticar, todos los literales se fuerzan a 1.
    """
    model = cp_model.CpModel()

    N = puzzle_data["N"]
    sospechosos = puzzle_data["sospechosos"]
    victima = puzzle_data["victima"]
    personas = sospechosos + [victima]
    num_personas = len(personas)
    idx_victima = num_personas - 1
    idx = {nombre: i for i, nombre in enumerate(personas)}

    # -------------------------------------------------------------
    # 1. VARIABLES BOOLEANAS DE OCUPACIÓN
    # -------------------------------------------------------------
    # celda[(p, r, c)] == 1 si la persona p está en la fila r, columna c
    celda = {}
    for p in range(num_personas):
        for r in range(N):
            for c in range(N):
                celda[(p, r, c)] = model.NewBoolVar(f"celda_{p}_{r}_{c}")

    # -------------------------------------------------------------
    # 2. RESTRICCIONES ESTRUCTURALES DEL TABLERO
    # -------------------------------------------------------------
    # Cada persona debe ocupar exactamente una casilla
    for p in range(num_personas):
        model.Add(sum(celda[(p, r, c)] for r in range(N) for c in range(N)) == 1)

    # Principio AllDifferent: nadie comparte fila ni columna
    for r in range(N):
        model.Add(sum(celda[(p, r, c)] for p in range(num_personas) for c in range(N)) <= 1)

    for c in range(N):
        model.Add(sum(celda[(p, r, c)] for p in range(num_personas) for r in range(N)) <= 1)

    # -------------------------------------------------------------
    # 3. PROYECCIÓN A COORDENADAS (X, Y) Y HABITACIÓN (Z)
    # -------------------------------------------------------------
    mapa_hab = puzzle_data["habitaciones"]
    ids_hab = sorted(set(mapa_hab.values()))

    X = [model.NewIntVar(0, N - 1, f"X_{p}") for p in personas]
    Y = [model.NewIntVar(0, N - 1, f"Y_{p}") for p in personas]
    Z = [model.NewIntVar(min(ids_hab), max(ids_hab), f"Z_{p}") for p in personas]

    for p in range(num_personas):
        model.Add(X[p] == sum(r * celda[(p, r, c)] for r in range(N) for c in range(N)))
        model.Add(Y[p] == sum(c * celda[(p, r, c)] for r in range(N) for c in range(N)))
        model.Add(Z[p] == sum(mapa_hab[(r, c)] * celda[(p, r, c)] for r in range(N) for c in range(N)))

    # -------------------------------------------------------------
    # 4. REGLA INTRÍNSECA DE MURDOKU: LA VÍCTIMA Y EL ASESINO
    # -------------------------------------------------------------
    # La víctima comparte habitación con exactamente un sospechoso (el asesino).
    # Restricción reificada: la condición "víctima en h" activa la cuenta.
    for h in ids_hab:
        vic_en_h = model.NewBoolVar(f"vic_en_hab_{h}")
        model.Add(Z[idx_victima] == h).OnlyEnforceIf(vic_en_h)
        model.Add(Z[idx_victima] != h).OnlyEnforceIf(vic_en_h.Not())

        sospechosos_en_h = []
        for s_idx in range(len(sospechosos)):
            s_en_h = model.NewBoolVar(f"s_{s_idx}_en_hab_{h}")
            model.Add(Z[s_idx] == h).OnlyEnforceIf(s_en_h)
            model.Add(Z[s_idx] != h).OnlyEnforceIf(s_en_h.Not())
            sospechosos_en_h.append(s_en_h)

        model.Add(sum(sospechosos_en_h) == 1).OnlyEnforceIf(vic_en_h)

    # -------------------------------------------------------------
    # 5. REGLA GLOBAL DE OBSTÁCULOS FÍSICOS
    # -------------------------------------------------------------
    # Nadie puede estar sobre mesas, plantas, computadoras, etc.
    muebles = puzzle_data.get("muebles", {})
    obstaculos_config = puzzle_data.get("obstaculos", ["mesas", "plantas", "computadora"])

    for tipo_obs in obstaculos_config:
        for r, c in muebles.get(tipo_obs, []):
            for p in range(num_personas):
                model.Add(celda[(p, r, c)] == 0)

    # -------------------------------------------------------------
    # 6. PISTAS ESPECÍFICAS (validación estricta)
    # -------------------------------------------------------------
    def persona_idx(nombre, pista):
        if nombre not in idx:
            raise ValueError(f"Pista con persona desconocida '{nombre}': {pista}")
        return idx[nombre]

    literales = []
    for pista in puzzle_data.get("pistas", []):
        tipo = pista.get("tipo")
        if tipo not in TIPOS_PISTA:
            raise ValueError(f"Tipo de pista desconocido '{tipo}': {pista}")

        lit = model.NewBoolVar(f"pista_{len(literales)}")
        literales.append((pista, lit))

        def agregar(restriccion, lit=lit):
            restriccion.OnlyEnforceIf(lit)

        if tipo == "direccion_relativa":
            p_orig = persona_idx(pista.get("origen"), pista)
            p_dest = persona_idx(pista.get("destino"), pista)
            direccion = pista.get("direccion")
            if direccion == "norte":
                agregar(model.Add(X[p_orig] < X[p_dest]))
            elif direccion == "sur":
                agregar(model.Add(X[p_orig] > X[p_dest]))
            elif direccion == "este":
                agregar(model.Add(Y[p_orig] > Y[p_dest]))
            elif direccion == "oeste":
                agregar(model.Add(Y[p_orig] < Y[p_dest]))
            else:
                raise ValueError(f"Dirección desconocida '{direccion}': {pista}")
            continue

        p_idx = persona_idx(pista.get("persona"), pista)

        if tipo == "columna_fija":
            agregar(model.Add(Y[p_idx] == pista["columna"]))

        elif tipo == "fila_fija":
            agregar(model.Add(X[p_idx] == pista["fila"]))

        elif tipo == "habitacion_fija":
            if pista["habitacion"] not in ids_hab:
                raise ValueError(f"Habitación inexistente en la pista: {pista}")
            agregar(model.Add(Z[p_idx] == pista["habitacion"]))

        elif tipo in ("sobre_objeto", "no_sobre_objeto"):
            targets = muebles.get(pista.get("objeto"), [])
            suma = sum(celda[(p_idx, r, c)] for r, c in targets)
            # Si no se detectó ningún mueble de ese tipo, "sobre" es infactible
            agregar(model.Add(suma == (1 if tipo == "sobre_objeto" else 0)))

        elif tipo in ("adyacente_a", "no_adyacente_a"):
            vecinos = _vecinos_de(muebles.get(pista.get("objeto"), []), N)
            suma = sum(celda[(p_idx, r, c)] for r, c in vecinos)
            agregar(model.Add(suma >= 1) if tipo == "adyacente_a" else model.Add(suma == 0))

    if not reificar:
        for _, lit in literales:
            model.Add(lit == 1)

    return model, personas, X, Y, Z, celda, literales


def resolver_murdoku(puzzle_data):
    """Resuelve una instancia de Murdoku a partir de los datos extraídos por visión."""
    model, personas, X, Y, Z, _, _ = _construir_modelo(puzzle_data)
    sospechosos = puzzle_data["sospechosos"]
    victima = puzzle_data["victima"]

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        posiciones = {}
        for i, p in enumerate(personas):
            posiciones[p] = {
                "fila": solver.Value(X[i]),
                "columna": solver.Value(Y[i]),
                "habitacion": solver.Value(Z[i])
            }

        victima_hab = posiciones[victima]["habitacion"]
        asesino = None
        for s in sospechosos:
            if posiciones[s]["habitacion"] == victima_hab:
                asesino = s
                break

        return {
            "exito": True,
            "posiciones": posiciones,
            "victima": victima,
            "asesino": asesino,
            "tiempo_ms": solver.WallTime() * 1000
        }

    return {"exito": False, "mensaje": "No se encontró solución factible."}


class _ContadorSoluciones(cp_model.CpSolverSolutionCallback):
    """Guarda hasta 'limite' soluciones y detiene la búsqueda."""

    def __init__(self, personas, X, Y, limite):
        super().__init__()
        self._personas, self._X, self._Y = personas, X, Y
        self._limite = limite
        self.soluciones = []

    def on_solution_callback(self):
        self.soluciones.append({
            p: (self.Value(self._X[i]), self.Value(self._Y[i]))
            for i, p in enumerate(self._personas)
        })
        if len(self.soluciones) >= self._limite:
            self.StopSearch()


def contar_soluciones(puzzle_data, limite=2):
    """
    Enumera hasta 'limite' soluciones distintas del puzzle.
    Un acertijo bien planteado devuelve exactamente 1 (solución única).
    """
    model, personas, X, Y, _, _, _ = _construir_modelo(puzzle_data)
    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True
    callback = _ContadorSoluciones(personas, X, Y, limite)
    solver.Solve(model, callback)
    return callback.soluciones


def _modelo_con_colocaciones(puzzle_data, colocaciones, reificar=False):
    """
    Modelo con las ubicaciones del jugador ({persona: (fila, columna)}).
    Devuelve (modelo, literales, marcas, celda, idx); 'marcas' es [(persona, (r, c), BoolVar)].
    Las marcas NO se fuerzan: quien llama decide si las usa como supuestos o las fija.
    """
    modelo, personas, _, _, _, celda, literales = _construir_modelo(puzzle_data, reificar=reificar)
    idx = {n: i for i, n in enumerate(personas)}
    marcas = []
    for nombre, (r, c) in colocaciones.items():
        if nombre not in idx:
            raise ValueError(f"Persona desconocida en las ubicaciones: {nombre}")
        marcas.append((nombre, (r, c), celda[(idx[nombre], r, c)]))
    return modelo, literales, marcas, celda, idx


def diagnosticar_conflicto(puzzle_data, colocaciones):
    """
    Comprueba si las ubicaciones del jugador son compatibles con todas las pistas.

    Las pistas (reificadas) y las ubicaciones se pasan como supuestos: si el modelo es
    infactible, CP-SAT devuelve un subconjunto de supuestos que ya basta para la contradicción.
    Devuelve {"consistente": bool, "personas": [...], "pistas": [pista, ...]}.
    """
    modelo, literales, marcas, _, _ = _modelo_con_colocaciones(puzzle_data, colocaciones, reificar=True)
    modelo.AddAssumptions([lit for _, lit in literales] + [m for _, _, m in marcas])

    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    if solver.Solve(modelo) != cp_model.INFEASIBLE:
        return {"consistente": True, "personas": [], "pistas": []}

    nucleo = set(solver.SufficientAssumptionsForInfeasibility())
    return {
        "consistente": False,
        "personas": [nombre for nombre, _, m in marcas if m.Index() in nucleo],
        "pistas": [pista for pista, lit in literales if lit.Index() in nucleo],
    }


def celdas_factibles(puzzle_data, persona, colocaciones, candidatas=None):
    """
    Celdas donde 'persona' puede estar en alguna solución que respete todas las pistas y las
    ubicaciones del jugador. 'candidatas' acota las celdas a probar (una resolución por celda).
    """
    N = puzzle_data["N"]
    candidatas = candidatas if candidatas is not None else [(r, c) for r in range(N) for c in range(N)]
    otras = {n: pos for n, pos in colocaciones.items() if n != persona}
    modelo, _, marcas, celda, idx = _modelo_con_colocaciones(puzzle_data, otras)
    for _, _, m in marcas:
        modelo.Add(m == 1)

    factibles = []
    for r, c in candidatas:
        modelo.ClearAssumptions()
        modelo.AddAssumption(celda[(idx[persona], r, c)])
        solver = cp_model.CpSolver()
        solver.parameters.num_workers = 1
        if solver.Solve(modelo) in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            factibles.append((r, c))
    return factibles
