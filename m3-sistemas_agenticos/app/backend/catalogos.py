"""Catálogos fijos del dominio."""

DEPARTAMENTOS_VALIDOS = [
    "Tecnología",
    "Ventas",
    "Finanzas",
    "Recursos Humanos",
    "Operaciones",
]

# Festivos oficiales (Ley Federal del Trabajo, art. 74) para los años que la
# aplicación acepta en las solicitudes de vacaciones (HU-10).
FESTIVOS_POR_ANIO: dict[int, list[str]] = {
    2026: [
        "2026-01-01",
        "2026-02-02",
        "2026-03-16",
        "2026-05-01",
        "2026-09-16",
        "2026-11-16",
        "2026-12-25",
    ],
    2027: [
        "2027-01-01",
        "2027-02-01",
        "2027-03-15",
        "2027-05-01",
        "2027-09-16",
        "2027-11-15",
        "2027-12-25",
    ],
}

TOPE_DIAS_ANUAL = 12
