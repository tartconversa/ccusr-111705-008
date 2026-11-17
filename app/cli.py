"""公开目录与详情采集演示：目录之后追加规格、轮播素材与授权详情的可追溯记录。"""
import json
import sys
from .capture import read_catalog, observe_detail
from .records import save_observations
from .review import review_observations

ORIGIN = 'http://127.0.0.1:8765/'
STORAGE = 'var/observations.sqlite3'

def main():
    catalog = read_catalog(ORIGIN)
    print(json.dumps(catalog, ensure_ascii=False, indent=2))
    if len(sys.argv) > 1:
        targets = [(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)]
    else:
        targets = [(item['id'], None) for item in catalog]
    observations = [observe_detail(ORIGIN, item_id, selection) for item_id, selection in targets]
    saved = save_observations(STORAGE, observations)
    print(f'已追加 {saved} 条采集记录到 {STORAGE}')
    print(json.dumps(review_observations(observations), ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
