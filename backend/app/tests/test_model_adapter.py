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
