"""Pruebas E2E para HU-01: registrar empleados."""

import re
import uuid
from datetime import date, timedelta

import httpx
import pytest
from playwright.sync_api import expect


def _correo_unico(prefijo: str) -> str:
    return f"{prefijo}.{uuid.uuid4().hex}@empresa.com"


def _llenar_formulario(page, datos: dict) -> None:
    page.get_by_test_id("empleado-nombre").fill(datos["nombre"])
    page.get_by_test_id("empleado-correo").fill(datos["correo"])
    page.get_by_test_id("empleado-puesto").fill(datos["puesto"])
    page.get_by_test_id("empleado-departamento").select_option(label=datos["departamento"])
    page.get_by_test_id("empleado-fecha-ingreso").fill(datos["fecha_ingreso"])


def test_cp_22_registrar_empleado_con_datos_validos(page, url_web):
    """CP-22: Registrar un empleado con datos válidos."""
    datos = {
        "nombre": "Ana López",
        "correo": _correo_unico("ana.lopez"),
        "puesto": "Analista de Datos",
        "departamento": "Tecnología",
        "fecha_ingreso": "2024-01-15",
    }

    page.goto(url_web)
    _llenar_formulario(page, datos)
    page.get_by_test_id("empleado-guardar").click()

    mensaje = page.get_by_test_id("mensaje-exito")
    expect(mensaje).to_be_visible()
    expect(mensaje).to_contain_text(re.compile(r"EMP-\d{4}"))


def test_cp_23_rechaza_correo_duplicado_sin_importar_mayusculas(page, url_web, url_api):
    """CP-23: Rechazar un correo duplicado sin importar mayúsculas."""
    correo = _correo_unico("ana.lopez")
    original = httpx.post(
        f"{url_api}/api/empleados",
        json={
            "nombre": "Ana López",
            "correo": correo,
            "puesto": "Analista de Datos",
            "departamento": "Tecnología",
            "fecha_ingreso": "2024-01-15",
        },
    )
    assert original.status_code == 201

    datos = {
        "nombre": "Ana Lopez Segunda",
        "correo": correo.upper(),
        "puesto": "Analista Junior",
        "departamento": "Tecnología",
        "fecha_ingreso": "2024-03-01",
    }

    page.goto(url_web)
    _llenar_formulario(page, datos)
    page.get_by_test_id("empleado-guardar").click()

    mensaje = page.get_by_test_id("mensaje-error")
    expect(mensaje).to_have_text("El correo ya está registrado")


def test_cp_24_rechaza_correo_no_corporativo(page, url_web):
    """CP-24: Rechazar un correo que no es corporativo."""
    datos = {
        "nombre": "Jorge Díaz",
        "correo": f"jorge.diaz.{uuid.uuid4().hex}@gmail.com",
        "puesto": "Técnico",
        "departamento": "Operaciones",
        "fecha_ingreso": "2024-01-20",
    }

    page.goto(url_web)
    _llenar_formulario(page, datos)
    page.get_by_test_id("empleado-guardar").click()

    mensaje = page.get_by_test_id("mensaje-error")
    expect(mensaje).to_have_text("Usa el correo corporativo @empresa.com")


def test_cp_25_rechaza_registro_sin_nombre(page, url_web):
    """CP-25: Rechazar el registro cuando falta un campo obligatorio (nombre)."""
    datos = {
        "nombre": "",
        "correo": _correo_unico("sinnombre"),
        "puesto": "Analista",
        "departamento": "Ventas",
        "fecha_ingreso": "2024-01-10",
    }

    page.goto(url_web)
    _llenar_formulario(page, datos)
    page.get_by_test_id("empleado-guardar").click()

    campo_nombre = page.get_by_test_id("empleado-nombre")
    expect(campo_nombre).to_have_attribute("aria-invalid", "true")


@pytest.mark.skip(
    reason=(
        "CP-26 no se puede ejercer desde la UI: el <select> de "
        "empleado-departamento solo ofrece las opciones del catálogo que "
        "devuelve GET /api/departamentos, así que no existe forma de que un "
        "usuario seleccione un departamento fuera del catálogo. La regla ya "
        "queda cubierta a nivel de API en CP-13."
    )
)
def test_cp_26_rechaza_departamento_fuera_del_catalogo(page, url_web):
    """CP-26: Rechazar un departamento que no está en el catálogo."""


def test_cp_27_rechaza_fecha_de_ingreso_futura(page, url_web):
    """CP-27: Rechazar una fecha de ingreso futura.

    El caso original fija una fecha de "hoy" hipotética (2026-06-15); como la
    validación corre contra la fecha real del sistema, se calcula una fecha
    futura relativa al momento de ejecución para ejercer la misma regla.
    """
    fecha_futura = (date.today() + timedelta(days=1)).isoformat()
    datos = {
        "nombre": "Pedro Sánchez",
        "correo": _correo_unico("pedro.sanchez"),
        "puesto": "Desarrollador",
        "departamento": "Tecnología",
        "fecha_ingreso": fecha_futura,
    }

    page.goto(url_web)
    _llenar_formulario(page, datos)
    page.get_by_test_id("empleado-guardar").click()

    mensaje = page.get_by_test_id("mensaje-error")
    expect(mensaje).to_have_text("La fecha de ingreso no puede ser futura")


def test_cp_28_rechaza_nombre_demasiado_corto(page, url_web):
    """CP-28: Rechazar un nombre demasiado corto."""
    datos = {
        "nombre": "A",
        "correo": _correo_unico("a"),
        "puesto": "Auxiliar",
        "departamento": "Operaciones",
        "fecha_ingreso": "2024-01-20",
    }

    page.goto(url_web)
    _llenar_formulario(page, datos)
    page.get_by_test_id("empleado-guardar").click()

    campo_nombre = page.get_by_test_id("empleado-nombre")
    expect(campo_nombre).to_have_attribute("aria-invalid", "true")


def test_cp_29_rechaza_puesto_demasiado_corto(page, url_web):
    """CP-29: Rechazar un puesto demasiado corto."""
    datos = {
        "nombre": "Luis Gómez",
        "correo": _correo_unico("puesto.corto"),
        "puesto": "A",
        "departamento": "Ventas",
        "fecha_ingreso": "2024-01-20",
    }

    page.goto(url_web)
    _llenar_formulario(page, datos)
    page.get_by_test_id("empleado-guardar").click()

    campo_puesto = page.get_by_test_id("empleado-puesto")
    expect(campo_puesto).to_have_attribute("aria-invalid", "true")
