# Manual de Docker para Orquestación de ETL con Airflow

## 1. Comandos Básicos de Docker y Docker Compose

### Gestión de Contenedores

```bash
# Iniciar servicios definidos en docker-compose.yml
docker-compose up

# Iniciar servicios en modo detached (en segundo plano)
docker-compose up -d

# Iniciar servicios y reconstruir imágenes
docker-compose up --build

# Detener servicios
docker-compose down

# Detener servicios y eliminar volúmenes
docker-compose down -v

# Detener servicios y eliminar imágenes
docker-compose down --rmi all

# Detener servicios y eliminar contenedores huérfanos
docker-compose down --remove-orphans

# Reiniciar servicios
docker-compose restart

# Reiniciar un servicio específico
docker-compose restart airflow-webserver
```

### Visualización del Estado de Contenedores

```bash
# Listar contenedores en ejecución
docker ps

# Listar todos los contenedores (incluso los detenidos)
docker ps -a

# Ver logs de todos los servicios
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs airflow-scheduler

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico en tiempo real
docker-compose logs -f airflow-webserver

# Ver estadísticas de uso de recursos
docker stats
```

### Ejecución de Comandos en Contenedores

```bash
# Ejecutar un comando en un contenedor en ejecución
docker exec -it <container_id> bash

# Ejecutar un comando específico en un servicio
docker-compose exec airflow-webserver airflow list_dags

# Ejecutar bash en un servicio específico
docker-compose exec airflow-webserver bash
```

## 2. Comandos Específicos para Airflow

### Operaciones con DAGs

```bash
# Listar todos los DAGs
docker-compose exec airflow-webserver airflow list_dags

# Comprobar la sintaxis de un DAG
docker-compose exec airflow-webserver python -c "import airflow; from airflow.utils.dag_processing import SimpleDagBag; SimpleDagBag('/opt/airflow/dags/my_dag.py').import_errors"

# Ejecutar un DAG manualmente
docker-compose exec airflow-webserver airflow trigger_dag my_dag_id

# Pausar un DAG
docker-compose exec airflow-webserver airflow pause my_dag_id

# Reanudar un DAG
docker-compose exec airflow-webserver airflow unpause my_dag_id

# Eliminar un DAG (incluidos registros y estado)
docker-compose exec airflow-webserver airflow delete_dag my_dag_id
```

### Gestión de Variables y Conexiones

```bash
# Listar variables de Airflow
docker-compose exec airflow-webserver airflow variables list

# Establecer una variable
docker-compose exec airflow-webserver airflow variables set my_var my_value

# Obtener una variable
docker-compose exec airflow-webserver airflow variables get my_var

# Listar conexiones
docker-compose exec airflow-webserver airflow connections list

# Añadir una conexión
docker-compose exec airflow-webserver airflow connections add \
  --conn-id my_postgres_conn \
  --conn-type postgres \
  --conn-host postgres \
  --conn-login airflow \
  --conn-password airflow \
  --conn-port 5432 \
  --conn-schema airflow
```

## 3. Gestión de Bases de Datos (PostgreSQL)

### Conexión y Consultas a PostgreSQL

```bash
# Conectar a PostgreSQL desde la línea de comandos
docker-compose exec postgres psql -U airflow -d airflow

# Ejecutar una consulta desde fuera del contenedor
docker-compose exec postgres psql -U airflow -d airflow -c "SELECT * FROM dag_run LIMIT 5;"

# Hacer un backup de la base de datos
docker-compose exec postgres pg_dump -U airflow airflow > backup.sql

# Restaurar un backup
cat backup.sql | docker exec -i postgres_container psql -U airflow -d airflow

# Ver el tamaño de las tablas
docker-compose exec postgres psql -U airflow -d airflow -c "
SELECT
    table_name,
    pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as total_size
FROM
    information_schema.tables
WHERE
    table_schema = 'public'
ORDER BY
    pg_total_relation_size(quote_ident(table_name)) DESC;
"
```

### Comandos Útiles para PostgreSQL

```bash
# Ver las conexiones activas a la base de datos
docker-compose exec postgres psql -U airflow -d airflow -c "
SELECT * FROM pg_stat_activity WHERE datname = 'airflow';
"

# Terminar todas las conexiones a una base de datos
docker-compose exec postgres psql -U airflow -d airflow -c "
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'airflow' AND pid <> pg_backend_pid();
"

# Ver estadísticas de uso de índices
docker-compose exec postgres psql -U airflow -d airflow -c "
SELECT
    relname as table_name,
    indexrelname as index_name,
    idx_scan as index_scans
FROM
    pg_stat_user_indexes
ORDER BY
    idx_scan DESC;
"
```

