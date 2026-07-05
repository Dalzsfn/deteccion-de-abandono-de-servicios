# Sistema de Predicción de Abandono y Estrategias de Retención

Este proyecto tiene como objetivo desarrollar un sistema inteligente para la detección temprana de clientes en riesgo de abandono (churn) en gimnasios. La solución integra modelos de aprendizaje automático para la clasificación y modelos de lenguaje de gran escala (LLM) para la generación automatizada de estrategias de comunicación personalizadas.

Estado del proyecto: En desarrollo — backend funcional end-to-end.

## Descripción del Proyecto

El sistema busca optimizar la retención de socios mediante un enfoque proactivo. A diferencia de los métodos tradicionales reactivos, este proyecto utiliza el historial de comportamiento del cliente para predecir la probabilidad de baja. Una vez identificado el riesgo, el sistema emplea IA generativa para redactar mensajes de fidelización específicos, basándose en los factores exactos que motivan el posible abandono, y los envía directamente al cliente a través de Telegram.

## Avance Actual

1. **Persistencia de Datos**: Base de datos en PostgreSQL con el dataset sintético de 110 socios y su historial completo de suscripciones, asistencias y compras. Incluye una vista (`vista_clientes`) que calcula en tiempo real las 11 features de entrada al modelo —antigüedad como cliente, frecuencia promedio histórica de asistencias, frecuencia del último mes, meses restantes de contrato, gasto en servicios adicionales, entre otras— directamente a partir de las tablas base (`clientes`, `suscripcion`, `asistencias`, `compras`). Además, se gestionan dos tablas adicionales: `telegram_links` para la vinculación segura de cuentas de Telegram, y `sugerencias_enviadas` para registrar qué clientes ya recibieron una comunicación y evitar duplicados.

2. **Modelo de Clasificación**: Red neuronal implementada en PyTorch (`RedPrediccionChurn`), con arquitectura secuencial de cuatro capas lineales (input → 32 → 16 → 8 → 1), activaciones ReLU y Dropout del 20 % en las capas intermedias. La salida es un único logit con función de pérdida `BCEWithLogitsLoss`; la probabilidad final se obtiene aplicando `sigmoid` en inferencia. El preprocesamiento utiliza un `ColumnTransformer` de scikit-learn (StandardScaler para variables de distribución normal, MinMaxScaler para variables sesgadas o acotadas), y el balanceo de clases se realiza con SMOTE sobre el conjunto de entrenamiento completo antes del split. El modelo entrenado se persiste en `ml_pipeline/modelo_churn.pth` junto con el preprocesador serializado.

3. **Explicabilidad con SHAP**: Implementada en producción mediante `KernelExplainer` de SHAP, conectado directamente a la red neuronal de PyTorch a través de una función envolvente (`modelo_para_shap`) que ejecuta el forward pass en modo `no_grad`. Por cada cliente en riesgo se calculan los valores SHAP y se exponen los dos factores de mayor peso absoluto como justificación de la predicción.

4. **Generación de Sugerencias con LLM**: Operativa utilizando Ollama con el modelo `phi3` ejecutado localmente. A partir del factor de riesgo principal identificado por SHAP, el servicio selecciona una instrucción estratégica predefinida y la pasa al LLM con un prompt estricto: un único mensaje de Telegram de máximo tres líneas, en tono amigable y sin mencionar riesgos ni probabilidades.

5. **API con FastAPI**: Implementada con arquitectura por capas: `routes` (endpoints), `services` (lógica de negocio) y `database/queries.py` (acceso a datos con `SQLAlchemy` usando `text()` puro, sin ORM). El bot de Telegram se inicializa y detiene junto con el servidor mediante el mecanismo `lifespan` de FastAPI. Endpoints disponibles:
   - `GET  /api/clientes/clientes` — lista todos los socios con sus datos calculados.
   - `POST /api/ml/predicciones` — ejecuta el modelo sobre todos los clientes y devuelve los que están en riesgo.
   - `GET  /api/ml/predicciones/{cliente_id}` — detalle de un cliente en riesgo: probabilidad, factores SHAP y sugerencia generada por el LLM.
   - `POST /api/telegram/enviar-sugerencia/{cliente_id}` — envía al cliente la sugerencia que ya se mostró en el panel, sin volver a invocar el LLM.
   - `GET  /api/telegram/sugerencias-enviadas` — historial de todos los envíos realizados.

