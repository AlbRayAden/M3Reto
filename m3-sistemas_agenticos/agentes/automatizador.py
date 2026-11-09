"""Sesión 3 · Agente 5, automatizador: casos de prueba -> pruebas con pytest y Playwright.

Uso:  python -m agentes.automatizador HU-01
"""
import sys

from agentes.base import APP, SALIDA
from agentes.claude_code import EDICION, ejecutar_claude_code

INSTRUCCIONES = """Eres el ingeniero de automatización de pruebas del equipo. Conviertes casos de prueba
en pruebas automatizadas. Nunca modificas el código de la aplicación: si una prueba falla
porque la aplicación está mal, lo reportas, no lo arreglas."""

ESCRITURA = ["tests/*"]
PROGRAMAS = {"cd", "ls", "cat", "python", "python3", "pytest"}

TAREA = """Automatiza los casos de prueba de {hu}:

{casos}

Reglas:
- tests/conftest.py define dos fixtures: `url_api` (variable URL_API, por defecto http://localhost:8000)
  y `url_web` (variable URL_WEB, por defecto http://localhost:8080). Si ya existe, consérvalo.
- Casos de nivel "api": tests/api/test_{hu_min}.py con pytest y httpx.
- Casos de nivel "e2e": tests/e2e/test_{hu_min}_e2e.py con pytest-playwright (fixture `page`),
  usando page.get_by_test_id(...) con los data-testid de CLAUDE.md.
  La pantalla responde de forma asíncrona: después de cada acción verifica siempre con `expect` de
  playwright.sync_api (to_be_visible, to_have_text, to_have_attribute), que espera al resultado.
  Nunca uses is_visible(), inner_text() o get_attribute() para afirmar justo después de una acción.
- Un test por caso; su docstring empieza con el id del caso (por ejemplo "CP-03: ...").
- Cada test crea sus propios datos con correos únicos (uuid) para poder repetirse sin choques.
  La base de datos persiste entre ejecuciones: nunca reutilices un empleado entre tests, porque lo que
  registra un test (por ejemplo, días ya usados en un año) cambiaría el resultado de otro.
- Si un caso depende de fechas (antigüedad, saldos por año), crea el empleado con la fecha_ingreso que dan
  los datos del caso y usa esas fechas fijas; nunca calcules fechas a partir de hoy. En las consultas por año
  manda siempre el año de forma explícita.
- Si un caso necesita un estado previo (solicitudes ya registradas, empleado dado de baja), créalo por la API
  dentro del mismo test antes de la acción que se prueba.
- Compara el código de respuesta y el mensaje con igualdad exacta (==), copiando el texto de los casos
  y de CLAUDE.md letra por letra; no uses `in` ni comparaciones parciales para los mensajes.
- Comprueba la sintaxis con `python -m pytest tests --collect-only -q`. No ejecutes las pruebas completas.
Responde con la lista de archivos y cuántos tests escribiste."""



def automatizar(hu: str, errores: str = "") -> tuple[str, float]:
    casos = (SALIDA / hu / "casos_prueba.json").read_text(encoding="utf-8")
    prompt = TAREA.format(hu=hu, casos=casos, hu_min=hu.lower().replace("-", "_"))
    if errores:
        prompt += f"\n\nEstas pruebas fallaron y el diagnóstico dice que el error está en la prueba:\n{errores}"
    return ejecutar_claude_code(prompt, agente="automatizador", cwd=APP, herramientas=EDICION,
                                escritura=ESCRITURA, programas=PROGRAMAS, instrucciones=INSTRUCCIONES)


if __name__ == "__main__":
    print(automatizar(sys.argv[1])[0])
