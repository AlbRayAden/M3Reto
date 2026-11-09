"""Pruebas E2E para HU-03: editar y dar de baja a un empleado."""

import uuid

import httpx
from playwright.sync_api import expect


def _correo_unico(prefijo: str) -> str:
    return f"{prefijo}.{uuid.uuid4().hex}@empresa.com"


def _crear_empleado(url_api, **sobrescritos) -> dict:
    datos = {
        "nombre": "Ana Pérez",
        "correo": _correo_unico("ana.perez"),
        "puesto": "Analista",
        "departamento": "Ventas",
        "fecha_ingreso": "2023-05-10",
    }
    datos.update(sobrescritos)
    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_cp_02_editar_puesto_y_departamento_de_empleado_activo(page, url_web, url_api):
    """CP-02: Editar puesto y departamento de un empleado activo."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp02"))

    page.goto(url_web)
    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()
    page.get_by_test_id("empleado-puesto").fill("Analista Senior")
    page.get_by_test_id("empleado-departamento").select_option(label="Tecnología")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_contain_text("Analista Senior")
    expect(fila).to_contain_text("Tecnología")


def test_cp_10_dar_de_baja_a_empleado_activo(page, url_web, url_api):
    """CP-10: Dar de baja a un empleado activo."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp10"), fecha_ingreso="2023-05-10")

    page.goto(url_web)
    page.get_by_test_id(f"baja-empleado-{empleado['id']}").click()
    page.get_by_test_id("empleado-fecha-baja").fill("2026-03-15")
    page.get_by_test_id("confirmar-baja").click()

    expect(page.get_by_test_id(f"fila-empleado-{empleado['id']}")).to_be_visible()
    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")
