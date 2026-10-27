from typing import Optional
from pydantic import BaseModel, Field


class RespuestaSalud(BaseModel):
    estado: str = Field(..., json_schema_extra={"example": "saludable"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})
    entorno: str = Field(..., json_schema_extra={"example": "produccion"})
    servicio: str = Field(..., json_schema_extra={"example": "Microservicio de Inventario de Productos"})


class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Laptop Gamer Pro"})
    descripcion: Optional[str] = Field(None, max_length=500, json_schema_extra={"example": "Intel i7, 16GB RAM, RTX 4060"})
    precio: float = Field(..., gt=0, json_schema_extra={"example": 1299.99})
    stock: int = Field(..., ge=0, json_schema_extra={"example": 15})
    categoria: str = Field(..., min_length=2, max_length=50, json_schema_extra={"example": "Tecnología"})


class ProductoCrear(ProductoBase):
    pass


class ProductoActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    categoria: Optional[str] = Field(None, min_length=2, max_length=50)


class ProductoRespuesta(ProductoBase):
    id: int = Field(..., json_schema_extra={"example": 1})


class SolicitudDescuento(BaseModel):
    porcentaje: float = Field(..., gt=0, lt=100, json_schema_extra={"example": 15.0})


class RespuestaError(BaseModel):
    detalle: str = Field(..., json_schema_extra={"example": "Recurso no encontrado"})


# Alias para retrocompatibilidad
HealthResponse = RespuestaSalud
ProductBase = ProductoBase
ProductCreate = ProductoCrear
ProductUpdate = ProductoActualizar
ProductResponse = ProductoRespuesta
DiscountRequest = SolicitudDescuento
ErrorResponse = RespuestaError
