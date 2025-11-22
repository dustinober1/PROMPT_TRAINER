"""
End-to-end API checks for Sprint 1 deliverables.

Uses a temp SQLite database (set via DATABASE_URL) to keep tests isolated
from the developer's local data.
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


def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/health")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "healthy"
    assert payload["database"] == "connected"


def test_paper_crud_flow():
    client = TestClient(app)

    # Create rubric to associate
    rubric_resp = client.post(
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
    rubric_id = rubric_resp.json()["id"]

    # Create
    create_resp = client.post(
        "/api/papers/",
        json={
            "title": "Test Paper",
            "content": "This is Sprint 1 paper content.",
            "rubric_id": rubric_id,
        },
    )
    assert create_resp.status_code == 201
    paper_id = create_resp.json()["id"]
    assert create_resp.json()["rubric_id"] == rubric_id

    # List shows one paper
    list_resp = client.get("/api/papers/")
    assert list_resp.status_code == 200
    papers = list_resp.json()
    assert len(papers) == 1
    assert papers[0]["rubric_id"] == rubric_id
    assert papers[0]["rubric_name"] == "Essay Rubric"

    # Update title
    update_resp = client.put(f"/api/papers/{paper_id}", json={"title": "Updated Title"})
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated Title"

    # Delete
    delete_resp = client.delete(f"/api/papers/{paper_id}")
    assert delete_resp.status_code == 204

    # Verify empty
    list_after = client.get("/api/papers/")
    assert list_after.status_code == 200
    assert list_after.json() == []


def test_paper_creation_rejects_missing_rubric():
    client = TestClient(app)
    resp = client.post(
        "/api/papers/",
        json={
            "title": "Paper with missing rubric",
            "content": "Content goes here",
            "rubric_id": 999,
        },
    )
    assert resp.status_code == 404
    assert "Rubric with id 999 not found" in resp.json()["detail"]


def test_rubric_crud_and_criterion_guards():
    client = TestClient(app)

    payload = {
        "name": "Essay Rubric",
        "description": "Baseline rubric",
        "scoring_type": "yes_no",
        "criteria": [
            {"name": "Thesis", "description": "Has thesis", "order": 0},
            {"name": "Grammar", "description": "Good grammar", "order": 1},
        ],
    }

    # Create rubric with criteria
    create_resp = client.post("/api/rubrics/", json=payload)
    assert create_resp.status_code == 201
    rubric = create_resp.json()
    rubric_id = rubric["id"]
    first_criterion_id = rubric["criteria"][0]["id"]

    # List shows one rubric
    list_resp = client.get("/api/rubrics/")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # Get returns full criteria
    get_resp = client.get(f"/api/rubrics/{rubric_id}")
    assert get_resp.status_code == 200
    assert len(get_resp.json()["criteria"]) == 2

    # Update rubric name
    update_resp = client.put(f"/api/rubrics/{rubric_id}", json={"name": "Updated Rubric"})
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated Rubric"

    # Update a criterion
    crit_update = client.put(
        f"/api/rubrics/{rubric_id}/criteria/{first_criterion_id}",
        json={"name": "Thesis Updated"},
    )
    assert crit_update.status_code == 200
    assert crit_update.json()["name"] == "Thesis Updated"

    # Delete one criterion (allowed while more than one exists)
    crit_delete = client.delete(f"/api/rubrics/{rubric_id}/criteria/{first_criterion_id}")
    assert crit_delete.status_code == 204

    # Attempt to delete last remaining criterion should fail
    remaining = client.get(f"/api/rubrics/{rubric_id}").json()["criteria"]
    last_criterion_id = remaining[0]["id"]
    last_delete = client.delete(
        f"/api/rubrics/{rubric_id}/criteria/{last_criterion_id}"
    )
    assert last_delete.status_code == 400

    # Delete rubric (cascade cleanup)
    rubric_delete = client.delete(f"/api/rubrics/{rubric_id}")
    assert rubric_delete.status_code == 204

    # Verify no rubrics remain
    final_list = client.get("/api/rubrics/")
    assert final_list.status_code == 200
    assert final_list.json() == []


def test_evaluation_creation_stub():
    client = TestClient(app)

    # Create rubric
    rubric_resp = client.post(
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
    rubric_id = rubric_resp.json()["id"]

    # Create paper
    paper_resp = client.post(
        "/api/papers/",
        json={
            "title": "Test Paper",
            "content": "This is content for evaluation.",
            "rubric_id": rubric_id,
        },
    )
    paper_id = paper_resp.json()["id"]

    # Create evaluation (stubbed)
    eval_resp = client.post(
        "/api/evaluations/",
        json={"paper_id": paper_id, "rubric_id": rubric_id},
    )
    assert eval_resp.status_code == 201
    payload = eval_resp.json()
    assert payload["paper_id"] == paper_id
    assert payload["rubric_id"] == rubric_id
    assert "prompt_id" in payload
    assert payload["model_response"] is not None

    # List evaluations
    list_resp = client.get("/api/evaluations/")
    assert list_resp.status_code == 200
    evaluations = list_resp.json()
    assert len(evaluations) == 1
    assert evaluations[0]["paper_id"] == paper_id
    assert isinstance(evaluations[0]["model_response"], dict)
    assert evaluations[0]["paper_title"] == "Test Paper"
    assert evaluations[0]["rubric_name"] == "Essay Rubric"

    # Prompt stats incremented
    prompt_list = client.get("/api/evaluations/").json()
    assert prompt_list[0]["prompt_id"] > 0


def test_evaluation_creation_validates_rubric_and_paper():
    client = TestClient(app)

    # Missing paper
    missing_paper = client.post(
        "/api/evaluations/",
        json={"paper_id": 999, "rubric_id": 1},
    )
    assert missing_paper.status_code == 404

    # Create a paper but no rubric
    paper_resp = client.post(
        "/api/papers/",
        json={"title": "No Rubric Paper", "content": "Test content for validation."},
    )
    paper_id = paper_resp.json()["id"]

    missing_rubric = client.post(
        "/api/evaluations/",
        json={"paper_id": paper_id, "rubric_id": 999},
    )
    assert missing_rubric.status_code == 404
