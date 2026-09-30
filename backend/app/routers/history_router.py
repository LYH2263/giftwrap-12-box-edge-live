from fastapi import APIRouter, HTTPException
from app.repositories import history as repo
from app.services import run_service
router = APIRouter()
@router.get("/runs")
def runs(limit: int = 50): return {"items": repo.list_runs(limit)}
@router.get("/runs/{rid}")
def get_run(rid: int):
    r = repo.get_run(rid)
    if not r: raise HTTPException(404)
    return r
@router.post("/runs/{rid}/verify")
def verify_run(rid: int):
    return run_service.verify_run(rid)
