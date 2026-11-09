"""Punto de entrada de la API de gestión de empleados."""

from fastapi import FastAPI

from database import Base, engine
from routers import empleados

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestión de empleados")

app.include_router(empleados.router)


@app.get("/api/salud")
def salud() -> dict[str, str]:
    return {"estado": "ok"}