## 4. Monitoreo y Solución de Problemas

### Monitoreo de Recursos

```bash
# Ver uso de recursos de los contenedores
docker stats

# Ver espacio en disco utilizado por Docker
docker system df

# Ver espacio en disco detallado
docker system df -v

# Verificar redes de Docker
docker network ls

# Verificar volúmenes de Docker
docker volume ls
```

### Limpieza y Optimización

```bash
# Eliminar contenedores detenidos
docker container prune

# Eliminar imágenes sin usar
docker image prune

# Eliminar volúmenes sin usar
docker volume prune

# Eliminar redes sin usar
docker network prune

# Eliminar todo lo no utilizado (contenedores, imágenes, volúmenes, redes)
docker system prune

# Eliminar todo, incluyendo volúmenes no utilizados
docker system prune -a --volumes
```

### Diagnóstico de Problemas

```bash
# Ver eventos de Docker
docker events

# Ver logs del sistema Docker
sudo journalctl -u docker

# Verificar la configuración de Docker
docker info

# Verificar la versión de Docker
docker version

# Verificar la conectividad entre contenedores
docker-compose exec airflow-webserver ping postgres

# Comprobar estado de salud de un contenedor
docker inspect --format='{{.State.Health.Status}}' <container_id>
```

## 5. Personalización y Escenarios Avanzados

### Modificación de Configuraciones en Tiempo Real

```bash
# Escalar servicios (aumentar el número de workers)
docker-compose up -d --scale airflow-worker=3

# Reiniciar un servicio con una variable de entorno modificada
docker-compose stop airflow-webserver
AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True docker-compose up -d airflow-webserver

# Ver todas las variables de entorno de un contenedor
docker-compose exec airflow-webserver env | sort
```

### Gestión de Volúmenes

```bash
# Crear un volumen
docker volume create airflow-data

# Inspeccionar un volumen
docker volume inspect airflow-data

# Hacer backup de un volumen
docker run --rm -v airflow-data:/source -v $(pwd):/backup alpine tar czf /backup/airflow-data.tar.gz -C /source .

# Restaurar un volumen desde un backup
docker run --rm -v airflow-data:/target -v $(pwd):/backup alpine sh -c "rm -rf /target/* && tar xzf /backup/airflow-data.tar.gz -C /target"
```

### Operaciones con Redes

```bash
# Crear una red personalizada
docker network create --driver bridge airflow-network

# Inspeccionar una red
docker network inspect airflow-network

# Conectar un contenedor existente a una red
docker network connect airflow-network <container_id>

# Desconectar un contenedor de una red
docker network disconnect airflow-network <container_id>
```

## 6. Integración con Sistemas ETL

### Ejecución de Scripts ETL en Contenedores

```bash
# Ejecutar un script Python en un contenedor
docker-compose exec airflow-worker python /scripts/my_etl_script.py

# Cargar datos desde un archivo local al contenedor
docker cp ./data.csv airflow-worker:/tmp/data.csv

# Ejecutar un script ETL con argumentos
docker-compose exec airflow-worker python /scripts/process_data.py --date 2023-01-01 --input /data/input.csv --output /data/output.csv
```

### Gestión de Dependencias

```bash
# Instalar una dependencia Python en tiempo de ejecución
docker-compose exec airflow-worker pip install pandas==1.5.3

# Verificar dependencias instaladas
docker-compose exec airflow-worker pip freeze

# Actualizar requirements.txt y reconstruir la imagen
echo "pandas==1.5.3" >> requirements.txt
docker-compose build airflow-worker
docker-compose up -d airflow-worker
```

## 7. Ejemplo de docker-compose.yml para Airflow

