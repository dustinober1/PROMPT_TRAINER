"""
Tests for Sprint 6: Advanced Rubric Scoring Types

Tests three scoring types:
- yes_no: Simple binary scoring (existing)
- meets_not_meets: Standards-based grading (new)
- numerical: Point-based scoring with min/max ranges (new)
"""

import os
import pytest
from fastapi.testclient import TestClient

# Use test database
os.environ["DATABASE_URL"] = "sqlite:////tmp/prompt_trainer_test_sprint6.db"

from app.main import app  # noqa: E402
from app.core.database import drop_all_tables, init_db  # noqa: E402


@pytest.fixture(autouse=True)
def reset_db():
    """Fresh database for each test."""
    drop_all_tables()
    init_db()
    yield
    drop_all_tables()


def test_create_rubric_with_yes_no_scoring():
    """Test that yes/no scoring (existing functionality) still works"""
    client = TestClient(app)

    resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Yes/No Rubric",
            "description": "Simple binary scoring",
            "scoring_type": "yes_no",
            "criteria": [
                {"name": "Has thesis", "description": "Paper has clear thesis", "order": 0},
                {"name": "Good grammar", "description": "No major grammatical errors", "order": 1},
            ],
        },
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["scoring_type"] == "yes_no"
    assert len(data["criteria"]) == 2
    assert data["criteria"][0]["name"] == "Has thesis"
    assert data["criteria"][0]["description"] == "Paper has clear thesis"


def test_create_rubric_with_meets_not_meets_scoring():
    """Test creating rubric with meets/does-not-meet standards-based scoring"""
    client = TestClient(app)

    resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Standards Rubric",
            "description": "Meets Common Core standards",
            "scoring_type": "meets_not_meets",
            "criteria": [
                {
                    "name": "Writing Standard W.1",
                    "description": "Write arguments to support claims",
                    "order": 0
                },
                {
                    "name": "Language Standard L.2",
                    "description": "Demonstrate command of conventions",
                    "order": 1
                },
            ],
        },
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["scoring_type"] == "meets_not_meets"
    assert len(data["criteria"]) == 2


def test_create_rubric_with_numerical_scoring():
    """Test creating rubric with numerical scoring including min/max ranges"""
    client = TestClient(app)

    resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Points-Based Rubric",
            "description": "Numerical point scoring",
            "scoring_type": "numerical",
            "criteria": [
                {
                    "name": "Thesis clarity",
                    "description": "Quality of thesis statement",
                    "order": 0,
                    "min_score": 0,
                    "max_score": 5
                },
                {
                    "name": "Evidence quality",
                    "description": "Strength of supporting evidence",
                    "order": 1,
                    "min_score": 0,
                    "max_score": 10
                },
            ],
        },
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["scoring_type"] == "numerical"
    assert len(data["criteria"]) == 2

    # Verify min/max scores are stored
    assert data["criteria"][0]["min_score"] == 0
    assert data["criteria"][0]["max_score"] == 5
    assert data["criteria"][1]["min_score"] == 0
    assert data["criteria"][1]["max_score"] == 10


def test_numerical_rubric_requires_min_max_scores():
    """Test that numerical rubrics reject criteria without min/max scores"""
    client = TestClient(app)

    # Missing min_score
    resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Invalid Numerical Rubric",
            "scoring_type": "numerical",
            "criteria": [
                {
                    "name": "Criterion without min",
                    "order": 0,
                    "max_score": 10
                    # min_score missing
                },
            ],
        },
    )

    assert resp.status_code == 422  # Validation error
    error_detail = resp.json()["detail"]
    assert "min_score" in str(error_detail).lower()


def test_numerical_rubric_requires_min_less_than_max():
    """Test that min_score must be less than max_score"""
    client = TestClient(app)

    # min >= max (invalid)
    resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Invalid Range Rubric",
            "scoring_type": "numerical",
            "criteria": [
                {
                    "name": "Invalid range",
                    "order": 0,
                    "min_score": 10,
                    "max_score": 5  # max < min (invalid!)
                },
            ],
        },
    )

    assert resp.status_code == 422
    error_detail = str(resp.json()["detail"])
    assert "less than" in error_detail.lower()


def test_numerical_rubric_min_equals_max_rejected():
    """Test that min_score == max_score is rejected"""
    client = TestClient(app)

    resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Equal Min/Max Rubric",
            "scoring_type": "numerical",
            "criteria": [
                {
                    "name": "Equal range",
                    "order": 0,
                    "min_score": 5,
                    "max_score": 5  # Equal (invalid!)
                },
            ],
        },
    )

    assert resp.status_code == 422


