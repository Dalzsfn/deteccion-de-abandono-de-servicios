from fastapi import APIRouter, HTTPException
from backend.app.services import churn_service
from backend.database.queries import get_clientes
from backend.database.queries import get_cliente

router = APIRouter()

@router.post("/predicciones")
def post_predicciones():
    try:
        clientes = get_clientes()
        predicciones = churn_service.predecir_abandono(clientes)
        return {"predicciones": predicciones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#Añadir información del shap para los clientes de riesgo
@router.post("/predicciones/{cliente_id}")
def post_prediccion_riesgo(cliente_id: int):
    try:
        cliente = get_cliente(cliente_id)
        shap_values = churn_service.obtener_shap_values(cliente)
        return {"shap_values": shap_values}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))