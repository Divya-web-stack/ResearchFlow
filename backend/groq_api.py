import json
import os
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

try:
    from groq import GroqClient
except ImportError:  # pragma: no cover
    GroqClient = None


class GroqAPI:
    def __init__(self, api_key: str | None = None, model: str = "groq-1") -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required for Groq API access")

        self.client = GroqClient(api_key=self.api_key) if GroqClient is not None else None

    def chat(self, prompt: str) -> str:
        if self.client is not None:
            response = self.client.responses.create(model=self.model, input=prompt)
            return self._extract_response_text(response)

        if requests is None:
            raise RuntimeError("The requests library is required when groq package is not installed")

        url = "https://api.groq.ai/v1/responses"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "input": prompt}
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return self._extract_response_text(data)

    def _extract_response_text(self, response: Any) -> str:
        if isinstance(response, dict):
            output = response.get("output")
            if isinstance(output, list) and output:
                content = output[0].get("content") if isinstance(output[0], dict) else None
                if isinstance(content, list) and content:
                    text = content[0].get("text") if isinstance(content[0], dict) else None
                    if isinstance(text, str):
                        return text
        elif hasattr(response, "output"):
            output = getattr(response, "output")
            if isinstance(output, list) and output:
                content = getattr(output[0], "content", None)
                if isinstance(content, list) and content:
                    text = getattr(content[0], "text", None)
                    if isinstance(text, str):
                        return text
        return json.dumps(response, default=str)
