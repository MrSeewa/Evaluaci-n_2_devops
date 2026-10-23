from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})
    environment: str = Field(..., json_schema_extra={"example": "production"})
    service: str = Field(..., json_schema_extra={"example": "Product Inventory Microservice"})


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Laptop Gamer Pro"})
    description: Optional[str] = Field(None, max_length=500, json_schema_extra={"example": "Intel i7, 16GB RAM, RTX 4060"})
    price: float = Field(..., gt=0, json_schema_extra={"example": 1299.99})
    stock: int = Field(..., ge=0, json_schema_extra={"example": 15})
    category: str = Field(..., min_length=2, max_length=50, json_schema_extra={"example": "Tecnología"})


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=2, max_length=50)


class ProductResponse(ProductBase):
    id: int = Field(..., json_schema_extra={"example": 1})


class DiscountRequest(BaseModel):
    percentage: float = Field(..., gt=0, lt=100, json_schema_extra={"example": 15.0})


class ErrorResponse(BaseModel):
    detail: str = Field(..., json_schema_extra={"example": "Recurso no encontrado"})

