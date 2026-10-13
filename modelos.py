from pydantic import BaseModel, Field, field_validator, model_validator


class Concepto(BaseModel):
    termino: str = Field(description="Término o concepto importante identificado en los apuntes.")
    explicacion: str = Field(description="Explicación clara del término, basada en el contenido de los apuntes.")


class Tarjeta(BaseModel):
    pregunta: str = Field(description="Pregunta breve para repasar un dato o concepto de los apuntes.")
    respuesta: str = Field(description="Respuesta correcta y concisa a la pregunta de repaso.")


class Pregunta(BaseModel):
    enunciado: str = Field(description="Enunciado claro de una pregunta de opción múltiple sobre los apuntes.")
    opciones: list[str] = Field(description="Lista de opciones de respuesta para la pregunta.")
    correcta: int = Field(description="Índice, empezando en cero, de la opción correcta dentro de la lista de opciones.")

    @field_validator("opciones")
    @classmethod
    def validar_opciones(cls, opciones: list[str]) -> list[str]:
        if len(opciones) != 4:
            raise ValueError(f"La pregunta debe tener exactamente cuatro opciones; se recibieron {len(opciones)}.")
        if len({opcion.casefold() for opcion in opciones}) != 4:
            raise ValueError("Las cuatro opciones deben ser distintas, sin diferencias solo de mayúsculas y minúsculas.")
        return opciones

    @model_validator(mode="after")
    def validar_indice_correcta(self) -> "Pregunta":
        if not 0 <= self.correcta < len(self.opciones):
            raise ValueError(
                f"El índice correcta debe estar entre 0 y {len(self.opciones) - 1}; "
                f"se recibió {self.correcta}."
            )
        return self


class Apunte(BaseModel):
    titulo: str = Field(description="Título breve que represente el tema principal de la página.")
    materia: str = Field(description="Nombre de la materia a la que corresponde el contenido.")
    resumen: str = Field(description="Resumen claro y fiel de las ideas principales de la página.")
    conceptos: list[Concepto] = Field(description="Lista de términos importantes de la página con sus explicaciones.")
    tarjetas: list[Tarjeta] = Field(description="Lista de tarjetas de pregunta y respuesta para estudiar el contenido.")
    examen: list[Pregunta] = Field(description="Lista de preguntas de opción múltiple basadas en los apuntes.")
    dificultad: int = Field(description="Nivel de dificultad general del contenido, expresado como un número entero.")

    @field_validator("conceptos")
    @classmethod
    def validar_cantidad_conceptos(cls, conceptos: list[Concepto]) -> list[Concepto]:
        if len(conceptos) < 3:
            raise ValueError(f"El apunte debe incluir al menos 3 conceptos; se recibieron {len(conceptos)}.")
        return conceptos

    @field_validator("tarjetas")
    @classmethod
    def validar_cantidad_tarjetas(cls, tarjetas: list[Tarjeta]) -> list[Tarjeta]:
        if len(tarjetas) < 5:
            raise ValueError(f"El apunte debe incluir al menos 5 tarjetas; se recibieron {len(tarjetas)}.")
        return tarjetas

    @field_validator("examen")
    @classmethod
    def validar_cantidad_preguntas(cls, examen: list[Pregunta]) -> list[Pregunta]:
        if len(examen) < 3:
            raise ValueError(f"El examen debe incluir al menos 3 preguntas; se recibieron {len(examen)}.")
        return examen

    @field_validator("dificultad")
    @classmethod
    def validar_dificultad(cls, dificultad: int) -> int:
        if not 1 <= dificultad <= 5:
            raise ValueError(f"La dificultad debe estar entre 1 y 5; se recibió {dificultad}.")
        return dificultad
