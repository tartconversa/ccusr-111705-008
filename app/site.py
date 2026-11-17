"""本地演练门户：只对环回地址提供公开目录和详情，不调用外部系统。"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from html import escape
from .portal_behaviour import detail_fragment, source_extension, material_variants, license_variants

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'fixtures' / 'portal.json').read_text(encoding='utf-8'))

def render_index():
    cards = ''.join(f'<article class="card" data-key="{escape(item["id"])}"><h2>{escape(item["name"])}</h2><p>{escape(item["summary"])}</p><a href="/detail?id={escape(item["id"])}">查看详情</a></article>' for item in DATA['items'])
    return f'<!doctype html><html lang="zh"><meta charset="utf-8"><title>{escape(DATA["title"])}</title><h1>{escape(DATA["title"])}</h1><nav><a href="/">目录</a></nav><main>{cards}</main></html>'

def render_detail(item):
    options = ''.join(f'<option value="{escape(str(choice))}">{escape(str(choice))}</option>' for choice in item['choices'])
    fragment = detail_fragment(item) + source_extension(item)
    return f"""<!doctype html><html lang="zh"><meta charset="utf-8"><title>{escape(item['name'])}</title><a href="/">返回目录</a><main data-key="{escape(item['id'])}"><h1>{escape(item['name'])}</h1><p id="summary">{escape(item['summary'])}</p><label>{escape(DATA['dimensions'][0])}<select id="choice">{options}</select></label><button id="details" type="button">{escape(DATA['dimensions'][1])}</button><section id="panel" aria-live="polite"></section><button id="preview" type="button">{escape(DATA['dimensions'][2])}</button><section id="result" aria-live="polite"></section>{fragment}</main><script>
const choice=document.getElementById('choice'); const panel=document.getElementById('panel'); const result=document.getElementById('result');
choice.addEventListener('change',()=>{{panel.textContent='';result.textContent='';}});
document.getElementById('details').addEventListener('click',()=>{{panel.textContent='读取中';setTimeout(()=>{{panel.textContent=choice.value+'：'+{json.dumps(item['detail'], ensure_ascii=False)};}},45);}});
document.getElementById('preview').addEventListener('click',()=>{{result.textContent='核对中';setTimeout(()=>{{result.textContent=choice.value+'：'+{json.dumps(item['preview'], ensure_ascii=False)};}},45);}});
</script></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path == '/':
            body, code = render_index(), 200
        elif parsed.path == '/detail':
            key = parse_qs(parsed.query).get('id', [''])[0]
            item = next((row for row in DATA['items'] if row['id'] == key), None)
            body, code = (render_detail(item), 200) if item else ('未找到', 404)
        elif parsed.path == '/material':
            query = parse_qs(parsed.query)
            product = query.get('product', [''])[0]
            variant = query.get('variant', [''])[0]
            revision = query.get('revision', [''])[0]
            item = next((row for row in DATA['items'] if row['id'] == product), None)
            if item and variant in material_variants(item) and revision.isdigit():
                color = '#ad4043' if variant == '红色款' else '#365c99'
                body, code = f'<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96"><rect width="96" height="96" fill="{color}"/><circle cx="48" cy="48" r="24" fill="#f4dda3"/></svg>', 200
            else:
                body, code = '未找到', 404
        elif parsed.path == '/license':
            query = parse_qs(parsed.query)
            product = query.get('product', [''])[0]
            variant = query.get('variant', [''])[0]
            revision = query.get('revision', [''])[0]
            item = next((row for row in DATA['items'] if row['id'] == product), None)
            if item and variant in license_variants(item) and revision.isdigit():
                body, code = f'<main data-product="{escape(product)}" data-variant="{escape(variant)}" data-revision="{escape(revision)}">本地演练授权说明</main>', 200
            else:
                body, code = '未找到', 404
        else:
            body, code = '未找到', 404
        encoded = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'image/svg+xml' if parsed.path == '/material' and code == 200 else 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
    def log_message(self, *args):
        pass

def start_server():
    return ThreadingHTTPServer(('127.0.0.1', 0), Handler)

if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 8765), Handler)
    print('本地演练门户已启动：http://127.0.0.1:8765', flush=True)
    server.serve_forever()
