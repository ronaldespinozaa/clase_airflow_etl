"""
ETL DAG básico que extrae datos de una API, los transforma y los carga en una base de datos.
"""
import os
import json
from datetime import datetime, timedelta

import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago

# Cargar variables de entorno
load_dotenv()

# Configuración por defecto para el DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5), # Tiempo de espera entre reintentos
}

# Configuración de la conexión a la base de datos destino
DB_USER = os.getenv("ETL_DB_USER", "airflow")
DB_PASSWORD = os.getenv("ETL_DB_PASSWORD", "airflow")
DB_HOST = os.getenv("ETL_DB_HOST", "postgres")
DB_PORT = os.getenv("ETL_DB_PORT", "5432")
DB_NAME = os.getenv("ETL_DB_NAME", "etl_data")

# API Key para OpenWeatherMap
API_KEY = os.getenv("API_KEY", "")

# Configuración de SQLAlchemy
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
Base = declarative_base()

# Definición del modelo de datos
class WeatherData(Base):
    __tablename__ = 'weather_data'
    
    id = Column(Integer, primary_key=True)
    city = Column(String(50))
    country = Column(String(10))
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    description = Column(String(100))
    timestamp = Column(String(30))
    
# Funciones para el ETL

def extract_data(**kwargs):
    """
    Función que extrae datos de la API de OpenWeatherMap para varias ciudades.
    """
    # Lista de ciudades para obtener datos
    cities = ["London", "New York", "Tokyo", "Sydney", "Mexico City","Madrid", "Berlin", "Paris", "Rome", "Beijing","Lima","Caracas","Buenos Aires","Santiago","Bogotá"]
    
    data = []
    for city in cities:
        try:
            # Hacer solicitud a la API
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            
            if response.status_code == 200:
                weather_data = response.json()
                
                # Extraer información relevante
                city_data = {
                    'city': city,
                    'country': weather_data.get('sys', {}).get('country', ''),
                    'temperature': weather_data.get('main', {}).get('temp', 0),
                    'humidity': weather_data.get('main', {}).get('humidity', 0),
                    'pressure': weather_data.get('main', {}).get('pressure', 0),
                    'description': weather_data.get('weather', [{}])[0].get('description', ''),
                    'date': weather_data.get('dt', 0),
                    'timestamp': datetime.now().isoformat()
                }
                
                data.append(city_data)
                print(f"Datos extraídos para {city}")
            else:
                print(f"Error al obtener datos para {city}: {response.status_code}")
                
        except Exception as e:
            print(f"Error al procesar datos para {city}: {e}")
    
    # Guardar datos extraídos para pasar a la siguiente tarea
    kwargs['ti'].xcom_push(key='raw_data', value=data)
    print(f"Extraídos datos para {len(data)} ciudades.")
    return data


def transform_data(**kwargs):
    """
    Función que transforma los datos extraídos.
    - Convierte temperaturas de Celsius a Fahrenheit
    - Normaliza los nombres de las ciudades
    - Añade categoría de temperatura
    """
    # Obtener datos de la tarea anterior
    ti = kwargs['ti']
    raw_data = ti.xcom_pull(task_ids='extract_data', key='raw_data')
    
    # Convertir a DataFrame para facilitar la manipulación
    df = pd.DataFrame(raw_data)
    
    # Transformaciones
    # 1. Convertir temperatura a Fahrenheit
    df['temperature_f'] = df['temperature'] * 9/5 + 32
    
    # 2. Normalizar nombres de ciudades (a mayúsculas)
    df['city'] = df['city'].str.title()
    
    # 3. Añadir categoría de temperatura
    def get_temp_category(temp):
        if temp < 10:
            return 'Frío'
        elif temp < 25:
            return 'Templado'
        else:
            return 'Caliente'
    
    df['temp_category'] = df['temperature'].apply(get_temp_category)
    
    # Convertir de nuevo a lista de diccionarios
    transformed_data = df.to_dict('records')
    
    # Guardar datos transformados para la siguiente tarea
    ti.xcom_push(key='transformed_data', value=transformed_data)
    print(f"Datos transformados: {len(transformed_data)} registros")
    return transformed_data

def load_data(**kwargs):
    """
    Función que carga los datos transformados en la base de datos.
    """
    # Obtener datos transformados
    ti = kwargs['ti']
    transformed_data = ti.xcom_pull(task_ids='transform_data', key='transformed_data')
    
    try:
        # Primero, conectarse a la base de datos PostgreSQL por defecto para crear la base de datos etl_data si no existe
        default_engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres")
        with default_engine.connect() as conn:
            # Desactivar autocommit para poder ejecutar CREATE DATABASE
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            # Verificar si la base de datos existe
            result = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'")
            exists = result.scalar()
            if not exists:
                # Crear la base de datos si no existe
                conn.execute(f"CREATE DATABASE {DB_NAME}")
                print(f"Base de datos {DB_NAME} creada exitosamente")
            else:
                print(f"Base de datos {DB_NAME} ya existe")
        
        # Ahora conectarse a la base de datos etl_data para crear tablas y cargar datos
        engine = create_engine(DATABASE_URL)
        
        # Crear tablas si no existen
        Base.metadata.create_all(engine)
        
        # Crear sesión
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Insertar datos
        for item in transformed_data:
            # Crear objeto WeatherData
            weather_record = WeatherData(
                city=item['city'],
                country=item['country'],
                temperature=item['temperature'],
                humidity=item['humidity'],
                pressure=item['pressure'],
                description=item['description'],
                timestamp=item['timestamp']
            )
            
            # Añadir a la sesión
            session.add(weather_record)
        
        # Commit de la transacción
        session.commit()
        session.close()
        
        print(f"Datos cargados exitosamente: {len(transformed_data)} registros")
        return True
    
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return False

# Definición del DAG
dag = DAG(
    'etl_weather_data', # Nombre del DAG
    default_args=default_args, # Argumentos por defecto
    description='ETL básico para datos meteorológicos',# Descripción del DAG
    schedule_interval=timedelta(minutes=60), # schedule_interval='@hourly',  schedule_interval='0 * * * *',
    start_date=datetime(2025,4,23), # Fecha de inicio del DAG
    catchup=False, # Sí ejecutar tareas pasadas
    tags=['etl', 'weather', 'bootcamp'],
)

# Definición de tareas
start_task = DummyOperator(
    task_id='start_etl',
    dag=dag,
)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    provide_context=True,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    provide_context=True,
    dag=dag,
)

end_task = DummyOperator(
    task_id='end_etl',
    dag=dag,
)

# Definir el orden de las tareas
start_task >> extract_task >> transform_task >> load_task >> end_task
   