import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

DB_NAME = "bot_memory.db"

SYSTEM_PROMPT = {
    "role": "system",
    "content": "Eres Claudia, una asistente virtual inteligente, servicial y amable."
}