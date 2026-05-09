from fastapi import FastAPI
from backend.database.queries import get_clientes

app = FastAPI(title="API de Retención de Gimnasio")

@app.get("/")
def health_check():
    return {"estado": "Servidor corriendo perfectamente"}




    