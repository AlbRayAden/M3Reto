import { useEffect, useState } from 'react'
import { crearEmpleado, obtenerDepartamentos } from '../api.js'

const VALORES_INICIALES = {
  nombre: '',
  correo: '',
  puesto: '',
  departamento: '',
  fecha_ingreso: '',
}

export default function FormularioEmpleado({ onEmpleadoCreado }) {
  const [valores, setValores] = useState(VALORES_INICIALES)
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
      const empleado = await crearEmpleado(valores)
      setMensajeExito(`Empleado registrado con número ${empleado.numero_empleado}`)
      setValores(VALORES_INICIALES)
      onEmpleadoCreado?.()
    } catch (error) {
      setCamposInvalidos(error.campos ?? [])
      setMensajeError(error.mensaje)
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
      <h2>Registrar empleado</h2>

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
        Correo
        <input
          data-testid="empleado-correo"
          aria-invalid={camposInvalidos.includes('correo')}
          value={valores.correo}
          onChange={(e) => actualizarCampo('correo', e.target.value)}
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
    </form>
  )
}
