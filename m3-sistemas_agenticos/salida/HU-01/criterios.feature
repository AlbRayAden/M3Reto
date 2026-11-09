# language: es
Característica: Registrar empleado
  Como persona del área de Recursos Humanos
  quiero registrar a un empleado con su nombre, correo corporativo, puesto, departamento y fecha de ingreso
  para darlo de alta en la empresa

  Escenario: Registrar un empleado con datos válidos
    Dado que no existe ningún empleado con el correo "ana.lopez@empresa.com"
    Cuando registro un empleado con nombre "Ana López", correo "ana.lopez@empresa.com", puesto "Analista de Datos", departamento "Tecnología" y fecha de ingreso "2024-01-15"
    Entonces la respuesta tiene el código 201
    Y el empleado creado tiene numero_empleado "EMP-0001"
    Y el empleado creado tiene estado "activo"
    Y la pantalla muestra el mensaje de éxito con el número de empleado asignado

  Escenario: El número de empleado es consecutivo al registrar un segundo empleado
    Dado que ya existe el empleado con numero_empleado "EMP-0001"
    Cuando registro un empleado con nombre "Carlos Ruiz", correo "carlos.ruiz@empresa.com", puesto "Vendedor", departamento "Ventas" y fecha de ingreso "2024-02-01"
    Entonces la respuesta tiene el código 201
    Y el empleado creado tiene numero_empleado "EMP-0002"

  Escenario: Rechazar un correo duplicado sin importar mayúsculas
    Dado que ya existe un empleado registrado con el correo "ana.lopez@empresa.com"
    Cuando registro un empleado con nombre "Ana Lopez Segunda", correo "Ana.Lopez@Empresa.com", puesto "Analista Junior", departamento "Tecnología" y fecha de ingreso "2024-03-01"
    Entonces la respuesta tiene el código 409
    Y el mensaje de error es "El correo ya está registrado"

  Escenario: Guardar el correo en minúsculas aunque se capture con mayúsculas
    Dado que no existe ningún empleado con el correo "maria.perez@empresa.com"
    Cuando registro un empleado con nombre "María Pérez", correo "Maria.Perez@EMPRESA.com", puesto "Contadora", departamento "Finanzas" y fecha de ingreso "2024-01-10"
    Entonces la respuesta tiene el código 201
    Y el empleado creado tiene el correo "maria.perez@empresa.com"

  Escenario: Rechazar un correo que no es corporativo
    Dado que no existe ningún empleado con el correo "jorge.diaz@gmail.com"
    Cuando registro un empleado con nombre "Jorge Díaz", correo "jorge.diaz@gmail.com", puesto "Técnico", departamento "Operaciones" y fecha de ingreso "2024-01-20"
    Entonces la respuesta tiene el código 422
    Y el mensaje de error es "Usa el correo corporativo @empresa.com"

  Escenario: Rechazar un nombre demasiado corto
    Dado que no existe ningún empleado con el correo "a@empresa.com"
    Cuando registro un empleado con nombre "A", correo "a@empresa.com", puesto "Auxiliar", departamento "Operaciones" y fecha de ingreso "2024-01-20"
    Entonces la respuesta tiene el código 422
    Y la pantalla indica que el campo "nombre" debe corregirse

  Escenario: Aceptar un nombre con exactamente 2 caracteres
    Dado que no existe ningún empleado con el correo "jo@empresa.com"
    Cuando registro un empleado con nombre "Jo", correo "jo@empresa.com", puesto "Auxiliar Operativo", departamento "Operaciones" y fecha de ingreso "2024-01-20"
    Entonces la respuesta tiene el código 201

  Escenario: Rechazar un nombre que supera los 80 caracteres
    Dado que no existe ningún empleado con el correo "nombre.largo@empresa.com"
    Cuando registro un empleado con nombre "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" (81 caracteres), correo "nombre.largo@empresa.com", puesto "Gerente", departamento "Finanzas" y fecha de ingreso "2024-01-20"
    Entonces la respuesta tiene el código 422
    Y la pantalla indica que el campo "nombre" debe corregirse

  Escenario: Aceptar un nombre con exactamente 80 caracteres
    Dado que no existe ningún empleado con el correo "nombre.limite@empresa.com"
    Cuando registro un empleado con nombre "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" (80 caracteres), correo "nombre.limite@empresa.com", puesto "Gerente", departamento "Finanzas" y fecha de ingreso "2024-01-20"
    Entonces la respuesta tiene el código 201

  Escenario: Rechazar un puesto demasiado corto
    Dado que no existe ningún empleado con el correo "puesto.corto@empresa.com"
    Cuando registro un empleado con nombre "Luis Gómez", correo "puesto.corto@empresa.com", puesto "A", departamento "Ventas" y fecha de ingreso "2024-01-20"
    Entonces la respuesta tiene el código 422
    Y la pantalla indica que el campo "puesto" debe corregirse

  Escenario: Aceptar un puesto con exactamente 60 caracteres
    Dado que no existe ningún empleado con el correo "puesto.limite@empresa.com"
    Cuando registro un empleado con nombre "Luis Gómez", correo "puesto.limite@empresa.com", puesto "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB" (60 caracteres), departamento "Ventas" y fecha de ingreso "2024-01-20"
    Entonces la respuesta tiene el código 201

  Escenario: Rechazar un puesto que supera los 60 caracteres
    Dado que no existe ningún empleado con el correo "puesto.largo@empresa.com"
    Cuando registro un empleado con nombre "Luis Gómez", correo "puesto.largo@empresa.com", puesto "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB" (61 caracteres), departamento "Ventas" y fecha de ingreso "2024-01-20"
    Entonces la respuesta tiene el código 422
    Y la pantalla indica que el campo "puesto" debe corregirse

  Escenario: Rechazar un departamento que no está en el catálogo
    Dado que el catálogo de departamentos válidos es "Tecnología, Ventas, Finanzas, Recursos Humanos, Operaciones"
    Cuando registro un empleado con nombre "Sofía Torres", correo "depto.invalido@empresa.com", puesto "Analista", departamento "Marketing" y fecha de ingreso "2024-01-20"
    Entonces la respuesta tiene el código 422
    Y la pantalla indica que el campo "departamento" debe corregirse

  Escenario: Rechazar una fecha de ingreso futura
    Dado que la fecha de hoy es "2026-06-15"
    Cuando registro un empleado con nombre "Pedro Sánchez", correo "pedro.sanchez@empresa.com", puesto "Desarrollador", departamento "Tecnología" y fecha de ingreso "2026-06-16"
    Entonces la respuesta tiene el código 422
    Y el mensaje de error es "La fecha de ingreso no puede ser futura"

  Escenario: Aceptar una fecha de ingreso igual al día de hoy
    Dado que la fecha de hoy es "2026-06-15"
    Cuando registro un empleado con nombre "Pedro Sánchez", correo "pedro.sanchez2@empresa.com", puesto "Desarrollador", departamento "Tecnología" y fecha de ingreso "2026-06-15"
    Entonces la respuesta tiene el código 201

  Escenario: Aceptar una fecha de ingreso un día antes de hoy
    Dado que la fecha de hoy es "2026-06-15"
    Cuando registro un empleado con nombre "Laura Méndez", correo "laura.mendez@empresa.com", puesto "Diseñadora", departamento "Recursos Humanos" y fecha de ingreso "2026-06-14"
    Entonces la respuesta tiene el código 201

  Esquema del escenario: Rechazar el registro cuando falta un campo obligatorio
    Dado que no existe ningún empleado con el correo "<correo>"
    Cuando registro un empleado con nombre "<nombre>", correo "<correo>", puesto "<puesto>", departamento "<departamento>" y fecha de ingreso "<fecha_ingreso>"
    Entonces la respuesta tiene el código 422
    Y la pantalla indica que el campo "<campo_faltante>" debe corregirse

    Ejemplos:
      | nombre      | correo                   | puesto   | departamento | fecha_ingreso | campo_faltante |
      |             | sinnombre@empresa.com    | Analista | Ventas       | 2024-01-10    | nombre         |
      | Marco Vidal |                          | Analista | Ventas       | 2024-01-10    | correo         |
      | Marco Vidal | marco.vidal@empresa.com  |          | Ventas       | 2024-01-10    | puesto         |
      | Marco Vidal | marco.vidal2@empresa.com | Analista | Ventas       |               | fecha_ingreso  |

  Escenario: El estado inicial de un empleado registrado es activo
    Dado que no existe ningún empleado con el correo "nuevo.ingreso@empresa.com"
    Cuando registro un empleado con nombre "Nuevo Ingreso", correo "nuevo.ingreso@empresa.com", puesto "Becario", departamento "Operaciones" y fecha de ingreso "2024-01-01"
    Entonces la respuesta tiene el código 201
    Y el empleado creado tiene estado "activo"

# Preguntas abiertas
# - Las reglas de negocio no especifican el texto exacto del detalle de error 422 para "cualquier otro dato inválido"
#   (regla 3); se asumió que la pantalla únicamente señala el nombre del campo a corregir, sin un mensaje fijo documentado.
# - No se especifica si al faltar varios campos obligatorios a la vez la API reporta todos o solo el primero;
#   los escenarios del esquema cubren un campo faltante a la vez por falta de esa definición.
