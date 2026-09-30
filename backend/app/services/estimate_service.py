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
    try:
        calc = paper_area(box["length"], box["width"], box["height"], ov)
        ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
    except ValueError:
        raise HTTPException(422, "box dimensions must be positive")
    # 新预览跟主数据；落库时把当时三边一起写进快照，旧 run 不受日后改尺寸影响。
    payload = {
        "box_id": box_id,
        "box_name": box["name"],
        "length": box["length"],
        "width": box["width"],
        "height": box["height"],
        **calc,
        "ribbon": ribbon,
    }
    run_id = history.insert_run(box_id, ov, payload, note) if save else None
    return {"box": box, "run_id": run_id, **calc, "ribbon": ribbon}
