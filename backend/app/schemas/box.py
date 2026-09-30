import math
from pydantic import BaseModel

class BoxUpdate(BaseModel):
    length: float
    width: float
    height: float

def valid_dimensions(body: BoxUpdate) -> bool:
    return all(math.isfinite(v) and v > 0 for v in (body.length, body.width, body.height))
