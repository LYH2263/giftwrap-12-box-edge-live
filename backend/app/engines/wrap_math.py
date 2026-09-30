import math

def _positive_dims(length, width, height):
    L, W, H = float(length), float(width), float(height)
    if not all(math.isfinite(v) for v in (L, W, H)) or min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")
    return L, W, H

def paper_area(length: float, width: float, height: float, overlap: float = 1.15) -> dict:
    L, W, H = _positive_dims(length, width, height)
    base = 2 * (L * W + L * H + W * H)
    need = base * float(overlap)
    return {"box_surface": round(base, 3), "overlap": float(overlap), "paper_m2": round(need, 3)}


def ribbon_estimate(length: float, width: float, height: float, wrap_style: str = "cross") -> dict:
    """Helper: approximate ribbon length in meters (not stored as primary metric)."""
    L, W, H = _positive_dims(length, width, height)
    girth = 2 * (W + H)
    if wrap_style == "band":
        meters = girth + 0.3
    else:
        meters = girth * 2 + L + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}
