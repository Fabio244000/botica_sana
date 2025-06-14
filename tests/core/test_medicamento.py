from datetime import datetime, timedelta

import pydantic
import pytest

from core.models.enums import Presentacion
from core.models.medicamento import Medicamento


# ————————————————————————————————————————————————————————————————
#   1. Creación válida
# ————————————————————————————————————————————————————————————————
def test_medicamento_valid() -> None:
    med = Medicamento(
        nombre="Amoxicilina",
        principio_activo="Amoxicilina",
        presentacion=Presentacion.CAPSULA,
        precio_venta=5.25,
        laboratorio="Acme Labs",
    )
    assert med.nombre == "Amoxicilina"
    assert med.presentacion == Presentacion.CAPSULA
    assert isinstance(med.precio_venta, float)
    # timestamp reciente (±5 s)
    assert datetime.utcnow() - med.creado_en < timedelta(seconds=5)


# ————————————————————————————————————————————————————————————————
#   2. Nombre demasiado corto
# ————————————————————————————————————————————————————————————————
def test_nombre_min_longitud() -> None:
    with pytest.raises(pydantic.ValidationError):
        Medicamento(
            nombre="Ib",  # < 3 caracteres
            principio_activo="Ibuprofeno",
            presentacion="tableta",
            precio_venta=3.0,
        )


# ————————————————————————————————————————————————————————————————
#   3. Precio debe ser positivo
# ————————————————————————————————————————————————————————————————
@pytest.mark.parametrize("precio", [0, -1, -0.01])
def test_precio_positivo(precio) -> None:
    with pytest.raises(pydantic.ValidationError):
        Medicamento(
            nombre="Paracetamol",
            principio_activo="Acetaminofén",
            presentacion="tableta",
            precio_venta=precio,
        )


# ————————————————————————————————————————————————————————————————
#   4. Presentación inválida
# ————————————————————————————————————————————————————————————————
def test_presentacion_invalida() -> None:
    with pytest.raises(pydantic.ValidationError):
        Medicamento(
            nombre="Cetirizina",
            principio_activo="Cetirizina",
            presentacion="jarabeee",  # valor fuera del enum
            precio_venta=2.8,
        )
