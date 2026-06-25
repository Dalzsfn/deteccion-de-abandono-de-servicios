# PulseTrack — Dashboard de Churn

Frontend vanilla para el panel de retención de socios del gimnasio.

## Requisitos

- Backend FastAPI corriendo en `http://127.0.0.1:8000`
- Un servidor HTTP local (no abras `index.html` directamente con `file://` — los módulos ES6 requieren HTTP)

## Levantar el frontend

Desde la carpeta `frontend/`:

```bash
# Python 3
python -m http.server 5500

# O con Node (si tienes npx)
npx serve -p 5500
```

Abre: **http://localhost:5500**

## Endpoints consumidos

| Acción | Método | Ruta |
|--------|--------|------|
| Listar socios | GET | `/api/clientes/clientes` |
| Ejecutar modelo | POST | `/api/ml/predicciones` |
| Detalle de riesgo | GET | `/api/ml/predicciones/{cliente_id}` |

La URL base se configura en `js/config.js`.

## Estructura

```
frontend/
├── index.html
├── css/
│   └── styles.css
└── js/
    ├── config.js   → URLs de la API
    ├── api.js      → Llamadas fetch
    ├── ui.js       → Renderizado y componentes visuales
    └── app.js      → Estado y lógica principal
```

## Levantar el backend

Desde la raíz del proyecto:

```bash
uvicorn backend.app.main:app --reload
```
