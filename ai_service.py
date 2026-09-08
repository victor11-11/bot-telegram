import openai
from config import NVIDIA_API_KEY

client = openai.OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY,
)

def generate_response(messages: list) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        temperature=1,
        top_p=1,
        max_tokens=4096
    )
    return response.choices[0].message.content