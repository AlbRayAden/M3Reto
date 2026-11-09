"""Sesión 1 · Agente 1, analista: historia de usuario -> criterios de aceptación en Gherkin.

Uso:  python -m agentes.analista historias/HU-01-registrar-empleado.md
"""
import re
import sys
from pathlib import Path

from agentes.base import RAIZ, SALIDA, ejecutar_agente, herramientas_archivos, hu_de, rel

SISTEMA = """Eres analista de producto en un equipo de software. Conviertes historias de usuario
en criterios de aceptación escritos en Gherkin, en español.

Cómo trabajas:
1. Lee la historia, contexto/reglas_negocio.md y contexto/convenciones_app.md (ahí están la API,
   los códigos de respuesta y los mensajes de error exactos).
2. Escribe {destino}. La primera línea es `# language: es` y usas las palabras clave
   Característica, Escenario, Dado, Cuando, Entonces, Y.
3. Incluye el camino feliz y un escenario de error por cada regla de negocio y por cada mensaje de error
   que aplique a ESTA historia. En cada escenario de error escribe el código de respuesta y el mensaje
   copiado letra por letra (acentos y puntuación incluidos); donde el mensaje lleva un número, pon el valor concreto.
4. Incluye los casos límite que el contexto describe: por ejemplo, usar exactamente lo que queda de un tope
   y pasarse por uno, o cumplir una condición justo en la fecha límite y un día antes.
5. Cada escenario se puede verificar desde la pantalla o la API: datos concretos, nada de «funciona bien».
6. No inventes reglas. Si falta información, agrégala al final como comentarios bajo `# Preguntas abiertas`.
7. Responde al final con una sola línea: cuántos escenarios escribiste."""


def mensajes_requeridos(historia: Path) -> list[str]:
    """Mensajes exactos que la historia exige: los `detail` de las convenciones que la historia cita.

    Solo aplica si la historia menciona un archivo contexto/convenciones_*.md (por ejemplo HU-10);
    para las demás historias devuelve una lista vacía y el validador se comporta como antes.
    """
    texto = historia.read_text(encoding="utf-8")
    mensajes: list[str] = []
    for nombre in sorted(set(re.findall(r"contexto/(convenciones_[\w-]+\.md)", texto))):
        ruta = RAIZ / "contexto" / nombre
        if not ruta.exists():
            continue
        conv = ruta.read_text(encoding="utf-8")
        mensajes += re.findall(r"\|\s*\d{3}\s*\|\s*`([^`]+)`\s*\|", conv)      # filas: | código | `mensaje` |
        mensajes += re.findall(r"^.*\bexacto\b.*:\s*`([^`]+)`\s*$", conv, flags=re.MULTILINE)  # «… exacto …: `…`»
    return mensajes


def patron_mensaje(mensaje: str) -> re.Pattern:
    """Convierte un mensaje con marcadores (N, M, AAAA) en una expresión que acepta valores concretos."""
    patron = re.escape(mensaje)
    patron = re.sub(r"\bAAAA\b", lambda _: r"\d{4}", patron)
    patron = re.sub(r"\b[NM]\b", lambda _: r"\d+", patron)
    return re.compile(patron)


def mensajes_faltantes(texto: str, requeridos: list[str]) -> list[str]:
    """Los mensajes requeridos que no aparecen letra por letra en `texto`."""
    return [m for m in requeridos if not patron_mensaje(m).search(texto)]


def escenarios(gherkin: str) -> list[str]:
    return re.findall(r"^\s*Escenario:\s*(.+?)\s*$", gherkin, flags=re.MULTILINE)


def preguntas_abiertas(gherkin: str) -> list[str]:
    if "# Preguntas abiertas" not in gherkin:
        return []
    bloque = gherkin.split("# Preguntas abiertas", 1)[1]
    return [l.lstrip("# -").strip() for l in bloque.splitlines() if l.strip().lstrip("#").strip()]


def validar_gherkin(texto: str, requeridos: list[str] | None = None) -> list[str]:
    """Evaluador determinista: devuelve los problemas encontrados; vacío = válido.

    `requeridos` son los mensajes exactos que deben aparecer en algún escenario (ver mensajes_requeridos).
    """
    problemas = []
    if not texto.lstrip().startswith("# language: es"):
        problemas.append("La primera línea debe ser '# language: es'.")
    if "Característica:" not in texto:
        problemas.append("Falta 'Característica:'.")
    bloques = re.split(r"^\s*Escenario:", texto, flags=re.MULTILINE)[1:]
    if len(bloques) < 2:
        problemas.append("Se esperan al menos 2 escenarios (camino feliz y un error).")
    for i, bloque in enumerate(bloques, 1):
        for clave in ("Dado", "Cuando", "Entonces"):
            if not re.search(rf"^\s*{clave}\b", bloque, flags=re.MULTILINE):
                problemas.append(f"El escenario {i} no tiene '{clave}'.")
    for m in mensajes_faltantes(texto, requeridos or []):
        problemas.append(f"Ningún escenario usa el mensaje exacto «{m}» (cópialo letra por letra de las convenciones).")
    return problemas


def generar_criterios(historia: Path, max_intentos: int = 2) -> Path:
    carpeta = SALIDA / hu_de(historia)
    destino = carpeta / "criterios.feature"
    herramientas = herramientas_archivos(lectura=[RAIZ / "historias", RAIZ / "contexto"], escritura=carpeta)
    tarea = f"Historia de usuario: {rel(historia)}"
    requeridos = mensajes_requeridos(historia)
    for intento in range(1, max_intentos + 1):
        print(f"Analista · intento {intento}")
        ejecutar_agente(SISTEMA.format(destino=rel(destino)), herramientas, tarea, nombre="analista")
        problemas = validar_gherkin(destino.read_text(encoding="utf-8"), requeridos) if destino.exists() \
            else [f"No se escribió {rel(destino)}."]
        if not problemas:
            return destino
        # Reflexión guiada por un evaluador determinista: el agente recibe los problemas y corrige
        print("  Validador rechazó el intento:\n  - " + "\n  - ".join(problemas))   # evidencia para decisiones.md
        tarea += "\n\nTu versión anterior tiene estos problemas; corrígelos:\n- " + "\n- ".join(problemas)
    raise ValueError("Criterios inválidos tras varios intentos:\n- " + "\n- ".join(problemas))


if __name__ == "__main__":
    ruta = generar_criterios(Path(sys.argv[1]).resolve())
    texto = ruta.read_text(encoding="utf-8")
    print(f"\nListo: {rel(ruta)} · {len(escenarios(texto))} escenarios")
    for p in preguntas_abiertas(texto):
        print("  Pregunta abierta:", p)
