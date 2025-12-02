import ollama

LOCAL_MODEL_NAME = "gemma3:4b"
CLOUD_MODEL_NAME = "llama3.1:8b"

def call_local_model(prompt: str) -> str:

    response = ollama.chat(
        model = LOCAL_MODEL_NAME,
        messages = [
            {"role": "system", "content": "You are a helpful local assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["message"]["content"].strip()

# -------------------------------------------------------------------------------------

def call_cloud_model(prompt: str) -> str:

    response = ollama.chat(
        model = CLOUD_MODEL_NAME,
        messages = [
            {"role": "system", "content": "You are a powerful AI assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["message"]["content"].strip()