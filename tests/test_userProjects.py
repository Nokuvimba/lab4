# tests/test_user_project_put_patch_simple.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, get_db
from app.models import Base

# use an in-memory sqlite so every run is clean + fast
engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)

@pytest.fixture
def client():
    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

# tiny helpers
def make_user(client, **over):
    payload = {
        "name": "User",
        "email": "user@atu.ie",
        "age": 20,
        "student_id": "S1111111",
        **over,
    }
    r = client.post("/api/users", json=payload)
    assert r.status_code == 201, r.text
    return r.json()

def make_project(client, owner_id, **over):
    payload = {"name": "Proj", "description": "Desc", "owner_id": owner_id, **over}
    r = client.post("/api/projects", json=payload)
    assert r.status_code == 201, r.text
    return r.json()

# ---------- USERS ----------
def test_user_put_simple(client):
    u = make_user(client, name="Before", email="before@atu.ie", student_id="S2222222", age=19)
    uid = u["id"]

    body = {
        "name": "After PUT",
        "email": "after@atu.ie",
        "age": 42,
        "student_id": "S3333333",
    }
    r = client.put(f"/api/users/{uid}", json=body)
    assert r.status_code == 200
    out = r.json()
    assert out["id"] == uid
    assert out["name"] == "After PUT"
    assert out["email"] == "after@atu.ie"
    assert out["age"] == 42
    assert out["student_id"] == "S3333333"

def test_user_patch_simple(client):
    u = make_user(client, name="Patchy", email="patch@atu.ie", student_id="S4444444", age=27)
    uid = u["id"]

    body = {"email": "patch.updated@atu.ie", "age": 28}  # leave name + student_id alone
    r = client.patch(f"/api/users/{uid}", json=body)
    assert r.status_code == 200
    out = r.json()
    assert out["email"] == "patch.updated@atu.ie"
    assert out["age"] == 28
    assert out["name"] == "Patchy"
    assert out["student_id"] == "S4444444"

# ---------- PROJECTS ----------
def test_project_put_simple(client):
    owner1 = make_user(client, email="one@atu.ie", student_id="S5555555")["id"]
    p = make_project(client, owner_id=owner1, name="Old", description="Old Desc")
    pid = p["id"]

    owner2 = make_user(client, email="two@atu.ie", student_id="S6666666")["id"]
    body = {"name": "New", "description": "New Desc", "owner_id": owner2}
    r = client.put(f"/api/projects/{pid}", json=body)
    assert r.status_code == 200
    out = r.json()
    assert out["id"] == pid
    assert out["name"] == "New"
    assert out["description"] == "New Desc"
    assert out["owner_id"] == owner2  # moved project

def test_project_patch_simple(client):
    owner = make_user(client, email="owner@atu.ie", student_id="S7777777")["id"]
    p = make_project(client, owner_id=owner, name="Before", description="Keep")
    pid = p["id"]

    body = {"name": "After"}  # only touch the name
    r = client.patch(f"/api/projects/{pid}", json=body)
    assert r.status_code == 200
    out = r.json()
    assert out["name"] == "After"
    assert out["description"] == "Keep"
    assert out["owner_id"] == owner