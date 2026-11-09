# Reporte · HU-03

**Estado:** LISTA
**Costo de agentes:** 3.92 USD
**Ciclos de corrección:** 2

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (15 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 1 failed, 78 passed, 4 skipped, 1 warning in 8.76s
- Triage → desarrollador: La pantalla renderiza dos elementos con el mismo data-testid="empleado-puesto": uno en el formulario de registro de un nuevo empleado y otro en el formulario de edición del empleado existente. Al estar ambos formularios presentes en el DOM simultáneamente (por ejemplo, uno visible para alta y otro para edición en la misma vista), el selector get_by_test_id("empleado-puesto") resuelve a 2 elementos, violando el modo estricto de Playwright. Las convenciones de la aplicación exigen que cada data-testid identifique de forma única al elemento correspondiente según el contexto (edición vs. registro), por lo que la aplicación debe distinguir ambos campos (p. ej. ocultando/desmontando el formulario de registro mientras se edita, o usando un contenedor/testid distinto para cada formulario) para que el criterio de aceptación de edición pueda cumplirse sin ambigüedad.
- Código corregido; redespliegue OK
- Pruebas E2E: 1 failed, 78 passed, 4 skipped, 1 warning in 14.82s
- Triage → desarrollador: Al editar un empleado (caso de prueba: editar puesto y departamento de un empleado activo) la aplicación no muestra el elemento con data-testid "mensaje-exito" tras guardar los cambios. El snapshot de la página muestra que seguimos en la vista del formulario de registro ("Registrar empleado"), lo que indica que la navegación/edición al empleado 7 y el guardado no completaron el flujo esperado ni renderizaron el mensaje de confirmación definido en el criterio de aceptación.
- Código corregido; redespliegue OK
- Pruebas E2E: 79 passed, 4 skipped, 1 warning in 9.84s

## Última ejecución de pruebas
```
79 passed, 4 skipped, 1 warning in 9.84s

```