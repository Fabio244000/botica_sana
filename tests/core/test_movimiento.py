from datetime import datetime, timedelta

import pydantic
import pytest

from core.models.enums import TipoMovimiento
from core.models.movimiento import Movimiento


# ————————————————————————————————————————————————————————————————
#   1. Creación válida
# ————————————————————————————————————————————————————————————————
def test_movimiento_valido() -> None:
    mv = Movimiento(
        lote_id=10,
        tipo=TipoMovimiento.ENTRADA,
        cantidad=5,
        motivo="compra proveedor",
    )
    # id aún None (lo asignará la capa de infraestructura)
    assert mv.id is None
    assert mv.tipo == TipoMovimiento.ENTRADA
    assert mv.cantidad == 5
    # Timestamp generado hace menos de 5 s
    assert datetime.utcnow() - mv.creado_en < timedelta(seconds=5)


# ————————————————————————————————————————————————————————————————
#   2. lote_id debe ser positivo
# ————————————————————————————————————————————————————————————————
def test_lote_id_no_positivo() -> None:
    with pytest.raises(pydantic.ValidationError):
        Movimiento(
            lote_id=0,  # inválido
            tipo="salida",
            cantidad=1,
            motivo="error",
        )


# ————————————————————————————————————————————————————————————————
#   3. cantidad debe ser > 0
# ————————————————————————————————————————————————————————————————
@pytest.mark.parametrize("qty", [0, -1])
def test_cantidad_positiva(qty) -> None:
    with pytest.raises(pydantic.ValidationError):
        Movimiento(
            lote_id=1,
            tipo="entrada",
            cantidad=qty,
            motivo="ajuste",
        )


# ————————————————————————————————————————————————————————————————
#   4. tipo fuera del enum
# ————————————————————————————————————————————————————————————————
def test_tipo_invalido() -> None:
    with pytest.raises(pydantic.ValidationError):
        Movimiento(
            lote_id=1,
            tipo="transferencia",  # no existe en TipoMovimiento
            cantidad=2,
            motivo="corrida",
        )


# ————————————————————————————————————————————————————————————————
#   5. motivo supera 120 caracteres
# ————————————————————————————————————————————————————————————————
def test_motivo_longitud_maxima() -> None:
    with pytest.raises(pydantic.ValidationError):
        Movimiento(
            lote_id=1,
            tipo="entrada",
            cantidad=1,
            motivo="x" * 121,  # 121 caracteres
        )
