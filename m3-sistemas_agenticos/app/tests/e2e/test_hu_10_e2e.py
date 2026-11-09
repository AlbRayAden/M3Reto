"""Pruebas E2E para HU-10: solicitudes de vacaciones."""

import uuid

import httpx
from playwright.sync_api import expect


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


def _abrir_formulario(page, url_web, empleado_id: int) -> None:
    page.goto(url_web)
    boton = page.get_by_test_id(f"vacaciones-abrir-{empleado_id}")
    expect(boton).to_be_visible()
    boton.click()


def _enviar_solicitud(page, fecha_inicio: str, fecha_fin: str) -> None:
    page.get_by_test_id("vacaciones-fecha-inicio").fill(fecha_inicio)
    page.get_by_test_id("vacaciones-fecha-fin").fill(fecha_fin)
    page.get_by_test_id("vacaciones-enviar").click()


def test_ce_01_camino_feliz_descontando_festivos_y_fines_de_semana(page, url_web, url_api):
    """CE-01: Camino feliz - se registra la solicitud descontando festivos y fines de semana."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("ce01"), fecha_ingreso="2024-01-10")

    _abrir_formulario(page, url_web, empleado["id"])
    _enviar_solicitud(page, "2026-09-14", "2026-09-18")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 4 días hábiles. Te quedan 8 días hábiles en 2026."
    )


def test_ce_02_consultar_saldo_del_anio_tras_registrar_una_solicitud(page, url_web, url_api):
    """CE-02: Camino feliz - consultar el saldo del año tras registrar una solicitud."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("ce02"), fecha_ingreso="2024-01-10")
    _registrar_vacacion(url_api, empleado["id"], "2026-12-21", "2026-12-31")

    _abrir_formulario(page, url_web, empleado["id"])

    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("4")


def test_ce_03_error_pasarse_del_tope_por_un_solo_dia_habil(page, url_web, url_api):
    """CE-03: Regla 2 (error) - pasarse del tope por un solo día hábil."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("ce03"), fecha_ingreso="2024-01-10")
    _registrar_vacacion(url_api, empleado["id"], "2026-04-06", "2026-04-09")

    _abrir_formulario(page, url_web, empleado["id"])
    _enviar_solicitud(page, "2026-08-03", "2026-08-13")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "La solicitud excede los días disponibles: quedan 8 días hábiles"
    )


def test_ce_04_error_le_falta_un_dia_para_la_antiguedad(page, url_web, url_api):
    """CE-04: Regla 1 (error) - le falta un día para cumplir el año de antigüedad."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("ce04"), fecha_ingreso="2025-12-21")

    _abrir_formulario(page, url_web, empleado["id"])
    _enviar_solicitud(page, "2026-12-20", "2026-12-20")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_ce_05_error_fecha_fin_anterior_a_fecha_inicio(page, url_web, url_api):
    """CE-05: Error - la fecha de fin es anterior a la fecha de inicio."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("ce05"), fecha_ingreso="2024-01-10")

    _abrir_formulario(page, url_web, empleado["id"])
    _enviar_solicitud(page, "2026-07-10", "2026-07-05")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_ce_06_error_el_periodo_cruza_de_un_anio_calendario_a_otro(page, url_web, url_api):
    """CE-06: Error - el periodo cruza de un año calendario a otro."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("ce06"), fecha_ingreso="2024-01-10")

    _abrir_formulario(page, url_web, empleado["id"])
    _enviar_solicitud(page, "2026-12-28", "2027-01-08")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_ce_07_error_periodo_completo_en_fin_de_semana(page, url_web, url_api):
    """CE-07: Regla 3 (error) - el periodo cae completo en fin de semana y no tiene días hábiles."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("ce07"), fecha_ingreso="2024-01-10")

    _abrir_formulario(page, url_web, empleado["id"])
    _enviar_solicitud(page, "2026-07-11", "2026-07-12")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "El periodo no incluye días hábiles"
    )


def test_ce_08_limite_usar_exactamente_los_dias_habiles_que_quedan(page, url_web, url_api):
    """CE-08: Regla 2 (límite) - usar exactamente los días hábiles que quedan en el año."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("ce08"), fecha_ingreso="2024-01-10")
    _registrar_vacacion(url_api, empleado["id"], "2026-06-01", "2026-06-05")

    _abrir_formulario(page, url_web, empleado["id"])
    _enviar_solicitud(page, "2026-07-13", "2026-07-21")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 7 días hábiles. Te quedan 0 días hábiles en 2026."
    )
