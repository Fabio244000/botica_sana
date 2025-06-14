from enum import Enum


class Presentacion(str, Enum):
    """Formas farmacéuticas admitidas en la botica."""

    TABLETA = "tableta"
    CAPSULA = "capsula"
    JARABE = "jarabe"
    CREMA = "crema"
    SOLUCION = "solucion"


class TipoMovimiento(str, Enum):
    """Identifica si es entrada o salida de inventario."""

    ENTRADA = "entrada"
    SALIDA = "salida"
