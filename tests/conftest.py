import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import product_service


@pytest.fixture(autouse=True)
def reset_service_state():
    """Reinicia el estado del almacén antes de cada test."""
    product_service.reset_store()
    yield
    product_service.reset_store()


@pytest.fixture
def client():
    """Cliente HTTP de prueba para interactuar con la app FastAPI."""
    with TestClient(app) as test_client:
        yield test_client