def test_non_numerical_rubrics_ignore_min_max():
    """Test that yes_no and meets_not_meets rubrics don't require min/max"""
    client = TestClient(app)

    # yes_no without min/max should work
    resp1 = client.post(
        "/api/rubrics/",
        json={
            "name": "Yes/No Rubric",
            "scoring_type": "yes_no",
            "criteria": [{"name": "Criterion 1", "order": 0}],
        },
    )
    assert resp1.status_code == 201

    # meets_not_meets without min/max should work
    resp2 = client.post(
        "/api/rubrics/",
        json={
            "name": "Meets Rubric",
            "scoring_type": "meets_not_meets",
            "criteria": [{"name": "Criterion 1", "order": 0}],
        },
    )
    assert resp2.status_code == 201


def test_criterion_description_sanitization():
    """Test that criterion descriptions reject script tags"""
    client = TestClient(app)

    resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Test Rubric",
            "scoring_type": "yes_no",
            "criteria": [
                {
                    "name": "Malicious criterion",
                    "description": "<script>alert('xss')</script>",
                    "order": 0
                },
            ],
        },
    )

    assert resp.status_code == 422
    assert "script" in str(resp.json()["detail"]).lower()


def test_criterion_description_length_validation():
    """Test that descriptions respect max length (2000 chars)"""
    client = TestClient(app)

    # Create a description that's too long (2001 characters)
    long_description = "x" * 2001

    resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Test Rubric",
            "scoring_type": "yes_no",
            "criteria": [
                {
                    "name": "Long description criterion",
                    "description": long_description,
                    "order": 0
                },
            ],
        },
    )

    assert resp.status_code == 422


def test_evaluation_with_meets_not_meets_rubric():
    """Test end-to-end evaluation with meets/not-meets scoring"""
    client = TestClient(app)

    # Create meets/not-meets rubric
    rubric_resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Standards Rubric",
            "scoring_type": "meets_not_meets",
            "criteria": [
                {"name": "Writing Standard", "order": 0},
                {"name": "Language Standard", "order": 1},
            ],
        },
    )
    rubric_id = rubric_resp.json()["id"]

    # Create paper
    paper_resp = client.post(
        "/api/papers/",
        json={
            "title": "Test Essay",
            "content": "This is an essay that should be evaluated.",
            "rubric_id": rubric_id,
        },
    )
    paper_id = paper_resp.json()["id"]

    # Create evaluation
    eval_resp = client.post(
        "/api/evaluations/",
        json={"paper_id": paper_id, "rubric_id": rubric_id},
    )

    assert eval_resp.status_code == 201
    eval_data = eval_resp.json()

    # Verify stub adapter returned "meets" for meets_not_meets rubric
    assert "evaluations" in eval_data["model_response"]
    evals = eval_data["model_response"]["evaluations"]
    assert len(evals) == 2
    # StubModelAdapter should return "meets" for meets_not_meets type
    assert evals[0]["score"] == "meets"


def test_evaluation_with_numerical_rubric():
    """Test end-to-end evaluation with numerical scoring"""
    client = TestClient(app)

    # Create numerical rubric
    rubric_resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Points Rubric",
            "scoring_type": "numerical",
            "criteria": [
                {
                    "name": "Thesis",
                    "order": 0,
                    "min_score": 0,
                    "max_score": 10
                },
                {
                    "name": "Evidence",
                    "order": 1,
                    "min_score": 0,
                    "max_score": 20
                },
            ],
        },
    )
    rubric_id = rubric_resp.json()["id"]

    # Create paper
    paper_resp = client.post(
        "/api/papers/",
        json={
            "title": "Test Essay",
            "content": "This is an essay for numerical evaluation.",
            "rubric_id": rubric_id,
        },
    )
    paper_id = paper_resp.json()["id"]

    # Create evaluation
    eval_resp = client.post(
        "/api/evaluations/",
        json={"paper_id": paper_id, "rubric_id": rubric_id},
    )

    assert eval_resp.status_code == 201
    eval_data = eval_resp.json()

    # Verify stub adapter returned numerical scores
    evals = eval_data["model_response"]["evaluations"]
    assert len(evals) == 2
    # StubModelAdapter should return midpoint for numerical scores
    assert evals[0]["score"] == 5  # (0 + 10) // 2
    assert evals[1]["score"] == 10  # (0 + 20) // 2


