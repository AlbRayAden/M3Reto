# Reporte · HU-01

**Estado:** LISTA
**Costo de agentes:** 5.56 USD
**Ciclos de corrección:** 2

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (29 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 5 failed, 23 passed, 1 skipped, 1 warning in 31.92s
- Triage → desarrollador: La API no valida que la fecha_ingreso no sea futura: el escenario "Rechazar una fecha de ingreso futura" exige código 422 y mensaje "La fecha de ingreso no puede ser futura" cuando la fecha excede la fecha de hoy simulada, pero el backend está devolviendo 201, aceptando el registro. Esto arrastra también las fallas E2E relacionadas (test_cp_27 espera mensaje-error y nunca aparece porque el backend crea el empleado con éxito).
- Código corregido; redespliegue OK
- Pruebas E2E: 6 failed, 22 passed, 1 skipped, 1 warning in 32.06s
- Triage → desarrollador: La validación de fecha de ingreso futura no está implementada (o está mal implementada) en el backend: al registrar un empleado con fecha de ingreso posterior a la fecha actual, la API responde 201 en vez de 422 con el mensaje "La fecha de ingreso no puede ser futura". Esto también provoca fallos en cascada en el E2E (test_cp_27) porque el frontend nunca recibe el error para mostrar mensaje-error, y afecta otros tests que dependían de datos consistentes (test_cp_22, test_cp_25, test_cp_28, test_cp_29 fallan por botón guardar deshabilitado o mensaje no visible, posiblemente por validaciones de campos obligatorios/longitud también ausentes o mal conectadas en el formulario que depende del mismo flujo de validación del backend).
- Código corregido; redespliegue OK
- Pruebas E2E: 3 failed, 25 passed, 1 skipped, 1 warning in 1.83s
- Escalado a una persona → automatizador: las pruebas E2E afirman antes de que la pantalla responda; reescribe las aserciones con expect de Playwright
- Pruebas corregidas
- Pruebas E2E: 28 passed, 1 skipped, 1 warning in 1.92s

## Última ejecución de pruebas
```
28 passed, 1 skipped, 1 warning in 1.92s

```