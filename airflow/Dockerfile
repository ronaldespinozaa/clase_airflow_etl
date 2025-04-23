FROM apache/airflow:2.7.1-python3.9

# El usuario por defecto es airflow, pero para instalar dependencias del sistema se necesita permisos de root
# Cambiar a root para instalar dependencias del sistema
USER root 

# Instalar dependencias del sistema. Se está ejecutando en un contenedor de Debian, por lo que se usa apt-get
# Se instalan las dependencias necesarias para la conexión a PostgreSQL y para compilar paquetes de Python que requieren compilación
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         build-essential \
         libpq-dev \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow

# Copiar requirements e instalar dependencias de Python
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt