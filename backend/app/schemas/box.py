from pydantic import BaseModel, Field

class BoxUpdate(BaseModel):
    # 三边必填且必须为正数；0/负数/缺失/非有限值（NaN/Inf）由 Pydantic 统一判 422。
    length: float = Field(gt=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)
