"""Configuración de la base de datos SQLite para la aplicación de empleados."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

CARPETA_DATOS = os.path.join(os.path.dirname(__file__), "datos")
os.makedirs(CARPETA_DATOS, exist_ok=True)

RUTA_BASE_DATOS = os.path.join(CARPETA_DATOS, "empleados.db")
URL_BASE_DATOS = f"sqlite:///{RUTA_BASE_DATOS}"

engine = create_engine(
    URL_BASE_DATOS, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
