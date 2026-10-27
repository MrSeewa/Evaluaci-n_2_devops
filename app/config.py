import os

NOMBRE_APP = os.getenv("NOMBRE_APP", os.getenv("APP_NAME", "Microservicio de Inventario de Productos"))
VERSION_APP = os.getenv("VERSION_APP", os.getenv("APP_VERSION", "1.0.0"))
ENTORNO_APP = os.getenv("ENTORNO_APP", os.getenv("APP_ENV", "production"))
PUERTO = int(os.getenv("PUERTO", os.getenv("PORT", "8000")))
# Se permite enlace a 0.0.0.0 exclusivamente para escucha en contenedores Docker/K8s
HOST = os.getenv("HOST", "0.0.0.0")  # nosec B104

# Alias para mantener retrocompatibilidad con entornos y contenedores
APP_NAME = NOMBRE_APP
APP_VERSION = VERSION_APP
APP_ENV = ENTORNO_APP
PORT = PUERTO
