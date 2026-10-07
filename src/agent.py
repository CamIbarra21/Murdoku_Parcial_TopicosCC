"""
Agente redactor del tutor de Murdoku.

El solver decide QUÉ pista dar (src/tutor.py). Este módulo solo le pide a un LLM local
(Ollama) que reformule ese mensaje con un tono de detective, y descarta cualquier respuesta
que agregue información: nombres o números que no estaban en el mensaje original.
Si Ollama no responde o el texto se rechaza, se devuelve el mensaje determinista.
"""

import re

import requests

URL_OLLAMA = "http://localhost:11434/api/generate"


def _numeros(texto: str) -> set:
    return set(re.findall(r"\d+", texto))


def _oraciones(texto: str) -> int:
    return len([o for o in re.split(r"[.!?¿¡]+", texto) if o.strip()])


def respuesta_es_fiel(original: str, reformulado: str, nombres: list) -> bool:
    """
    El texto reformulado debe decir lo mismo que el original: conserva todos sus números,
    nombres y citas textuales («...») y no agrega números ni nombres nuevos. Así no se filtran
    posiciones o culpables ni se pierden los datos que el jugador necesita.
    """
    if not reformulado.strip():
        return False
    if _numeros(reformulado) != _numeros(original):
        return False
    original_min, reformulado_min = original.lower(), reformulado.lower()
    for nombre in nombres:
        if (nombre.lower() in original_min) != (nombre.lower() in reformulado_min):
            return False
    citas = re.findall(r"«(.+?)»", original)
    if not all(cita.lower() in reformulado_min for cita in citas):
        return False
    # Una reescritura fiel no agrega razonamiento: cabe en poco más que el original
    if len(reformulado) > 1.35 * len(original) + 40:
        return False
    return _oraciones(reformulado) <= _oraciones(original) + 1


def reformular_pista(mensaje: str, nombres: list, modelo: str = "llama3.2:3b") -> tuple:
    """
    Devuelve (texto, fuente) con fuente "solver+llm" si el LLM reformuló con éxito o
    "solver" si se usa el mensaje determinista original.
    """
    prompt = f"""Eres el "Detective Tutor" de un juego de lógica llamado Murdoku.
Reescribe el siguiente mensaje con tono de detective amable, en español, con un saludo muy corto y sin explicaciones adicionales.
REGLAS: no agregues datos, deducciones, nombres ni números nuevos; conserva todos los que aparecen
y copia sin cambios cualquier texto entre «»;
no digas quién es el asesino; si hay una pregunta, déjala como pregunta.

MENSAJE:
{mensaje}

REESCRITURA:"""
    try:
        r = requests.post(URL_OLLAMA, timeout=25, json={
            "model": modelo, "prompt": prompt, "stream": False, "options": {"temperature": 0.2}})
        r.raise_for_status()
        texto = r.json()["response"].strip()
    except Exception:
        return mensaje, "solver"

    if respuesta_es_fiel(mensaje, texto, nombres):
        return texto, "solver+llm"
    return mensaje, "solver"
