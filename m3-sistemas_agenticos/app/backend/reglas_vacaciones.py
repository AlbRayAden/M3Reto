"""Reglas de negocio de vacaciones (HU-10), sin dependencias de FastAPI."""

from datetime import date, timedelta

from catalogos import FESTIVOS_POR_ANIO


def anio_valido(anio: int) -> bool:
    return anio in FESTIVOS_POR_ANIO


def dias_habiles(fecha_inicio: date, fecha_fin: date) -> int:
    festivos = set()
    for anio in range(fecha_inicio.year, fecha_fin.year + 1):
        festivos.update(FESTIVOS_POR_ANIO.get(anio, []))

    total = 0
    dia = fecha_inicio
    while dia <= fecha_fin:
        if dia.weekday() < 5 and dia.isoformat() not in festivos:
            total += 1
        dia += timedelta(days=1)
    return total


def cumple_antiguedad(fecha_ingreso: date, fecha_inicio: date) -> bool:
    try:
        aniversario = fecha_ingreso.replace(year=fecha_ingreso.year + 1)
    except ValueError:
        # 29 de febrero en un año no bisiesto: el aniversario cae el 1 de marzo.
        aniversario = date(fecha_ingreso.year + 1, 3, 1)
    return fecha_inicio >= aniversario
