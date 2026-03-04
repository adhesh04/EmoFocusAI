import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

SYSTEM_PROMPT = """
You are an AI that analyzes reflective journal entries.
Return ONLY a valid JSON object with the following fields:
- emotion (string)
- stress_score (float between 0 and 1)
- cognitive_state (string)
- summary (1 sentence)

Do not include explanations or extra text.
"""

def analyze_journal(text: str) -> dict:
    prompt = f"""
{SYSTEM_PROMPT}

Journal Entry:
{text}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code != 200:
        raise RuntimeError("Ollama LLM call failed")

    result = response.json()["response"]

    # Defensive JSON parsing
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {
            "emotion": "unknown",
            "stress_score": 0.0,
            "cognitive_state": "undetermined",
            "summary": "Unable to parse journal analysis."
        }
