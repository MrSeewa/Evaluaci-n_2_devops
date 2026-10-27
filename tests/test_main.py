import pytest
from app.services import ServicioProducto
from app.schemas import ProductoActualizar


def test_endpoint_raiz(cliente):
    """Verifica que el endpoint raíz responda correctamente."""
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["estado"] == "en_linea"
    assert "version" in datos
    assert datos["documentacion"] == "/docs"


def test_endpoint_salud(cliente):
    """Verifica el healthcheck para Docker y Kubernetes."""
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["estado"] == "saludable"
    assert datos["servicio"] == "Microservicio de Inventario de Productos"
    assert "version" in datos
    assert "entorno" in datos


def test_listar_productos_por_defecto(cliente):
    """Verifica el listado de productos precargados."""
    respuesta = cliente.get("/api/v1/productos")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert isinstance(datos, list)
    assert len(datos) >= 3


def test_listar_productos_filtro_categoria(cliente):
    """Verifica el filtro por categoría existente."""
    respuesta = cliente.get("/api/v1/productos?categoria=Periféricos")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert len(datos) == 2
    for elemento in datos:
        assert elemento["categoria"] == "Periféricos"


def test_listar_productos_filtro_categoria_vacio(cliente):
    """Verifica filtro por categoría sin coincidencias."""
    respuesta = cliente.get("/api/v1/productos?categoria=Inexistente")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos == []


def test_obtener_producto_por_id_exitoso(cliente):
    """Verifica la obtención de un producto existente."""
    respuesta = cliente.get("/api/v1/productos/1")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["id"] == 1
    assert datos["nombre"] == "Laptop Pro 15"
    assert datos["precio"] == 1200.0


def test_obtener_producto_por_id_no_encontrado(cliente):
    """Verifica error 404 al buscar producto inexistente."""
    respuesta = cliente.get("/api/v1/productos/9999")
    assert respuesta.status_code == 404
    datos = respuesta.json()
    assert "no encontrado" in datos["detail"].lower()


def test_crear_producto_exitoso(cliente):
    """Verifica la creación exitosa de un producto (201 Created)."""
    carga_util = {
        "nombre": "Monitor UltraWide 34",
        "descripcion": "Pantalla curva 144Hz IPS",
        "precio": 450.50,
        "stock": 8,
        "categoria": "Monitores"
    }
    respuesta = cliente.post("/api/v1/productos", json=carga_util)
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["id"] is not None
    assert datos["nombre"] == carga_util["nombre"]
    assert datos["precio"] == 450.50
    assert datos["stock"] == 8

    # Verificar que ahora aparece en el listado
    respuesta_consulta = cliente.get(f"/api/v1/productos/{datos['id']}")
    assert respuesta_consulta.status_code == 200


def test_crear_producto_datos_invalidos(cliente):
    """Verifica que validaciones de esquema fallen (422) con datos inválidos."""
    # Precio negativo
    precio_invalido = {
        "nombre": "Producto Inválido",
        "precio": -10.0,
        "stock": 5,
        "categoria": "Test"
    }
    respuesta_precio = cliente.post("/api/v1/productos", json=precio_invalido)
    assert respuesta_precio.status_code == 422

    # Stock negativo
    stock_invalido = {
        "nombre": "Producto Inválido",
        "precio": 50.0,
        "stock": -1,
        "categoria": "Test"
    }
    respuesta_stock = cliente.post("/api/v1/productos", json=stock_invalido)
    assert respuesta_stock.status_code == 422

    # Nombre vacío
    nombre_vacio = {
        "nombre": "",
        "precio": 50.0,
        "stock": 5,
        "categoria": "Test"
    }
    respuesta_nombre = cliente.post("/api/v1/productos", json=nombre_vacio)
    assert respuesta_nombre.status_code == 422


def test_actualizar_producto_exitoso(cliente):
    """Verifica actualización de producto existente."""
    datos_actualizacion = {
        "precio": 1050.00,
        "stock": 7
    }
    respuesta = cliente.put("/api/v1/productos/1", json=datos_actualizacion)
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["precio"] == 1050.00
    assert datos["stock"] == 7
    assert datos["nombre"] == "Laptop Pro 15"  # Se mantiene intacto


def test_actualizar_producto_no_encontrado(cliente):
    """Verifica error 404 al intentar actualizar producto inexistente."""
    respuesta = cliente.put("/api/v1/productos/9999", json={"precio": 50.0})
    assert respuesta.status_code == 404


def test_eliminar_producto_exitoso(cliente):
    """Verifica eliminación de producto existente (204 No Content)."""
    respuesta = cliente.delete("/api/v1/productos/2")
    assert respuesta.status_code == 204

    # Verificar que ya no existe
    respuesta_consulta = cliente.get("/api/v1/productos/2")
    assert respuesta_consulta.status_code == 404


def test_eliminar_producto_no_encontrado(cliente):
    """Verifica error 404 al intentar eliminar producto inexistente."""
    respuesta = cliente.delete("/api/v1/productos/9999")
    assert respuesta.status_code == 404


def test_aplicar_descuento_logica_negocio(cliente):
    """Verifica la lógica de negocio del cálculo de descuentos."""
    # Producto 1 cuesta 1200.00. Con 10% de descuento debe quedar en 1080.00
    solicitud = {"porcentaje": 10.0}
    respuesta = cliente.post("/api/v1/productos/1/aplicar-descuento", json=solicitud)
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["precio"] == 1080.00


def test_aplicar_descuento_porcentajes_invalidos(cliente):
    """Verifica validación de rangos para descuentos (0 < porcentaje < 100)."""
    # 0% no es permitido
    respuesta_cero = cliente.post("/api/v1/productos/1/aplicar-descuento", json={"porcentaje": 0})
    assert respuesta_cero.status_code == 422

    # 100% no es permitido
    respuesta_cien = cliente.post("/api/v1/productos/1/aplicar-descuento", json={"porcentaje": 100})
    assert respuesta_cien.status_code == 422

    # Negativo no es permitido
    respuesta_negativa = cliente.post("/api/v1/productos/1/aplicar-descuento", json={"porcentaje": -5})
    assert respuesta_negativa.status_code == 422


def test_aplicar_descuento_producto_no_encontrado(cliente):
    """Verifica error 404 al aplicar descuento a producto inexistente."""
    respuesta = cliente.post("/api/v1/productos/9999/aplicar-descuento", json={"porcentaje": 15.0})
    assert respuesta.status_code == 404


def test_servicio_producto_pruebas_unitarias_directas():
    """Pruebas unitarias directas sobre ServicioProducto para máxima cobertura."""
    servicio = ServicioProducto()
    servicio.reiniciar_almacen()

    # Probar excepción de rango en aplicar_descuento directamente
    with pytest.raises(ValueError):
        servicio.aplicar_descuento(1, 0.0)

    with pytest.raises(ValueError):
        servicio.aplicar_descuento(1, 150.0)

    # Probar descuento en producto que no existe
    resultado = servicio.aplicar_descuento(999, 20.0)
    assert resultado is None

    # Probar borrado de id no existente
    assert servicio.eliminar_producto(999) is False

    # Probar actualización de id no existente
    assert servicio.actualizar_producto(999, ProductoActualizar(nombre="Test")) is None

    # Probar métodos alias
    servicio.reset_store()
    assert len(servicio.list_all()) >= 3
    assert servicio.get_by_id(1) is not None
    assert servicio.update_product(1, ProductoActualizar(nombre="Nuevo")).nombre == "Nuevo"
    assert servicio.delete_product(3) is True
    assert servicio.apply_discount(1, 10.0) is not None
