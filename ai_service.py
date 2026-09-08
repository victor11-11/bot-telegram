import base64
import openai
from config import NVIDIA_API_KEY, TEXT_MODEL, VISION_MODEL

client = openai.OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY,
)

def generate_response(messages: list) -> str:
    """Genera respuesta de texto utilizando el historial de chat."""
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=messages,
        temperature=1,
        top_p=1,
        max_tokens=4096
    )
    return response.choices[0].message.content

def analyze_image(image_bytes: bytes, prompt: str = "Describe esta imagen en detalle:") -> str:
    """Analiza una imagen enviada por el usuario usando un modelo multimodal."""
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        max_tokens=1024
    )
    return response.choices[0].message.content

def transcribe_audio(audio_file_path: str) -> str:
    """Transcribe un archivo de audio usando la API de OpenAI/NVIDIA."""
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="nvidia/canary-1b", # O usa "whisper-1" si apuntas a OpenAI
            file=audio_file
        )
    return transcript.text