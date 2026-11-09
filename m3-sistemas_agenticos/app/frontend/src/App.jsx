import { useCallback, useEffect, useState } from 'react'
import FormularioEmpleado from './componentes/FormularioEmpleado.jsx'
import DirectorioEmpleados from './componentes/DirectorioEmpleados.jsx'
import BuscadorEmpleados from './componentes/BuscadorEmpleados.jsx'
import { obtenerEmpleados } from './api.js'
import './App.css'

function App() {
  const [empleados, setEmpleados] = useState([])
  const [busqueda, setBusqueda] = useState('')
  const [departamento, setDepartamento] = useState('')

  const cargarEmpleados = useCallback(() => {
    obtenerEmpleados({ buscar: busqueda, departamento })
      .then(setEmpleados)
      .catch(() => setEmpleados([]))
  }, [busqueda, departamento])

  useEffect(() => {
    cargarEmpleados()
  }, [cargarEmpleados])

  return (
    <main>
      <h1>Gestión de empleados</h1>
      <FormularioEmpleado onEmpleadoCreado={cargarEmpleados} />
      <BuscadorEmpleados
        busqueda={busqueda}
        departamento={departamento}
        onCambiarBusqueda={setBusqueda}
        onCambiarDepartamento={setDepartamento}
      />
      <DirectorioEmpleados empleados={empleados} />
    </main>
  )
}

export default App
