import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from config import SYSTEM_PROMPT
from database import get_user_history, save_user_history
from ai_service import generate_response

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user_history(user_id, [SYSTEM_PROMPT])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="¡Hola! Soy Claudia. ¿En qué puedo ayudarte hoy?"
    )

async def reset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user_history(user_id, [SYSTEM_PROMPT])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🔄 Memoria reiniciada. Hemos comenzado una nueva conversación."
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # Indicador "Escribiendo..."
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action=ChatAction.TYPING
    )

    history = get_user_history(user_id)
    history.append({"role": "user", "content": user_text})

    # Ventana deslizante de historial (System Prompt + últimos 10 mensajes)
    if len(history) > 11:
        history = [SYSTEM_PROMPT] + history[-10:]

    try:
        bot_reply = generate_response(history)
        history.append({"role": "assistant", "content": bot_reply})
        save_user_history(user_id, history)

        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=bot_reply
        )
    except Exception as e:
        logging.error(f"Error al procesar mensaje de {user_id}: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Lo siento, ocurrió un error al procesar tu solicitud."
        )