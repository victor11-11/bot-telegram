import os
import logging
from collections import defaultdict
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import openai

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

SYSTEM_PROMPT = {
    "role": "system",
    "content": "Eres Claudia, una asistente virtual inteligente, servicial y amable."
}

user_conversations = defaultdict(list)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = [SYSTEM_PROMPT]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="¡Hola! Soy Claudia. ¿En qué puedo ayudarte hoy?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in user_conversations or not user_conversations[user_id]:
        user_conversations[user_id] = [SYSTEM_PROMPT]

    user_conversations[user_id].append({"role": "user", "content": user_text})

    if len(user_conversations[user_id]) > 11:
        user_conversations[user_id] = [SYSTEM_PROMPT] + user_conversations[user_id][-10:]

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=user_conversations[user_id],
        )
        bot_reply = response.choices[0].message.content
        user_conversations[user_id].append({"role": "assistant", "content": bot_reply})
        await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_reply)

    except Exception as e:
        logging.error(f"Error al procesar mensaje: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Lo siento, ocurrió un error al procesar tu solicitud."
        )

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    application.run_polling()