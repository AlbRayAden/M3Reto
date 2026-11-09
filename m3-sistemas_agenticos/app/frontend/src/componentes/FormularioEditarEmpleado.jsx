import { useEffect, useState } from 'react'
import { editarEmpleado, obtenerDepartamentos } from '../api.js'

export default function FormularioEditarEmpleado({ empleado, onEmpleadoActualizado, onCerrar }) {
  const [valores, setValores] = useState({
    nombre: empleado.nombre,
    puesto: empleado.puesto,
    departamento: empleado.departamento,
    fecha_ingreso: empleado.fecha_ingreso,
  })
  const [departamentos, setDepartamentos] = useState([])
  const [camposInvalidos, setCamposInvalidos] = useState([])
  const [mensajeError, setMensajeError] = useState('')
  const [mensajeExito, setMensajeExito] = useState('')

  useEffect(() => {
    obtenerDepartamentos()
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  function actualizarCampo(campo, valor) {
    setValores((anteriores) => ({ ...anteriores, [campo]: valor }))
  }

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensajeError('')
    setMensajeExito('')
    setCamposInvalidos([])

    try {
      await editarEmpleado(empleado.id, valores)
      setMensajeExito('Empleado actualizado correctamente')
      onEmpleadoActualizado?.()
    } catch (error) {
      setCamposInvalidos(error.campos ?? [])
      setMensajeError(error.mensaje)
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
      <h3>Editar empleado</h3>

      <label>
        Nombre
        <input
          data-testid="empleado-nombre"
          aria-invalid={camposInvalidos.includes('nombre')}
          value={valores.nombre}
          onChange={(e) => actualizarCampo('nombre', e.target.value)}
        />
      </label>

      <label>
        Puesto
        <input
          data-testid="empleado-puesto"
          aria-invalid={camposInvalidos.includes('puesto')}
          value={valores.puesto}
          onChange={(e) => actualizarCampo('puesto', e.target.value)}
        />
      </label>

      <label>
        Departamento
        <select
          data-testid="empleado-departamento"
          aria-invalid={camposInvalidos.includes('departamento')}
          value={valores.departamento}
          onChange={(e) => actualizarCampo('departamento', e.target.value)}
        >
          <option value="">Selecciona un departamento</option>
          {departamentos.map((departamento) => (
            <option key={departamento} value={departamento}>
              {departamento}
            </option>
          ))}
        </select>
      </label>

      <label>
        Fecha de ingreso
        <input
          type="date"
          data-testid="empleado-fecha-ingreso"
          aria-invalid={camposInvalidos.includes('fecha_ingreso')}
          value={valores.fecha_ingreso}
          onChange={(e) => actualizarCampo('fecha_ingreso', e.target.value)}
        />
      </label>

      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}

      <button type="button" onClick={onCerrar}>
        Cerrar
      </button>
    </form>
  )
}
