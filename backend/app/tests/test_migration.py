import json
from fastapi.testclient import TestClient
from app.db import connect
from app import seed

NEW_COLUMNS = {"length", "width", "height", "wrap_style"}


def _build_legacy_db():
    # 模拟升级前的旧结构：calc_runs 只有 6 列、无快照，面积仅在 result_json。
    c = connect()
    c.executescript("""
    CREATE TABLE boxes(id INTEGER PRIMARY KEY,name TEXT,length REAL,width REAL,height REAL,data_quality TEXT,note TEXT);
    CREATE TABLE papers(id INTEGER PRIMARY KEY,name TEXT,roll_width REAL,data_quality TEXT,note TEXT);
    CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT);
    CREATE TABLE calc_runs(id INTEGER PRIMARY KEY AUTOINCREMENT,box_id INT,overlap REAL,result_json TEXT,note TEXT,created_at TEXT);
    """)
    c.execute("INSERT INTO boxes VALUES (1,'书型盒',0.3,0.2,0.15,'clean','')")
    legacy_result = {
        "box_surface": 0.27, "overlap": 1.15, "paper_m2": 0.31,
        "ribbon": {"wrap_style": "cross", "ribbon_m": 1.8}, "box_id": 1,
    }
    c.execute(
        "INSERT INTO calc_runs(box_id,overlap,result_json,note,created_at) VALUES (?,?,?,?,?)",
        (1, 1.15, json.dumps(legacy_result), "", "2026-01-01T00:00:00+00:00"),
    )
    c.commit()
    c.close()


def test_init_db_idempotent(db_path):
    seed.init_db()
    seed.init_db()
    c = connect()
    try:
        cols = {r["name"] for r in c.execute("PRAGMA table_info(calc_runs)")}
    finally:
        c.close()
    assert NEW_COLUMNS <= cols


def test_legacy_run_gets_nullable_columns_and_no_verify(db_path):
    _build_legacy_db()
    seed.init_db()  # 触发补列迁移
    seed.init_db()  # 再来一次，验证幂等

    c = connect()
    try:
        cols = {r["name"] for r in c.execute("PRAGMA table_info(calc_runs)")}
        assert NEW_COLUMNS <= cols
    finally:
        c.close()

    from app.repositories import history
    run = history.list_runs()[0]
    assert run["has_snapshot"] is False
    assert run["length"] is None and run["wrap_style"] is None
    # 旧档冻结面积仍可从 result_json 读出
    assert run["result"]["paper_m2"] == 0.31

    from app.main import app
    with TestClient(app) as client:
        assert client.get(f"/api/runs/{run['id']}").status_code == 200
        assert client.post(f"/api/runs/{run['id']}/verify", json={}).status_code == 409
