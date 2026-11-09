"""Pruebas de API para HU-02: directorio y búsqueda de empleados."""

import re
import uuid

import httpx
import pytest


def _tag() -> str:
    return uuid.uuid4().hex[:8]


def _correo_unico(prefijo: str) -> str:
    return f"{prefijo}.{uuid.uuid4().hex}@empresa.com"


def _datos_validos(**sobrescritos) -> dict:
    datos = {
        "nombre": "Empleado de Prueba",
        "correo": _correo_unico("empleado"),
        "puesto": "Analista de Pruebas",
        "departamento": "Tecnología",
        "fecha_ingreso": "2024-01-15",
    }
    datos.update(sobrescritos)
    return datos


def _crear_empleado(url_api, **sobrescritos) -> dict:
    respuesta = httpx.post(f"{url_api}/api/empleados", json=_datos_validos(**sobrescritos))
    assert respuesta.status_code == 201
    return respuesta.json()


def test_cp_01_directorio_completo_con_columnas(url_api):
    """CP-01: Ver el directorio completo con sus columnas.

    La precondición original incluye un tercer empleado dado de baja; como la
    API de HU-02 no expone ningún endpoint para dar de baja a un empleado (ver
    CP-02), aquí se verifica la estructura con dos empleados activos.
    """
    tag = _tag()
    empleado_a = _crear_empleado(
        url_api,
        nombre=f"Ana López {tag}",
        correo=_correo_unico(f"ana.lopez.{tag}"),
        puesto="Analista de Datos",
        departamento="Tecnología",
    )
    empleado_b = _crear_empleado(
        url_api,
        nombre=f"Carlos Ruiz {tag}",
        correo=_correo_unico(f"carlos.ruiz.{tag}"),
        puesto="Ejecutivo de Ventas",
        departamento="Ventas",
    )

    respuesta = httpx.get(f"{url_api}/api/empleados")

    assert respuesta.status_code == 200
    por_correo = {e["correo"]: e for e in respuesta.json()}

    fila_a = por_correo[empleado_a["correo"]]
    assert re.fullmatch(r"EMP-\d{4}", fila_a["numero_empleado"])
    assert fila_a["nombre"] == f"Ana López {tag}"
    assert fila_a["puesto"] == "Analista de Datos"
    assert fila_a["departamento"] == "Tecnología"
    assert fila_a["estado"] == "activo"

    fila_b = por_correo[empleado_b["correo"]]
    assert re.fullmatch(r"EMP-\d{4}", fila_b["numero_empleado"])
    assert fila_b["nombre"] == f"Carlos Ruiz {tag}"
    assert fila_b["puesto"] == "Ejecutivo de Ventas"
    assert fila_b["departamento"] == "Ventas"
    assert fila_b["estado"] == "activo"


@pytest.mark.skip(
    reason=(
        "CP-02 necesita un empleado con estado 'baja' como precondición, pero "
        "la API de HU-02 no expone ningún endpoint para dar de baja a un "
        "empleado (funcionalidad de una historia aparte, aún no implementada). "
        "No se puede crear esa precondición por la API."
    )
)
def test_cp_02_empleado_baja_sigue_en_directorio(url_api):
    """CP-02: Un empleado dado de baja sigue apareciendo en el directorio."""


def test_cp_03_buscar_por_nombre_sin_importar_mayusculas(url_api):
    """CP-03: Buscar por nombre sin importar mayúsculas o minúsculas."""
    tag = _tag()
    nombre = f"Ana López {tag}"
    empleado = _crear_empleado(url_api, nombre=nombre, correo=_correo_unico(f"ana.lopez.{tag}"))

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": nombre.upper()})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    coincidencia = next(e for e in cuerpo if e["correo"] == empleado["correo"])
    assert coincidencia["nombre"] == nombre


def test_cp_04_buscar_por_parte_del_nombre_no_solo_al_inicio(url_api):
    """CP-04: Buscar por una parte del nombre (coincidencia parcial, no solo al inicio)."""
    tag = _tag()
    nombre = f"Ana López {tag}"
    empleado = _crear_empleado(url_api, nombre=nombre, correo=_correo_unico(f"ana.lopez.{tag}"))
    fragmento = f"lópez {tag}"

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": fragmento})

    assert respuesta.status_code == 200
    correos = [e["correo"] for e in respuesta.json()]
    assert empleado["correo"] in correos


