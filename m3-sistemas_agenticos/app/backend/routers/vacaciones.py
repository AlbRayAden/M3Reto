"""Rutas de la API para solicitudes de vacaciones (HU-10)."""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from catalogos import TOPE_DIAS_ANUAL
from database import obtener_db
from esquemas import SaldoVacacionesRespuesta, VacacionCrear, VacacionRespuesta
from modelos import Empleado, Vacacion
from reglas_vacaciones import anio_valido, cumple_antiguedad, dias_habiles

router = APIRouter(prefix="/api", tags=["vacaciones"])

# Mismo criterio que routers/empleados.py: México opera en horario del Centro
# (UTC-6) todo el año, así que se usa un desfase fijo para "hoy".
DESFASE_HORA_NEGOCIO = timedelta(hours=-6)


def _hoy() -> date:
    return (datetime.utcnow() + DESFASE_HORA_NEGOCIO).date()


def _obtener_empleado_o_404(empleado_id: int, db: Session) -> Empleado:
    empleado = db.get(Empleado, empleado_id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


def _dias_usados_en_anio(db: Session, empleado_id: int, anio: int) -> int:
    solicitudes = (
        db.query(Vacacion)
        .filter(Vacacion.empleado_id == empleado_id)
        .filter(Vacacion.fecha_inicio.like(f"{anio}-%"))
        .all()
    )
    return sum(solicitud.dias_habiles for solicitud in solicitudes)


@router.post(
    "/empleados/{empleado_id}/vacaciones",
    response_model=VacacionRespuesta,
    status_code=201,
)
def crear_vacacion(
    empleado_id: int, datos: VacacionCrear, db: Session = Depends(obtener_db)
) -> VacacionRespuesta:
    empleado = _obtener_empleado_o_404(empleado_id, db)

    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se pueden solicitar vacaciones para un empleado dado de baja",
        )

    fecha_inicio = date.fromisoformat(datos.fecha_inicio)
    fecha_fin = date.fromisoformat(datos.fecha_fin)

    if fecha_fin < fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio",
        )

    if fecha_inicio.year != fecha_fin.year:
        raise HTTPException(
            status_code=400,
            detail="Las vacaciones deben estar dentro de un mismo año calendario",
        )

    anio = fecha_inicio.year
    if not anio_valido(anio):
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden solicitar vacaciones en 2026 y 2027",
        )

    fecha_ingreso = date.fromisoformat(empleado.fecha_ingreso)
    if not cumple_antiguedad(fecha_ingreso, fecha_inicio):
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un año de antigüedad a la fecha de inicio",
        )

    habiles = dias_habiles(fecha_inicio, fecha_fin)
    if habiles == 0:
        raise HTTPException(status_code=400, detail="El periodo no incluye días hábiles")

    usados = _dias_usados_en_anio(db, empleado_id, anio)
    disponibles = TOPE_DIAS_ANUAL - usados
    if habiles > disponibles:
        raise HTTPException(
            status_code=400,
            detail=f"La solicitud excede los días disponibles: quedan {disponibles} días hábiles",
        )

    vacacion = Vacacion(
        empleado_id=empleado_id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        dias_habiles=habiles,
    )
    db.add(vacacion)
    db.commit()
    db.refresh(vacacion)

    return VacacionRespuesta(
        id=vacacion.id,
        empleado_id=vacacion.empleado_id,
        fecha_inicio=vacacion.fecha_inicio,
        fecha_fin=vacacion.fecha_fin,
        dias_habiles=vacacion.dias_habiles,
        dias_restantes=disponibles - habiles,
    )


@router.get("/empleados/{empleado_id}/vacaciones", response_model=SaldoVacacionesRespuesta)
def consultar_saldo(
    empleado_id: int, anio: int | None = None, db: Session = Depends(obtener_db)
) -> SaldoVacacionesRespuesta:
    _obtener_empleado_o_404(empleado_id, db)

    anio_consulta = anio if anio is not None else _hoy().year

    solicitudes = (
        db.query(Vacacion)
        .filter(Vacacion.empleado_id == empleado_id)
        .filter(Vacacion.fecha_inicio.like(f"{anio_consulta}-%"))
        .order_by(Vacacion.id)
        .all()
    )
    usados = sum(solicitud.dias_habiles for solicitud in solicitudes)

    return SaldoVacacionesRespuesta(
        empleado_id=empleado_id,
        anio=anio_consulta,
        dias_usados=usados,
        dias_disponibles=TOPE_DIAS_ANUAL - usados,
        solicitudes=solicitudes,
    )
