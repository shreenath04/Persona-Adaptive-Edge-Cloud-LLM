import ollama
import json

MODEL_NAME = "gemma3:4b"

def call_gemma(prompt: str) -> str:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful AI that strictly follows instructions."},
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"].strip()

# -----------------------------------------------------------------------------------------------------------

TRAIT_SYSTEM_PROMPT = """
You convert a user's self-description into a compact persona profile for an AI assistant.

Given the user's description, extract:

- persona_description: 1–2 sentences summarizing who they are.
- tone_preferences: how they like responses (e.g. 'detailed', 'concise', 'step-by-step', 'friendly').
- expertise_level: 'beginner', 'intermediate', or 'advanced' (for technical topics).
- preferred_language: language code, like 'en'.
- response_style: extra style preferences (e.g. 'use bullet points', 'include code examples').

Respond ONLY as a minified JSON object with exactly these keys.
No extra text, no explanations, no markdown.
"""


def generate_traits_from_description(raw_description: str) -> dict:
    prompt = TRAIT_SYSTEM_PROMPT + f'\n\nUSER_DESCRIPTION: """{raw_description}"""'
    raw_output = call_gemma(prompt).strip()

    #print("Raw model output:")
    #print(raw_output)

    # Remove accidental code fencing if present
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`").strip()
        raw_output = raw_output.replace("json", "").replace("JSON", "").strip()

    raw_output = raw_output.strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        print("\nModel output still isn't valid JSON. You may need to tune prompt.\n")
        raise

# ---------------------------------------------------------------------------------------------------------------

