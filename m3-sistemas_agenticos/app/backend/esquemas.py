"""Esquemas Pydantic de la aplicación de empleados."""

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from catalogos import DEPARTAMENTOS_VALIDOS


class EmpleadoCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    correo: str = Field(min_length=1)
    puesto: str = Field(min_length=2, max_length=60)
    departamento: str
    fecha_ingreso: str = Field(min_length=1)

    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str) -> str:
        if valor not in DEPARTAMENTOS_VALIDOS:
            raise ValueError("Departamento fuera del catálogo")
        return valor

    @field_validator("fecha_ingreso")
    @classmethod
    def validar_formato_fecha(cls, valor: str) -> str:
        try:
            date.fromisoformat(valor)
        except ValueError as exc:
            raise ValueError("Formato de fecha inválido, usa AAAA-MM-DD") from exc
        return valor


class EmpleadoRespuesta(BaseModel):
    id: int
    numero_empleado: str
    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: str
    estado: str
    fecha_baja: str | None
    creado_en: datetime

    model_config = {"from_attributes": True}
