from fastapi import APIRouter, HTTPException
from backend.app.services import ml_service_nn
from backend.database.queries import get_clientes

router = APIRouter()

@router.post("/predicciones")
def post_predicciones():
    try:
        clientes = get_clientes()
        predicciones = ml_service_nn.predecir_abandono(clientes)
        return {"predicciones": predicciones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#Añadir información del shap para los clientes de riesgo