"""Pruebas de API para HU-10: solicitudes de vacaciones."""

import uuid

import httpx
import pytest


def _correo_unico(prefijo: str) -> str:
    return f"{prefijo}.{uuid.uuid4().hex}@empresa.com"


def _crear_empleado(url_api, **sobrescritos) -> dict:
    datos = {
        "nombre": "Empleado de Prueba",
        "correo": _correo_unico("empleado"),
        "puesto": "Analista de Pruebas",
        "departamento": "Tecnología",
        "fecha_ingreso": "2024-01-15",
    }
    datos.update(sobrescritos)
    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)
    assert respuesta.status_code == 201
    return respuesta.json()


def _registrar_vacacion(url_api, empleado_id: int, fecha_inicio: str, fecha_fin: str) -> dict:
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado_id}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def test_cp_01_camino_feliz_descontando_festivos_y_fines_de_semana(url_api):
    """CP-01: Camino feliz - se registra la solicitud descontando festivos y fines de semana."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp01"), fecha_ingreso="2024-01-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-09-14", "fecha_fin": "2026-09-18"},
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 4
    assert cuerpo["dias_restantes"] == 8


def test_cp_02_consultar_saldo_del_anio_tras_registrar_una_solicitud(url_api):
    """CP-02: Camino feliz - consultar el saldo del año tras registrar una solicitud."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp02"), fecha_ingreso="2024-01-10")
    _registrar_vacacion(url_api, empleado["id"], "2026-12-21", "2026-12-31")

    respuesta = httpx.get(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones", params={"anio": 2026}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["empleado_id"] == empleado["id"]
    assert cuerpo["anio"] == 2026
    assert cuerpo["dias_usados"] == 8
    assert cuerpo["dias_disponibles"] == 4
    solicitudes = cuerpo["solicitudes"]
    assert len(solicitudes) == 1
    assert solicitudes[0]["fecha_inicio"] == "2026-12-21"
    assert solicitudes[0]["fecha_fin"] == "2026-12-31"
    assert solicitudes[0]["dias_habiles"] == 8


def test_cp_03_limite_usar_exactamente_los_dias_habiles_que_quedan(url_api):
    """CP-03: Regla 2 (límite) - usar exactamente los días hábiles que quedan en el año."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp03"), fecha_ingreso="2024-01-10")
    _registrar_vacacion(url_api, empleado["id"], "2026-06-01", "2026-06-05")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-13", "fecha_fin": "2026-07-21"},
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 7
    assert cuerpo["dias_restantes"] == 0


def test_cp_04_error_pasarse_del_tope_por_un_solo_dia_habil(url_api):
    """CP-04: Regla 2 (error) - pasarse del tope por un solo día hábil."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp04"), fecha_ingreso="2024-01-10")
    _registrar_vacacion(url_api, empleado["id"], "2026-04-06", "2026-04-09")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-08-03", "fecha_fin": "2026-08-13"},
    )

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 8 días hábiles"
    )


def test_cp_05_error_el_tope_del_anio_ya_esta_agotado(url_api):
    """CP-05: Regla 2 (error) - el tope del año ya está agotado."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp05"), fecha_ingreso="2024-01-10")
    _registrar_vacacion(url_api, empleado["id"], "2026-06-01", "2026-06-16")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-10-05", "fecha_fin": "2026-10-05"},
    )

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 0 días hábiles"
    )


def test_cp_06_limite_cumple_exactamente_un_anio_de_antiguedad(url_api):
    """CP-06: Regla 1 (límite) - cumple exactamente un año de antigüedad el día de inicio."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp06"), fecha_ingreso="2025-12-21")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-21"},
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 1
    assert cuerpo["dias_restantes"] == 11


def test_cp_07_error_le_falta_un_dia_para_la_antiguedad(url_api):
    """CP-07: Regla 1 (error) - le falta un día para cumplir el año de antigüedad."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp07"), fecha_ingreso="2025-12-21")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-12-20", "fecha_fin": "2026-12-20"},
    )

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp_08_error_periodo_completo_en_fin_de_semana(url_api):
    """CP-08: Regla 3 (error) - el periodo cae completo en fin de semana y no tiene días hábiles."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp08"), fecha_ingreso="2024-01-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-11", "fecha_fin": "2026-07-12"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp_09_error_fecha_fin_anterior_a_fecha_inicio(url_api):
    """CP-09: Error - la fecha de fin es anterior a la fecha de inicio."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp09"), fecha_ingreso="2024-01-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-10", "fecha_fin": "2026-07-05"},
    )

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"] == "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp_10_error_el_periodo_cruza_de_un_anio_calendario_a_otro(url_api):
    """CP-10: Error - el periodo cruza de un año calendario a otro."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp10"), fecha_ingreso="2024-01-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-12-28", "fecha_fin": "2027-01-08"},
    )

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp_11_error_el_anio_no_esta_en_la_tabla_de_festivos(url_api):
    """CP-11: Error - el año solicitado no está en la tabla de festivos."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp11"), fecha_ingreso="2024-01-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2028-01-10", "fecha_fin": "2028-01-14"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Solo se pueden solicitar vacaciones en 2026 y 2027"


def test_cp_12_error_el_empleado_no_existe(url_api):
    """CP-12: Error - el empleado no existe."""
    respuesta = httpx.post(
        f"{url_api}/api/empleados/9999/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


@pytest.mark.skip(
    reason=(
        "CP-13 necesita un empleado con estado 'baja' como precondición, pero "
        "la API no expone ningún endpoint para dar de baja a un empleado "
        "(funcionalidad de una historia aparte, aún no implementada). No se "
        "puede crear esa precondición por la API."
    )
)
def test_cp_13_error_el_empleado_esta_dado_de_baja(url_api):
    """CP-13: Error - el empleado está dado de baja."""
