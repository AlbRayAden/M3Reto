# language: es

Característica: Editar y dar de baja a un empleado
  Como persona del área de Recursos Humanos
  quiero cambiar el puesto y el departamento de un empleado, y poder darlo de baja
  para mantener el directorio al día sin perder el historial

  # --- Camino feliz: edición ---

  Escenario: Editar puesto y departamento de un empleado activo
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007", correo "ana@empresa.com", nombre "Ana Pérez", puesto "Analista", departamento "Ventas" y fecha_ingreso "2023-05-10"
    Cuando edito al empleado 7 con data-testid "editar-empleado-7"
    Y cambio el campo "empleado-puesto" a "Analista Senior"
    Y cambio el campo "empleado-departamento" a "Tecnología"
    Y presiono "empleado-guardar"
    Entonces la respuesta tiene código 200
    Y el mensaje en "mensaje-exito" confirma la actualización
    Y el empleado 7 tiene puesto "Analista Senior"
    Y el empleado 7 tiene departamento "Tecnología"
    Y el numero_empleado del empleado 7 sigue siendo "EMP-0007"
    Y el correo del empleado 7 sigue siendo "ana@empresa.com"

  # --- Regla: número de empleado y correo no se editan ---

  Escenario: El número de empleado y el correo no cambian aunque se envíen en la petición
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007", correo "ana@empresa.com", puesto "Analista" y departamento "Ventas"
    Cuando envío una edición del empleado 7 con correo "otro@empresa.com" y numero_empleado "EMP-9999", junto con puesto "Analista Senior" y departamento "Tecnología"
    Entonces la respuesta tiene código 200
    Y el correo del empleado 7 sigue siendo "ana@empresa.com"
    Y el numero_empleado del empleado 7 sigue siendo "EMP-0007"

  # --- Regla: puesto obligatorio, de 2 a 60 caracteres (incluye límites) ---

  Esquema del escenario: Editar el puesto en los límites exactos de longitud permitida
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007", correo "ana@empresa.com" y puesto "Analista"
    Cuando edito al empleado 7 con puesto "<puesto>"
    Entonces la respuesta tiene código <codigo>

    Ejemplos:
      | puesto                                                        | codigo |
      | AB                                                             | 200    |
      | 123456789012345678901234567890123456789012345678901234567890 | 200    |

  Escenario: Editar el puesto con 1 carácter se rechaza por ser menor al mínimo
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007", correo "ana@empresa.com" y puesto "Analista"
    Cuando edito al empleado 7 con puesto "A"
    Entonces la respuesta tiene código 422
    Y la pantalla muestra en "mensaje-error" que el campo "puesto" debe corregirse

  Escenario: Editar el puesto con 61 caracteres se rechaza por exceder el máximo
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007", correo "ana@empresa.com" y puesto "Analista"
    Cuando edito al empleado 7 con puesto "1234567890123456789012345678901234567890123456789012345678901"
    Entonces la respuesta tiene código 422
    Y la pantalla muestra en "mensaje-error" que el campo "puesto" debe corregirse

  # --- Regla: departamento debe ser uno del catálogo ---

  Escenario: Editar el departamento con un valor fuera del catálogo se rechaza
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007", correo "ana@empresa.com" y departamento "Ventas"
    Cuando edito al empleado 7 con departamento "Marketing"
    Entonces la respuesta tiene código 422
    Y la pantalla muestra en "mensaje-error" que el campo "departamento" debe corregirse

  # --- Camino feliz: dar de baja ---

  Escenario: Dar de baja a un empleado activo
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007", correo "ana@empresa.com" y fecha_ingreso "2023-05-10"
    Cuando doy de baja al empleado 7 con data-testid "baja-empleado-7"
    Y lleno "empleado-fecha-baja" con "2026-03-15"
    Y presiono "confirmar-baja"
    Entonces la respuesta tiene código 200
    Y el empleado 7 tiene estado "baja"
    Y el empleado 7 tiene fecha_baja "2026-03-15"
    Y el empleado 7 sigue apareciendo en "tabla-empleados" en la fila "fila-empleado-7"
    Y el campo "estado-empleado-7" muestra el texto "Baja"

  # --- Regla: fecha_baja no puede ser anterior a fecha_ingreso (límite exacto) ---

  Escenario: Dar de baja con fecha_baja igual a la fecha_ingreso se acepta
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007", correo "ana@empresa.com" y fecha_ingreso "2023-05-10"
    Cuando doy de baja al empleado 7 con fecha_baja "2023-05-10"
    Entonces la respuesta tiene código 200
    Y el empleado 7 tiene fecha_baja "2023-05-10"

  Escenario: Dar de baja con fecha_baja un día antes de la fecha_ingreso se rechaza
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007", correo "ana@empresa.com" y fecha_ingreso "2023-05-10"
    Cuando doy de baja al empleado 7 con fecha_baja "2023-05-09"
    Entonces la respuesta tiene código 422
    Y la pantalla muestra en "mensaje-error" que el campo "fecha_baja" debe corregirse

  # --- Regla 6: un empleado dado de baja no se puede editar ---

  Escenario: Intentar editar a un empleado dado de baja
    Dado que existe un empleado con id 7, numero_empleado "EMP-0007", correo "ana@empresa.com", puesto "Analista", estado "baja" y fecha_baja "2026-03-15"
    Cuando edito al empleado 7 con puesto "Analista Senior"
    Entonces la respuesta tiene código 409
    Y el mensaje en "mensaje-error" es "No se puede editar a un empleado dado de baja"
    Y el empleado 7 conserva su puesto "Analista"

  # --- Empleado inexistente ---

  Escenario: Intentar editar a un empleado que no existe
    Dado que no existe ningún empleado con id 999
    Cuando edito al empleado 999 con puesto "Analista Senior"
    Entonces la respuesta tiene código 404
    Y el mensaje en "mensaje-error" es "Empleado no encontrado"

  Escenario: Intentar dar de baja a un empleado que no existe
    Dado que no existe ningún empleado con id 999
    Cuando doy de baja al empleado 999 con fecha_baja "2026-03-15"
    Entonces la respuesta tiene código 404
    Y el mensaje en "mensaje-error" es "Empleado no encontrado"

# Preguntas abiertas
# - ¿El formulario de edición de HU-03 permite modificar también "nombre" y "fecha_ingreso",
#   o únicamente "puesto" y "departamento" como indica el texto de la historia? Las reglas
#   generales de "nombre" y "fecha_ingreso" (longitud, no futura) existen en reglas_negocio.md,
#   pero no está confirmado si aplican en este formulario de edición.
# - La regla 3 ("cualquier otro dato inválido responde 422 y la pantalla muestra qué campo
#   corregir") no define el texto exacto del mensaje de error; los escenarios de validación de
#   "puesto" y "departamento" y de "fecha_baja" anterior a "fecha_ingreso" asumen únicamente el
#   código 422 y que se señala el campo, sin un texto literal a verificar.
# - ¿Intentar dar de baja a un empleado que ya está en estado "baja" debe responder con error
#   (por ejemplo 409, reutilizando el mensaje de la regla 6) o es una operación sin efecto? No
#   está especificado en reglas_negocio.md.
# - No se especifica la ruta exacta de la API para editar (¿PUT o PATCH `/api/empleados/{id}`?)
#   ni para dar de baja (¿`/api/empleados/{id}/baja`?); los escenarios se describen desde la
#   pantalla y en términos de código de respuesta para no asumir una ruta no documentada.
