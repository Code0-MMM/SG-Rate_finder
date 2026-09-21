import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from config import DB_PATH, MASTER_PATH, PUBLISHED_PATH
from search_engine import normalize


SCHEMA = """
CREATE TABLE IF NOT EXISTS general_rates(id INTEGER PRIMARY KEY, category TEXT NOT NULL, payment_method TEXT, rate REAL NOT NULL, effective_date TEXT NOT NULL, source_file TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS brands(id INTEGER PRIMARY KEY, brand_name TEXT NOT NULL, normalized_name TEXT NOT NULL, category TEXT, payment_method TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS brand_rates(id INTEGER PRIMARY KEY, brand_id INTEGER NOT NULL REFERENCES brands(id), rate REAL NOT NULL, effective_date TEXT NOT NULL, source_file TEXT);
CREATE TABLE IF NOT EXISTS app_meta(key TEXT PRIMARY KEY, value TEXT);
CREATE INDEX IF NOT EXISTS idx_brands_name ON brands(normalized_name);
"""


def connect(path=DB_PATH):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(SCHEMA)
    return db


def replace_data(parsed, filename, path=DB_PATH):
    # SQLite's REAL affinity accepts text; validate before touching active rows.
    for r in parsed.general_rates:
        if not isinstance(r['rate'], (int, float)):
            raise ValueError('Invalid general rate')
    for b in parsed.brands:
        for r in b['rates']:
            if not isinstance(r['rate'], (int, float)):
                raise ValueError('Invalid brand rate')
    db = connect(path)
    now = datetime.now().isoformat(timespec="seconds")
    try:
        with db:
            db.execute("DELETE FROM brand_rates")
            db.execute("DELETE FROM brands")
            db.execute("DELETE FROM general_rates")
            db.execute("DELETE FROM app_meta")
            db.executemany("INSERT INTO general_rates(category,payment_method,rate,effective_date,source_file,updated_at) VALUES (:category,:payment_method,:rate,:effective_date,:source_file,:updated_at)",
                           [dict(r, source_file=filename, updated_at=now) for r in parsed.general_rates])
            for b in parsed.brands:
                cur = db.execute("INSERT INTO brands(brand_name,normalized_name,category,payment_method,note) VALUES (?,?,?,?,?)",
                                 (b['brand_name'], normalize(b['brand_name']), b['category'], b['payment_method'], b['note']))
                db.executemany("INSERT INTO brand_rates(brand_id,rate,effective_date,source_file) VALUES (?,?,?,?)",
                               [(cur.lastrowid, r['rate'], r['effective_date'], filename) for r in b['rates']])
            db.executemany("INSERT INTO app_meta(key,value) VALUES (?,?)", [
                ('last_update', now[:10]), ('source_filename', filename),
                ('source_month', parsed.source_month), ('latest_effective_date', parsed.latest_effective_date)])
    finally:
        db.close()


def load_data(path=DB_PATH):
    if Path(path) == DB_PATH and not DB_PATH.exists() and PUBLISHED_PATH.exists():
        with open(PUBLISHED_PATH, encoding='utf-8') as f:
            published = json.load(f)
        return published['brands'], published['general_rates'], published['meta']
    db = connect(path)
    try:
        brands = [dict(x) for x in db.execute("SELECT * FROM brands")]
        rates = [dict(x) for x in db.execute("SELECT * FROM brand_rates")]
        general = [dict(x) for x in db.execute("SELECT * FROM general_rates")]
        meta = {x['key']: x['value'] for x in db.execute("SELECT * FROM app_meta")}
        by_id = {b['id']: b for b in brands}
        for b in brands:
            b['rates'] = []
        for r in rates:
            if r['brand_id'] in by_id:
                by_id[r['brand_id']]['rates'].append(r)
        return brands, general, meta
    finally:
        db.close()


def load_master(path=MASTER_PATH):
    if not Path(path).exists():
        return {}
    with open(path, encoding='utf-8-sig', newline='') as f:
        return {normalize(r['brand_name']): r['category'].strip() for r in csv.DictReader(f)
                if r.get('brand_name') and r.get('category')}
