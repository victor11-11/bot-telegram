import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Convierte el ID de administrador a entero (agrega tu ID en el archivo .env)
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

DB_NAME = "bot_memory.db"

# Modelos NVIDIA NIM
TEXT_MODEL = "openai/gpt-oss-20b"
VISION_MODEL = "meta/llama-3.2-11b-vision-instruct"

SYSTEM_PROMPT = {
    "role": "system",
    "content": "Eres Claudia, una asistente virtual inteligente, servicial y amable."
}