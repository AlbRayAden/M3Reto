"""Pruebas E2E para HU-02: directorio y búsqueda de empleados."""

import uuid

import httpx
import pytest
from playwright.sync_api import expect


def _tag() -> str:
    return uuid.uuid4().hex[:8]


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


def test_cp_11_directorio_completo_con_columnas(page, url_web, url_api):
    """CP-11: Ver el directorio completo con sus columnas.

    La precondición original incluye un tercer empleado dado de baja; como la
    API aún no expone un endpoint para dar de baja a un empleado (ver CP-12),
    aquí se verifica la estructura con dos empleados activos. Se acota la
    tabla con la búsqueda del tag único de este test para que el conteo de
    filas sea determinista en una base de datos persistente.
    """
    tag = _tag()
    empleado_a = _crear_empleado(
        url_api,
        nombre=f"Ana López {tag}",
        correo=_correo_unico(f"ana.{tag}"),
        departamento="Tecnología",
    )
    empleado_b = _crear_empleado(
        url_api,
        nombre=f"Carlos Ruiz {tag}",
        correo=_correo_unico(f"carlos.{tag}"),
        departamento="Ventas",
    )

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(tag)

    filas = page.get_by_test_id("tabla-empleados").locator("tbody tr")
    expect(filas).to_have_count(2)

    expect(page.get_by_test_id(f"fila-empleado-{empleado_a['id']}")).to_be_visible()
    expect(page.get_by_test_id(f"numero-empleado-{empleado_a['id']}")).to_have_text(
        empleado_a["numero_empleado"]
    )
    expect(page.get_by_test_id(f"estado-empleado-{empleado_a['id']}")).to_have_text("Activo")

    expect(page.get_by_test_id(f"fila-empleado-{empleado_b['id']}")).to_be_visible()
    expect(page.get_by_test_id(f"estado-empleado-{empleado_b['id']}")).to_have_text("Activo")


@pytest.mark.skip(
    reason=(
        "CP-12 necesita un empleado con estado 'baja' como precondición, pero "
        "la API de HU-02 no expone ningún endpoint para dar de baja a un "
        "empleado (funcionalidad de una historia aparte, aún no implementada). "
        "No se puede crear esa precondición por la API."
    )
)
def test_cp_12_empleado_baja_sigue_en_directorio(page, url_web):
    """CP-12: Un empleado dado de baja sigue apareciendo en el directorio."""


def test_cp_13_buscar_por_nombre_sin_importar_mayusculas(page, url_web, url_api):
    """CP-13: Buscar por nombre sin importar mayúsculas o minúsculas."""
    tag = _tag()
    nombre = f"Ana López {tag}"
    empleado = _crear_empleado(url_api, nombre=nombre, correo=_correo_unico(f"ana.{tag}"))

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(nombre.upper())

    filas = page.get_by_test_id("tabla-empleados").locator("tbody tr")
    expect(filas).to_have_count(1)
    expect(page.get_by_test_id(f"fila-empleado-{empleado['id']}")).to_be_visible()


def test_cp_14_buscar_por_parte_del_nombre_no_solo_al_inicio(page, url_web, url_api):
    """CP-14: Buscar por una parte del nombre (coincidencia parcial, no solo al inicio)."""
    tag = _tag()
    nombre = f"Ana López {tag}"
    empleado = _crear_empleado(url_api, nombre=nombre, correo=_correo_unico(f"ana.{tag}"))
    fragmento = f"lópez {tag}"

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(fragmento)

    filas = page.get_by_test_id("tabla-empleados").locator("tbody tr")
    expect(filas).to_have_count(1)
    expect(page.get_by_test_id(f"fila-empleado-{empleado['id']}")).to_be_visible()


def test_cp_15_filtrar_por_departamento(page, url_web, url_api):
    """CP-15: Filtrar por departamento.

    Filtrar solo por departamento no basta para un conteo determinista en una
    base de datos persistente (otras ejecuciones pueden haber dejado más
    empleados en 'Ventas'); se combina con la búsqueda del tag único del
    empleado creado en este test.
    """
    tag = _tag()
    empleado = _crear_empleado(
        url_api,
        nombre=f"Carlos Ruiz {tag}",
        correo=_correo_unico(f"carlos.{tag}"),
        departamento="Ventas",
    )

    page.goto(url_web)
    page.get_by_test_id("filtro-departamento").select_option(label="Ventas")
    page.get_by_test_id("buscar-empleados").fill(tag)

    filas = page.get_by_test_id("tabla-empleados").locator("tbody tr")
    expect(filas).to_have_count(1)
    expect(page.get_by_test_id(f"fila-empleado-{empleado['id']}")).to_be_visible()


def test_cp_16_combinar_busqueda_y_filtro_por_departamento(page, url_web, url_api):
    """CP-16: Combinar búsqueda y filtro por departamento.

    El paso original busca por 'maría', una palabra que coincidiría con
    cualquier María creada por otras ejecuciones en una base de datos
    persistente; se busca en su lugar por el nombre completo con el tag único
    de este test para que el conteo de filas sea determinista.
    """
    tag = _tag()
    nombre = f"María Fernández {tag}"
    empleado = _crear_empleado(
        url_api,
        nombre=nombre,
        correo=_correo_unico(f"maria.{tag}"),
        departamento="Finanzas",
    )

    page.goto(url_web)
    page.get_by_test_id("filtro-departamento").select_option(label="Finanzas")
    page.get_by_test_id("buscar-empleados").fill(nombre.lower())

    filas = page.get_by_test_id("tabla-empleados").locator("tbody tr")
    expect(filas).to_have_count(1)
    expect(page.get_by_test_id(f"fila-empleado-{empleado['id']}")).to_be_visible()


def test_cp_17_busqueda_sin_resultados(page, url_web):
    """CP-17: Búsqueda sin resultados muestra el mensaje correspondiente."""
    busqueda = f"xyz-no-existe-{_tag()}"

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(busqueda)

    filas = page.get_by_test_id("tabla-empleados").locator("tbody tr")
    expect(filas).to_have_count(0)
    expect(page.get_by_test_id("sin-resultados")).to_be_visible()


def test_cp_18_limpiar_busqueda_muestra_todos_los_empleados(page, url_web, url_api):
    """CP-18: Limpiar la búsqueda vuelve a mostrar todos los empleados.

    En una base de datos persistente no hay un total fijo de 3 empleados; se
    toma el total real vía la API justo antes de la prueba y se compara contra
    lo que muestra la tabla al borrar la búsqueda.
    """
    tag = _tag()
    empleado_a = _crear_empleado(
        url_api, nombre=f"Ana López {tag}", correo=_correo_unico(f"ana.{tag}")
    )
    empleado_b = _crear_empleado(
        url_api, nombre=f"Carlos Ruiz {tag}", correo=_correo_unico(f"carlos.{tag}")
    )

    total_esperado = len(httpx.get(f"{url_api}/api/empleados").json())

    page.goto(url_web)
    campo_busqueda = page.get_by_test_id("buscar-empleados")
    campo_busqueda.fill(tag)

    filas = page.get_by_test_id("tabla-empleados").locator("tbody tr")
    expect(filas).to_have_count(2)

    campo_busqueda.fill("")

    expect(filas).to_have_count(total_esperado)
    expect(page.get_by_test_id(f"fila-empleado-{empleado_a['id']}")).to_be_visible()
    expect(page.get_by_test_id(f"fila-empleado-{empleado_b['id']}")).to_be_visible()