```yaml
version: '3'
services:
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    ports:
      - "5432:5432"
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 30s
      retries: 50

  airflow-webserver:
    image: apache/airflow:2.6.1
    restart: always
    depends_on:
      - postgres
      - redis
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://:@redis:6379/0
      - AIRFLOW__CORE__FERNET_KEY=46BKJoQYlPPOexq0OhDZnIlNepKFf87WFwLbfzqDDho=
      - AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true
      - AIRFLOW__CORE__LOAD_EXAMPLES=false
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./scripts:/scripts
    ports:
      - "8080:8080"
    command: webserver
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 10s
      timeout: 10s
      retries: 5

  airflow-scheduler:
    image: apache/airflow:2.6.1
    restart: always
    depends_on:
      - airflow-webserver
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://:@redis:6379/0
      - AIRFLOW__CORE__FERNET_KEY=46BKJoQYlPPOexq0OhDZnIlNepKFf87WFwLbfzqDDho=
      - AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true
      - AIRFLOW__CORE__LOAD_EXAMPLES=false
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./scripts:/scripts
    command: scheduler

  airflow-worker:
    image: apache/airflow:2.6.1
    restart: always
    depends_on:
      - airflow-scheduler
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://:@redis:6379/0
      - AIRFLOW__CORE__FERNET_KEY=46BKJoQYlPPOexq0OhDZnIlNepKFf87WFwLbfzqDDho=
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./scripts:/scripts
      - ./data:/data
    command: celery worker

  airflow-init:
    image: apache/airflow:2.6.1
    depends_on:
      - postgres
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://:@redis:6379/0
      - AIRFLOW__CORE__FERNET_KEY=46BKJoQYlPPOexq0OhDZnIlNepKFf87WFwLbfzqDDho=
      - AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true
      - AIRFLOW__CORE__LOAD_EXAMPLES=false
      - _AIRFLOW_DB_UPGRADE=true
      - _AIRFLOW_WWW_USER_CREATE=true
      - _AIRFLOW_WWW_USER_USERNAME=airflow
      - _AIRFLOW_WWW_USER_PASSWORD=airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    command: version
    restart: "no"

volumes:
  postgres-db-volume:
```

## 8. Seguridad y Mejores Prácticas

### Protección de Credenciales

```bash
# Usar variables de entorno en lugar de hardcoding
export POSTGRES_PASSWORD=secure_password
docker-compose up -d

# Usar Docker Secrets (en Docker Swarm)
echo "secure_password" | docker secret create postgres_password -
```

### Mejores Prácticas de Seguridad

```bash
# Limitar permisos en archivos de configuración
chmod 600 .env

# Restringir el acceso a la red
docker network create --internal airflow_internal

# Verificar vulnerabilidades en imágenes
docker scan apache/airflow:2.6.1
```

### Backup y Restauración

```bash
# Backup completo de la configuración
tar -czvf airflow_backup.tar.gz ./dags ./logs ./plugins ./scripts ./docker-compose.yml

# Backup de datos críticos solamente
tar -czvf airflow_critical_data.tar.gz ./dags ./plugins
```

## 9. Escenarios de Resolución de Problemas Comunes

### Problemas de Conexión a Base de Datos

```bash
# Verificar conectividad
docker-compose exec airflow-webserver nc -zv postgres 5432

# Verificar credenciales
docker-compose exec airflow-webserver python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg2://airflow:airflow@postgres/airflow')
try:
    connection = engine.connect()
    print('Conexión exitosa')
    connection.close()
except Exception as e:
    print(f'Error de conexión: {e}')
"
```

### Problemas con los DAGs

```bash
# Recargar DAGs manualmente
docker-compose exec airflow-webserver airflow dags reserialize

# Verificar permisos en archivos DAG
docker-compose exec airflow-webserver ls -la /opt/airflow/dags

# Limpiar archivos __pycache__
docker-compose exec airflow-webserver find /opt/airflow/dags -name "__pycache__" -type d -exec rm -rf {} +
```

### Problemas de Memoria y Recursos

```bash
# Verificar uso de memoria
docker stats --no-stream

# Aumentar límite de memoria para un servicio
docker-compose up -d --scale airflow-worker=3 --memory="2g" airflow-worker

# Verificar logs de OOM (Out of Memory)
docker-compose exec airflow-webserver dmesg | grep -i kill
```

## 10. Comandos para Integraciones Comunes

### Integración con S3

```bash
# Instalar dependencias para S3
docker-compose exec airflow-webserver pip install apache-airflow-providers-amazon

# Verificar plugins instalados
docker-compose exec airflow-webserver airflow providers list
```

### Integración con Spark

```bash
# Instalar dependencias para Spark
docker-compose exec airflow-webserver pip install apache-airflow-providers-apache-spark

# Ejecutar un job Spark desde Airflow
docker-compose exec airflow-worker spark-submit --master local[*] /scripts/spark_job.py
```

### Integración con Kafka

```bash
# Instalar dependencias para Kafka
docker-compose exec airflow-webserver pip install apache-airflow-providers-apache-kafka

# Verificar la conectividad con Kafka
docker-compose exec airflow-worker kafkacat -b kafka:9092 -L
```