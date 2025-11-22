"""
Sprint 5 checks: accuracy metric endpoint and sanitization guards.
"""

import os
import pytest
from fastapi.testclient import TestClient

# isolate DB
os.environ["DATABASE_URL"] = "sqlite:////tmp/prompt_trainer_test.db"

from app.main import app  # noqa: E402
from app.core.database import drop_all_tables, init_db  # noqa: E402


@pytest.fixture(autouse=True)
def reset_db():
    drop_all_tables()
    init_db()
    yield
    drop_all_tables()


def _seed_rubric_and_paper(client: TestClient):
    rubric = client.post(
        "/api/rubrics/",
        json={
            "name": "Essay Rubric",
            "description": "Baseline rubric",
            "scoring_type": "yes_no",
            "criteria": [
                {"name": "Thesis", "description": "Has thesis", "order": 0},
            ],
        },
    ).json()
    paper = client.post(
        "/api/papers/",
        json={
            "title": "Essay One",
            "content": "This is an essay.",
            "rubric_id": rubric["id"],
        },
    ).json()
    return rubric, paper


def test_accuracy_endpoint_updates_after_feedback():
    client = TestClient(app)
    rubric, paper = _seed_rubric_and_paper(client)

    eval_resp = client.post("/api/evaluations/", json={"paper_id": paper["id"], "rubric_id": rubric["id"]})
    assert eval_resp.status_code == 201
    evaluation = eval_resp.json()

    # Initially no correctness, so accuracy is None
    metrics = client.get("/api/metrics/accuracy")
    assert metrics.status_code == 200
    body = metrics.json()
    assert body["total"] == 0
    assert body["pending"] == 1
    assert body["correct"] == 0
    assert body["accuracy_percent"] is None

    # Mark correct should update accuracy
    client.patch(f"/api/evaluations/{evaluation['id']}/feedback?is_correct=true")
    metrics_after = client.get("/api/metrics/accuracy").json()
    assert metrics_after["total"] == 1
    assert metrics_after["pending"] == 0
    assert metrics_after["correct"] == 1
    assert metrics_after["accuracy_percent"] == 100.0


def test_sanitization_blocks_script_injection():
    client = TestClient(app)

    bad_rubric = client.post(
        "/api/rubrics/",
        json={
            "name": "<script>alert(1)</script>",
            "description": "desc",
            "scoring_type": "yes_no",
            "criteria": [{"name": "Safe", "description": "desc", "order": 0}],
        },
    )
    assert bad_rubric.status_code == 422

    bad_paper = client.post(
        "/api/papers/",
        json={
            "title": "Bad",
            "content": "<script>alert('xss')</script> content with script",
            "rubric_id": None,
        },
    )
    assert bad_paper.status_code == 422

    bad_prompt = client.post(
        "/api/prompts/",
        json={
            "template_text": "<script>bad</script> {{paper_content}} {{rubric}}",
        },
    )
    assert bad_prompt.status_code == 422
