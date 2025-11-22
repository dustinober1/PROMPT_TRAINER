"""
Model adapter interface and a stub provider for development.

MI-001: Model abstraction layer
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import os
import httpx


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

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
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


def get_adapter() -> ModelAdapter:
    """Select adapter based on env OLLAMA_ENABLED=true/false."""
    use_ollama = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"
    if use_ollama:
        return OllamaAdapter()
    return StubModelAdapter()
