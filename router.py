import json
from typing import Dict, Any

from traits_gen import call_gemma

# Hard rule: long requests always go to the cloud model
WORD_LENGTH_THRESHOLD = 500

ROUTE_LOCAL = "LOCAL_SMALL_MODEL"
ROUTE_CLOUD = "CLOUD_LARGE_MODEL"


ROUTER_SYSTEM_PROMPT = """
You are a router in a hybrid edge–cloud AI system.

You have access to TWO models:

1) LOCAL_SMALL_MODEL
   - A 4B-parameter Gemma model running on the user's machine.
   - Fast and cheap.
   - This should be the DEFAULT choice in most cases.

2) CLOUD_LARGE_MODEL
   - An 8B-parameter Llama model.
   - Slower and more expensive.
   - Use this only when the extra capability clearly matters.

Your job:
1. Decide whether to use LOCAL_SMALL_MODEL or CLOUD_LARGE_MODEL.
2. Build a final_prompt string that we will send directly to the chosen model.

Routing principles (VERY IMPORTANT):

- Start from the assumption: "LOCAL_SMALL_MODEL is enough".
- Use LOCAL_SMALL_MODEL for:
  - Short or medium-length questions.
  - Everyday Q&A: definitions, explanations, basic reasoning, small examples.
  - Simple coding help or small code snippets.
  - Casual chat, jokes, preferences, simple planning.

- Escalate to CLOUD_LARGE_MODEL only when you see **clear signals** that a stronger model is needed, such as:
  - The user explicitly asks for a very detailed, exhaustive, or long answer.
  - The task requires deep, multi-step reasoning across many components (e.g. complex system design, long essays, multi-stage plans).
  - The user requests large code generation, complex refactoring, or analysis over a lot of text or code.
  - The request is very long and clearly not trivial to handle with a small model.

- When you are unsure or the request is borderline, prefer LOCAL_SMALL_MODEL.
  Your goal is to minimize CLOUD_LARGE_MODEL usage while still keeping answer quality good enough for the user.

The final_prompt you build should:
- Respect persona_description, tone_preferences, expertise_level, and response_style.
- Include clear instructions to the model about how to respond for this specific user.
- Include the user's request verbatim somewhere.

Respond ONLY as a minified JSON object with exactly these keys:
- route: "LOCAL_SMALL_MODEL" or "CLOUD_LARGE_MODEL"
- final_prompt: the full prompt string to send to that model

No explanations, no markdown, no extra keys.
""".strip()

# ----------------------------------------------------------------------

def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        # remove surrounding ``` and optional language tag
        text = text.strip("`").strip()
        text = text.replace("json", "").replace("JSON", "").strip()
    return text.strip()

# -----------------------------------------------------------------------

def _build_router_prompt(traits: Dict[str, Any], user_request: str) -> str:
    payload = {
        "traits": traits,
        "request": user_request,
    }
    payload_json = json.dumps(payload, ensure_ascii=False)
    return ROUTER_SYSTEM_PROMPT + "\n\nINPUT_JSON:\n" + payload_json

# --------------------------------------------------------------------------

def decide_route_and_build_prompt(traits: Dict[str, Any], user_request: str) -> Dict[str, str]:
    """
    Decide whether to use the local or cloud model and construct the final prompt.

    Returns:
        {
            "route": "LOCAL_SMALL_MODEL" or "CLOUD_LARGE_MODEL",
            "final_prompt": "..."
        }
    """
    # 1) Hard length rule: very long requests → cloud, no Gemma needed
    word_count = len(user_request.split())
    if word_count > WORD_LENGTH_THRESHOLD:
        # You can tune this template later
        final_prompt = (
            "You are a powerful large language model.\n\n"
            f"User persona: {traits.get('persona_description', '')}\n"
            f"Tone preferences: {traits.get('tone_preferences', '')}\n"
            f"Response style: {traits.get('response_style', '')}\n\n"
            "User request:\n"
            f"{user_request}"
        )
        return {
            "route": ROUTE_CLOUD,
            "final_prompt": final_prompt,
        }

    # 2) Use Gemma to decide + engineer prompt
    prompt = _build_router_prompt(traits, user_request)
    raw_output = call_gemma(prompt)
    raw_output = _strip_code_fences(raw_output)

    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        # Fallback: if Gemma messes up, default to local with a simple prompt
        final_prompt = (
            "You are an AI assistant.\n\n"
            f"User persona: {traits.get('persona_description', '')}\n"
            f"Tone preferences: {traits.get('tone_preferences', '')}\n"
            f"Response style: {traits.get('response_style', '')}\n\n"
            "User request:\n"
            f"{user_request}"
        )
        return {
            "route": ROUTE_LOCAL,
            "final_prompt": final_prompt,
        }

    route = data.get("route", ROUTE_LOCAL)
    final_prompt = data.get("final_prompt", "")

    # Small safety: normalize route
    if route not in {ROUTE_LOCAL, ROUTE_CLOUD}:
        route = ROUTE_LOCAL

    if not final_prompt:
        # Fallback if Gemma forgot to fill it
        final_prompt = (
            "You are an AI assistant.\n\n"
            f"User persona: {traits.get('persona_description', '')}\n"
            f"Tone preferences: {traits.get('tone_preferences', '')}\n"
            f"Response style: {traits.get('response_style', '')}\n\n"
            "User request:\n"
            f"{user_request}"
        )

    return {"route": route, "final_prompt": final_prompt}