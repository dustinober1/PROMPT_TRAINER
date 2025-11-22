"""
Model adapter interface and a stub provider for development.

MI-001: Model abstraction layer
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


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
