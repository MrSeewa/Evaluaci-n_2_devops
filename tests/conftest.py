import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import servicio_producto


@pytest.fixture(autouse=True)
def reiniciar_estado_servicio():
    """Reinicia el estado del almacén antes y después de cada prueba."""
    servicio_producto.reiniciar_almacen()
    yield
    servicio_producto.reiniciar_almacen()


@pytest.fixture
def cliente():
    """Cliente HTTP de prueba para interactuar con la aplicación FastAPI."""
    with TestClient(app) as cliente_prueba:
        yield cliente_prueba


# Alias para retrocompatibilidad
@pytest.fixture
def client(cliente):
    return cliente
