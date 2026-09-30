import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    # connect() 在调用时读取 app.db 全局 DB_PATH，必须在建库/启动前打补丁。
    path = tmp_path / "app.db"
    import app.db as db
    import app.config as config
    monkeypatch.setattr(db, "DB_PATH", path)
    monkeypatch.setattr(config, "DB_PATH", path)
    return path


@pytest.fixture
def client(db_path):
    from app import seed
    seed.init_db()  # 全新库建表 + 种子
    from app.main import app
    with TestClient(app) as c:  # 启动事件再跑一次 init_db，兼验幂等
        yield c
