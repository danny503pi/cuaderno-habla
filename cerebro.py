import json

from google.genai import Client, types
from pydantic import ValidationError

from modelos import Apunte


MODELO = "gemini-3.8-flash"
INSTRUCCION_SISTEMA = (
    "Actuá como un profesor paciente de bachillerato de El Salvador. "
    "Escribí siempre en español salvadoreño claro. Basate únicamente en lo que "
    "se ve en la imagen y no inventés temas. Si la foto está borrosa, decilo en "
    "el resumen en vez de inventar. Hacé que las opciones incorrectas del "
    "examen sean creíbles, no absurdas, y variá la posición de la respuesta "
    "correcta entre las preguntas."
)


class ImagenIlegible(Exception):
    """La página no se pudo interpretar como un apunte válido."""


def crear_cliente(api_key: str) -> Client:
    if not api_key or not api_key.strip():
        raise ValueError("La llave de la API no puede estar vacía.")
    return Client(api_key=api_key)


def analizar_pagina(datos_imagen: bytes, tipo_mime: str, cliente: Client) -> Apunte:
    if not datos_imagen:
        raise ValueError("Tenés que proporcionar una imagen para analizar.")

    respuesta = cliente.models.generate_content(
        model=MODELO,
        contents=[
            types.Part.from_bytes(data=datos_imagen, mime_type=tipo_mime),
            "Analizá esta página y prepará un apunte para estudiar.",
        ],
        config=types.GenerateContentConfig(
            system_instruction=INSTRUCCION_SISTEMA,
            response_mime_type="application/json",
            response_schema=Apunte,
            temperature=0.4,
        ),
    )

    parsed = respuesta.parsed
    if isinstance(parsed, Apunte):
        return parsed
    if parsed is not None:
        try:
            return Apunte.model_validate(parsed)
        except (TypeError, ValidationError):
            pass

    texto = respuesta.text
    if texto:
        try:
            return Apunte.model_validate(json.loads(texto))
        except (json.JSONDecodeError, TypeError, ValidationError):
            pass

    raise ImagenIlegible(
        "No pudimos leer bien esta página. Probá con una foto más clara, "
        "enfocada y con buena iluminación."
    )


def calificar(apunte: Apunte, respuestas: dict) -> tuple[int, int]:
    aciertos = sum(
        respuestas.get(indice, respuestas.get(str(indice))) == pregunta.correcta
        for indice, pregunta in enumerate(apunte.examen)
    )
    return aciertos, len(apunte.examen)
