import math
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app import seed
from app.routers import api_router
app = FastAPI(title="Giftwrap", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def _json_safe(v):
    # NaN/Infinity 会让 JSONResponse 崩溃（把 422 变成 500），统一清洗为 None。
    if isinstance(v, float):
        return v if math.isfinite(v) else None
    if isinstance(v, dict):
        return {k: _json_safe(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_json_safe(x) for x in v]
    return v

@app.exception_handler(RequestValidationError)
def _on_validation_error(request: Request, exc: RequestValidationError):
    # 手造安全明细：默认处理器回显 input 时遇到 NaN/Infinity 会让 JSONResponse 崩溃
    # （把 422 变成 500），ctx 里还可能带不可序列化的异常对象。
    detail = []
    for err in exc.errors():
        detail.append({
            "type": err.get("type"),
            "loc": list(err.get("loc", [])),
            "msg": err.get("msg"),
            "input": _json_safe(err.get("input")),
        })
    return JSONResponse(status_code=422, content={"detail": detail})

@app.on_event("startup")
def _startup(): seed.init_db()
app.include_router(api_router)
@app.get("/api/health")
def health(): return {"ok": True, "project": "giftwrap"}
