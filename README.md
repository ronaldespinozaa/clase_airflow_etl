# ETL con Airflow y Docker para el Bootcamp de Data Science DS102024

Este repositorio contiene una implementación básica de un ETL (Extract, Transform, Load) utilizando Apache Airflow como orquestador, Docker para la contenerización y SQLAlchemy para interactuar con la base de datos. Está diseñado específicamente para estudiantes de un bootcamp de Data Engineering, con un enfoque en la simplicidad y facilidad de uso.

## Estructura del proyecto

```
airflow-etl/
│
├── .env                     # Variables de entorno para la configuración
├── .gitignore               # Archivos y directorios a ignorar por Git
├── docker-compose.yml       # Configuración de los servicios de Docker
├── requirements.txt         # Dependencias Python
├── TUTORIAL.md              # Tutorial detallado para estudiantes
│
├── airflow/
│   ├── Dockerfile           # Configuración para construir la imagen de Airflow
│   └── dags/                # Directorio donde se almacenan los DAGs
│       ├── __init__.py
│       └── etl_dag.py       # DAG para el proceso ETL
│
└── notebooks/               # Notebooks educativos
    ├── airflow_conceptos_fundamentales.ipynb  # Teoría de Airflow
    └── airflow_laboratorio_practico.ipynb     # Ejercicios prácticos
```

## ¿Qué hace este ETL?

Este ETL realiza un proceso simple pero completo:

1. **Extracción**: Obtiene datos meteorológicos de varias ciudades desde la API de OpenWeatherMap (o genera datos simulados)
2. **Transformación**: Convierte temperaturas, normaliza nombres de ciudades y añade categorías
3. **Carga**: Almacena los datos procesados en una base de datos PostgreSQL

## Puesta en marcha rápida

1. **Clona este repositorio**
   ```bash
   git clone https://github.com/tu-usuario/airflow-etl-basico.git
   cd airflow-etl-basico
   ```

2. **Inicia los servicios con Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Accede a la interfaz web de Airflow**
   - URL: http://localhost:8080
   - Usuario: admin
   - Contraseña: admin

4. **Activa el DAG**
   - Busca el DAG llamado "etl_weather_data"
   - Actívalo con el interruptor y observa su ejecución

## Visualizando los datos

Después de que el DAG se haya ejecutado correctamente, puedes visualizar los datos cargados en la base de datos PostgreSQL:

### Usando la línea de comandos

1. **Conéctate al contenedor de PostgreSQL**:
   ```bash
   docker exec -it airflow-postgres-1 bash
   ```

2. **Accede a la base de datos etl_data**:
   ```bash
   psql -U airflow -d etl_data
   ```

3. **Consulta los datos**:
   ```sql
   -- Ver las tablas disponibles
   \dt
   
   -- Consultar datos meteorológicos
   SELECT * FROM weather_data;
   
   -- Salir de psql
   \q
   ```

### Usando herramientas gráficas (pgAdmin, DBeaver, etc.)

Puedes conectarte a la base de datos desde tu máquina local con estos parámetros:

- **Host**: localhost (o 127.0.0.1)
- **Puerto**: 5432
- **Usuario**: airflow
- **Contraseña**: airflow
- **Base de datos**: etl_data

### Usando Database Client en VS Code

1. Instala la extensión "Database Client" en VS Code
2. Crea una nueva conexión PostgreSQL con:
   - **Host**: localhost
   - **Port**: 5432
   - **User**: airflow
   - **Password**: airflow
   - **Database**: etl_data

## Material educativo

El repositorio contiene dos notebooks educativos:

- **airflow_conceptos_fundamentales.ipynb**: Explica la teoría detrás de Airflow (arquitectura, componentes, patrones)
- **airflow_laboratorio_practico.ipynb**: Ofrece ejercicios prácticos para reforzar los conocimientos

También se incluye un tutorial detallado (**TUTORIAL.md**) que explica paso a paso cómo funciona este ETL y cómo se integran las diferentes tecnologías.

## Personalización

Puedes personalizar este proyecto fácilmente:

1. **Cambiar la fuente de datos**: Modifica la función `extract_data()` para consumir otra API
2. **Ajustar transformaciones**: Modifica la función `transform_data()` para aplicar otras transformaciones
3. **Cambiar el destino**: Modifica la función `load_data()` para almacenar en otro tipo de base de datos

## Recursos adicionales

- [Documentación oficial de Apache Airflow](https://airflow.apache.org/docs/)
- [Tutoriales de SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [Documentación de la API de OpenWeatherMap](https://openweathermap.org/api)
