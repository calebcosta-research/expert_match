import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
from opensearchpy import OpenSearchException
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.app import main, models, database


@pytest.fixture()
def client(tmp_path):
    # setup in-memory database
    db_url = f"sqlite:///{tmp_path}/test.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)

    # patch session in app and database modules
    main.database.SessionLocal = TestingSessionLocal
    database.SessionLocal = TestingSessionLocal

    yield TestClient(main.app)


def create_sample_data(db):
    e1 = models.Expert(name="Alice", email="alice@example.com")
    e2 = models.Expert(name="Bob", email="bob@example.com")
    p = models.Project(organization_name="Org", description="project")
    db.add_all([e1, e2, p])
    db.commit()
    db.refresh(e1)
    db.refresh(e2)
    db.refresh(p)
    return e1, e2, p


def test_match_experts_success(client, monkeypatch):
    with database.SessionLocal() as db:
        e1, e2, p = create_sample_data(db)

    dummy = MagicMock()
    dummy.search.return_value = {
        "hits": {
            "hits": [
                {"_source": {"id": e2.id}},
                {"_source": {"id": e1.id}},
            ]
        }
    }
    monkeypatch.setattr(database, "get_opensearch_client", lambda: dummy)

    resp = client.get(f"/projects/{p.id}/matches")
    assert resp.status_code == 200
    data = resp.json()
    assert [ex["id"] for ex in data["experts"]] == [e2.id, e1.id]


def test_match_experts_os_unavailable(client, monkeypatch):
    with database.SessionLocal() as db:
        _, _, p = create_sample_data(db)

    dummy = MagicMock()
    dummy.search.side_effect = OpenSearchException("connection failed")
    monkeypatch.setattr(database, "get_opensearch_client", lambda: dummy)

    resp = client.get(f"/projects/{p.id}/matches")
    assert resp.status_code == 503
