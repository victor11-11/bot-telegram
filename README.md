# Claudia - Telegram Bot

Asistente virtual para Telegram enfocado en la integración de modelos de lenguaje mediante OpenRouter y gestión de contexto conversacional por usuario.

---

## Características

* **Integración de IA:** Procesamiento de texto utilizando el modelo `meta-llama/llama-3.3-70b-instruct` a través de OpenRouter API.
* **Gestión de Contexto:** Seguimiento del historial de conversación individual (límite de 10 interacciones por usuario).
* **Manejo Seguro de Credenciales:** Separación de variables de entorno mediante archivos `.env`.
* **Despliegue:** Preparado para ejecución continua en servidores VPS (AWS Lightsail) con `systemd`.

---

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **Librerías principales:** `python-telegram-bot`, `openai`, `python-dotenv`
* **Infraestructura:** AWS Lightsail (Ubuntu)

---

## Instalación y Configuración Local

### 1. Clonar el repositorio

```bash
git clone git@github.com:victor11-11/bot-telegram.git
cd bot-telegram

python3 -m venv venv

# En Linux / macOS
source venv/bin/activate

# En Windows
# venv\Scripts\activate

pip install python-telegram-bot openai python-dotenv

# Credenciales del Bot de Telegram
TELEGRAM_TOKEN=tu_token_de_telegram

# Credenciales de OpenRouter API
OPENROUTER_API_KEY=tu_openrouter_api_key

python bot.py