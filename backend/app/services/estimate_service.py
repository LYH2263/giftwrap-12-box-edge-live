from fastapi import HTTPException
from app.engines.wrap_math import paper_area, ribbon_estimate
from app.repositories import boxes, history, settings_repo

def run_estimate(box_id: int, overlap: float | None, wrap_style: str, save: bool, note: str):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")
    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()
    L, W, H = box["length"], box["width"], box["height"]
    try:
        calc = paper_area(L, W, H, ov)
        ribbon = ribbon_estimate(L, W, H, wrap_style)
    except ValueError as exc:
        # clean 盒若三边异常（如脏值穿透），返回 422 而不是 500。
        raise HTTPException(422, str(exc))
    # 新预览/落库都以 boxes 当前三边为准；落库时再把三边冻结进 run。
    payload = {**calc, "ribbon": ribbon, "box_id": box_id,
               "length": L, "width": W, "height": H}
    run_id = (
        history.insert_run(box_id, ov, payload, note, dims=(L, W, H), wrap_style=wrap_style)
        if save else None
    )
    return {"box": box, "run_id": run_id, **calc, "ribbon": ribbon}
