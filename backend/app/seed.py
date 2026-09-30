from app.db import connect

# 历史 run 除 box_id 外，需冻结写入瞬间的输入：三边与丝带绕法（overlap 已有独立列）。
# 计算输出（paper_m2/ribbon_m/box_surface）仍只存在 result_json，避免双份真相。
RUN_SNAPSHOT_COLUMNS = {
    "length": "REAL",
    "width": "REAL",
    "height": "REAL",
    "wrap_style": "TEXT",
}

def _ensure_columns(c, table, wanted):
    have = {r["name"] for r in c.execute(f"PRAGMA table_info({table})")}
    for name, decl in wanted.items():
        if name not in have:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {name} {decl}")

def init_db():
    c = connect()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS boxes(id INTEGER PRIMARY KEY,name TEXT,length REAL,width REAL,height REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS papers(id INTEGER PRIMARY KEY,name TEXT,roll_width REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
    CREATE TABLE IF NOT EXISTS calc_runs(id INTEGER PRIMARY KEY AUTOINCREMENT,box_id INT,overlap REAL,length REAL,width REAL,height REAL,wrap_style TEXT,result_json TEXT,note TEXT,created_at TEXT);
    """)
    # 老库的 calc_runs 没有快照列，幂等补齐；旧行新列为 NULL。
    _ensure_columns(c, "calc_runs", RUN_SNAPSHOT_COLUMNS)
    if c.execute("SELECT COUNT(*) c FROM boxes").fetchone()["c"] == 0:
        c.executemany("INSERT INTO boxes(name,length,width,height,data_quality,note) VALUES (?,?,?,?,?,?)",[
            ("书型盒",0.30,0.20,0.15,"clean",""),
            ("方形礼盒",0.25,0.25,0.10,"clean",""),
            ("脏数据-负高",0.2,0.2,-0.1,"dirty","高度负"),
        ])
        c.executemany("INSERT INTO papers(name,roll_width,data_quality,note) VALUES (?,?,?,?)",[
            ("哑光纸1.0m",1.0,"clean",""),
            ("牛皮纸0.7m",0.7,"clean",""),
        ])
        c.execute("INSERT INTO settings(key,value) VALUES ('overlap','1.15')")
        c.commit()
    c.close()
