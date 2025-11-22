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
    """
    Stub adapter that returns deterministic responses based on scoring type.

    Tech Tip: This adapter is useful for development and testing without
    needing a real model. It generates realistic-looking responses for each scoring type.
    """

    def evaluate(self, paper_content: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
        criteria = rubric.get("criteria", [])
        scoring_type = rubric.get("scoring_type", "yes_no")

        evaluations = []
        for c in criteria:
            # Generate appropriate score based on scoring type
            if scoring_type == "yes_no":
                score = "yes"
            elif scoring_type == "meets_not_meets":
                score = "meets"
            elif scoring_type == "numerical":
                # Return a score in the middle of the range
                min_score = c.get("min_score", 0)
                max_score = c.get("max_score", 10)
                score = (min_score + max_score) // 2
            else:
                score = "yes"  # fallback

            evaluations.append({
                "criterion_id": c.get("id"),
                "criterion_name": c.get("name"),
                "score": score,
                "reasoning": f"Stubbed evaluation for {scoring_type} scoring",
            })

        return {"evaluations": evaluations}


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
        """
        Build evaluation prompt with detailed criterion information.

        Tech Tip: The prompt includes scoring type instructions so the model
        knows what format to return (yes/no, meets/not-meets, or numerical).
        """
        scoring_type = rubric.get("scoring_type", "yes_no")
        criteria_details = []

        for c in rubric.get("criteria", []):
            criterion_text = f"- {c.get('name', 'Criterion')} (id {c.get('id')})"

            # Add description if available
            description = c.get("description")
            if description:
                criterion_text += f"\n  Description: {description}"

            # Add scoring instructions based on type
            if scoring_type == "yes_no":
                criterion_text += "\n  Scoring: Respond with 'yes' or 'no'"
            elif scoring_type == "meets_not_meets":
                criterion_text += "\n  Scoring: Respond with 'meets' or 'does_not_meet'"
            elif scoring_type == "numerical":
                min_score = c.get("min_score", 0)
                max_score = c.get("max_score", 10)
                criterion_text += f"\n  Scoring: Provide a numerical score from {min_score} to {max_score}"

            criteria_details.append(criterion_text)

        criteria_text = "\n\n".join(criteria_details)

        return (
            "You are an educational evaluator. Evaluate the paper against each criterion.\n"
            f"Rubric: {rubric.get('name', 'Unnamed')}\n"
            f"Scoring Type: {scoring_type}\n\n"
            "Criteria:\n"
            f"{criteria_text}\n\n"
            "Paper:\n"
            f"{paper_content}\n\n"
            "For each criterion, provide:\n"
            "1. Your score (following the scoring type specified)\n"
            "2. Brief reasoning for your decision\n\n"
            "Format your response clearly with criterion IDs."
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
