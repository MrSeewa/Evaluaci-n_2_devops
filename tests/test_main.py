import pytest
from app.services import ProductService


def test_root_endpoint(client):
    """Verifica que el endpoint raíz responda correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "version" in data
    assert data["docs"] == "/docs"


def test_health_check_endpoint(client):
    """Verifica el healthcheck para Docker y Kubernetes."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Product Inventory Microservice"
    assert "version" in data
    assert "environment" in data


def test_list_products_default(client):
    """Verifica el listado de productos precargados."""
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_list_products_filter_category(client):
    """Verifica el filtro por categoría existente."""
    response = client.get("/api/v1/products?category=Periféricos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for item in data:
        assert item["category"] == "Periféricos"


def test_list_products_filter_category_empty(client):
    """Verifica filtro por categoría sin coincidencias."""
    response = client.get("/api/v1/products?category=Inexistente")
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_product_by_id_success(client):
    """Verifica la obtención de un producto existente."""
    response = client.get("/api/v1/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Laptop Pro 15"
    assert data["price"] == 1200.0


def test_get_product_by_id_not_found(client):
    """Verifica error 404 al buscar producto inexistente."""
    response = client.get("/api/v1/products/9999")
    assert response.status_code == 404
    data = response.json()
    assert "no encontrado" in data["detail"].lower()


def test_create_product_success(client):
    """Verifica la creación exitosa de un producto (201 Created)."""
    payload = {
        "name": "Monitor UltraWide 34",
        "description": "Pantalla curva 144Hz IPS",
        "price": 450.50,
        "stock": 8,
        "category": "Monitores"
    }
    response = client.post("/api/v1/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == payload["name"]
    assert data["price"] == 450.50
    assert data["stock"] == 8

    # Verificar que ahora aparece en el listado
    get_res = client.get(f"/api/v1/products/{data['id']}")
    assert get_res.status_code == 200


def test_create_product_invalid_data(client):
    """Verifica que validaciones de esquema fallen (422) con datos inválidos."""
    # Precio negativo
    bad_price_payload = {
        "name": "Producto Inválido",
        "price": -10.0,
        "stock": 5,
        "category": "Test"
    }
    response = client.post("/api/v1/products", json=bad_price_payload)
    assert response.status_code == 422

    # Stock negativo
    bad_stock_payload = {
        "name": "Producto Inválido",
        "price": 50.0,
        "stock": -1,
        "category": "Test"
    }
    response = client.post("/api/v1/products", json=bad_stock_payload)
    assert response.status_code == 422

    # Nombre vacío
    empty_name_payload = {
        "name": "",
        "price": 50.0,
        "stock": 5,
        "category": "Test"
    }
    response = client.post("/api/v1/products", json=empty_name_payload)
    assert response.status_code == 422


def test_update_product_success(client):
    """Verifica actualización de producto existente."""
    update_payload = {
        "price": 1050.00,
        "stock": 7
    }
    response = client.put("/api/v1/products/1", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 1050.00
    assert data["stock"] == 7
    assert data["name"] == "Laptop Pro 15"  # Se mantiene intacto


def test_update_product_not_found(client):
    """Verifica error 404 al intentar actualizar producto inexistente."""
    response = client.put("/api/v1/products/9999", json={"price": 50.0})
    assert response.status_code == 404


def test_delete_product_success(client):
    """Verifica eliminación de producto existente (204 No Content)."""
    response = client.delete("/api/v1/products/2")
    assert response.status_code == 204

    # Verificar que ya no existe
    get_res = client.get("/api/v1/products/2")
    assert get_res.status_code == 404


def test_delete_product_not_found(client):
    """Verifica error 404 al intentar eliminar producto inexistente."""
    response = client.delete("/api/v1/products/9999")
    assert response.status_code == 404


def test_apply_discount_business_logic(client):
    """Verifica la lógica de negocio del cálculo de descuentos."""
    # Producto 1 cuesta 1200.00. Con 10% de descuento debe quedar en 1080.00
    response = client.post("/api/v1/products/1/apply-discount", json={"percentage": 10.0})
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 1080.00


def test_apply_discount_invalid_percentages(client):
    """Verifica validación de rangos para descuentos (0 < percentage < 100)."""
    # 0% no es permitido
    res_zero = client.post("/api/v1/products/1/apply-discount", json={"percentage": 0})
    assert res_zero.status_code == 422

    # 100% no es permitido
    res_hundred = client.post("/api/v1/products/1/apply-discount", json={"percentage": 100})
    assert res_hundred.status_code == 422

    # Negativo no es permitido
    res_neg = client.post("/api/v1/products/1/apply-discount", json={"percentage": -5})
    assert res_neg.status_code == 422


def test_apply_discount_product_not_found(client):
    """Verifica error 404 al aplicar descuento a producto inexistente."""
    response = client.post("/api/v1/products/9999/apply-discount", json={"percentage": 15.0})
    assert response.status_code == 404


def test_product_service_direct_unit_tests():
    """Pruebas unitarias directas sobre ProductService para cobertura de ramas."""
    service = ProductService()
    service.reset_store()

    # Probar excepción de rango en apply_discount directamente
    with pytest.raises(ValueError):
        service.apply_discount(1, 0.0)

    with pytest.raises(ValueError):
        service.apply_discount(1, 150.0)

    # Probar descuento en producto que no existe
    res = service.apply_discount(999, 20.0)
    assert res is None

    # Probar borrado de id no existente
    assert service.delete_product(999) is False

    # Probar actualización de id no existente
    from app.schemas import ProductUpdate
    assert service.update_product(999, ProductUpdate(name="Test")) is None

