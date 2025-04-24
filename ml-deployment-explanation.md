# DAG Avanzado: Despliegue de Modelos ML

Este documento explica el DAG avanzado para despliegue de modelos de machine learning incluido en el archivo `ml_model_deployment_dag.py`. Este DAG es un ejemplo conceptual con funciones vacías, diseñado para visualizar en el webserver de Airflow un flujo de trabajo complejo de MLOps.

## Propósito

El DAG simula un pipeline completo de MLOps, desde la preparación de datos hasta el despliegue y monitoreo de un modelo de machine learning en producción. Aunque las funciones están vacías (solo contienen declaraciones `print`), la estructura del DAG muestra el flujo de trabajo y las dependencias entre tareas que se visualizarían en la interfaz de Airflow.

## Estructura del DAG

El DAG contiene los siguientes componentes principales:

1. **Verificación y espera de datos**: Verifica que los datos necesarios estén disponibles
2. **Preparación de datos** (TaskGroup): Descarga, valida, preprocesa y divide los datos
3. **Entrenamiento y evaluación** (TaskGroup): Entrena el modelo, evalúa su rendimiento y registra en MLflow
4. **Decisión de despliegue** (BranchPythonOperator): Decide si el modelo cumple con los criterios para ser desplegado
5. **Despliegue del modelo** (TaskGroup): Genera artefactos, despliega API y ejecuta pruebas
6. **Visualización y monitoreo** (TaskGroup): Configura dashboards y sistemas de monitoreo
7. **Notificaciones**: Envía notificaciones sobre el éxito o fallo del proceso

## Características avanzadas implementadas

### 1. Task Groups

El DAG utiliza `TaskGroup` para organizar tareas relacionadas en grupos lógicos, lo que mejora la visualización en la interfaz de Airflow:

```python
with TaskGroup(group_id='preparacion_datos', dag=dag) as grupo_preparacion:
    # Tareas relacionadas con la preparación de datos
```

### 2. Branching

Utiliza `BranchPythonOperator` para implementar lógica condicional que decide si el modelo debe desplegarse basado en su rendimiento:

```python
decidir_despliegue = BranchPythonOperator(
    task_id='decidir_despliegue',
    python_callable=decidir_despliegue,
    dag=dag,
)
```

### 3. Sensores

Implementa `FileSensor` para esperar la disponibilidad de archivos de datos:

```python
esperar_datos = FileSensor(
    task_id='esperar_datos',
    filepath='/data/raw/dataset.csv',
    poke_interval=300,
    timeout=60 * 60 * 12,
    mode='reschedule',
    dag=dag,
)
```

### 4. Trigger Rules personalizadas

Usa diferentes trigger rules para controlar cuándo se ejecutan ciertas tareas:

```python
notificar_exito = PythonOperator(
    task_id='notificar_despliegue_exitoso',
    python_callable=notificar_despliegue_exitoso,
    trigger_rule='all_success',  # Solo se ejecuta si todas las tareas anteriores tienen éxito
    dag=dag,
)

fin = DummyOperator(
    task_id='fin',
    trigger_rule='one_success',  # Se ejecuta si al menos una ruta tiene éxito
    dag=dag,
)
```

### 5. Documentación integrada

Incluye documentación detallada en formato Markdown directamente en el DAG:

```python
doc_md="""
# DAG de Despliegue de Modelo ML
Este DAG implementa un flujo de trabajo completo de MLOps:
...
"""
```

## Cómo visualizar este DAG en Airflow

Para visualizar este DAG en la interfaz web de Airflow:

1. Coloca el archivo `ml_model_deployment_dag.py` en el directorio `airflow/dags/`
2. Reinicia el scheduler de Airflow si es necesario
3. Accede a la interfaz web de Airflow (por defecto en http://localhost:8080)
4. El DAG aparecerá en la lista con el ID `ml_model_deployment_advanced`
5. Puedes visualizar la estructura del grafo en la vista "Graph" o "Grid"

Nota: Este DAG es solo para visualización y no ejecutará ninguna lógica real, ya que todas las funciones están vacías.

## Personalización para casos de uso específicos

Este DAG puede servir como plantilla para implementar flujos de trabajo de MLOps reales. Para adaptarlo a tus necesidades:

1. Implementa las funciones vacías con tu lógica de negocio real
2. Ajusta las rutas de archivos y configuraciones según tu entorno
3. Modifica las dependencias entre tareas según tu flujo de trabajo específico
4. Agrega o elimina tareas según sea necesario

## Extensiones posibles

Para extender este DAG en un entorno real, considera las siguientes adiciones:

1. **Integración con servicios cloud**: AWS SageMaker, Azure ML, Google AI Platform
2. **Alertas avanzadas**: Integración con Slack, Teams o sistemas de tickets
3. **A/B Testing**: Implementar despliegue paralelo de múltiples variantes del modelo
4. **Rollback automático**: Lógica para revertir a versiones anteriores si se detectan problemas
5. **Feature Store**: Integración con repositorios de características para entrenamiento e inferencia
