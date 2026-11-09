"""Pruebas de API para HU-01: registrar empleados."""

import re
import uuid
from datetime import date, timedelta

import httpx


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


def _campos_invalidos(cuerpo: dict) -> list[str]:
    return [error["loc"][-1] for error in cuerpo["detail"]]


def test_cp_01_registrar_empleado_con_datos_validos(url_api):
    """CP-01: Registrar un empleado con datos válidos."""
    datos = _datos_validos(correo=_correo_unico("ana.lopez"))

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert re.fullmatch(r"EMP-\d{4}", cuerpo["numero_empleado"])
    assert cuerpo["estado"] == "activo"


def test_cp_02_numero_empleado_es_consecutivo(url_api):
    """CP-02: El número de empleado es consecutivo al registrar un segundo empleado."""
    primero = httpx.post(
        f"{url_api}/api/empleados", json=_datos_validos(correo=_correo_unico("primero"))
    )
    segundo = httpx.post(
        f"{url_api}/api/empleados", json=_datos_validos(correo=_correo_unico("carlos.ruiz"))
    )

    assert primero.status_code == 201
    assert segundo.status_code == 201

    numero_primero = int(primero.json()["numero_empleado"].split("-")[1])
    numero_segundo = int(segundo.json()["numero_empleado"].split("-")[1])
    assert numero_segundo == numero_primero + 1


def test_cp_03_rechaza_correo_duplicado_sin_importar_mayusculas(url_api):
    """CP-03: Rechazar un correo duplicado sin importar mayúsculas."""
    correo = _correo_unico("ana.lopez")
    original = httpx.post(f"{url_api}/api/empleados", json=_datos_validos(correo=correo))
    assert original.status_code == 201

    duplicado = httpx.post(
        f"{url_api}/api/empleados",
        json=_datos_validos(nombre="Ana Lopez Segunda", correo=correo.upper()),
    )

    assert duplicado.status_code == 409
    assert duplicado.json()["detail"] == "El correo ya está registrado"


def test_cp_04_guarda_el_correo_en_minusculas(url_api):
    """CP-04: Guardar el correo en minúsculas aunque se capture con mayúsculas."""
    correo_mixto = f"Maria.Perez.{uuid.uuid4().hex}@EMPRESA.com"

    respuesta = httpx.post(f"{url_api}/api/empleados", json=_datos_validos(correo=correo_mixto))

    assert respuesta.status_code == 201
    assert respuesta.json()["correo"] == correo_mixto.lower()


def test_cp_05_rechaza_correo_no_corporativo(url_api):
    """CP-05: Rechazar un correo que no es corporativo."""
    datos = _datos_validos(nombre="Jorge Díaz", correo=f"jorge.diaz.{uuid.uuid4().hex}@gmail.com")

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "Usa el correo corporativo @empresa.com"


def test_cp_06_rechaza_nombre_demasiado_corto(url_api):
    """CP-06: Rechazar un nombre demasiado corto."""
    datos = _datos_validos(nombre="A", correo=_correo_unico("a"))

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert "nombre" in _campos_invalidos(respuesta.json())


def test_cp_07_acepta_nombre_con_exactamente_dos_caracteres(url_api):
    """CP-07: Aceptar un nombre con exactamente 2 caracteres."""
    datos = _datos_validos(nombre="Jo", correo=_correo_unico("jo"))

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 201


def test_cp_08_rechaza_nombre_que_supera_80_caracteres(url_api):
    """CP-08: Rechazar un nombre que supera los 80 caracteres."""
    datos = _datos_validos(nombre="A" * 81, correo=_correo_unico("nombre.largo"))

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert "nombre" in _campos_invalidos(respuesta.json())


def test_cp_09_acepta_nombre_con_exactamente_80_caracteres(url_api):
    """CP-09: Aceptar un nombre con exactamente 80 caracteres."""
    datos = _datos_validos(nombre="A" * 80, correo=_correo_unico("nombre.limite"))

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 201


def test_cp_10_rechaza_puesto_demasiado_corto(url_api):
    """CP-10: Rechazar un puesto demasiado corto."""
    datos = _datos_validos(
        nombre="Luis Gómez", correo=_correo_unico("puesto.corto"), puesto="A"
    )

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert "puesto" in _campos_invalidos(respuesta.json())


