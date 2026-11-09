# language: es
# HU-02 · Consultar el directorio de empleados

Característica: Consultar el directorio de empleados
  Como persona del área de Recursos Humanos
  Quiero ver el directorio de empleados, buscarlos por nombre o correo y filtrarlos por departamento
  Para encontrar rápido a una persona

  Antecedentes:
    Dado que existen los siguientes empleados registrados:
      | id | numero_empleado | nombre           | correo                       | puesto               | departamento       | estado |
      | 1  | EMP-0001        | Ana López        | ana.lopez@empresa.com        | Analista de Datos    | Tecnología         | activo |
      | 2  | EMP-0002        | Carlos Ruiz      | carlos.ruiz@empresa.com      | Ejecutivo de Ventas  | Ventas             | activo |
      | 3  | EMP-0003        | María Fernández  | maria.fernandez@empresa.com  | Contadora            | Finanzas           | baja   |

  Escenario: Camino feliz - ver el directorio completo con sus columnas
    Dado que estoy en la pantalla del directorio de empleados
    Cuando consulto "GET /api/empleados"
    Entonces la respuesta tiene código 200
    Y la tabla "tabla-empleados" muestra 3 filas
    Y la fila "fila-empleado-1" muestra el número de empleado "EMP-0001", el nombre "Ana López", el puesto "Analista de Datos", el departamento "Tecnología" y el estado "Activo"
    Y la fila "fila-empleado-2" muestra el número de empleado "EMP-0002", el nombre "Carlos Ruiz", el puesto "Ejecutivo de Ventas", el departamento "Ventas" y el estado "Activo"
    Y la fila "fila-empleado-3" muestra el número de empleado "EMP-0003", el nombre "María Fernández", el puesto "Contadora", el departamento "Finanzas" y el estado "Baja"

  Escenario: Un empleado dado de baja sigue apareciendo en el directorio
    Dado que el empleado "María Fernández" tiene estado "baja"
    Cuando consulto el directorio sin filtros
    Entonces la fila "fila-empleado-3" está presente en "tabla-empleados"
    Y el campo "estado-empleado-3" muestra el texto "Baja"

  Escenario: Buscar por nombre sin importar mayúsculas o minúsculas
    Dado que estoy en la pantalla del directorio de empleados
    Cuando escribo "ANA LÓPEZ" en el campo "buscar-empleados"
    Entonces la tabla "tabla-empleados" muestra 1 fila
    Y la fila "fila-empleado-1" está presente en "tabla-empleados"

  Escenario: Buscar por una parte del nombre (coincidencia parcial, no solo al inicio)
    Dado que estoy en la pantalla del directorio de empleados
    Cuando escribo "lóp" en el campo "buscar-empleados"
    Entonces la tabla "tabla-empleados" muestra 1 fila
    Y la fila "fila-empleado-1" está presente en "tabla-empleados"

  Escenario: Buscar por correo sin importar mayúsculas o minúsculas
    Dado que estoy en la pantalla del directorio de empleados
    Cuando escribo "CARLOS.RUIZ@EMPRESA.COM" en el campo "buscar-empleados"
    Entonces la tabla "tabla-empleados" muestra 1 fila
    Y la fila "fila-empleado-2" está presente en "tabla-empleados"

  Escenario: Filtrar por departamento
    Dado que estoy en la pantalla del directorio de empleados
    Cuando selecciono "Ventas" en el campo "filtro-departamento"
    Entonces la tabla "tabla-empleados" muestra 1 fila
    Y la fila "fila-empleado-2" está presente en "tabla-empleados"

  Escenario: Combinar búsqueda y filtro por departamento
    Dado que selecciono "Finanzas" en el campo "filtro-departamento"
    Cuando escribo "maría" en el campo "buscar-empleados"
    Entonces la tabla "tabla-empleados" muestra 1 fila
    Y la fila "fila-empleado-3" está presente en "tabla-empleados"

  Escenario: Búsqueda sin resultados muestra el mensaje correspondiente
    Dado que estoy en la pantalla del directorio de empleados
    Cuando escribo "xyz-no-existe" en el campo "buscar-empleados"
    Entonces la tabla "tabla-empleados" muestra 0 filas
    Y el elemento "sin-resultados" es visible

  Escenario: Filtro por departamento sin resultados muestra el mensaje correspondiente
    Dado que estoy en la pantalla del directorio de empleados
    Cuando selecciono "Recursos Humanos" en el campo "filtro-departamento"
    Entonces la tabla "tabla-empleados" muestra 0 filas
    Y el elemento "sin-resultados" es visible

  Escenario: Limpiar la búsqueda vuelve a mostrar todos los empleados
    Dado que escribo "ana" en el campo "buscar-empleados"
    Cuando borro el contenido del campo "buscar-empleados"
    Entonces la tabla "tabla-empleados" muestra 3 filas

# Preguntas abiertas
# - No se especifica si la búsqueda por nombre/correo es por coincidencia parcial (substring) o solo
#   por prefijo/palabra completa. Se asumió coincidencia parcial (substring) por ser lo más común
#   en un buscador de directorio; falta confirmarlo con el dueño del producto.
# - No se especifica si búsqueda y filtro de departamento se combinan con AND o si el filtro de
#   departamento anula la búsqueda. Se asumió que se combinan con AND (deben cumplirse ambas condiciones).
# - El contexto no documenta parámetros de query de la API (por ejemplo `?buscar=` o `?departamento=`)
#   para `GET /api/empleados`; se usó el endpoint base y se describió el comportamiento desde la pantalla.
# - No se especifica si existe paginación ni orden por defecto de las filas en el directorio.
