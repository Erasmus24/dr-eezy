"""
Thin client for a locally-running Ollama server (https://ollama.com) — a free,
open-source tool for running open-weight LLMs (Llama 3.1, Phi-3, Mistral, etc.)
entirely on your own machine, with no API key and no data leaving your laptop.

Only `requests` is used (no extra SDK), talking to Ollama's REST API directly:
https://github.com/ollama/ollama/blob/main/docs/api.md
"""
import requests

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1:8b"


class OllamaUnavailableError(Exception):
    """Raised when the local Ollama server cannot be reached."""


class OllamaClient:
    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = OLLAMA_BASE_URL, timeout: int = 60):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def generate(self, prompt: str, system: str = "") -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
        }
        try:
            r = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
            r.raise_for_status()
        except requests.RequestException as e:
            raise OllamaUnavailableError(
                f"Could not reach Ollama at {self.base_url}. "
                f"Is it running? Try `ollama serve` and `ollama pull {self.model}`. ({e})"
            )
        return r.json().get("response", "").strip()
