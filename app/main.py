from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import NOMBRE_APP, VERSION_APP, ENTORNO_APP
from app.schemas import (
    RespuestaSalud,
    ProductoRespuesta,
    ProductoCrear,
    ProductoActualizar,
    SolicitudDescuento,
    RespuestaError
)
from app.services import servicio_producto

app = FastAPI(
    title=NOMBRE_APP,
    version=VERSION_APP,
    description="Microservicio REST de Gestión de Productos e Inventario para Evaluación Parcial N°2 DOY0101."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Raíz"])
def raiz():
    return {
        "servicio": NOMBRE_APP,
        "version": VERSION_APP,
        "estado": "en_linea",
        "documentacion": "/docs"
    }


@app.get(
    "/health",
    response_model=RespuestaSalud,
    tags=["Salud"],
    summary="Healthcheck del microservicio para Kubernetes y Docker Compose"
)
def verificar_salud():
    return RespuestaSalud(
        estado="saludable",
        version=VERSION_APP,
        entorno=ENTORNO_APP,
        servicio=NOMBRE_APP
    )


@app.get(
    "/api/v1/productos",
    response_model=List[ProductoRespuesta],
    tags=["Productos"],
    summary="Listar todos los productos con filtro opcional por categoría"
)
@app.get(
    "/api/v1/products",
    response_model=List[ProductoRespuesta],
    include_in_schema=False
)
def listar_productos(categoria: Optional[str] = Query(None, description="Filtrar por categoría")):
    return servicio_producto.listar_todos(categoria=categoria)


@app.get(
    "/api/v1/productos/{id_producto}",
    response_model=ProductoRespuesta,
    responses={404: {"model": RespuestaError}},
    tags=["Productos"],
    summary="Obtener un producto por su ID"
)
@app.get(
    "/api/v1/products/{id_producto}",
    response_model=ProductoRespuesta,
    include_in_schema=False
)
def obtener_producto(id_producto: int):
    producto = servicio_producto.obtener_por_id(id_producto)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {id_producto} no encontrado"
        )
    return producto


@app.post(
    "/api/v1/productos",
    response_model=ProductoRespuesta,
    status_code=status.HTTP_201_CREATED,
    tags=["Productos"],
    summary="Crear un nuevo producto"
)
@app.post(
    "/api/v1/products",
    response_model=ProductoRespuesta,
    include_in_schema=False
)
def crear_producto(datos_producto: ProductoCrear):
    return servicio_producto.crear_producto(datos_producto)


@app.put(
    "/api/v1/productos/{id_producto}",
    response_model=ProductoRespuesta,
    responses={404: {"model": RespuestaError}},
    tags=["Productos"],
    summary="Actualizar un producto existente"
)
@app.put(
    "/api/v1/products/{id_producto}",
    response_model=ProductoRespuesta,
    include_in_schema=False
)
def actualizar_producto(id_producto: int, datos_producto: ProductoActualizar):
    producto_actualizado = servicio_producto.actualizar_producto(id_producto, datos_producto)
    if not producto_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {id_producto} no encontrado para actualizar"
        )
    return producto_actualizado


@app.delete(
    "/api/v1/productos/{id_producto}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": RespuestaError}},
    tags=["Productos"],
    summary="Eliminar un producto por ID"
)
@app.delete(
    "/api/v1/products/{id_producto}",
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False
)
def eliminar_producto(id_producto: int):
    eliminado = servicio_producto.eliminar_producto(id_producto)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {id_producto} no encontrado para eliminar"
        )
    return None


@app.post(
    "/api/v1/productos/{id_producto}/aplicar-descuento",
    response_model=ProductoRespuesta,
    responses={
        400: {"model": RespuestaError},
        404: {"model": RespuestaError}
    },
    tags=["Lógica de Negocio"],
    summary="Aplica un porcentaje de descuento calculando el nuevo precio"
)
@app.post(
    "/api/v1/products/{id_producto}/apply-discount",
    response_model=ProductoRespuesta,
    include_in_schema=False
)
def aplicar_descuento(id_producto: int, solicitud_descuento: SolicitudDescuento):
    try:
        producto_con_descuento = servicio_producto.aplicar_descuento(id_producto, solicitud_descuento.porcentaje)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not producto_con_descuento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {id_producto} no encontrado para aplicar descuento"
        )
    return producto_con_descuento