6. **Integración con Telegram**: Funcional en modo polling (sin webhook, adecuado para entorno local). La vinculación de cuentas es segura: el cliente escribe `/start` al bot (`@pulsetrackgym`), que le solicita compartir su número de teléfono mediante el mecanismo nativo de Telegram (contact sharing). El bot normaliza el número al formato local ecuatoriano y lo busca en la columna `celular` de la tabla `clientes`. No se expone ningún identificador interno en ningún enlace. Una vez vinculado, el operador puede enviar la sugerencia de retención desde el panel con un solo clic; el sistema protege contra reenvíos duplicados al mismo cliente.

7. **Frontend**: Dashboard operativo desarrollado en JavaScript vanilla sin framework ni herramienta de build, con arquitectura modular: `config.js` (URLs de la API), `api.js` (llamadas HTTP), `ui.js` (renderizado de HTML) y `app.js` (estado y orquestación). Incluye: listado filtrable de todos los socios, botón para ejecutar el modelo (que actualiza la vista mostrando solo los clientes en riesgo), modal de detalle por cliente con probabilidad de abandono, indicador visual por tramos, factores SHAP y sugerencia del LLM, botón de envío por Telegram con control de estado (deshabilitado si ya se envió), y panel colapsable con el historial de sugerencias enviadas.

## Tecnologías Utilizadas

### Backend y Datos
- **Python 3.13+**: Lenguaje principal de desarrollo.
- **PostgreSQL 15+**: Sistema de gestión de base de datos relacional. Almacena el dataset sintético y los datos operativos (vinculaciones de Telegram, registro de envíos).
- **SQLAlchemy**: Usado únicamente para gestión de conexiones y ejecución de consultas con `text()` — sin ORM.
- **FastAPI**: Framework para la API REST, con soporte asíncrono y gestión del ciclo de vida del servidor (`lifespan`).
- **python-dotenv**: Carga de variables de entorno desde `backend/.env`.

### Inteligencia Artificial y Ciencia de Datos
- **PyTorch**: Framework de deep learning para la definición, entrenamiento e inferencia de la red neuronal `RedPrediccionChurn`.
- **scikit-learn**: Utilizado en el pipeline de preprocesamiento (`ColumnTransformer`, `StandardScaler`, `MinMaxScaler`) que se serializa junto al modelo.
- **imbalanced-learn**: Balanceo del dataset de entrenamiento con SMOTE.
- **Pandas y NumPy**: Manipulación y análisis de estructuras de datos.
- **SHAP**: Explicabilidad de la predicción mediante `KernelExplainer` conectado a la red neuronal de PyTorch.
- **Ollama + phi3**: Ejecución local del modelo de lenguaje para generar los mensajes de retención personalizados.

### Frontend
- **HTML + CSS + JavaScript vanilla**: Sin framework ni build tool. CSS moderno con Container Queries, `color-mix()`, `light-dark()`, `:has()` y View Transitions API.

### Integraciones
- **python-telegram-bot (v21+)**: Bot de Telegram en modo polling para la vinculación de cuentas y el envío de sugerencias directamente a los clientes.

## Arquitectura de la Solución

El flujo de trabajo se describe en los siguientes pasos:

1. **Extracción**: La vista `vista_clientes` de PostgreSQL calcula en tiempo real las features de entrada al modelo a partir de las tablas de suscripciones, asistencias y compras de cada socio.
2. **Clasificación**: La red neuronal en PyTorch evalúa el perfil de cada cliente y produce una probabilidad de abandono. Los clientes con probabilidad ≥ 0,5 se clasifican en riesgo.
3. **Explicabilidad**: SHAP `KernelExplainer` determina los dos factores de mayor peso en la predicción de cada cliente en riesgo, identificando el motivo principal.
4. **Generación**: El factor principal se pasa a `phi3` vía Ollama, que redacta un mensaje de retención breve y personalizado siguiendo una instrucción estratégica predefinida por tipo de riesgo.
5. **Notificación**: El operador revisa la sugerencia en el panel de administración y, con un clic, la envía al cliente directamente por Telegram. El sistema garantiza que cada cliente reciba como máximo un envío.

## Configuración del Entorno

