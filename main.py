import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import TELEGRAM_TOKEN
from database import init_db
from handlers import start_handler, reset_handler, message_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # Inicializar Base de Datos
    init_db()

    # Construir aplicación de Telegram
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Registrar Manejadores
    application.add_handler(CommandHandler('start', start_handler))
    application.add_handler(CommandHandler('reset', reset_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    # Iniciar polling
    application.run_polling()

if __name__ == '__main__':
    main()