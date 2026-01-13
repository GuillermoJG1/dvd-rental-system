FROM python:3.11-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos e instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# CORRECCIÓN CLAVE: Copiar el contenido de 'app/' directamente a '/app/'
COPY app/ .

EXPOSE 8000

# CORRECCIÓN CLAVE: Ejecutar 'main:app' directamente (ya no app.main:app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]