def test_update_criterion_with_min_max_scores():
    """Test updating criterion to add/modify min/max scores"""
    client = TestClient(app)

    # Create numerical rubric
    rubric_resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Test Rubric",
            "scoring_type": "numerical",
            "criteria": [
                {
                    "name": "Original",
                    "order": 0,
                    "min_score": 0,
                    "max_score": 5
                },
            ],
        },
    )
    rubric_id = rubric_resp.json()["id"]
    criterion_id = rubric_resp.json()["criteria"][0]["id"]

    # Update the criterion's score range
    update_resp = client.put(
        f"/api/rubrics/{rubric_id}/criteria/{criterion_id}",
        json={
            "min_score": 0,
            "max_score": 10  # Changed from 5 to 10
        },
    )

    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["min_score"] == 0
    assert updated["max_score"] == 10


def test_various_numerical_ranges():
    """Test different common numerical ranges work correctly"""
    client = TestClient(app)

    # Test various ranges: 0-1, 0-5, 0-10, 0-100
    ranges = [
        (0, 1),    # Binary-like numerical
        (0, 5),    # 5-point scale
        (0, 10),   # 10-point scale
        (0, 100),  # Percentage-like
        (1, 10),   # Non-zero minimum
    ]

    for min_val, max_val in ranges:
        resp = client.post(
            "/api/rubrics/",
            json={
                "name": f"Rubric {min_val}-{max_val}",
                "scoring_type": "numerical",
                "criteria": [
                    {
                        "name": f"Criterion {min_val}-{max_val}",
                        "order": 0,
                        "min_score": min_val,
                        "max_score": max_val
                    },
                ],
            },
        )

        assert resp.status_code == 201, f"Failed for range {min_val}-{max_val}"
        data = resp.json()
        assert data["criteria"][0]["min_score"] == min_val
        assert data["criteria"][0]["max_score"] == max_val


def test_feedback_entry_with_explanation():
    """Test that feedback can include optional explanation (FC-006)"""
    client = TestClient(app)

    # Create rubric and paper
    rubric_resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Test Rubric",
            "scoring_type": "yes_no",
            "criteria": [{"name": "Thesis", "order": 0}],
        },
    )
    rubric_id = rubric_resp.json()["id"]

    paper_resp = client.post(
        "/api/papers/",
        json={
            "title": "Test Paper",
            "content": "Content here.",
            "rubric_id": rubric_id,
        },
    )
    paper_id = paper_resp.json()["id"]

    # Create evaluation
    eval_resp = client.post(
        "/api/evaluations/",
        json={"paper_id": paper_id, "rubric_id": rubric_id},
    )
    eval_id = eval_resp.json()["id"]
    criterion_id = eval_resp.json()["model_response"]["evaluations"][0]["criterion_id"]

    # Submit feedback WITH explanation
    feedback_resp = client.post(
        f"/api/evaluations/{eval_id}/feedback",
        json={
            "criterion_id": criterion_id,
            "model_score": "yes",  # The model's original score
            "user_corrected_score": "no",  # User's correction
            "user_explanation": "Model missed the key evidence in paragraph 3"
        },
    )

    assert feedback_resp.status_code == 201, f"Error: {feedback_resp.json()}"
    feedback_data = feedback_resp.json()
    assert feedback_data["user_explanation"] == "Model missed the key evidence in paragraph 3"


def test_feedback_entry_without_explanation():
    """Test that feedback works without explanation (optional field)"""
    client = TestClient(app)

    # Create rubric and paper
    rubric_resp = client.post(
        "/api/rubrics/",
        json={
            "name": "Test Rubric",
            "scoring_type": "yes_no",
            "criteria": [{"name": "Thesis", "order": 0}],
        },
    )
    rubric_id = rubric_resp.json()["id"]

    paper_resp = client.post(
        "/api/papers/",
        json={
            "title": "Test Paper",
            "content": "Content here.",
            "rubric_id": rubric_id,
        },
    )
    paper_id = paper_resp.json()["id"]

    # Create evaluation
    eval_resp = client.post(
        "/api/evaluations/",
        json={"paper_id": paper_id, "rubric_id": rubric_id},
    )
    eval_id = eval_resp.json()["id"]
    criterion_id = eval_resp.json()["model_response"]["evaluations"][0]["criterion_id"]

    # Submit feedback WITHOUT explanation
    feedback_resp = client.post(
        f"/api/evaluations/{eval_id}/feedback",
        json={
            "criterion_id": criterion_id,
            "model_score": "yes",  # The model's original score
            "user_corrected_score": "no"  # User's correction
            # No user_explanation field - it's optional
        },
    )

    assert feedback_resp.status_code == 201, f"Error: {feedback_resp.json()}"
    feedback_data = feedback_resp.json()
    # Explanation should be None/null
    assert feedback_data.get("user_explanation") is None or feedback_data["user_explanation"] == ""
