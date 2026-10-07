"""Tests del parser de testimonios (sin visión ni Ollama)."""

import pytest

from src.parser_pistas import construir_pistas, parsear_oracion

SALAS = [
    {"id": 1, "nombre": "Gerencia"},
    {"id": 2, "nombre": "Archivo"},
    {"id": 3, "nombre": "Sala de Lectura", "alias": ["Lectura"]},
]
PERSONAS = ["Felipe", "Carlos", "Diana", "David"]


def parsear(oracion, persona="Felipe", N=6):
    pistas, ok = parsear_oracion(oracion, persona, PERSONAS, SALAS, N)
    return pistas, ok


@pytest.mark.parametrize("texto, indice", [
    ("Ella estaba en la primera columna.", 0),
    ("Ella estaba en la tercera columna.", 2),
    ("Ella estaba en la sexta columna.", 5),
    ("Ella estaba en la última columna.", 5),
])
def test_columna_ordinal_es_indice_cero(texto, indice):
    pistas, ok = parsear(texto)
    assert ok
    assert pistas == [{"tipo": "columna_fija", "persona": "Felipe", "columna": indice}]


def test_ultima_fila_depende_del_tamano_del_tablero():
    pistas, _ = parsear("Él estaba en la última fila.", N=8)
    assert pistas[0] == {"tipo": "fila_fija", "persona": "Felipe", "fila": 7}


def test_adyacencia_y_negacion():
    assert parsear("Él estaba al lado de una laptop.")[0] == [
        {"tipo": "adyacente_a", "persona": "Felipe", "objeto": "computadora"}]
    assert parsear("Él no estaba al lado de una mesa.")[0] == [
        {"tipo": "no_adyacente_a", "persona": "Felipe", "objeto": "mesas"}]


def test_silla_sentado_y_negacion():
    assert parsear("Ella estaba sentada en una silla.")[0][0]["tipo"] == "sobre_objeto"
    assert parsear("Él no estaba sentado en una silla.")[0][0]["tipo"] == "no_sobre_objeto"
    assert parsear("Él no estaba en una silla.")[0][0]["tipo"] == "no_sobre_objeto"


def test_direccion_relativa_resuelve_el_destino():
    pistas, _ = parsear("Él estaba al sur de Carlos.")
    assert pistas == [{"tipo": "direccion_relativa", "origen": "Felipe",
                       "destino": "Carlos", "direccion": "sur"}]


def test_destino_con_ruido_de_ocr():
    pistas, _ = parsear("Él estaba al norte de Carlcs.")  # OCR erró una letra
    assert pistas[0]["destino"] == "Carlos"


def test_sala_por_nombre_y_alias_con_tildes_y_mayusculas():
    assert parsear("Él estaba en la GERENCIA.")[0] == [
        {"tipo": "habitacion_fija", "persona": "Felipe", "habitacion": 1}]
    assert parsear("Ella estaba en Lectura.")[0][0]["habitacion"] == 3
    assert parsear("Ella estaba en la Sala de Lectura.")[0][0]["habitacion"] == 3


def test_oracion_compuesta_produce_varias_pistas():
    pistas, _ = parsear("Ella estaba sentada en una silla en la Gerencia.", "Diana")
    assert {p["tipo"] for p in pistas} == {"sobre_objeto", "habitacion_fija"}


def test_frase_desconocida_no_se_reconoce():
    pistas, ok = parsear("Él estaba bailando bajo la lluvia.")
    assert pistas == [] and not ok


def test_construir_pistas_detecta_victima_aunque_el_ocr_la_deforme():
    tarjetas = [
        {"nombre": "Felipe", "texto": "Él estaba en la tercera columna."},
        {"nombre": "Carlos", "texto": "Él estaba en la primera fila."},
        {"nombre": "Diana", "texto": "Ella estaba en la Gerencia."},
        {"nombre": "Elena", "texto": "Ella estaba en el Archivo."},
        {"nombre": "Gabriel", "texto": "Él estaba al sur de Carlos."},
        {"nombre": "David", "texto": "La Víctica. Hallado en el Archivo, solo con el asesino."},
    ]
    sospechosos, victima, pistas, no_reconocidas = construir_pistas(tarjetas, SALAS, 6, usar_llm=False)
    assert victima == "David"
    assert sospechosos == ["Felipe", "Carlos", "Diana", "Elena", "Gabriel"]
    assert no_reconocidas == []
    assert {"tipo": "habitacion_fija", "persona": "David", "habitacion": 2} in pistas


def test_construir_pistas_reporta_frases_sin_interpretar():
    tarjetas = [{"nombre": n, "texto": "Él estaba en la primera columna."} for n in "ABCDE"]
    tarjetas.append({"nombre": "F", "texto": "La Víctima. Algo incomprensible."})
    *_, no_reconocidas = construir_pistas(tarjetas, SALAS, 6, usar_llm=False)
    assert no_reconocidas == [("F", "Algo incomprensible.")]
