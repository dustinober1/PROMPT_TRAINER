"""
Sprint 4 end-to-end checks for evaluations + feedback.

Uses a temp SQLite database to keep tests isolated from local data.
"""

import os
import pytest
from fastapi.testclient import TestClient

# Point the app at a disposable SQLite database before imports create the engine
os.environ["DATABASE_URL"] = "sqlite:////tmp/prompt_trainer_test.db"

from app.main import app  # noqa: E402
from app.core.database import drop_all_tables, init_db  # noqa: E402


@pytest.fixture(autouse=True)
def reset_db():
    """Fresh database for each test to keep state isolated."""
    drop_all_tables()
    init_db()
    yield
    drop_all_tables()


def _create_rubric(client: TestClient):
    resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Essay Rubric",
            "description": "Baseline rubric",
            "scoring_type": "yes_no",
            "criteria": [
                {"name": "Thesis", "description": "Has thesis", "order": 0},
                {"name": "Grammar", "description": "Good grammar", "order": 1},
            ],
        },
    )
    assert resp.status_code == 201
    return resp.json()


def _create_paper(client: TestClient, rubric_id: int):
    resp = client.post(
        "/api/papers/",
        json={"title": "Integration Paper", "content": "Some content", "rubric_id": rubric_id},
    )
    assert resp.status_code == 201
    return resp.json()


def test_evaluation_feedback_roundtrip():
    """Create evaluation, add per-criterion feedback, and verify round-trip payload."""
    client = TestClient(app)
    rubric = _create_rubric(client)
    paper = _create_paper(client, rubric_id=rubric["id"])

    eval_resp = client.post(
        "/api/evaluations/",
        json={"paper_id": paper["id"], "rubric_id": rubric["id"]},
    )
    assert eval_resp.status_code == 201
    evaluation = eval_resp.json()

    assert evaluation["rubric_name"] == rubric["name"]
    assert len(evaluation["rubric_criteria"]) == len(rubric["criteria"])
    assert len(evaluation["model_response"]["evaluations"]) == len(rubric["criteria"])

    criterion_id = rubric["criteria"][0]["id"]
    fb_resp = client.post(
        f"/api/evaluations/{evaluation['id']}/feedback",
        json={
            "criterion_id": criterion_id,
            "model_score": "yes",
            "user_corrected_score": "no",
            "user_explanation": "Thesis missing",
        },
    )
    assert fb_resp.status_code == 201

    detail = client.get(f"/api/evaluations/{evaluation['id']}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["is_correct"] is False  # feedback sets incorrect by default
    assert any(fb["criterion_id"] == criterion_id for fb in body["feedback"])
    assert any(c["id"] == criterion_id for c in body["rubric_criteria"])

    mark_correct = client.patch(f"/api/evaluations/{evaluation['id']}/feedback?is_correct=true")
    assert mark_correct.status_code == 200
    patched = mark_correct.json()
    assert patched["is_correct"] is True
    assert len(patched["feedback"]) == 1


def test_overall_feedback_without_criterion():
    """Allow overall feedback (no criterion) while keeping evaluation links intact."""
    client = TestClient(app)
    rubric = _create_rubric(client)
    paper = _create_paper(client, rubric_id=rubric["id"])

    eval_resp = client.post(
        "/api/evaluations/",
        json={"paper_id": paper["id"], "rubric_id": rubric["id"]},
    )
    evaluation_id = eval_resp.json()["id"]

    fb_resp = client.post(
        f"/api/evaluations/{evaluation_id}/feedback",
        json={
            "model_score": "yes",
            "user_corrected_score": "no",
            "user_explanation": "Overall incorrect",
        },
    )
    assert fb_resp.status_code == 201
    fb_body = fb_resp.json()
    assert fb_body["criterion_id"] is None

    detail = client.get(f"/api/evaluations/{evaluation_id}")
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["is_correct"] is False
    assert len(detail_body["feedback"]) == 1
    assert detail_body["feedback"][0]["criterion_id"] is None


def test_prompt_default_creation_and_explicit_selection():
    """Ensure default prompt is auto-created and explicit prompt_id is honored."""
    client = TestClient(app)
    rubric = _create_rubric(client)
    paper = _create_paper(client, rubric_id=rubric["id"])

    # No prompt specified -> default prompt should be created and used
    default_eval = client.post(
        "/api/evaluations/",
        json={"paper_id": paper["id"], "rubric_id": rubric["id"]},
    )
    assert default_eval.status_code == 201
    default_eval_body = default_eval.json()
    default_prompt_id = default_eval_body["prompt_id"]

    prompts_after_default = client.get("/api/prompts/")
    assert prompts_after_default.status_code == 200
    prompts_list = prompts_after_default.json()
    assert any(p["id"] == default_prompt_id for p in prompts_list)

    # Create a custom prompt and ensure evaluation uses it when specified
    custom_prompt = client.post(
        "/api/prompts/",
        json={"template_text": "Custom prompt text with {{paper_content}} and {{rubric}}", "is_active": True},
    )
    assert custom_prompt.status_code == 201
    custom_prompt_id = custom_prompt.json()["id"]

    custom_eval = client.post(
        "/api/evaluations/",
        json={"paper_id": paper["id"], "rubric_id": rubric["id"], "prompt_id": custom_prompt_id},
    )
    assert custom_eval.status_code == 201
    assert custom_eval.json()["prompt_id"] == custom_prompt_id

    prompts_after_custom = client.get("/api/prompts/")
    assert prompts_after_custom.status_code == 200
    prompt_ids = [p["id"] for p in prompts_after_custom.json()]
    assert default_prompt_id in prompt_ids
    assert custom_prompt_id in prompt_ids
