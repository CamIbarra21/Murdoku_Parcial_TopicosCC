"""Tests del tutor: pistas deterministas del solver y guardia contra texto inventado del LLM."""

import re

import pytest

from src.agent import reformular_pista, respuesta_es_fiel
from src.catalogo import obtener_caso, puzzle_desde_caso
from src.solver import celdas_factibles, diagnosticar_conflicto
from src.tutor import candidatas_por_reglas, proxima_pista, validar_jugada


@pytest.fixture(scope="module")
def oficina():
    caso = obtener_caso("caso_02")
    sol = {n: tuple(v) for n, v in caso["solucion"].items()}
    return puzzle_desde_caso(caso), sol


def test_sin_ubicaciones_no_hay_conflicto(oficina):
    puzzle, _ = oficina
    assert diagnosticar_conflicto(puzzle, {})["consistente"]


def test_ubicaciones_correctas_son_consistentes(oficina):
    puzzle, sol = oficina
    parcial = dict(list(sol.items())[:4])
    assert diagnosticar_conflicto(puzzle, parcial)["consistente"]


def test_el_conflicto_senala_la_pista_reificada_responsable(oficina):
    puzzle, _ = oficina
    # Diana debe sentarse en una silla; (1,0) no lo es
    diag = diagnosticar_conflicto(puzzle, {"Diana": (1, 0)})
    assert not diag["consistente"]
    assert diag["personas"] == ["Diana"]
    assert {"tipo": "sobre_objeto", "persona": "Diana", "objeto": "sillas"} in diag["pistas"]


def test_dos_personas_en_la_misma_fila_es_conflicto(oficina):
    puzzle, sol = oficina
    mal = {"Diana": sol["Diana"], "Gabriel": (sol["Diana"][0], 5)}
    assert not diagnosticar_conflicto(puzzle, mal)["consistente"]


def test_celdas_factibles_coincide_con_la_solucion_unica(oficina):
    puzzle, sol = oficina
    assert celdas_factibles(puzzle, "Diana", {}) == [sol["Diana"]]


def test_las_reglas_simples_nunca_descartan_la_casilla_real(oficina):
    puzzle, sol = oficina
    for persona, pos in sol.items():
        otras = {n: p for n, p in sol.items() if n != persona}
        assert pos in candidatas_por_reglas(puzzle, persona, otras)


@pytest.mark.parametrize("nivel", [1, 2])
def test_los_primeros_niveles_no_revelan_casillas(oficina, nivel):
    puzzle, _ = oficina
    pista = proxima_pista(puzzle, {}, nivel)
    assert pista["tipo"] == "pista"
    assert not re.search(r"fila \d+, columna \d+", pista["mensaje"])
    assert pista["candidatas"] is None


def test_el_nivel_3_lista_solo_casillas_factibles(oficina):
    puzzle, sol = oficina
    pista = proxima_pista(puzzle, {}, 3)
    assert pista["candidatas"]
    assert tuple(sol[pista["persona"]]) in {tuple(c) for c in pista["candidatas"]}


def test_la_pista_no_apunta_a_una_persona_ya_ubicada(oficina):
    puzzle, sol = oficina
    ubicadas = dict(list(sol.items())[:3])
    pista = proxima_pista(puzzle, ubicadas, 1)
    assert pista["persona"] not in ubicadas


def test_con_un_error_la_pista_es_un_aviso_de_conflicto(oficina):
    puzzle, _ = oficina
    pista = proxima_pista(puzzle, {"Diana": (1, 0)}, 1)
    assert pista["tipo"] == "conflicto"
    assert "Diana" in pista["mensaje"]


def test_validar_parcial_conflicto_y_resuelto(oficina):
    puzzle, sol = oficina
    assert validar_jugada(puzzle, dict(list(sol.items())[:2]))["estado"] == "parcial"
    assert validar_jugada(puzzle, {"Diana": (1, 0)})["estado"] == "conflicto"
    final = validar_jugada(puzzle, sol)
    assert final["estado"] == "resuelto" and final["asesino"] == "Carlos"


def test_validar_no_revela_la_solucion(oficina):
    puzzle, sol = oficina
    msg = validar_jugada(puzzle, dict(list(sol.items())[:2]))["mensaje"]
    assert not re.search(r"fila \d+", msg)


# ---------------- guardia del LLM ----------------
NOMBRES = ["Ana", "Beto", "Cata"]


def test_respuesta_fiel_acepta_reformulaciones_sin_datos_nuevos():
    original = "Fíjate en Ana: «Ella estaba en la columna 2». ¿Qué casillas descarta?"
    assert respuesta_es_fiel(original, "Detective, observa a Ana: «Ella estaba en la columna 2». ¿Qué casillas descarta?", NOMBRES)


def test_respuesta_que_pierde_la_cita_o_los_datos_se_rechaza():
    original = "Fíjate en Ana: «Ella estaba en la columna 2». ¿Qué casillas descarta?"
    assert not respuesta_es_fiel(original, "Buenas noticias, tenemos una pista sobre Ana.", NOMBRES)
    assert not respuesta_es_fiel("Ana solo cabe en 2 casillas.", "Ana solo cabe en pocas casillas.", NOMBRES)


def test_respuesta_con_numeros_nuevos_se_rechaza():
    original = "Ana solo cabe en 2 casillas."
    assert not respuesta_es_fiel(original, "Ana está en la fila 5, columna 3.", NOMBRES)


def test_respuesta_que_nombra_a_otra_persona_se_rechaza():
    original = "Fíjate en Ana y en su columna."
    assert not respuesta_es_fiel(original, "Fíjate en Ana; creo que Beto es el asesino.", NOMBRES)


def test_sin_ollama_se_usa_el_mensaje_determinista(monkeypatch):
    import requests

    def sin_servidor(*a, **k):
        raise requests.ConnectionError("sin Ollama")

    monkeypatch.setattr(requests, "post", sin_servidor)
    assert reformular_pista("Mensaje base.", NOMBRES) == ("Mensaje base.", "solver")


def test_si_el_llm_inventa_se_conserva_el_mensaje_del_solver(monkeypatch):
    import requests

    class Falsa:
        def raise_for_status(self): pass
        def json(self): return {"response": "Ana está en la fila 4, columna 4."}

    monkeypatch.setattr(requests, "post", lambda *a, **k: Falsa())
    assert reformular_pista("Fíjate en Ana.", NOMBRES) == ("Fíjate en Ana.", "solver")


def test_respuesta_con_razonamiento_extra_se_rechaza():
    original = "Fíjate en Ana: «Ella estaba en la columna 2». ¿Qué casillas descarta?"
    inventado = ("Buenas tardes, amigo. Fíjate en Ana: «Ella estaba en la columna 2». Esto significa que la silla "
                 "de la Gerencia se puede descartar porque Ana la ocupaba y por eso nadie más puede sentarse allí. "
                 "¿Qué otras casillas descartarías?")
    assert not respuesta_es_fiel(original, inventado, NOMBRES)
