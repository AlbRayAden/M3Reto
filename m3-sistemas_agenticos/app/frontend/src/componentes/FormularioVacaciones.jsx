import { useEffect, useState } from 'react'
import { crearVacacion, obtenerSaldoVacaciones } from '../api.js'

export default function FormularioVacaciones({ empleadoId, onCerrar }) {
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [anio, setAnio] = useState(null)
  const [disponibles, setDisponibles] = useState(null)
  const [mensaje, setMensaje] = useState('')

  function cargarSaldo() {
    obtenerSaldoVacaciones(empleadoId)
      .then((saldo) => {
        setAnio(saldo.anio)
        setDisponibles(saldo.dias_disponibles)
      })
      .catch(() => setDisponibles(null))
  }

  useEffect(() => {
    cargarSaldo()
  }, [empleadoId])

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensaje('')

    try {
      const resultado = await crearVacacion(empleadoId, {
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
      })
      const anioSolicitud = fechaInicio.slice(0, 4)
      setMensaje(
        `Solicitud registrada: ${resultado.dias_habiles} días hábiles. Te quedan ${resultado.dias_restantes} días hábiles en ${anioSolicitud}.`,
      )
      cargarSaldo()
    } catch (error) {
      setMensaje(error.mensaje)
    }
  }

  return (
    <div>
      <h3>Solicitar vacaciones</h3>
      <p>
        Días disponibles en {anio ?? '—'}:{' '}
        <span data-testid="vacaciones-disponibles">{disponibles ?? '—'}</span>
      </p>

      <form onSubmit={manejarEnvio}>
        <label>
          Fecha de inicio
          <input
            type="date"
            data-testid="vacaciones-fecha-inicio"
            value={fechaInicio}
            onChange={(e) => setFechaInicio(e.target.value)}
          />
        </label>

        <label>
          Fecha de fin
          <input
            type="date"
            data-testid="vacaciones-fecha-fin"
            value={fechaFin}
            onChange={(e) => setFechaFin(e.target.value)}
          />
        </label>

        <button type="submit" data-testid="vacaciones-enviar">
          Enviar solicitud
        </button>
      </form>

      {mensaje && <p data-testid="vacaciones-mensaje">{mensaje}</p>}

      <button type="button" onClick={onCerrar}>
        Cerrar
      </button>
    </div>
  )
}
