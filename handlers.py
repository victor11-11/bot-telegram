import os
import logging
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from config import SYSTEM_PROMPT, ADMIN_USER_ID
from database import get_user_history, save_user_history
from ai_service import generate_response, analyze_image, transcribe_audio

def restricted(func):
    """Decorador para asegurar que solo el ADMIN_USER_ID pueda usar el bot."""
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if ADMIN_USER_ID != 0 and user_id != ADMIN_USER_ID:
            logging.warning(f"Acceso denegado para el usuario {user_id}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⛔ *Acceso denegado:* Este bot es de uso privado.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

@restricted
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user_history(user_id, [SYSTEM_PROMPT])
    welcome_text = (
        "¡Hola! Soy *Claudia*, tu asistente virtual personal. 🤖✨\n\n"
        "Puedo procesar texto, responder a notas de voz y analizar imágenes.\n\n"
        "📌 *Comandos:*\n"
        "• `/start` - Iniciar\n"
        "• `/reset` - Reiniciar memoria\n"
        "• `/help` - Ayuda"
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome_text,
        parse_mode=ParseMode.MARKDOWN
    )

@restricted
async def reset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user_history(user_id, [SYSTEM_PROMPT])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🔄 *Memoria reiniciada.* Hemos comenzado una nueva conversación.",
        parse_mode=ParseMode.MARKDOWN
    )

@restricted
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "ℹ️ *Centro de Ayuda - Claudia*\n\n"
        "• Envía **texto** para conversar normalmente.\n"
        "• Envía una **nota de voz** y la transcribiré/responderé.\n"
        "• Envía una **imagen** (con o sin pie de foto) para que la analice.\n"
        "• Usa `/reset` para limpiar la memoria del chat."
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_text,
        parse_mode=ParseMode.MARKDOWN
    )

@restricted
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    history = get_user_history(user_id)
    history.append({"role": "user", "content": user_text})

    if len(history) > 11:
        history = [SYSTEM_PROMPT] + history[-10:]

    try:
        bot_reply = generate_response(history)
        history.append({"role": "assistant", "content": bot_reply})
        save_user_history(user_id, history)

        try:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_reply, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_reply)

    except Exception as e:
        logging.error(f"Error al procesar mensaje: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ No pude procesar tu solicitud.")

@restricted
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa notas de voz enviadas por el usuario."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    file_id = update.message.voice.file_id
    new_file = await context.bot.get_file(file_id)
    file_path = f"temp_{file_id}.ogg"
    
    await new_file.download_to_drive(file_path)

    try:
        # Transcribir nota de voz
        transcription = transcribe_audio(file_path)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=f"🎙️ *Transcripción:* _{transcription}_", 
            parse_mode=ParseMode.MARKDOWN
        )

        # Procesar la transcripción como mensaje de texto
        update.message.text = transcription
        await message_handler(update, context)

    except Exception as e:
        logging.error(f"Error procesando voz: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Ocurrió un error al procesar tu nota de voz.")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@restricted
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa imágenes enviadas por el usuario."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    photo_file = await update.message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()
    
    prompt = update.message.caption if update.message.caption else "Describe esta imagen en detalle:"

    try:
        reply = analyze_image(bytes(image_bytes), prompt)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
    except Exception as e:
        logging.error(f"Error procesando imagen: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ No pude analizar la imagen.")