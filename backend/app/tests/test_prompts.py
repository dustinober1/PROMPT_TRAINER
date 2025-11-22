from fastapi.testclient import TestClient
from app.main import app
from app.core.database import drop_all_tables, init_db
import pytest


@pytest.fixture(autouse=True)
def reset_db():
    drop_all_tables()
    init_db()
    yield
    drop_all_tables()


def test_prompt_create_and_list():
    client = TestClient(app)

    base_template = "Evaluate: {{paper_content}} with rubric {{rubric}}"
    resp = client.post("/api/prompts/", json={"template_text": base_template})
    assert resp.status_code == 201
    p1 = resp.json()

    resp2 = client.post(
        "/api/prompts/",
        json={
            "template_text": base_template + " v2",
            "parent_version_id": p1["id"],
            "is_active": True,
        },
    )
    assert resp2.status_code == 201
    p2 = resp2.json()
    assert p2["version"] == p1["version"] + 1
    assert p2["is_active"] is True

    list_resp = client.get("/api/prompts/")
    assert list_resp.status_code == 200
    prompts = list_resp.json()
    assert len(prompts) == 2
    assert any(p["is_active"] for p in prompts)


def test_prompt_validation_and_activation():
    client = TestClient(app)
    base_template = "Evaluate: {{paper_content}} with rubric {{rubric}}"

    # Missing placeholders should fail
    bad = client.post("/api/prompts/", json={"template_text": "No placeholders"})
    assert bad.status_code == 422

    # Create inactive prompt
    p1 = client.post("/api/prompts/", json={"template_text": base_template, "is_active": False}).json()

    # Update template and activate
    update_resp = client.put(
        f"/api/prompts/{p1['id']}",
        json={"template_text": base_template + " updated", "is_active": True},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["is_active"] is True

    # Create another prompt and activate it, previous should deactivate
    p2 = client.post("/api/prompts/", json={"template_text": base_template + ' v2', "is_active": False}).json()
    activate_resp = client.post(f"/api/prompts/{p2['id']}/activate")
    assert activate_resp.status_code == 200
    list_resp = client.get("/api/prompts/")
    actives = [p for p in list_resp.json() if p["is_active"]]
    assert len(actives) == 1
    assert actives[0]["id"] == p2["id"]
