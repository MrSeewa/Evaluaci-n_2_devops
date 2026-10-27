from typing import Dict, List, Optional
from app.schemas import ProductoCrear, ProductoActualizar, ProductoRespuesta


class ServicioProducto:
    def __init__(self):
        self._productos: Dict[int, ProductoRespuesta] = {}
        self._siguiente_id = 1
        self._cargar_datos_iniciales()

    def _cargar_datos_iniciales(self) -> None:
        articulos_iniciales = [
            ProductoCrear(
                nombre="Laptop Pro 15",
                descripcion="Laptop para desarrolladores y alto rendimiento",
                precio=1200.0,
                stock=10,
                categoria="Computación"
            ),
            ProductoCrear(
                nombre="Mouse Inalámbrico",
                descripcion="Mouse ergonómico con sensor óptico",
                precio=25.50,
                stock=50,
                categoria="Periféricos"
            ),
            ProductoCrear(
                nombre="Teclado Mecánico RGB",
                descripcion="Switches mecánicos táctiles con retroiluminación",
                precio=89.90,
                stock=25,
                categoria="Periféricos"
            )
        ]
        for articulo in articulos_iniciales:
            self.crear_producto(articulo)

    def reiniciar_almacen(self) -> None:
        """Reinicia el almacén a los datos iniciales (usado para tests)."""
        self._productos.clear()
        self._siguiente_id = 1
        self._cargar_datos_iniciales()

    def listar_todos(self, categoria: Optional[str] = None) -> List[ProductoRespuesta]:
        articulos = list(self._productos.values())
        if categoria:
            articulos = [item for item in articulos if item.categoria.lower() == categoria.lower()]
        return articulos

    def obtener_por_id(self, id_producto: int) -> Optional[ProductoRespuesta]:
        return self._productos.get(id_producto)

    def crear_producto(self, datos: ProductoCrear) -> ProductoRespuesta:
        id_producto = self._siguiente_id
        self._siguiente_id += 1
        producto = ProductoRespuesta(
            id=id_producto,
            nombre=datos.nombre.strip(),
            descripcion=datos.descripcion.strip() if datos.descripcion else None,
            precio=round(datos.precio, 2),
            stock=datos.stock,
            categoria=datos.categoria.strip()
        )
        self._productos[id_producto] = producto
        return producto

    def actualizar_producto(self, id_producto: int, datos: ProductoActualizar) -> Optional[ProductoRespuesta]:
        actual = self.obtener_por_id(id_producto)
        if not actual:
            return None

        diccionario_actualizacion = datos.model_dump(exclude_unset=True)
        nuevos_valores = actual.model_dump()

        for clave, valor in diccionario_actualizacion.items():
            if valor is not None:
                if clave in ["nombre", "descripcion", "categoria"] and isinstance(valor, str):
                    nuevos_valores[clave] = valor.strip()
                elif clave == "precio":
                    nuevos_valores[clave] = round(float(valor), 2)
                else:
                    nuevos_valores[clave] = valor

        producto_actualizado = ProductoRespuesta(**nuevos_valores)
        self._productos[id_producto] = producto_actualizado
        return producto_actualizado

    def eliminar_producto(self, id_producto: int) -> bool:
        if id_producto in self._productos:
            del self._productos[id_producto]
            return True
        return False

    def aplicar_descuento(self, id_producto: int, porcentaje: float) -> Optional[ProductoRespuesta]:
        """Aplica un porcentaje de descuento al producto (0 < porcentaje < 100)."""
        if not (0 < porcentaje < 100):
            raise ValueError("El porcentaje de descuento debe estar estrictamente entre 0 y 100")

        producto = self.obtener_por_id(id_producto)
        if not producto:
            return None

        multiplicador_descuento = 1 - (porcentaje / 100.0)
        nuevo_precio = round(producto.precio * multiplicador_descuento, 2)
        if nuevo_precio <= 0:
            nuevo_precio = 0.01  # precio mínimo permitido

        return self.actualizar_producto(id_producto, ProductoActualizar(precio=nuevo_precio))

    # Métodos alias para retrocompatibilidad
    def reset_store(self) -> None:
        return self.reiniciar_almacen()

    def list_all(self, category: Optional[str] = None):
        return self.listar_todos(categoria=category)

    def get_by_id(self, product_id: int):
        return self.obtener_por_id(id_producto=product_id)

    def create_product(self, data: ProductoCrear):
        return self.crear_producto(datos=data)

    def update_product(self, product_id: int, data: ProductoActualizar):
        return self.actualizar_producto(id_producto=product_id, datos=data)

    def delete_product(self, product_id: int):
        return self.eliminar_producto(id_producto=product_id)

    def apply_discount(self, product_id: int, percentage: float):
        return self.aplicar_descuento(id_producto=product_id, porcentaje=percentage)


servicio_producto = ServicioProducto()
ProductService = ServicioProducto
product_service = servicio_producto
