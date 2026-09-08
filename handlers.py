import logging
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from config import SYSTEM_PROMPT
from database import get_user_history, save_user_history
from ai_service import generate_response

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user_history(user_id, [SYSTEM_PROMPT])
    welcome_text = (
        "¡Hola! Soy *Claudia*, tu asistente virtual. 🤖✨\n\n"
        "Puedo ayudarte a responder preguntas, redactar texto o analizar ideas.\n\n"
        "📌 *Comandos disponibles:*\n"
        "• `/start` - Iniciar el bot\n"
        "• `/reset` - Borrar la memoria y comenzar una nueva conversación\n"
        "• `/help` - Ver ayuda y soporte"
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome_text,
        parse_mode=ParseMode.MARKDOWN
    )

async def reset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user_history(user_id, [SYSTEM_PROMPT])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🔄 *Memoria reiniciada.* Hemos comenzado una nueva conversación.",
        parse_mode=ParseMode.MARKDOWN
    )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "ℹ️ *Centro de Ayuda - Claudia*\n\n"
        "• Envía cualquier mensaje de texto para conversar.\n"
        "• Mantengo el contexto de la conversación activa.\n"
        "• Si la conversación se vuelve muy larga o quieres cambiar de tema, usa `/reset`.\n"
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_text,
        parse_mode=ParseMode.MARKDOWN
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # Indicador de "Escribiendo..."
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action=ChatAction.TYPING
    )

    history = get_user_history(user_id)
    history.append({"role": "user", "content": user_text})

    # Ventana deslizante (System Prompt + últimos 10 mensajes)
    if len(history) > 11:
        history = [SYSTEM_PROMPT] + history[-10:]

    try:
        bot_reply = generate_response(history)
        history.append({"role": "assistant", "content": bot_reply})
        save_user_history(user_id, history)

        # Intenta enviar con formato Markdown; si falla por caracteres especiales, envía en texto plano
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=bot_reply,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=bot_reply
            )

    except Exception as e:
        logging.error(f"Error al procesar mensaje de {user_id}: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ *Contratiempo temporal:* No pude procesar tu solicitud. Por favor intenta de nuevo en unos momentos.",
            parse_mode=ParseMode.MARKDOWN
        )