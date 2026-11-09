# Decisiones · HU-10 Solicitar vacaciones

## 1. ¿Qué pasos son workflow y cuáles agente? ¿Por qué?

El orden es workflow: `construir_grafo()` fija filtro → criterios → casos → plan → código → despliegue y pruebas → triage, porque no cambia entre historias. Son agentes los pasos donde el modelo decide cómo trabajar: analista, diseñador, desarrollador, despliegue y automatizador eligen qué leer y cuántas veces escribir. El triage solo elige a quién enrutar, con salida estructurada. Verificar la app y correr pytest es código sin LLM.

## 2. ¿Cómo se validó cada salida? ¿Qué atrapó algún validador?

Los criterios pasan por `validar_gherkin`, y agregué `mensajes_requeridos()`, que exige los 9 mensajes exactos de las convenciones. Los casos pasan por Pydantic y `validar_plan` (cada escenario cubierto, cada mensaje presente). El código pasa por `verificar_app` y, al final, por pytest contra los contenedores. En HU-10 el validador rechazó el primer intento del analista: «El escenario 12 no tiene 'Dado'»; el segundo lo corrigió y quedaron 13 escenarios (reflexión con máximo 2 intentos). El resultado final fue 64 pruebas pasadas y 4 omitidas, sin ciclos de corrección. Además comprobé la API a mano con los ejemplos de las reglas: 8 días con 4 restantes y el aniversario exacto. HU-03 se procesó después de HU-10, porque el 409 de empleado dado de baja necesitaba su ruta de baja: lo comprobé contra la API y la suite completa quedó en 79 pasadas y 4 omitidas.

## 3. ¿Dónde intervine como persona y qué vi para decidir?

En dos pausas (humano en el bucle). Primero, en las preguntas abiertas: continué porque el límite del 29 de febrero no se puede alcanzar con solicitudes de 2026 y 2027, y `?anio=2028` no está definido en las reglas. Después, aprobé el plan al ver que extendía el código sin reemplazarlo, calculaba los días en el backend y seguía el orden de validación. El plan no mencionaba `dias_restantes` ni el texto exacto de éxito; lo aprobé sin rechazarlo y verifiqué ambos después en la API y en el front-end. En HU-01 intervine también en la escalada.

## 4. ¿Qué arquitectura usa la fábrica y por qué no otra?

Un workflow con supervisor determinista: el centro es código, y `salida/HU-xx/` funciona como pizarra en disco. Despliegue y automatización corren en paralelo y construir ↔ verificar es evaluador-optimizador. No usé un supervisor LLM porque el orden no varía y añadiría costo y variación sin ganar nada. Traspasos o red servirían para conversaciones o exploración abierta, no para etapas fijas con contratos.

## 5. ¿Qué corregí en el agente y por qué no en su resultado?

Corregir el resultado arregla una vez y rompe la auditoría; corregir al agente sirve para todas las historias.

- **Analista:** solo leía `reglas_negocio.md`, pero los mensajes están en las convenciones. Le agregué esa lectura y el validador de mensajes.
- **Diseñador:** se cortó por `max_tokens` con 20 escenarios en HU-01. En vez de subir el límite, le pedí un caso de API por escenario, máximo 8 E2E y pasos cortos.
- **Automatizador y triage:** en HU-01 quedaron 3 fallos E2E tras 2 ciclos, y el resultado cambiaba entre corridas. Las pruebas afirmaban con `is_visible()` justo después del clic. El triage culpó al desarrollador; escalé al automatizador, le exigí `expect` y enseñé ese patrón al triage. HU-02 y HU-10 ya pasaron sin ciclos.
