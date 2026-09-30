from app.db import connect

def list_boxes():
    c = connect()
    try:
        return [dict(r) for r in c.execute("SELECT * FROM boxes ORDER BY id").fetchall()]
    finally:
        c.close()

def get_box(bid):
    c = connect()
    try:
        r = c.execute("SELECT * FROM boxes WHERE id=?", (bid,)).fetchone()
        return dict(r) if r else None
    finally:
        c.close()

def update_box(bid, length, width, height):
    # 只改三边，绝不触碰 data_quality/note：脏盒不会因改成正数而被“洗白”。
    c = connect()
    try:
        cur = c.execute(
            "UPDATE boxes SET length=?, width=?, height=? WHERE id=?",
            (length, width, height, bid),
        )
        c.commit()
        return int(cur.rowcount)
    finally:
        c.close()
