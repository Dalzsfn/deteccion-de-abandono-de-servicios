from fastapi import FastAPI
from backend.app.routes import clientes_riesgo_routes, clientes_routes
from backend.database.queries import get_clientes

app = FastAPI(title="API de Retención de Gimnasio")

app.include_router(clientes_riesgo_routes.router, prefix="/api/ml", tags=["Predicciones"])
app.include_router(clientes_routes.router, prefix="/api/clientes", tags=["Base de Datos"])

@app.get("/")
def health_check():
    return {"estado": "Servidor corriendo perfectamente"}




    