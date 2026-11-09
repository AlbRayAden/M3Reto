import { useState } from 'react'
import FormularioVacaciones from './FormularioVacaciones.jsx'

export default function DirectorioEmpleados({ empleados }) {
  const [empleadoVacacionesAbierto, setEmpleadoVacacionesAbierto] = useState(null)

  function alternarVacaciones(empleadoId) {
    setEmpleadoVacacionesAbierto((actual) => (actual === empleadoId ? null : empleadoId))
  }

  return (
    <section>
      <h2>Directorio de empleados</h2>
      <table data-testid="tabla-empleados">
        <thead>
          <tr>
            <th>Número</th>
            <th>Nombre</th>
            <th>Correo</th>
            <th>Puesto</th>
            <th>Departamento</th>
            <th>Fecha de ingreso</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {empleados.map((empleado) => (
            <tr key={empleado.id} data-testid={`fila-empleado-${empleado.id}`}>
              <td data-testid={`numero-empleado-${empleado.id}`}>{empleado.numero_empleado}</td>
              <td>{empleado.nombre}</td>
              <td>{empleado.correo}</td>
              <td>{empleado.puesto}</td>
              <td>{empleado.departamento}</td>
              <td>{empleado.fecha_ingreso}</td>
              <td data-testid={`estado-empleado-${empleado.id}`}>
                {empleado.estado === 'activo' ? 'Activo' : 'Baja'}
              </td>
              <td>
                {empleado.estado === 'activo' && (
                  <button
                    type="button"
                    data-testid={`vacaciones-abrir-${empleado.id}`}
                    onClick={() => alternarVacaciones(empleado.id)}
                  >
                    Solicitar vacaciones
                  </button>
                )}
                {empleadoVacacionesAbierto === empleado.id && (
                  <FormularioVacaciones
                    empleadoId={empleado.id}
                    onCerrar={() => setEmpleadoVacacionesAbierto(null)}
                  />
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {empleados.length === 0 && <p data-testid="sin-resultados">No se encontraron empleados.</p>}
    </section>
  )
}
