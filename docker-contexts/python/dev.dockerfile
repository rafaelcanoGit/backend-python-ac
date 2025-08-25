# Imagen base ligera de Python
FROM python:3.11.8

# Evita prompts interactivos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo dentro del contenedor
WORKDIR /var/www/workspace

# Instala las dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt y luego instalar dependencias
COPY --from=root requirements.txt .
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente
# COPY --from=root . .

# Exponer el puerto (por si lo necesitas explícitamente)
# EXPOSE 5000

# Comando por defecto al iniciar el contenedor
CMD ["python3", "app/app.py"]

