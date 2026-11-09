# Fábrica de software con agentes · Módulo 3

Una cadena de seis agentes que convierte una historia de usuario en una aplicación de gestión de empleados desplegada y probada:

| # | Agente | Entrada | Salida | Sesión |
| --- | --- | --- | --- | --- |
| 1 | Analista | Historia de usuario | `salida/HU-xx/criterios.feature` | 1 |
| 2 | Diseñador de pruebas | Criterios | `salida/HU-xx/casos_prueba.json` | 1 |
| 3 | Desarrollador (Claude Code) | Criterios y casos | `app/backend`, `app/frontend` | 2 |
| 4 | Despliegue (Claude Code) | Código | Contenedores con Docker Compose | 3 |
| 5 | Automatizador (Claude Code) | Casos de prueba | `app/tests` (pytest + Playwright) | 3 |
| 6 | Flujo E2E con triage | Pruebas y app desplegada | `salida/HU-xx/reporte.md` | 4 |

## Requisitos

Python 3.12, Node 20 o superior, Docker Desktop, Claude Code y una clave de API de Anthropic con créditos.

**Mac o Linux**

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt
playwright install chromium
cp .env.example .env        # escribe ANTHROPIC_API_KEY, MODEL y PRESUPUESTO_USD
```

**Windows (PowerShell)**

```powershell
uv venv --python 3.12; .venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
playwright install chromium
Copy-Item .env.example .env   # escribe ANTHROPIC_API_KEY, MODEL y PRESUPUESTO_USD
```

Usa una ruta de carpeta sin espacios ni dos puntos: un `:` en la ruta rompe `PYTHONPATH` y puede romper los volúmenes de Docker. `.env` nunca se sube al repositorio.

## Uso

```bash
# Sesión 1: agentes por separado
python -m agentes.analista historias/HU-01-registrar-empleado.md
python -m agentes.disenador_pruebas salida/HU-01/criterios.feature

# Sesiones 2 a 4: la fábrica completa, cada vez con más agentes
python -m flujos.flujo_s2 historias/HU-01-registrar-empleado.md
python -m flujos.flujo_s3 historias/HU-01-registrar-empleado.md
python -m flujos.flujo_s4 historias/HU-01-registrar-empleado.md
```

Los patrones de cada sesión también tienen un ejemplo corto y ejecutable en [`ejemplos/`](ejemplos/README.md), por ejemplo `python -m ejemplos.s2_flujos.enrutamiento`.

La aplicación queda en http://localhost:8080 y la documentación de la API en http://localhost:8000/docs.

## Reto HU-10 · Solicitar vacaciones

El flujo se detiene para que una persona responda las preguntas abiertas y apruebe el plan. Si cierras la terminal en una pausa, el mismo comando la retoma, porque el estado se guarda en `checkpoints.sqlite`.

```bash
python -m flujos.flujo_s4 historias/HU-10-solicitar-vacaciones.md           # empieza o retoma
python -m flujos.flujo_s4 historias/HU-10-solicitar-vacaciones.md --nuevo   # descarta la pausa y empieza de cero
```

Si tras 2 ciclos las pruebas siguen fallando, la fábrica escala a una persona, que responde `desarrollador: <instrucción>`, `automatizador: <instrucción>`, `despliegue: <instrucción>` o `fin`.

**Ejemplo de uso de la API** (con la app desplegada):

```bash
curl -X POST http://localhost:8000/api/empleados/1/vacaciones \
  -H 'Content-Type: application/json' \
  -d '{"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31"}'
curl 'http://localhost:8000/api/empleados/1/vacaciones?anio=2026'
```

## Pruebas

Con la app desplegada (`docker compose ps` desde `app/`):

```bash
cd app
python -m pytest tests -q               # Mac o Linux; en Windows, con el entorno activado, es el mismo comando
```

## Evidencia

| Qué | Dónde |
|---|---|
| Criterios, casos y reporte | `salida/HU-10/` |
| Decisiones | `salida/HU-10/decisiones.md` |
| Seguridad | `salida/seguridad.md` y `salida/bloqueada/reporte.md` |
| Auditoría de herramientas | `auditoria.jsonl` |
| Cambios a la fábrica | `CHANGELOG.md` |
