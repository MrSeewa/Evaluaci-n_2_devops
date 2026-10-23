from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, APP_VERSION, APP_ENV
from app.schemas import (
    HealthResponse,
    ProductResponse,
    ProductCreate,
    ProductUpdate,
    DiscountRequest,
    ErrorResponse
)
from app.services import product_service

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Microservicio REST de Gestión de Productos e Inventario para Evaluación Parcial N°2 DOY0101."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": "online",
        "docs": "/docs"
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Healthcheck del microservicio para Kubernetes y Docker Compose"
)
def health_check():
    return HealthResponse(
        status="healthy",
        version=APP_VERSION,
        environment=APP_ENV,
        service=APP_NAME
    )


@app.get(
    "/api/v1/products",
    response_model=List[ProductResponse],
    tags=["Products"],
    summary="Listar todos los productos con filtro opcional por categoría"
)
def list_products(category: Optional[str] = Query(None, description="Filtrar por categoría")):
    return product_service.list_all(category=category)


@app.get(
    "/api/v1/products/{product_id}",
    response_model=ProductResponse,
    responses={404: {"model": ErrorResponse}},
    tags=["Products"],
    summary="Obtener un producto por su ID"
)
def get_product(product_id: int):
    product = product_service.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado"
        )
    return product


@app.post(
    "/api/v1/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"],
    summary="Crear un nuevo producto"
)
def create_product(product_in: ProductCreate):
    return product_service.create_product(product_in)


@app.put(
    "/api/v1/products/{product_id}",
    response_model=ProductResponse,
    responses={404: {"model": ErrorResponse}},
    tags=["Products"],
    summary="Actualizar un producto existente"
)
def update_product(product_id: int, product_in: ProductUpdate):
    updated = product_service.update_product(product_id, product_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado para actualizar"
        )
    return updated


@app.delete(
    "/api/v1/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    tags=["Products"],
    summary="Eliminar un producto por ID"
)
def delete_product(product_id: int):
    deleted = product_service.delete_product(product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado para eliminar"
        )
    return None


@app.post(
    "/api/v1/products/{product_id}/apply-discount",
    response_model=ProductResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse}
    },
    tags=["Business Logic"],
    summary="Aplica un porcentaje de descuento calculando el nuevo precio"
)
def apply_discount(product_id: int, discount_in: DiscountRequest):
    try:
        updated = product_service.apply_discount(product_id, discount_in.percentage)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado para aplicar descuento"
        )
    return updated

