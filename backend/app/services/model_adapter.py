"""
Model adapter interface and a stub provider for development.

MI-001: Model abstraction layer
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import httpx
from app.core.config import get_settings


class ModelAdapter(ABC):
    """Abstract base for model providers."""

    @abstractmethod
    def evaluate(self, paper_content: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
        """Return a structured evaluation response."""
        raise NotImplementedError


class StubModelAdapter(ModelAdapter):
    """Stub adapter that returns a deterministic response."""

    def evaluate(self, paper_content: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
        criteria = rubric.get("criteria", [])
        return {
            "evaluations": [
                {
                    "criterion_id": c.get("id"),
                    "criterion_name": c.get("name"),
                    "score": "yes",
                    "reasoning": "Stubbed evaluation",
                }
                for c in criteria
            ]
        }


class OllamaAdapter(ModelAdapter):
    """
    Minimal Ollama adapter using the /api/generate endpoint.
    Expects OLLAMA_MODEL env var (default: 'llama3.1:8b').
    """

    def __init__(self, base_url: str, model: str, timeout: int = 30):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    def evaluate(self, paper_content: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self._build_prompt(paper_content, rubric)
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                )
                resp.raise_for_status()
                data = resp.json()
                text = data.get("response", "")
                return {"raw": text}
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

    def _build_prompt(self, paper_content: str, rubric: Dict[str, Any]) -> str:
        criteria_lines = "\n".join(
            f"- {c.get('name', 'Criterion')} (id {c.get('id')})" for c in rubric.get("criteria", [])
        )
        return (
            "You are an evaluator. Given the rubric criteria, provide a judgment.\n"
            f"Rubric: {rubric.get('name', 'Unnamed')}\n"
            f"Criteria:\n{criteria_lines}\n\n"
            "Paper:\n"
            f"{paper_content}\n\n"
            "Return a concise evaluation."
        )


def get_adapter(provider: Optional[str] = None) -> ModelAdapter:
    """
    Select adapter based on provider or settings (MODEL_PROVIDER / OLLAMA_ENABLED).
    Priority: explicit provider arg > MODEL_PROVIDER env > OLLAMA_ENABLED flag > stub.
    """
    settings = get_settings()
    chosen = provider or settings.model_provider
    use_ollama = chosen == "ollama" or settings.ollama_enabled
    if use_ollama:
        return OllamaAdapter(base_url=settings.ollama_base_url, model=settings.ollama_model)
    return StubModelAdapter()
