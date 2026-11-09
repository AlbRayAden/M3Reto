import { useState } from 'react'
import { darDeBajaEmpleado } from '../api.js'

export default function FormularioBaja({ empleado, onEmpleadoActualizado, onCerrar }) {
  const [fechaBaja, setFechaBaja] = useState('')
  const [mensajeError, setMensajeError] = useState('')
  const [mensajeExito, setMensajeExito] = useState('')

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensajeError('')
    setMensajeExito('')

    try {
      await darDeBajaEmpleado(empleado.id, { fecha_baja: fechaBaja })
      setMensajeExito('Empleado dado de baja correctamente')
      onEmpleadoActualizado?.()
    } catch (error) {
      setMensajeError(error.mensaje)
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
      <h3>Dar de baja</h3>

      <label>
        Fecha de baja
        <input
          type="date"
          data-testid="empleado-fecha-baja"
          value={fechaBaja}
          onChange={(e) => setFechaBaja(e.target.value)}
        />
      </label>

      <button type="submit" data-testid="confirmar-baja">
        Confirmar baja
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}

      <button type="button" onClick={onCerrar}>
        Cerrar
      </button>
    </form>
  )
}
