import pytest
from app.services.model_adapter import StubModelAdapter


def test_stub_adapter_returns_yes_scores():
    adapter = StubModelAdapter()
    rubric = {
        "id": 1,
        "name": "Test Rubric",
        "criteria": [
            {"id": 1, "name": "Thesis"},
            {"id": 2, "name": "Grammar"},
        ],
    }
    result = adapter.evaluate("Paper content", rubric)
    assert "evaluations" in result
    assert len(result["evaluations"]) == 2
    assert all(entry["score"] == "yes" for entry in result["evaluations"])


def test_stub_adapter_handles_empty_criteria():
    adapter = StubModelAdapter()
    result = adapter.evaluate("Paper content", {"criteria": []})
    assert result["evaluations"] == []


def test_get_adapter_defaults_to_stub(monkeypatch):
    monkeypatch.delenv("OLLAMA_ENABLED", raising=False)
    from app.services.model_adapter import get_adapter
    adapter = get_adapter()
    assert isinstance(adapter, StubModelAdapter)


def test_get_adapter_ollama(monkeypatch):
    monkeypatch.setenv("OLLAMA_ENABLED", "true")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    from app.services.model_adapter import get_adapter, OllamaAdapter
    adapter = get_adapter()
    assert isinstance(adapter, OllamaAdapter)
