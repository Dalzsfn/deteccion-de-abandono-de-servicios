import os
import re
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from backend.database.queries import upsert_telegram_link, buscar_cliente_por_celular

logger = logging.getLogger(__name__)

_application: Application | None = None


def get_bot_token() -> str | None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return None
    return token


def normalizar_numero(numero_internacional: str) -> str:
    numero = re.sub(r"[\s\-\(\)]", "", numero_internacional)

    if numero.startswith("+"):
        numero = numero[1:]

    if numero.startswith("593"):
        numero = "0" + numero[3:]

    return numero


async def _handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    teclado = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Compartir mi número", request_contact=True)]],
        one_time_keyboard=True,
        resize_keyboard=True,
    )
    await update.message.reply_text(
        "Para vincular tu cuenta con el gimnasio, comparte tu número de teléfono.",
        reply_markup=teclado,
    )


async def _handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    contacto = update.message.contact

    if contacto.user_id and contacto.user_id != update.effective_user.id:
        await update.message.reply_text(
            "Solo puedes compartir tu propio número de teléfono.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    numero_raw = contacto.phone_number  
    numero_normalizado = normalizar_numero(numero_raw)

    print(f"\n\n==========================================")
    print(f"👉👉👉 ¡AQUÍ ESTÁ TU CHAT ID!: {chat_id} 👈👈👈")
    print(f"==========================================\n\n")
    
    logger.info(
        "Contacto recibido: raw=%s normalizado=%s chat_id=%s",
        numero_raw,
        numero_normalizado,
        chat_id,
    )

    cliente_id = buscar_cliente_por_celular(numero_normalizado)

    if cliente_id is None:
        await update.message.reply_text(
            "No encontramos ese número en nuestros registros. "
            "Verifica con el gimnasio si tu número está actualizado.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    try:
        upsert_telegram_link(cliente_id, chat_id)
        logger.info("Vinculado cliente_id=%s con chat_id=%s", cliente_id, chat_id)
        await update.message.reply_text(
            "¡Listo! Tu cuenta quedó vinculada correctamente. 💪",
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception as exc:
        logger.error("Error guardando vinculación cliente %s: %s", cliente_id, exc)
        await update.message.reply_text(
            "Ocurrió un error al vincular tu cuenta. Inténtalo de nuevo.",
            reply_markup=ReplyKeyboardRemove(),
        )


async def send_message(chat_id: int, text: str) -> None:
    if _application is None:
        raise RuntimeError("El bot de Telegram no está inicializado.")
    await _application.bot.send_message(chat_id=chat_id, text=text)


async def startup() -> None:
    global _application
    token = get_bot_token()
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN no configurado. El bot de Telegram estará desactivado.")
        return
        
    _application = Application.builder().token(token).build()
    _application.add_handler(CommandHandler("start", _handle_start))
    _application.add_handler(MessageHandler(filters.CONTACT, _handle_contact))
    await _application.initialize()
    await _application.start()
    await _application.updater.start_polling(allowed_updates=["message"])
    logger.info("Bot de Telegram iniciado en modo polling.")


async def shutdown() -> None:
    global _application
    if _application is None:
        return
    await _application.updater.stop()
    await _application.stop()
    await _application.shutdown()
    _application = None
    logger.info("Bot de Telegram detenido.")