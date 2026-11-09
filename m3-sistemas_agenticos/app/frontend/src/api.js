// Llamadas a la API de gestión de empleados. Siempre con rutas relativas.

function normalizarError(status, cuerpo) {
  const detail = cuerpo?.detail

  if (Array.isArray(detail)) {
    const campos = detail.map((error) => error.loc[error.loc.length - 1])
    return { status, campos, mensaje: 'Revisa los campos marcados.' }
  }

  return { status, campos: [], mensaje: detail ?? 'Ocurrió un error inesperado.' }
}

async function solicitar(ruta, opciones) {
  const respuesta = await fetch(ruta, opciones)
  const cuerpo = await respuesta.json().catch(() => null)

  if (!respuesta.ok) {
    throw normalizarError(respuesta.status, cuerpo)
  }

  return cuerpo
}

export function obtenerEmpleados(filtros = {}) {
  const parametros = new URLSearchParams()

  if (filtros.buscar) {
    parametros.set('buscar', filtros.buscar)
  }
  if (filtros.departamento) {
    parametros.set('departamento', filtros.departamento)
  }

  const query = parametros.toString()
  return solicitar(query ? `/api/empleados?${query}` : '/api/empleados')
}

export function obtenerDepartamentos() {
  return solicitar('/api/departamentos')
}

export function crearEmpleado(datos) {
  return solicitar('/api/empleados', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
}

export function editarEmpleado(empleadoId, datos) {
  return solicitar(`/api/empleados/${empleadoId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
}

export function darDeBajaEmpleado(empleadoId, datos) {
  return solicitar(`/api/empleados/${empleadoId}/baja`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
}

export function crearVacacion(empleadoId, datos) {
  return solicitar(`/api/empleados/${empleadoId}/vacaciones`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
}

export function obtenerSaldoVacaciones(empleadoId, anio) {
  const parametros = new URLSearchParams()

  if (anio) {
    parametros.set('anio', anio)
  }

  const query = parametros.toString()
  return solicitar(
    query
      ? `/api/empleados/${empleadoId}/vacaciones?${query}`
      : `/api/empleados/${empleadoId}/vacaciones`,
  )
}
