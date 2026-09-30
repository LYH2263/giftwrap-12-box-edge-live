import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    from app.main import app
    with TestClient(app) as c:
        yield c


def test_update_takes_effect_on_new_preview(client):
    # 盒1：书型盒 0.30×0.20×0.15
    r = client.put("/api/boxes/1", json={"length": 0.40, "width": 0.22, "height": 0.18})
    assert r.status_code == 200
    assert r.json()["length"] == 0.40

    est = client.get("/api/estimate", params={"box_id": 1}).json()
    base = 2 * (0.40 * 0.22 + 0.40 * 0.18 + 0.22 * 0.18)
    assert est["paper_m2"] == round(base * 1.15, 3)
    girth = 2 * (0.22 + 0.18)
    assert est["ribbon"]["ribbon_m"] == round(girth * 2 + 0.40 + 0.5, 2)


def test_nonpositive_update_rejected_and_original_kept(client):
    for bad in (0, -0.1):
        r = client.put("/api/boxes/1", json={"length": bad, "width": 0.20, "height": 0.15})
        assert r.status_code == 422
    cur = client.get("/api/boxes/1").json()
    assert (cur["length"], cur["width"], cur["height"]) == (0.30, 0.20, 0.15)


def test_run_keeps_snapshot_after_master_changes(client):
    saved = client.post("/api/estimate", json={"box_id": 1, "save": True}).json()
    old_area = saved["paper_m2"]
    old_ribbon = saved["ribbon"]["ribbon_m"]
    run_id = saved["run_id"]

    client.put("/api/boxes/1", json={"length": 0.50, "width": 0.30, "height": 0.20})

    # 新预览跟主数据
    new_est = client.get("/api/estimate", params={"box_id": 1}).json()
    assert new_est["paper_m2"] != old_area
    assert new_est["box"]["length"] == 0.50

    # 列表与详情仍携带写入时三边与面积
    listed = [r for r in client.get("/api/runs").json()["items"] if r["id"] == run_id][0]
    assert listed["result"]["length"] == 0.30
    assert listed["result"]["paper_m2"] == old_area

    detail = client.get(f"/api/runs/{run_id}").json()
    assert detail["result"]["length"] == 0.30
    assert detail["result"]["width"] == 0.20
    assert detail["result"]["height"] == 0.15
    assert detail["result"]["paper_m2"] == listed["result"]["paper_m2"]

    # 用写入时三边再干算，与回看互证
    replay = client.get(f"/api/runs/{run_id}/replay").json()
    assert replay["matches"] is True
    assert replay["stored"]["paper_m2"] == old_area
    assert replay["replay"]["paper_m2"] == old_area
    assert replay["stored"]["ribbon_m"] == old_ribbon


def test_dirty_box_excluded_from_estimate(client):
    dirty = [b for b in client.get("/api/boxes").json()["items"] if b["data_quality"] == "dirty"][0]
    assert client.get("/api/estimate", params={"box_id": dirty["id"]}).status_code == 422
    assert client.post("/api/estimate", json={"box_id": dirty["id"], "save": True}).status_code == 422
