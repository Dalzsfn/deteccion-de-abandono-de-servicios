# Sistema de Predicción de Abandono y Estrategias de Retención

Este proyecto tiene como objetivo desarrollar un sistema inteligente para la detección temprana de clientes en riesgo de abandono (churn) en gimnasios. La solución integra modelos de aprendizaje automático para la clasificación y modelos de lenguaje de gran escala (LLM) para la generación automatizada de estrategias de comunicación personalizadas.

Estado del proyecto: En desarrollo.

## Descripción del Proyecto

El sistema busca optimizar la retención de socios mediante un enfoque proactivo. A diferencia de los métodos tradicionales reactivos, este proyecto utiliza el historial de comportamiento del cliente para predecir la probabilidad de baja. Una vez identificado el riesgo, el sistema emplea IA generativa para redactar mensajes de fidelización específicos, basándose en los factores exactos que motivan el posible abandono.

## Avance Actual

A día de hoy, el proyecto se encuentra en su primera fase técnica:

1.  Persistencia de Datos: Implementación de la base de datos en PostgreSQL para el almacenamiento y gestión del dataset sintético de gimnasio.
2.  Procesamiento de Datos: Pipeline de limpieza y transformación de variables (ingeniería de características) desde la base de datos hacia el entorno de Python.
3.  Modelo de Clasificación: Entrenamiento y validación inicial del algoritmo de clasificación (Random Forest) para identificar clientes con alta probabilidad de abandono.

## Tecnologías Utilizadas

### Backend y Datos
- Python 3.13+: Lenguaje principal de desarrollo.
- PostgreSQL: Sistema de gestión de base de datos relacional para la persistencia del dataset.
- FastAPI: Framework utilizado para la construcción de la API de servicios (en implementación).

### Inteligencia Artificial y Ciencia de Datos
- Scikit-learn: Librería para el entrenamiento, prueba y evaluación del modelo de clasificación.
- Pandas y NumPy: Manipulación y análisis de estructuras de datos.
- SHAP (SHapley Additive exPlanations): Implementación de IA explicable para identificar los factores decisivos de riesgo por cada cliente.
- Ollama: Entorno para la ejecución local de modelos de lenguaje (LLM) como Phi-3 o Llama-3.

## Arquitectura de la Solución

El flujo de trabajo actual se describe en los siguientes pasos:

1.  Extracción: Consulta de datos socioeconómicos y de asistencia desde PostgreSQL.
2.  Clasificación: Evaluación del perfil del cliente a través del modelo de Machine Learning.
3.  Explicabilidad: Uso de SHAP para determinar qué variables (ej. fin de contrato, caída en frecuencia de visitas) pesan más en la predicción de riesgo.
4.  Generación (Próximamente): Envío de estos factores a un LLM local vía Ollama para redactar una oferta de retención.

## Configuración del Entorno

### Requisitos Previos
- PostgreSQL 15+ instalado y configurado.
- Python 3.13 o superior.
- Ollama instalado (para futuras pruebas de LLM).

### Instalación
1. Clonar el repositorio:
   git clone https://github.com/tu-usuario/gym-churn-ai.git

2. Crear y activar un entorno virtual:
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate

3. Instalar las dependencias necesarias:
   pip install -r requirements.txt

4. Configurar la base de datos:
   Asegúrese de ejecutar el script SQL proporcionado en la carpeta /db para poblar las tablas con el dataset sintético.

## Próximos Pasos
- Integración completa del módulo de generación de texto (LLM) mediante Ollama.
- Automatización de notificaciones a través de la API de Telegram.
- Desarrollo de un panel de administración para la visualización de métricas y clientes en riesgo.
