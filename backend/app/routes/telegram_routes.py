from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.services import telegram_service
from backend.database.queries import (
    get_chat_id,
    get_sugerencia_enviada,
    insertar_sugerencia_enviada,
    listar_sugerencias_enviadas,
)

router = APIRouter()

BOT_USERNAME = "pulsetrackgym"


class EnviarSugerenciaBody(BaseModel):
    mensaje: str


@router.post("/enviar-sugerencia/{cliente_id}")
async def enviar_sugerencia(cliente_id: int, body: EnviarSugerenciaBody):
    
    mensaje = body.mensaje.strip()
    if not mensaje:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")

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
