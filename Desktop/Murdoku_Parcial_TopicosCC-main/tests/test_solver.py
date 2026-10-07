"""Tests del modelo CP-SAT (sin visión)."""

import pytest

from src.catalogo import obtener_caso, puzzle_desde_caso
from src.solver import contar_soluciones, resolver_murdoku


def puzzle_minimo(pistas, muebles=None):
    """Tablero 3x3, dos salas (fila 0 / filas 1-2), 2 sospechosos y 1 víctima."""
    return {
        "N": 3,
        "sospechosos": ["Ana", "Beto"],
        "victima": "Cata",
        "habitaciones": {(r, c): (1 if r == 0 else 2) for r in range(3) for c in range(3)},
        "muebles": muebles or {},
        "pistas": pistas,
        "obstaculos": ["mesas", "plantas", "computadora"],
    }


def test_un_puzzle_sin_pistas_tiene_varias_soluciones():
    assert len(contar_soluciones(puzzle_minimo([]), limite=2)) == 2


def test_nadie_comparte_fila_ni_columna():
    r = resolver_murdoku(puzzle_minimo([]))
    pos = list(r["posiciones"].values())
    assert len({p["fila"] for p in pos}) == 3
    assert len({p["columna"] for p in pos}) == 3


def test_pistas_fijan_la_posicion():
    pistas = [
        {"tipo": "columna_fija", "persona": "Ana", "columna": 0},
        {"tipo": "fila_fija", "persona": "Ana", "fila": 1},
    ]
    r = resolver_murdoku(puzzle_minimo(pistas))
    assert (r["posiciones"]["Ana"]["fila"], r["posiciones"]["Ana"]["columna"]) == (1, 0)


def test_direccion_relativa():
    pistas = [{"tipo": "direccion_relativa", "origen": "Ana", "destino": "Beto", "direccion": "norte"}]
    for sol in contar_soluciones(puzzle_minimo(pistas), limite=10):
        assert sol["Ana"][0] < sol["Beto"][0]


def test_la_victima_solo_comparte_sala_con_el_asesino():
    for sol in contar_soluciones(puzzle_minimo([]), limite=20):
        sala = lambda p: 1 if sol[p][0] == 0 else 2
        if sala("Cata") == sala("Ana") == sala("Beto"):
            pytest.fail("dos sospechosos comparten sala con la víctima")


def test_nadie_pisa_obstaculos():
    muebles = {"mesas": [(0, 0), (1, 1), (2, 2)]}
    for sol in contar_soluciones(puzzle_minimo([], muebles), limite=20):
        assert all(pos not in muebles["mesas"] for pos in sol.values())


def test_tipo_de_pista_desconocido_lanza_error():
    with pytest.raises(ValueError, match="desconocido"):
        resolver_murdoku(puzzle_minimo([{"tipo": "teletransporte", "persona": "Ana"}]))


def test_persona_desconocida_lanza_error():
    with pytest.raises(ValueError, match="persona desconocida"):
        resolver_murdoku(puzzle_minimo([{"tipo": "columna_fija", "persona": "Zoe", "columna": 0}]))


def test_sobre_objeto_sin_muebles_es_infactible():
    r = resolver_murdoku(puzzle_minimo([{"tipo": "sobre_objeto", "persona": "Ana", "objeto": "sillas"}]))
    assert not r["exito"]


def test_la_tienda_se_resuelve_con_el_culpable_esperado():
    caso = obtener_caso("caso_01")
    r = resolver_murdoku(puzzle_desde_caso(caso))
    assert r["exito"] and r["asesino"] == "Barbara"
