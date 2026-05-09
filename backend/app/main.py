from fastapi import FastAPI
from backend.app.routes import clientes_routes, prediccion_routes
from backend.database.queries import get_clientes

app = FastAPI(title="API de Retención de Gimnasio")

app.include_router(prediccion_routes.router, prefix="/api/ml", tags=["Predicciones"])
app.include_router(clientes_routes.router, prefix="/api/clientes", tags=["Base de Datos"])

@app.get("/")
def health_check():
    return {"estado": "Servidor corriendo perfectamente"}




    