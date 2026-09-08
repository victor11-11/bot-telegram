import logging
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import TELEGRAM_TOKEN
from database import init_db
from handlers import start_handler, reset_handler, help_handler, message_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def post_init(application):
    """Configura el menú nativo de comandos en la interfaz de Telegram."""
    commands = [
        BotCommand("start", "Iniciar conversación con Claudia"),
        BotCommand("reset", "Reiniciar la memoria del chat"),
        BotCommand("help", "Ver información y comandos disponibles"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    # Inicializar Base de Datos
    init_db()

    # Construir aplicación de Telegram vinculando post_init
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Registrar Manejadores
    application.add_handler(CommandHandler('start', start_handler))
    application.add_handler(CommandHandler('reset', reset_handler))
    application.add_handler(CommandHandler('help', help_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    # Iniciar polling
    application.run_polling()

if __name__ == '__main__':
    main()