def test_cp_11_acepta_puesto_con_exactamente_60_caracteres(url_api):
    """CP-11: Aceptar un puesto con exactamente 60 caracteres."""
    datos = _datos_validos(
        nombre="Luis Gómez", correo=_correo_unico("puesto.limite"), puesto="B" * 60
    )

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 201


def test_cp_12_rechaza_puesto_que_supera_60_caracteres(url_api):
    """CP-12: Rechazar un puesto que supera los 60 caracteres."""
    datos = _datos_validos(
        nombre="Luis Gómez", correo=_correo_unico("puesto.largo"), puesto="B" * 61
    )

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert "puesto" in _campos_invalidos(respuesta.json())


def test_cp_13_rechaza_departamento_fuera_del_catalogo(url_api):
    """CP-13: Rechazar un departamento que no está en el catálogo."""
    datos = _datos_validos(
        nombre="Sofía Torres",
        correo=_correo_unico("depto.invalido"),
        departamento="Marketing",
    )

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert "departamento" in _campos_invalidos(respuesta.json())


def test_cp_14_rechaza_fecha_de_ingreso_futura(url_api):
    """CP-14: Rechazar una fecha de ingreso futura.

    El caso original fija una fecha de "hoy" hipotética (2026-06-15); como la API
    valida contra date.today() real y no admite fijar la fecha del sistema, se
    calcula una fecha futura relativa al momento de ejecución para ejercer la
    misma regla de negocio.
    """
    fecha_futura = (date.today() + timedelta(days=1)).isoformat()
    datos = _datos_validos(
        nombre="Pedro Sánchez",
        correo=_correo_unico("pedro.sanchez"),
        fecha_ingreso=fecha_futura,
    )

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "La fecha de ingreso no puede ser futura"


def test_cp_15_acepta_fecha_de_ingreso_igual_a_hoy(url_api):
    """CP-15: Aceptar una fecha de ingreso igual al día de hoy."""
    fecha_hoy = date.today().isoformat()
    datos = _datos_validos(
        nombre="Pedro Sánchez",
        correo=_correo_unico("pedro.sanchez2"),
        fecha_ingreso=fecha_hoy,
    )

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 201


def test_cp_16_acepta_fecha_de_ingreso_un_dia_antes_de_hoy(url_api):
    """CP-16: Aceptar una fecha de ingreso un día antes de hoy."""
    fecha_ayer = (date.today() - timedelta(days=1)).isoformat()
    datos = _datos_validos(
        nombre="Laura Méndez",
        correo=_correo_unico("laura.mendez"),
        departamento="Recursos Humanos",
        fecha_ingreso=fecha_ayer,
    )

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 201


def test_cp_17_rechaza_registro_sin_nombre(url_api):
    """CP-17: Rechazar el registro cuando falta un campo obligatorio (nombre)."""
    datos = _datos_validos(nombre="", correo=_correo_unico("sinnombre"))

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert "nombre" in _campos_invalidos(respuesta.json())


def test_cp_18_rechaza_registro_sin_correo(url_api):
    """CP-18: Rechazar el registro cuando falta un campo obligatorio (correo)."""
    datos = _datos_validos(nombre="Marco Vidal", correo="")

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert "correo" in _campos_invalidos(respuesta.json())


def test_cp_19_rechaza_registro_sin_puesto(url_api):
    """CP-19: Rechazar el registro cuando falta un campo obligatorio (puesto)."""
    datos = _datos_validos(
        nombre="Marco Vidal", correo=_correo_unico("marco.vidal"), puesto=""
    )

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert "puesto" in _campos_invalidos(respuesta.json())


def test_cp_20_rechaza_registro_sin_fecha_ingreso(url_api):
    """CP-20: Rechazar el registro cuando falta un campo obligatorio (fecha_ingreso)."""
    datos = _datos_validos(
        nombre="Marco Vidal", correo=_correo_unico("marco.vidal2"), fecha_ingreso=""
    )

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert "fecha_ingreso" in _campos_invalidos(respuesta.json())


def test_cp_21_estado_inicial_es_activo(url_api):
    """CP-21: El estado inicial de un empleado registrado es activo."""
    datos = _datos_validos(
        nombre="Nuevo Ingreso",
        correo=_correo_unico("nuevo.ingreso"),
        puesto="Becario",
        departamento="Operaciones",
        fecha_ingreso="2024-01-01",
    )

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "activo"
