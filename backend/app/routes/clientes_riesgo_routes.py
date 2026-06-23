from fastapi import APIRouter, HTTPException
from backend.app.services import churn_service, shap_service
from backend.database.queries import get_clientes, get_cliente

router = APIRouter()


@router.post("/predicciones")
def post_predicciones():
    try:
        clientes = get_clientes()
        clientes_en_riesgo = churn_service.listar_clientes_en_riesgo(clientes)
        return {"clientes_en_riesgo": clientes_en_riesgo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predicciones/{cliente_id}")
def get_detalle_prediccion(cliente_id: int):
    try:
        cliente = get_cliente(cliente_id)
        return shap_service.obtener_detalle_abandono(cliente)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
