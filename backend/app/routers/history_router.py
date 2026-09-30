from fastapi import APIRouter, HTTPException
from app.engines.wrap_math import paper_area, ribbon_estimate
from app.repositories import history as repo
router = APIRouter()
@router.get("/runs")
def runs(limit: int = 50): return {"items": repo.list_runs(limit)}
@router.get("/runs/{run_id}")
def get_run(run_id: int):
    r = repo.get_run(run_id)
    if not r: raise HTTPException(404)
    return r
@router.get("/runs/{run_id}/replay")
def replay_run(run_id: int):
    """用写入时快照三边按同一算法再干算，与归档结果互证；不碰主数据。"""
    r = repo.get_run(run_id)
    if not r: raise HTTPException(404)
    snap = r["result"]
    if not all(k in snap for k in ("length", "width", "height", "overlap", "ribbon")):
        raise HTTPException(422, "该 run 缺少写入时三边快照，无法复算")
    calc = paper_area(snap["length"], snap["width"], snap["height"], snap["overlap"])
    ribbon = ribbon_estimate(snap["length"], snap["width"], snap["height"], snap["ribbon"]["wrap_style"])
    stored = {
        "box_surface": snap["box_surface"],
        "paper_m2": snap["paper_m2"],
        "ribbon_m": snap["ribbon"]["ribbon_m"],
    }
    replay = {
        "box_surface": calc["box_surface"],
        "paper_m2": calc["paper_m2"],
        "ribbon_m": ribbon["ribbon_m"],
    }
    return {
        "run_id": run_id,
        "snapshot": {k: snap[k] for k in ("box_name", "length", "width", "height")},
        "stored": stored,
        "replay": replay,
        "matches": stored == replay,
    }
