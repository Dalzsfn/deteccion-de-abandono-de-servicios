from fastapi import APIRouter, HTTPException
from backend.app.services import shap_service, telegram_service
from backend.database.queries import (
    get_chat_id,
    get_cliente,
    get_sugerencia_enviada,
    insertar_sugerencia_enviada,
    listar_sugerencias_enviadas,
)

router = APIRouter()

BOT_USERNAME = "pulsetrackgym"


@router.post("/enviar-sugerencia/{cliente_id}")
async def enviar_sugerencia(cliente_id: int):
    chat_id = get_chat_id(cliente_id)
    if chat_id is None:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "sin_telegram",
                "mensaje": (
                    f"Este cliente aún no vinculó su cuenta de Telegram. "
                    f"Pídele que le escriba a @{BOT_USERNAME} y comparta "
                    f"su número de teléfono."
                ),
            },
        )

    ya_enviada = get_sugerencia_enviada(cliente_id)
    if ya_enviada is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya se envió una sugerencia a este cliente.",
        )

    cliente = get_cliente(cliente_id)

    try:
        detalle = shap_service.obtener_detalle_abandono(cliente)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    mensaje = detalle["sugerencia_retencion"]

    await telegram_service.send_message(chat_id, mensaje)
    insertar_sugerencia_enviada(cliente_id, mensaje)

    return {
        "enviado": True,
        "cliente_id": cliente_id,
        "mensaje_enviado": mensaje,
    }


@router.get("/sugerencias-enviadas")
def get_sugerencias_enviadas():
    return {"sugerencias": listar_sugerencias_enviadas()}
