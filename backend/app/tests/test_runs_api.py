from app.engines.wrap_math import paper_area
from app.db import connect


def _save_run(client, box_id=1):
    r = client.post("/api/estimate", json={"box_id": box_id, "save": True})
    assert r.status_code == 200
    return r.json()["run_id"]


def test_saved_run_carries_snapshot(client):
    run_id = _save_run(client)
    detail = client.get(f"/api/runs/{run_id}").json()
    assert detail["has_snapshot"] is True
    assert (detail["length"], detail["width"], detail["height"]) == (0.30, 0.20, 0.15)
    assert detail["wrap_style"] == "cross"
    # result_json 内也双保险冻结了三边
    assert (detail["result"]["length"], detail["result"]["width"], detail["result"]["height"]) == (0.30, 0.20, 0.15)


def test_changing_box_does_not_overwrite_history(client):
    run_id = _save_run(client)
    old_paper = paper_area(0.30, 0.20, 0.15, 1.15)["paper_m2"]  # 0.31

    assert client.patch("/api/boxes/1", json={"length": 0.40, "width": 0.30, "height": 0.20}).status_code == 200

    listed = next(r for r in client.get("/api/runs").json()["items"] if r["id"] == run_id)
    detail = client.get(f"/api/runs/{run_id}").json()
    for r in (listed, detail):
        assert (r["length"], r["width"], r["height"]) == (0.30, 0.20, 0.15)
        assert r["result"]["paper_m2"] == old_paper
    assert listed["result"]["paper_m2"] == detail["result"]["paper_m2"]


def test_verify_uses_snapshot_and_matches(client):
    run_id = _save_run(client)
    client.patch("/api/boxes/1", json={"length": 0.40, "width": 0.30, "height": 0.20})

    v = client.post(f"/api/runs/{run_id}/verify", json={}).json()
    assert v["all_match"] is True
    assert all(v["matches"].values())
    # 干算用的是写入时旧三边，而非改后的主数据
    assert v["dims"] == {"length": 0.30, "width": 0.20, "height": 0.15}
    assert v["recomputed"]["paper_m2"] == 0.31

    new_preview = client.get("/api/estimate?box_id=1").json()["paper_m2"]
    assert new_preview != v["recomputed"]["paper_m2"]


def test_zero_width_clean_box_estimate_is_422(client):
    c = connect()
    try:
        c.execute("UPDATE boxes SET width=0 WHERE id=2")
        c.commit()
    finally:
        c.close()
    assert client.get("/api/estimate?box_id=2").status_code == 422


def test_run_404(client):
    assert client.get("/api/runs/9999").status_code == 404
    assert client.post("/api/runs/9999/verify", json={}).status_code == 404
