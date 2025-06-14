from datetime import timedelta

from core.models.lote import Lote
from core.models.medicamento import Medicamento
from infrastructure.db import SessionLocal, engine
from infrastructure.models import *  # crea tablas para la prueba
from infrastructure.repos import LoteRepo, MedicamentoRepo


def setup_module():
    Base.metadata.create_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


def test_medicamento_repo_roundtrip():
    repo = MedicamentoRepo(SessionLocal())
    med = Medicamento(
        nombre="Paracetamol",
        principio_activo="Acetaminofén",
        laboratorio="Genfar",
        presentacion=Presentacion.TABLETA,
        precio_venta=2.5,
    )
    saved = repo.add(med)
    assert saved.id is not None
    assert repo.get(saved.id).nombre == "Paracetamol"
    assert len(list(repo.list())) == 1


def test_lote_repo_roundtrip():
    med_repo = MedicamentoRepo(SessionLocal())
    med = med_repo.add(
        Medicamento(
            nombre="Ibuprofeno",
            principio_activo="Ibuprofeno",
            presentacion="capsula",
            precio_venta=3.0,
        )
    )

    lote_repo = LoteRepo(SessionLocal())
    lote = Lote(
        codigo="L500",
        medicamento_id=med.id,
        fecha_vencimiento=date.today() + timedelta(days=180),
        stock=50,
    )
    saved = lote_repo.add(lote)
    assert saved.id is not None
    assert lote_repo.get(saved.id).codigo == "L500"
    assert len(list(lote_repo.list())) == 1
