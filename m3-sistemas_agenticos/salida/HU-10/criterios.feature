# language: es
Característica: Solicitar vacaciones
  Como empleado de la empresa
  quiero solicitar días de vacaciones indicando una fecha de inicio y una de fin
  para que mi solicitud quede registrada y sepa cuántos días me quedan en el año

  # El orden de validación es el de la tabla de convenciones_vacaciones.md:
  # empleado no existe > empleado de baja > fecha_fin < fecha_inicio > periodo cruza de año
  # > año fuera de tabla de festivos > antigüedad (regla 1) > sin días hábiles (regla 3)
  # > rebasa el tope (regla 2).

  Escenario: Camino feliz - se registra la solicitud descontando festivos y fines de semana
    Dado un empleado activo con id 7, número "EMP-0007" y fecha de ingreso "2024-01-10"
    Y que no ha usado ningún día hábil de vacaciones en 2026
    Cuando solicita vacaciones del "2026-09-14" al "2026-09-18"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" es 4
    Y el campo "dias_restantes" es 8
    Y el mensaje mostrado en "vacaciones-mensaje" es exactamente "Solicitud registrada: 4 días hábiles. Te quedan 8 días hábiles en 2026."

  Escenario: Camino feliz - consultar el saldo del año tras registrar una solicitud
    Dado un empleado activo con id 7, número "EMP-0007" y fecha de ingreso "2024-01-10"
    Y que registró una solicitud del "2026-12-21" al "2026-12-31" de 8 días hábiles
    Cuando consulta su saldo de vacaciones del año 2026
    Entonces la respuesta tiene código 200
    Y el campo "dias_usados" es 8
    Y el campo "dias_disponibles" es 4
    Y la lista "solicitudes" incluye la solicitud del "2026-12-21" al "2026-12-31" con 8 días hábiles

  Escenario: Regla 2 (límite) - usar exactamente los días hábiles que quedan en el año
    Dado un empleado activo con id 7, número "EMP-0007" y fecha de ingreso "2024-01-10"
    Y que ya usó 5 días hábiles de vacaciones en 2026
    Cuando solicita vacaciones del "2026-07-13" al "2026-07-21"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" es 7
    Y el campo "dias_restantes" es 0
    Y el mensaje mostrado en "vacaciones-mensaje" es exactamente "Solicitud registrada: 7 días hábiles. Te quedan 0 días hábiles en 2026."

  Escenario: Regla 2 (error) - pasarse del tope por un solo día hábil
    Dado un empleado activo con id 7, número "EMP-0007" y fecha de ingreso "2024-01-10"
    Y que ya usó 4 días hábiles de vacaciones en 2026
    Cuando solicita vacaciones del "2026-08-03" al "2026-08-13"
    Entonces la respuesta tiene código 400
    Y el campo "detail" es exactamente "La solicitud excede los días disponibles: quedan 8 días hábiles"

  Escenario: Regla 2 (error) - el tope del año ya está agotado
    Dado un empleado activo con id 7, número "EMP-0007" y fecha de ingreso "2024-01-10"
    Y que ya usó 12 días hábiles de vacaciones en 2026
    Cuando solicita vacaciones del "2026-10-05" al "2026-10-05"
    Entonces la respuesta tiene código 400
    Y el campo "detail" es exactamente "La solicitud excede los días disponibles: quedan 0 días hábiles"

  Escenario: Regla 1 (límite) - cumple exactamente un año de antigüedad el día de inicio
    Dado un empleado activo con id 8, número "EMP-0008" y fecha de ingreso "2025-12-21"
    Y que no ha usado ningún día hábil de vacaciones en 2026
    Cuando solicita vacaciones del "2026-12-21" al "2026-12-21"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" es 1
    Y el campo "dias_restantes" es 11

  Escenario: Regla 1 (error) - le falta un día para cumplir el año de antigüedad
    Dado un empleado activo con id 8, número "EMP-0008" y fecha de ingreso "2025-12-21"
    Cuando solicita vacaciones del "2026-12-20" al "2026-12-20"
    Entonces la respuesta tiene código 400
    Y el campo "detail" es exactamente "Se requiere al menos un año de antigüedad a la fecha de inicio"

  Escenario: Regla 3 (error) - el periodo cae completo en fin de semana y no tiene días hábiles
    Dado un empleado activo con id 7, número "EMP-0007" y fecha de ingreso "2024-01-10"
    Cuando solicita vacaciones del "2026-07-11" al "2026-07-12"
    Entonces la respuesta tiene código 400
    Y el campo "detail" es exactamente "El periodo no incluye días hábiles"

  Escenario: Error - la fecha de fin es anterior a la fecha de inicio
    Dado un empleado activo con id 7, número "EMP-0007" y fecha de ingreso "2024-01-10"
    Cuando solicita vacaciones del "2026-07-10" al "2026-07-05"
    Entonces la respuesta tiene código 400
    Y el campo "detail" es exactamente "La fecha de fin no puede ser anterior a la fecha de inicio"

  Escenario: Error - el periodo cruza de un año calendario a otro
    Dado un empleado activo con id 7, número "EMP-0007" y fecha de ingreso "2024-01-10"
    Cuando solicita vacaciones del "2026-12-28" al "2027-01-08"
    Entonces la respuesta tiene código 400
    Y el campo "detail" es exactamente "Las vacaciones deben estar dentro de un mismo año calendario"

  Escenario: Error - el año solicitado no está en la tabla de festivos
    Dado un empleado activo con id 7, número "EMP-0007" y fecha de ingreso "2024-01-10"
    Cuando solicita vacaciones del "2028-01-10" al "2028-01-14"
    Entonces la respuesta tiene código 400
    Y el campo "detail" es exactamente "Solo se pueden solicitar vacaciones en 2026 y 2027"

  Escenario: Error - el empleado no existe
    Dado que no existe ningún empleado registrado con id 9999
    Cuando solicita vacaciones para el empleado con id 9999 del "2026-07-06" al "2026-07-10"
    Entonces la respuesta tiene código 404
    Y el campo "detail" es exactamente "Empleado no encontrado"

  Escenario: Error - el empleado está dado de baja
    Dado un empleado con id 10, número "EMP-0010", estado "baja" y fecha de ingreso "2023-01-10"
    Cuando solicita vacaciones del "2026-07-06" al "2026-07-10"
    Entonces la respuesta tiene código 409
    Y el campo "detail" es exactamente "No se pueden solicitar vacaciones para un empleado dado de baja"

  # Preguntas abiertas
  # - Las reglas describen que cuando `fecha_ingreso` es 29 de febrero, el aniversario en un año
  #   no bisiesto cae el 1 de marzo. No se pudo construir un escenario de ese límite exacto porque
  #   la API solo acepta solicitudes en 2026 y 2027 (ambos no bisiestos) y el aniversario de un
  #   ingreso en 29 de febrero cae, como muy pronto, en 2025 o en años fuera de ese rango. Falta
  #   definir con negocio un ejemplo de ingreso en 29 de febrero cuyo primer aniversario caiga en
  #   2026 o 2027 para poder cubrir ese caso límite.
  # - No se especifica qué pasa si se solicitan vacaciones con un `anio` en la consulta de saldo
  #   (GET) que no esté en la tabla de festivos (por ejemplo 2028): ¿se responde 400, 200 con ceros,
  #   u otro comportamiento? Falta precisarlo en convenciones_vacaciones.md.
