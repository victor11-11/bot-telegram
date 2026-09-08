import logging
import traceback
import html
import json
from telegram import BotCommand, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_TOKEN, ADMIN_USER_ID
from database import init_db
from handlers import (
    start_handler, reset_handler, help_handler, 
    message_handler, voice_handler, photo_handler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def post_init(application):
    commands = [
        BotCommand("start", "Iniciar conversación con Claudia"),
        BotCommand("reset", "Reiniciar la memoria del chat"),
        BotCommand("help", "Ver información y comandos disponibles"),
    ]
    await application.bot.set_my_commands(commands)

async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un reporte de error detallado al administrador por Telegram."""
    logging.error("Excepción detectada:", exc_info=context.error)

    if ADMIN_USER_ID == 0:
        return

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    message = (
        f"🚨 *ALERTA DE ERROR EN VPS*\n\n"
        f"```python\n{html.escape(tb_string[-1000:])}\n```"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=message,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"No se pudo enviar la alerta de error al admin: {e}")

def main():
    init_db()

    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Registro del Manejador Global de Errores
    application.add_error_handler(global_error_handler)

    # Registros de Comandos
    application.add_handler(CommandHandler('start', start_handler))
    application.add_handler(CommandHandler('reset', reset_handler))
    application.add_handler(CommandHandler('help', help_handler))

    # Registros de Mensajes (Texto, Notas de Voz e Imágenes)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    application.run_polling()

if __name__ == '__main__':
    main()