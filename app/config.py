import os

APP_NAME = os.getenv("APP_NAME", "Product Inventory Microservice")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "production")
PORT = int(os.getenv("PORT", "8000"))
# Se permite enlace a 0.0.0.0 exclusivamente para escucha en contenedores Docker/K8s
HOST = os.getenv("HOST", "0.0.0.0")  # nosec B104