### Requisitos Previos
- PostgreSQL 15+ instalado y en ejecución.
- Python 3.13 o superior.
- Ollama instalado y corriendo localmente con el modelo `phi3` descargado (`ollama pull phi3`).
- Un bot de Telegram creado con `@BotFather` y su token disponible.

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Dalzsfn/deteccion-de-abandono-de-servicios.git
   cd deteccion-de-abandono-de-servicios
   ```

2. **Crear y activar un entorno virtual:**
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   # macOS / Linux:
   source .venv/bin/activate
   ```

3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar las variables de entorno:**

   Copia el archivo de ejemplo y rellena los valores:
   ```bash
   cp backend/.env.example backend/.env
   ```

   Edita `backend/.env` con los datos de tu entorno:
   ```env
   DB_USER=tu_usuario
   DB_PASSWORD=tu_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=nombre_de_tu_base_de_datos

   TELEGRAM_BOT_TOKEN=123456789:ABCdef...
   ```

   > **Importante:** `TELEGRAM_BOT_TOKEN` es obligatorio. El bot se inicializa en el `lifespan` de FastAPI y el servidor no arrancará si esta variable no está definida. Obtén el token creando un bot con `@BotFather` en Telegram.

5. **Inicializar la base de datos:**

   El script `backend/database/gym_seed.sql` crea todas las tablas, tipos, índices, la vista `vista_clientes` y carga los 110 clientes sintéticos con su historial completo. Ejecuta el script completo en tu instancia de PostgreSQL:

   ```bash
   # Con psql desde la línea de comandos:
   psql -U tu_usuario -d nombre_de_tu_base_de_datos -f backend/database/gym_seed.sql

   # O desde el cliente psql interactivo:
   \i backend/database/gym_seed.sql
   ```

   El script está envuelto en una transacción (`BEGIN` / `COMMIT`) y elimina las tablas existentes antes de recrearlas, por lo que es idempotente. Al finalizar correctamente verás el mensaje de `COMMIT`.

6. **Entrenar el modelo** (solo si no existe `ml_pipeline/modelo_churn.pth`):
   ```bash
   python -m ml_pipeline.train_model_nn
   ```
   Esto genera el archivo `modelo_churn.pth` con los pesos de la red neuronal y el preprocesador serializado.

7. **Levantar el backend:**
   ```bash
   uvicorn backend.app.main:app --reload
   ```
   El servidor arranca en `http://127.0.0.1:8000`. En consola deberías ver:
   ```
   INFO - Bot de Telegram iniciado en modo polling.
   ```

8. **Levantar el frontend:**

   Desde la carpeta `frontend/`, sirve los archivos estáticos con cualquier servidor HTTP local (los módulos ES6 requieren HTTP, no `file://`):
   ```bash
   # Con Python:
   python -m http.server 5500
   # O con Node.js:
   npx serve -p 5500
   ```
   Abre `http://localhost:5500` en el navegador.

### Referencia rápida de endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/api/clientes/clientes` | Lista todos los socios con sus features calculadas |
| `POST` | `/api/ml/predicciones` | Ejecuta el modelo y devuelve clientes en riesgo |
| `GET`  | `/api/ml/predicciones/{id}` | Detalle de riesgo: probabilidad, SHAP, sugerencia LLM |
| `POST` | `/api/telegram/enviar-sugerencia/{id}` | Envía la sugerencia al cliente por Telegram |
| `GET`  | `/api/telegram/sugerencias-enviadas` | Historial de sugerencias enviadas |

## Próximos Pasos

- **Visualización de métricas agregadas**: Ampliar el panel con tendencias históricas de riesgo, tasa de retención tras el envío de sugerencias e historial de campañas.
- **Flujo de aprobación**: Introducir un estado intermedio de revisión antes del envío masivo de sugerencias, para que el operador pueda editar el mensaje generado por el LLM antes de enviarlo.
- **Tests automatizados**: Implementar suite de pruebas unitarias e integración para los servicios críticos (clasificación, normalización de números de Telegram, validaciones de envío).
- **Variables de entorno documentadas**: Ampliar `.env.example` con todos los parámetros opcionales y sus valores por defecto a medida que el sistema crezca.
- **Instrucciones de despliegue**: Documentar el proceso para ejecutar el sistema en un entorno de servidor (systemd, Docker, etc.), incluyendo la gestión del polling de Telegram en producción.
