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

    resp = client.post("/api/prompts/", json={"template_text": "Prompt v1"})
    assert resp.status_code == 201
    p1 = resp.json()

    resp2 = client.post("/api/prompts/", json={"template_text": "Prompt v2", "parent_version_id": p1["id"]})
    assert resp2.status_code == 201
    p2 = resp2.json()
    assert p2["version"] == p1["version"] + 1

    list_resp = client.get("/api/prompts/")
    assert list_resp.status_code == 200
    prompts = list_resp.json()
    assert len(prompts) == 2
