from typing import Dict, List, Optional
from app.schemas import ProductCreate, ProductUpdate, ProductResponse


class ProductService:
    def __init__(self):
        self._products: Dict[int, ProductResponse] = {}
        self._next_id = 1
        self._seed_initial_data()

    def _seed_initial_data(self) -> None:
        initial_items = [
            ProductCreate(
                name="Laptop Pro 15",
                description="Laptop para desarrolladores y alto rendimiento",
                price=1200.0,
                stock=10,
                category="Computación"
            ),
            ProductCreate(
                name="Mouse Inalámbrico",
                description="Mouse ergonómico con sensor óptico",
                price=25.50,
                stock=50,
                category="Periféricos"
            ),
            ProductCreate(
                name="Teclado Mecánico RGB",
                description="Switches mecánicos táctiles con retroiluminación",
                price=89.90,
                stock=25,
                category="Periféricos"
            )
        ]
        for item in initial_items:
            self.create_product(item)

    def reset_store(self) -> None:
        """Reinicia el almacén a los datos iniciales (usado para tests)."""
        self._products.clear()
        self._next_id = 1
        self._seed_initial_data()

    def list_all(self, category: Optional[str] = None) -> List[ProductResponse]:
        items = list(self._products.values())
        if category:
            items = [item for item in items if item.category.lower() == category.lower()]
        return items

    def get_by_id(self, product_id: int) -> Optional[ProductResponse]:
        return self._products.get(product_id)

    def create_product(self, data: ProductCreate) -> ProductResponse:
        product_id = self._next_id
        self._next_id += 1
        product = ProductResponse(
            id=product_id,
            name=data.name.strip(),
            description=data.description.strip() if data.description else None,
            price=round(data.price, 2),
            stock=data.stock,
            category=data.category.strip()
        )
        self._products[product_id] = product
        return product

    def update_product(self, product_id: int, data: ProductUpdate) -> Optional[ProductResponse]:
        current = self.get_by_id(product_id)
        if not current:
            return None

        update_dict = data.model_dump(exclude_unset=True)
        new_values = current.model_dump()

        for key, value in update_dict.items():
            if value is not None:
                if key in ["name", "description", "category"] and isinstance(value, str):
                    new_values[key] = value.strip()
                elif key == "price":
                    new_values[key] = round(float(value), 2)
                else:
                    new_values[key] = value

        updated_product = ProductResponse(**new_values)
        self._products[product_id] = updated_product
        return updated_product

    def delete_product(self, product_id: int) -> bool:
        if product_id in self._products:
            del self._products[product_id]
            return True
        return False

    def apply_discount(self, product_id: int, percentage: float) -> Optional[ProductResponse]:
        """Aplica un porcentaje de descuento al producto (0 < percentage < 100)."""
        if not (0 < percentage < 100):
            raise ValueError("El porcentaje de descuento debe estar estrictamente entre 0 y 100")

        product = self.get_by_id(product_id)
        if not product:
            return None

        discount_multiplier = 1 - (percentage / 100.0)
        new_price = round(product.price * discount_multiplier, 2)
        if new_price <= 0:
            new_price = 0.01  # precio mínimo permitido

        return self.update_product(product_id, ProductUpdate(price=new_price))


product_service = ProductService()

