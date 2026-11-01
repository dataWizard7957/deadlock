import requests

OLLAMA_URL = "http://localhost:11434"
SYSTEM_PROMPT = (
    "You are the Dungeon Master of a short coding RPG about AI engineering. "
    "Answer in two or three sentences. Talk about the exact task in the prompt. "
    "For a hint, name the idea and do not write the corrected code. "
    "For a success or a failure, react to the code the player actually submitted."
)


def _session():
    session = requests.Session()
    session.trust_env = False
    return session


def list_models():
    try:
        response = _session().get(f"{OLLAMA_URL}/api/tags", timeout=3)
        response.raise_for_status()
        names = []
        for model in response.json().get("models", []):
            name = model.get("name", "")
            if name and "embed" not in name:
                names.append(name)
        return names or ["gemma2:2b"]
    except requests.RequestException:
        return ["gemma2:2b"]


def preferred_model(names):
    for name in ("gemma2:2b", "gemma:2b", "qwen3.5:2b", "gemma3:4b"):
        if name in names:
            return names.index(name)
    return 0


def query_dungeon_master(prompt, model_name="gemma2:2b"):
    payload = {
        "model": model_name,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {"num_predict": 120, "temperature": 0.7},
    }
    try:
        response = _session().post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
    except requests.Timeout:
        return "Ollama is running, but this reply took too long. Try the hint again."
    except requests.RequestException:
        return "Ollama is not reachable at http://localhost:11434."

    if response.status_code != 200:
        detail = response.text.strip().replace("\n", " ")
        return f"Ollama refused the request ({response.status_code}): {detail[:180]}"

    data = response.json()
    text = (data.get("response") or data.get("thinking") or "").strip()
    if not text:
        return "Ollama answered, but the reply was empty."
    return text
