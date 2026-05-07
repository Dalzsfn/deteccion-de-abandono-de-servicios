from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}   

@app.get("/clientes")
def read_clientes():
    return {"message": "Aquí se mostrarán los clientes"}

@app.get("/predicciones")
def read_predicciones():
    return {"message": "Aquí se mostrarán las predicciones de churn"}