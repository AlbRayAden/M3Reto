"""Pruebas de API para HU-03: editar y dar de baja a un empleado."""

import uuid

import httpx


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


def _editar(url_api, empleado: dict, **sobrescritos) -> httpx.Response:
    datos = {
        "nombre": empleado["nombre"],
        "puesto": empleado["puesto"],
        "departamento": empleado["departamento"],
        "fecha_ingreso": empleado["fecha_ingreso"],
    }
    datos.update(sobrescritos)
    return httpx.put(f"{url_api}/api/empleados/{empleado['id']}", json=datos)


def _campos_invalidos(cuerpo: dict) -> list[str]:
    return [error["loc"][-1] for error in cuerpo["detail"]]


def test_cp_01_editar_puesto_y_departamento_de_empleado_activo(url_api):
    """CP-01: Editar puesto y departamento de un empleado activo."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp01"))

    respuesta = _editar(url_api, empleado, puesto="Analista Senior", departamento="Tecnología")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["puesto"] == "Analista Senior"
    assert cuerpo["departamento"] == "Tecnología"
    assert cuerpo["numero_empleado"] == empleado["numero_empleado"]
    assert cuerpo["correo"] == empleado["correo"]


def test_cp_03_numero_empleado_y_correo_no_cambian_aunque_se_envien(url_api):
    """CP-03: El número de empleado y el correo no cambian aunque se envíen en la petición."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp03"))

    respuesta = _editar(
        url_api,
        empleado,
        puesto="Analista Senior",
        departamento="Tecnología",
        correo="otro@empresa.com",
        numero_empleado="EMP-9999",
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["correo"] == empleado["correo"]
    assert cuerpo["numero_empleado"] == empleado["numero_empleado"]


def test_cp_04_puesto_con_2_caracteres_se_acepta(url_api):
    """CP-04: Editar el puesto en los límites exactos de longitud permitida (2 caracteres)."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp04"))

    respuesta = _editar(url_api, empleado, puesto="AB")

    assert respuesta.status_code == 200


def test_cp_05_puesto_con_60_caracteres_se_acepta(url_api):
    """CP-05: Editar el puesto en los límites exactos de longitud permitida (60 caracteres)."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp05"))

    respuesta = _editar(url_api, empleado, puesto="1" * 60)

    assert respuesta.status_code == 200


def test_cp_06_puesto_con_1_caracter_se_rechaza(url_api):
    """CP-06: Editar el puesto con 1 carácter se rechaza por ser menor al mínimo."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp06"))

    respuesta = _editar(url_api, empleado, puesto="A")

    assert respuesta.status_code == 422
    assert "puesto" in _campos_invalidos(respuesta.json())


def test_cp_07_puesto_con_61_caracteres_se_rechaza(url_api):
    """CP-07: Editar el puesto con 61 caracteres se rechaza por exceder el máximo."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp07"))

    respuesta = _editar(url_api, empleado, puesto="1" * 61)

    assert respuesta.status_code == 422
    assert "puesto" in _campos_invalidos(respuesta.json())


def test_cp_08_departamento_fuera_del_catalogo_se_rechaza(url_api):
    """CP-08: Editar el departamento con un valor fuera del catálogo se rechaza."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp08"))

    respuesta = _editar(url_api, empleado, departamento="Marketing")

    assert respuesta.status_code == 422
    assert "departamento" in _campos_invalidos(respuesta.json())


def test_cp_09_dar_de_baja_a_empleado_activo(url_api):
    """CP-09: Dar de baja a un empleado activo."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp09"), fecha_ingreso="2023-05-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2026-03-15"}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "baja"
    assert cuerpo["fecha_baja"] == "2026-03-15"


def test_cp_11_fecha_baja_igual_a_fecha_ingreso_se_acepta(url_api):
    """CP-11: Dar de baja con fecha_baja igual a la fecha_ingreso se acepta."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp11"), fecha_ingreso="2023-05-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2023-05-10"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["fecha_baja"] == "2023-05-10"


def test_cp_12_fecha_baja_un_dia_antes_de_fecha_ingreso_se_rechaza(url_api):
    """CP-12: Dar de baja con fecha_baja un día antes de la fecha_ingreso se rechaza."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp12"), fecha_ingreso="2023-05-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2023-05-09"}
    )

    assert respuesta.status_code == 422
    assert (
        respuesta.json()["detail"]
        == "El campo fecha_baja no puede ser anterior a la fecha de ingreso"
    )


def test_cp_13_editar_a_empleado_dado_de_baja_se_rechaza(url_api):
    """CP-13: Intentar editar a un empleado dado de baja."""
    empleado = _crear_empleado(url_api, correo=_correo_unico("cp13"))
    baja = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2026-03-15"}
    )
    assert baja.status_code == 200

    respuesta = _editar(url_api, empleado, puesto="Analista Senior")

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "No se puede editar a un empleado dado de baja"

    verificacion = httpx.get(f"{url_api}/api/empleados", params={"buscar": empleado["correo"]})
    assert verificacion.json()[0]["puesto"] == "Analista"


def test_cp_14_editar_a_empleado_que_no_existe_se_rechaza(url_api):
    """CP-14: Intentar editar a un empleado que no existe."""
    respuesta = httpx.put(
        f"{url_api}/api/empleados/999999999",
        json={
            "nombre": "Nombre Cualquiera",
            "puesto": "Analista Senior",
            "departamento": "Tecnología",
            "fecha_ingreso": "2023-05-10",
        },
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp_15_dar_de_baja_a_empleado_que_no_existe_se_rechaza(url_api):
    """CP-15: Intentar dar de baja a un empleado que no existe."""
    respuesta = httpx.post(
        f"{url_api}/api/empleados/999999999/baja", json={"fecha_baja": "2026-03-15"}
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"
