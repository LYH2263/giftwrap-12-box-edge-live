import json
from datetime import datetime, timezone
from app.db import connect

_RUN_SELECT = (
    "SELECT r.*, b.name box_name FROM calc_runs r "
    "LEFT JOIN boxes b ON b.id=r.box_id"
)

def insert_run(box_id, overlap, result, note="", dims=None, wrap_style=None):
    # dims 为写入瞬间的 (length, width, height) 快照；老调用不传则为 NULL。
    length = width = height = None
    if dims:
        length, width, height = dims
    c = connect()
    try:
        cur = c.execute(
            """INSERT INTO calc_runs
               (box_id,overlap,length,width,height,wrap_style,result_json,note,created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (box_id, overlap, length, width, height, wrap_style,
             json.dumps(result, ensure_ascii=False), note,
             datetime.now(timezone.utc).isoformat()),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()

def _decorate(row):
    d = dict(row)
    d["result"] = json.loads(d.pop("result_json"))
    # 升级前的旧 run 没有三边快照列值：只显冻结面积，不提供干算。
    d["has_snapshot"] = all(d.get(k) is not None for k in ("length", "width", "height"))
    return d

def list_runs(limit=50):
    c = connect()
    try:
        rows = c.execute(
            f"{_RUN_SELECT} ORDER BY r.id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [_decorate(r) for r in rows]
    finally:
        c.close()

def get_run(run_id):
    c = connect()
    try:
        row = c.execute(
            f"{_RUN_SELECT} WHERE r.id=?",
            (run_id,),
        ).fetchone()
        return _decorate(row) if row else None
    finally:
        c.close()
