import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def fake_redis(monkeypatch):
    import fakeredis

    import app.memory.redis_store as rs

    r = fakeredis.FakeStrictRedis(decode_responses=True)
    monkeypatch.setattr(rs, "redis_client", r)
    return r


@pytest.fixture
def client(fake_redis):
    from app.main import app

    return TestClient(app)
