from ollama import Client

client = Client(host='http://localhost:11434')


def generate(
    prompt: str,
    model: str = "qwen3:8b"
):
    response = client.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response["message"]["content"]