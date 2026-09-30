from fastapi import HTTPException
from app.engines.wrap_math import paper_area, ribbon_estimate
from app.repositories import history

def _close(a, b, tol=1e-9):
    return a is not None and b is not None and abs(float(a) - float(b)) <= tol

def verify_run(run_id: int):
    # 干算（回看互证）：只允许读 run 自身的快照三边 + run 的 overlap/wrap_style，
    # 绝不通过 box_id 回查 boxes 当前尺寸，也不写入任何新 run。
    run = history.get_run(run_id)
    if run is None:
        raise HTTPException(404)
    if not run["has_snapshot"]:
        raise HTTPException(409, "旧档无三边快照")

    L, W, H = run["length"], run["width"], run["height"]
    ov = run["overlap"]
    style = (
        run.get("wrap_style")
        or (run["result"].get("ribbon") or {}).get("wrap_style")
        or "cross"
    )
    try:
        calc = paper_area(L, W, H, ov)
        ribbon = ribbon_estimate(L, W, H, style)
    except ValueError as exc:
        raise HTTPException(422, str(exc))

    stored = run["result"]
    stored_ribbon_m = (stored.get("ribbon") or {}).get("ribbon_m")
    matches = {
        "box_surface": _close(calc["box_surface"], stored.get("box_surface")),
        "paper_m2": _close(calc["paper_m2"], stored.get("paper_m2")),
        "ribbon_m": _close(ribbon["ribbon_m"], stored_ribbon_m),
    }
    return {
        "run_id": run_id,
        "dims": {"length": L, "width": W, "height": H},
        "overlap": ov,
        "wrap_style": style,
        "stored": {
            "box_surface": stored.get("box_surface"),
            "paper_m2": stored.get("paper_m2"),
            "ribbon_m": stored_ribbon_m,
        },
        "recomputed": {
            "box_surface": calc["box_surface"],
            "paper_m2": calc["paper_m2"],
            "ribbon_m": ribbon["ribbon_m"],
        },
        "matches": matches,
        "all_match": all(matches.values()),
    }
