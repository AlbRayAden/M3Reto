# Changelog

Cambios relevantes a los agentes, validadores, flujos y contexto de la fábrica para el reto HU-10.

## Contexto

- Se agregó `historias/HU-10-solicitar-vacaciones.md`, `contexto/reglas_vacaciones.md` y `contexto/convenciones_vacaciones.md`.
- Las reglas y convenciones se anexaron a `contexto/reglas_negocio.md` y `contexto/convenciones_app.md`, que son los archivos que reciben los agentes.

## Agentes

- **Analista:** lee también `convenciones_app.md`, copia los mensajes letra por letra e incluye casos límite. Se imprime qué rechaza el validador.
- **Diseñador de pruebas:** incluye fechas y estado previo en cada caso. Tras cortarse por `max_tokens` con 20 escenarios, ahora escribe un caso de API por escenario, máximo 8 E2E y pasos cortos.
- **Desarrollador:** extiende sin reescribir, copia literalmente rutas y mensajes, respeta el orden de validación y calcula las reglas en el backend.
- **Automatizador:** un empleado nuevo por prueba, fechas fijas y comparación exacta. Usa `expect` de Playwright, porque las aserciones inmediatas daban resultados inestables.
- **Triage:** recibe las convenciones y clasifica como culpa de la prueba las aserciones sin espera.

## Validadores

- `mensajes_requeridos()` extrae los mensajes exactos de las convenciones que cita la historia.
- `validar_gherkin()` y `validar_plan()` rechazan una salida a la que le falte alguno de esos mensajes. Las historias que no citan convenciones propias se validan igual que antes.

## Flujos

- `flujo_s4`: `SqliteSaver` en `checkpoints.sqlite`, en lugar de `InMemorySaver`.
- `flujo_s4`: nodo `escalar` con `interrupt`; tras `MAX_CICLOS` una persona decide quién corrige, con una sola escalada.
- `flujo_s2.ejecutar()`: retoma un hilo en pausa. La opción `--nuevo` descarta esa ejecución y empieza de cero.

## Hooks

- Sin cambios: `seguridad/hooks.py` se mantiene intacto.

## Dependencias y repositorio

- Se agregó `langgraph-checkpoint-sqlite` y se retiró `chromium`, un paquete de PyPI vacío; el navegador se instala con `playwright install chromium`.
- `auditoria.jsonl` ya no se ignora, porque es parte de la entrega. Se ignora `checkpoints.sqlite*`.
- `.env.example` ya no contiene una clave.
