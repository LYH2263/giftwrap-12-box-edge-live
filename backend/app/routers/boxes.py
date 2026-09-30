from fastapi import APIRouter, HTTPException
from app.repositories import boxes as repo
from app.schemas.box import BoxUpdate, valid_dimensions
router = APIRouter()
@router.get("/boxes")
def list_boxes(): return {"items": repo.list_boxes()}
@router.get("/boxes/{bid}")
def get_box(bid: int):
    r = repo.get_box(bid)
    if not r: raise HTTPException(404)
    return r
@router.put("/boxes/{bid}")
def update_box(bid: int, body: BoxUpdate):
    if not valid_dimensions(body):
        raise HTTPException(422, "长宽高必须均为正数")
    if repo.update_dimensions(bid, body.length, body.width, body.height) == 0:
        raise HTTPException(404)
    return repo.get_box(bid)
