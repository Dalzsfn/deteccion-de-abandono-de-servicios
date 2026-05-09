from fastapi import FastAPI
from backend.database.queries import get_clientes
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}   

@app.get("/clientes")
def read_clientes():
    return get_clientes()

@app.get("/predicciones")
def read_predicciones():
    return {"message": "Aquí se mostrarán las predicciones de churn"}