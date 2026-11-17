"""公开目录收据，不把目录缺失解释为详情不存在。"""
import json
import sqlite3
from pathlib import Path

def save_catalog(path, items):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS catalog (id TEXT PRIMARY KEY, source TEXT NOT NULL, payload TEXT NOT NULL)')
        for item in items:
            db.execute('INSERT OR REPLACE INTO catalog VALUES (?, ?, ?)', (item['id'], item['source'], json.dumps(item, ensure_ascii=False)))
    return len(items)

def save_detail_entries(path, entries):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS detail_entries (visit_id INTEGER PRIMARY KEY, item_id TEXT NOT NULL, business_key TEXT NOT NULL, source TEXT NOT NULL, payload TEXT NOT NULL)')
        for entry in entries:
            if entry['catalog_fact']['identity'] != entry['id']:
                raise ValueError('catalog and detail identity mismatch')
            db.execute('INSERT INTO detail_entries (item_id, business_key, source, payload) VALUES (?, ?, ?, ?)',
                       (entry['id'], entry['detail_fact']['business_key'], entry['source'], json.dumps(entry, ensure_ascii=False)))
    return len(entries)

def read_detail_entries(path):
    with sqlite3.connect(path) as db:
        rows = db.execute('SELECT payload FROM detail_entries ORDER BY visit_id').fetchall()
    return [json.loads(row[0]) for row in rows]

def save_observations(path, observations):
    """追加式保存详情采集记录；不同规格或不同素材版本各自成行，互不覆盖。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS observations (obs_id INTEGER PRIMARY KEY, item_id TEXT NOT NULL, business_key TEXT NOT NULL, material_key TEXT NOT NULL, observed_at TEXT NOT NULL, source TEXT NOT NULL, payload TEXT NOT NULL)')
        for observation in observations:
            if observation['catalog_fact']['identity'] != observation['id'] or observation['spec']['product'] != observation['id']:
                raise ValueError('catalog and detail identity mismatch')
            fact = observation['observation_fact']
            db.execute('INSERT INTO observations (item_id, business_key, material_key, observed_at, source, payload) VALUES (?, ?, ?, ?, ?, ?)',
                       (observation['id'], fact['business_key'], fact['material_key'], observation['observed_at'], observation['source'], json.dumps(observation, ensure_ascii=False)))
    return len(observations)

def read_observations(path):
    with sqlite3.connect(path) as db:
        rows = db.execute('SELECT payload FROM observations ORDER BY obs_id').fetchall()
    return [json.loads(row[0]) for row in rows]
