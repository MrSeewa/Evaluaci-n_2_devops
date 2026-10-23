# ==============================================================================
# Dockerfile Multi-Stage Optimizado para Microservicio FastAPI
# DOY0101 - Ingeniería DevOps (Evaluación Parcial N°2 - IE1)
# ==============================================================================

# ------------------------------------------------------------------------------
# Etapa 1: Builder (Compilación e instalación de dependencias aisladas)
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

# Instalar herramientas básicas de build sin cachés innecesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Crear entorno virtual aislado
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar dependencias e instalarlas en el entorno virtual
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ------------------------------------------------------------------------------
# Etapa 2: Runtime (Imagen final ligera, segura y sin privilegios de root)
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Variables de entorno para Python en contenedores
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_ENV=production \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Copiar el entorno virtual con dependencias de la etapa builder
COPY --from=builder /opt/venv /opt/venv

# Copiar el código fuente de la aplicación
COPY app/ ./app

# Crear usuario y grupo sin privilegios de root para cumplir estándares de seguridad
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -d /app -s /sbin/nologin -u 10001 appuser && \
    chown -R appuser:appgroup /app

# Cambiar al usuario no-root
USER appuser

# Exponer el puerto del servicio
EXPOSE 8000

# Healthcheck nativo utilizando la librería estándar de Python
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando de inicio del microservicio con servidor ASGI uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

