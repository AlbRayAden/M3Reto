"""Rutas de la API para el recurso de empleados."""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from catalogos import DEPARTAMENTOS_VALIDOS
from database import obtener_db
from esquemas import EmpleadoBaja, EmpleadoCrear, EmpleadoEditar, EmpleadoRespuesta
from modelos import Empleado

router = APIRouter(prefix="/api", tags=["empleados"])

# México opera en horario del Centro (UTC-6) todo el año desde la reforma de 2022
# que eliminó el horario de verano; se usa un desfase fijo para que "hoy" no
# dependa de la zona horaria configurada en el servidor donde corra la API.
DESFASE_HORA_NEGOCIO = timedelta(hours=-6)


def _hoy() -> date:
    return (datetime.utcnow() + DESFASE_HORA_NEGOCIO).date()


def _siguiente_numero_empleado(db: Session) -> str:
    total = db.query(func.count(Empleado.id)).scalar() or 0
    return f"EMP-{total + 1:04d}"


@router.post("/empleados", response_model=EmpleadoRespuesta, status_code=201)
def crear_empleado(datos: EmpleadoCrear, db: Session = Depends(obtener_db)) -> Empleado:
    correo_normalizado = datos.correo.strip().lower()

    if not correo_normalizado.endswith("@empresa.com"):
        raise HTTPException(status_code=422, detail="Usa el correo corporativo @empresa.com")

    existe = (
        db.query(Empleado)
        .filter(func.lower(Empleado.correo) == correo_normalizado)
        .first()
    )
    if existe is not None:
        raise HTTPException(status_code=409, detail="El correo ya está registrado")

    if date.fromisoformat(datos.fecha_ingreso) > _hoy():
        raise HTTPException(status_code=422, detail="La fecha de ingreso no puede ser futura")

    empleado = Empleado(
        numero_empleado=_siguiente_numero_empleado(db),
        nombre=datos.nombre,
        correo=correo_normalizado,
        puesto=datos.puesto,
        departamento=datos.departamento,
        fecha_ingreso=datos.fecha_ingreso,
        estado="activo",
        creado_en=datetime.utcnow(),
    )
    db.add(empleado)
    db.commit()
    db.refresh(empleado)
    return empleado


@router.get("/empleados", response_model=list[EmpleadoRespuesta])
def listar_empleados(
    buscar: str | None = None,
    departamento: str | None = None,
    db: Session = Depends(obtener_db),
) -> list[Empleado]:
    consulta = db.query(Empleado)

    if buscar:
        patron = f"%{buscar.lower()}%"
        consulta = consulta.filter(
            func.lower(Empleado.nombre).like(patron)
            | func.lower(Empleado.correo).like(patron)
        )

    if departamento:
        consulta = consulta.filter(Empleado.departamento == departamento)

    return consulta.order_by(Empleado.id).all()


@router.get("/departamentos", response_model=list[str])
def listar_departamentos() -> list[str]:
    return DEPARTAMENTOS_VALIDOS


@router.put("/empleados/{empleado_id}", response_model=EmpleadoRespuesta)
def editar_empleado(
    empleado_id: int, datos: EmpleadoEditar, db: Session = Depends(obtener_db)
) -> Empleado:
    empleado = db.get(Empleado, empleado_id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409, detail="No se puede editar a un empleado dado de baja"
        )

    empleado.nombre = datos.nombre
    empleado.puesto = datos.puesto
    empleado.departamento = datos.departamento
    empleado.fecha_ingreso = datos.fecha_ingreso
    db.commit()
    db.refresh(empleado)
    return empleado


@router.post("/empleados/{empleado_id}/baja", response_model=EmpleadoRespuesta)
def dar_de_baja_empleado(
    empleado_id: int, datos: EmpleadoBaja, db: Session = Depends(obtener_db)
) -> Empleado:
    empleado = db.get(Empleado, empleado_id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if date.fromisoformat(datos.fecha_baja) < date.fromisoformat(empleado.fecha_ingreso):
        raise HTTPException(
            status_code=422,
            detail="El campo fecha_baja no puede ser anterior a la fecha de ingreso",
        )

    empleado.estado = "baja"
    empleado.fecha_baja = datos.fecha_baja
    db.commit()
    db.refresh(empleado)
    return empleado
