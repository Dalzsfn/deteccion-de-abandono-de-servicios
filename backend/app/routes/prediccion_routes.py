from fastapi import APIRouter, HTTPException
from backend.app.services import ml_service
from backend.database.queries import get_clientes

router = APIRouter()

@router.post("/predicciones")
def post_predicciones():
    try:
        clientes = get_clientes()
        predicciones = ml_service.predecir_abandono(clientes)
        return {"predicciones": predicciones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))