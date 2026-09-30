import json
import pytest
from app.engines.wrap_math import paper_area


def test_patch_takes_effect_and_estimate_follows(client):
    r = client.patch("/api/boxes/1", json={"length": 0.40, "width": 0.30, "height": 0.20})
    assert r.status_code == 200
    body = r.json()
    assert (body["length"], body["width"], body["height"]) == (0.40, 0.30, 0.20)

    got = client.get("/api/boxes/1").json()
    assert (got["length"], got["width"], got["height"]) == (0.40, 0.30, 0.20)

    est = client.get("/api/estimate?box_id=1").json()
    expect = paper_area(0.40, 0.30, 0.20, 1.15)
    assert est["paper_m2"] == expect["paper_m2"]
    assert est["box"]["length"] == 0.40


@pytest.mark.parametrize("payload", [
    {"length": 0, "width": 0.2, "height": 0.15},
    {"length": 0.3, "width": -0.2, "height": 0.15},
    {"width": 0.2, "height": 0.15},                # 缺字段
    {"length": None, "width": 0.2, "height": 0.15},
])
def test_invalid_patch_rejected_and_keeps_old_dims(client, payload):
    before = client.get("/api/boxes/1").json()
    r = client.patch("/api/boxes/1", json=payload)
    assert r.status_code == 422
    after = client.get("/api/boxes/1").json()
    assert (after["length"], after["width"], after["height"]) == (
        before["length"], before["width"], before["height"]
    )


def test_nan_patch_rejected(client):
    body = json.dumps({"length": float("nan"), "width": 0.2, "height": 0.15})
    r = client.patch("/api/boxes/1", content=body, headers={"Content-Type": "application/json"})
    assert r.status_code == 422
    assert client.get("/api/boxes/1").json()["length"] == 0.30


def test_patch_missing_box_404(client):
    assert client.patch("/api/boxes/999", json={"length": 1, "width": 1, "height": 1}).status_code == 404


def test_dirty_box_stays_dirty_and_blocked_after_valid_patch(client):
    # 脏盒（种子 id=3）算纸被后端拦截
    assert client.get("/api/estimate?box_id=3").status_code == 422

    r = client.patch("/api/boxes/3", json={"length": 0.2, "width": 0.2, "height": 0.15})
    assert r.status_code == 200
    # 保存合法尺寸不洗白 data_quality：仍为 dirty，仍不可入算纸
    assert r.json()["data_quality"] == "dirty"
    assert client.get("/api/boxes/3").json()["data_quality"] == "dirty"
    assert client.get("/api/estimate?box_id=3").status_code == 422
