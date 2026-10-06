"""Tests del catálogo de casos y de la validez del dataset."""

import re

import pytest

import src.catalogo as catalogo
from src.solver import contar_soluciones

CASOS = catalogo.cargar_catalogo()


def test_hay_diez_casos_con_ids_y_archivos_estandar():
    assert len(CASOS) == 10
    assert [c["id"] for c in CASOS] == [f"caso_{i:02d}" for i in range(1, 11)]
    for c in CASOS:
        assert re.fullmatch(r"caso_\d{2}\.png", c["archivo"])
        assert c["archivo"] == f"{c['id']}.png"


def test_el_dataset_mezcla_grillas_6x6_y_8x8():
    assert {c["N"] for c in CASOS} == {6, 8}


@pytest.mark.parametrize("caso", CASOS, ids=lambda c: c["id"])
def test_cada_caso_tiene_solucion_unica_y_culpable_esperado(caso):
    puzzle = catalogo.puzzle_desde_caso(caso)
    assert puzzle["no_reconocidas"] == []
    soluciones = contar_soluciones(puzzle, limite=2)
    assert len(soluciones) == 1
    assert soluciones[0] == {n: tuple(v) for n, v in caso["solucion"].items()}

    sala = lambda p: puzzle["habitaciones"][soluciones[0][p]]
    culpables = [s for s in puzzle["sospechosos"] if sala(s) == sala(puzzle["victima"])]
    assert culpables == [caso["culpable"]]


def test_disponible_depende_de_que_exista_la_imagen(tmp_path, monkeypatch):
    monkeypatch.setattr(catalogo, "DIR_IMAGENES", tmp_path)
    caso = catalogo.obtener_caso("caso_04")
    assert not catalogo.resumen_caso(caso)["disponible"]

    (tmp_path / caso["archivo"]).write_bytes(b"png")
    resumen = catalogo.resumen_caso(caso)
    assert resumen["disponible"]
    assert resumen["url_imagen"] == "/casos/caso_04.png"
    assert resumen["grid"] == "6x6"


def test_caso_desconocido():
    with pytest.raises(KeyError):
        catalogo.obtener_caso("caso_99")
