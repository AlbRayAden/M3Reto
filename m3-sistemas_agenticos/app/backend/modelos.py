"""Modelos SQLAlchemy de la aplicación de empleados."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Empleado(Base):
    __tablename__ = "empleados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_empleado: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    correo: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    puesto: Mapped[str] = mapped_column(String(60), nullable=False)
    departamento: Mapped[str] = mapped_column(String(60), nullable=False)
    fecha_ingreso: Mapped[str] = mapped_column(String(10), nullable=False)
    estado: Mapped[str] = mapped_column(String(10), nullable=False, default="activo")
    fecha_baja: Mapped[str | None] = mapped_column(String(10), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
