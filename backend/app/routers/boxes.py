from fastapi import APIRouter, HTTPException
from app.repositories import boxes as repo
from app.schemas.box import BoxUpdate
router = APIRouter()
@router.get("/boxes")
def list_boxes(): return {"items": repo.list_boxes()}
@router.get("/boxes/{bid}")
def get_box(bid: int):
    r = repo.get_box(bid)
    if not r: raise HTTPException(404)
    return r
@router.patch("/boxes/{bid}")
def patch_box(bid: int, body: BoxUpdate):
    if not repo.get_box(bid): raise HTTPException(404)
    repo.update_box(bid, body.length, body.width, body.height)
    return repo.get_box(bid)
