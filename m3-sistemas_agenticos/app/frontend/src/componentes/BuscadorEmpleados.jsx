import { useEffect, useState } from 'react'
import { obtenerDepartamentos } from '../api.js'

export default function BuscadorEmpleados({ busqueda, departamento, onCambiarBusqueda, onCambiarDepartamento }) {
  const [departamentos, setDepartamentos] = useState([])

  useEffect(() => {
    obtenerDepartamentos()
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  return (
    <div>
      <input
        data-testid="buscar-empleados"
        placeholder="Buscar por nombre o correo"
        value={busqueda}
        onChange={(e) => onCambiarBusqueda(e.target.value)}
      />

      <select
        data-testid="filtro-departamento"
        value={departamento}
        onChange={(e) => onCambiarDepartamento(e.target.value)}
      >
        <option value="">Todos los departamentos</option>
        {departamentos.map((d) => (
          <option key={d} value={d}>
            {d}
          </option>
        ))}
      </select>
    </div>
  )
}