def test_cp_05_buscar_por_correo_sin_importar_mayusculas(url_api):
    """CP-05: Buscar por correo sin importar mayúsculas o minúsculas."""
    tag = _tag()
    correo = f"carlos.ruiz.{tag}@empresa.com"
    _crear_empleado(url_api, nombre=f"Carlos Ruiz {tag}", correo=correo)

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": correo.upper()})

    assert respuesta.status_code == 200
    coincidencias = [e for e in respuesta.json() if e["correo"] == correo]
    assert len(coincidencias) == 1


def test_cp_06_filtrar_por_departamento(url_api):
    """CP-06: Filtrar por departamento."""
    tag = _tag()
    empleado = _crear_empleado(
        url_api,
        nombre=f"Carlos Ruiz {tag}",
        correo=_correo_unico(f"carlos.ruiz.{tag}"),
        departamento="Ventas",
    )

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"departamento": "Ventas"})

    assert respuesta.status_code == 200
    por_correo = {e["correo"]: e for e in respuesta.json()}
    assert por_correo[empleado["correo"]]["departamento"] == "Ventas"


def test_cp_07_combinar_busqueda_y_filtro_por_departamento(url_api):
    """CP-07: Combinar búsqueda y filtro por departamento."""
    tag = _tag()
    nombre = f"María Fernández {tag}"
    empleado = _crear_empleado(
        url_api,
        nombre=nombre,
        correo=_correo_unico(f"maria.fernandez.{tag}"),
        departamento="Finanzas",
    )

    respuesta = httpx.get(
        f"{url_api}/api/empleados",
        params={"departamento": "Finanzas", "buscar": nombre},
    )

    assert respuesta.status_code == 200
    por_correo = {e["correo"]: e for e in respuesta.json()}
    coincidencia = por_correo[empleado["correo"]]
    assert coincidencia["departamento"] == "Finanzas"
    assert coincidencia["nombre"] == nombre


def test_cp_08_busqueda_sin_resultados(url_api):
    """CP-08: Búsqueda sin resultados muestra el mensaje correspondiente."""
    busqueda = f"xyz-no-existe-{_tag()}"

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": busqueda})

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_cp_09_filtro_por_departamento_sin_resultados(url_api):
    """CP-09: Filtro por departamento sin resultados muestra el mensaje correspondiente.

    El caso original filtra por 'Recursos Humanos', un departamento válido del
    catálogo que otras suites (por ejemplo HU-01) sí pueden poblar, así que no
    garantiza una respuesta vacía en una base de datos persistente. Se usa en
    su lugar un departamento fuera del catálogo: como `departamento` se valida
    al crear un empleado, ningún registro puede tenerlo y el filtro siempre da
    0 resultados.
    """
    respuesta = httpx.get(
        f"{url_api}/api/empleados",
        params={"departamento": f"Departamento-Inexistente-{_tag()}"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_cp_10_limpiar_busqueda_muestra_todos_los_empleados(url_api):
    """CP-10: Limpiar la búsqueda vuelve a mostrar todos los empleados.

    En una base de datos persistente no hay un total fijo de empleados; se
    verifica que, al quitar los filtros, la respuesta vuelve a incluir a los
    empleados creados en este test (antes acotados por una búsqueda).
    """
    tag = _tag()
    empleado_a = _crear_empleado(
        url_api, nombre=f"Ana López {tag}", correo=_correo_unico(f"ana.{tag}")
    )
    empleado_b = _crear_empleado(
        url_api, nombre=f"Carlos Ruiz {tag}", correo=_correo_unico(f"carlos.{tag}")
    )

    acotada = httpx.get(f"{url_api}/api/empleados", params={"buscar": tag})
    assert acotada.status_code == 200
    assert {e["correo"] for e in acotada.json()} == {
        empleado_a["correo"],
        empleado_b["correo"],
    }

    sin_filtro = httpx.get(f"{url_api}/api/empleados")
    assert sin_filtro.status_code == 200
    correos_sin_filtro = {e["correo"] for e in sin_filtro.json()}
    assert {empleado_a["correo"], empleado_b["correo"]} <= correos_sin_filtro
    assert len(sin_filtro.json()) >= len(acotada.json())
