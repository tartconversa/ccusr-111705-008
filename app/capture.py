"""使用真实 Chromium 浏览公开目录；详情采集产生可追溯的规格、素材与授权记录。"""
from datetime import datetime, timezone
from urllib.parse import urlsplit, urljoin
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from .domain import interpret_card, interpret_entry, interpret_observation

LOCAL_HOSTS = ('127.0.0.1', 'localhost')

def _check_local(origin):
    parts = urlsplit(origin)
    if parts.hostname not in LOCAL_HOSTS or parts.scheme != 'http':
        raise ValueError('只允许本地演练来源')

def _open_detail(page, origin, item_id):
    page.goto(origin, wait_until='domcontentloaded')
    card = page.locator(f'.card[data-key="{item_id}"]')
    if card.count() != 1:
        raise ValueError('card identity is not unique')
    summary = card.locator('p').inner_text()
    card.locator('a').click()
    if page.locator('main').get_attribute('data-key') != item_id:
        raise ValueError('detail identity differs from catalog')
    return {'id': item_id, 'summary': summary}

def read_catalog(origin):
    _check_local(origin)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(origin, wait_until='domcontentloaded')
            if not page.locator('main').count():
                raise ValueError('来源目录未加载')
            items = page.locator('.card').evaluate_all('(nodes) => nodes.map(n => ({id:n.dataset.key,name:n.querySelector("h2").textContent,summary:n.querySelector("p").textContent,href:n.querySelector("a").getAttribute("href")}))')
            return [{'source':page.url, **item, 'catalog_fact':interpret_card(item)} for item in items]
        finally:
            browser.close()

def read_detail_entry(origin, item_id, selection=None):
    _check_local(origin)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            catalog = _open_detail(page, origin, item_id)
            if selection is not None:
                page.locator('#variant').select_option(selection)
            catalog_fact = interpret_card(catalog)
            entry_signal = {'variant': page.locator('#variant').input_value(), 'material_variant': page.locator('#material-revision').get_attribute('data-variant'), 'product': page.locator('main').get_attribute('data-key')}
            return {'id': item_id, 'source': page.url, 'catalog_fact': catalog_fact,
                    'opening_summary': page.locator('#summary').inner_text(),
                    'detail_fact': interpret_entry(catalog_fact, entry_signal)}
        finally:
            browser.close()

def observe_detail(origin, item_id, selection=None, timeout_ms=3000):
    """走卡片到详情，在一次页面会话内记录规格选择、图片轮播与授权详情。

    返回的采集记录带来源地址、规格、素材版本与采集时刻；轮播懒加载失败、
    授权撤回或授权链接指向非授权站点时记入 gaps，不跟随环回以外的跳转。
    """
    _check_local(origin)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            catalog = _open_detail(page, origin, item_id)
            catalog_fact = interpret_card(catalog)
            detail_url = page.url
            if selection is not None:
                page.locator('#variant').select_option(selection)
            spec = {'product': page.locator('main').get_attribute('data-key'),
                    'variant': page.locator('#variant').input_value(),
                    'material_variant': page.locator('#material-revision').get_attribute('data-variant'),
                    'revision': page.locator('#material-revision').get_attribute('data-revision')}
            entry_fact = interpret_entry(catalog_fact, spec)
            gaps = []
            material = _observe_carousel(page, detail_url, gaps, timeout_ms)
            license_info = _observe_license(page, detail_url, spec, gaps, timeout_ms)
            return {'id': item_id, 'source': detail_url,
                    'observed_at': datetime.now(timezone.utc).isoformat(),
                    'catalog_fact': catalog_fact, 'detail_fact': entry_fact,
                    'spec': spec, 'material': material, 'license': license_info, 'gaps': gaps,
                    'observation_fact': interpret_observation(catalog_fact, spec, material['state'], license_info['state'])}
        finally:
            browser.close()

def _observe_carousel(page, detail_url, gaps, timeout_ms):
    page.locator('#gallery-next').click()
    revision_text = page.locator('#material-revision')
    try:
        revision_text.get_by_text('素材版本').wait_for(timeout=timeout_ms)
    except PlaywrightTimeoutError:
        gaps.append({'kind': 'material_lazy_load_timeout', 'label': '轮播懒加载未完成', 'source': detail_url})
        return {'state': 'pending', 'image_url': None, 'revision_text': revision_text.inner_text()}
    try:
        page.wait_for_function("() => { const image = document.querySelector('#material'); return !image.getAttribute('src') || image.complete; }", timeout=timeout_ms)
    except PlaywrightTimeoutError:
        gaps.append({'kind': 'material_lazy_load_timeout', 'label': '轮播懒加载未完成', 'source': detail_url})
    src = page.locator('#material').get_attribute('src')
    text = revision_text.inner_text()
    if src is None:
        gaps.append({'kind': 'material_cleared', 'label': '素材未提供', 'source': detail_url})
        return {'state': 'cleared', 'image_url': None, 'revision_text': text}
    image_url = urljoin(detail_url, src)
    natural = page.locator('#material').evaluate('(image) => image.naturalWidth')
    if natural and natural > 1:
        return {'state': 'loaded', 'image_url': image_url, 'revision_text': text}
    if natural == 1:
        return {'state': 'placeholder', 'image_url': image_url, 'revision_text': text}
    gaps.append({'kind': 'material_load_failed', 'label': '轮播素材加载失败', 'source': detail_url, 'image_url': image_url})
    return {'state': 'failed', 'image_url': image_url, 'revision_text': text}

def _observe_license(page, detail_url, spec, gaps, timeout_ms):
    href = page.locator('#license').get_attribute('href')
    note = page.locator('#license-revision').inner_text()
    if href is None:
        gaps.append({'kind': 'license_withdrawn', 'label': '授权详情已撤回', 'source': detail_url, 'note': note})
        return {'state': 'withdrawn', 'href': None, 'note': note}
    license_url = urljoin(detail_url, href)
    parts = urlsplit(license_url)
    if parts.scheme != 'http' or parts.hostname not in LOCAL_HOSTS:
        gaps.append({'kind': 'license_external', 'label': '授权详情指向非授权站点', 'source': detail_url, 'href': license_url})
        return {'state': 'external', 'href': license_url, 'note': note}
    response = page.goto(license_url, wait_until='domcontentloaded', timeout=timeout_ms)
    status = response.status if response is not None else None
    if status != 200:
        gaps.append({'kind': 'license_unavailable', 'label': '授权详情暂不可用', 'source': detail_url, 'href': license_url, 'status': status})
        return {'state': 'unavailable', 'href': license_url, 'note': note, 'status': status}
    main = page.locator('main')
    page_spec = {'product': main.get_attribute('data-product'),
                 'variant': main.get_attribute('data-variant'),
                 'revision': main.get_attribute('data-revision')}
    if page_spec != {'product': spec['product'], 'variant': spec['variant'], 'revision': spec['revision']}:
        gaps.append({'kind': 'license_revision_mismatch', 'label': '授权详情与所选规格版本不一致', 'source': detail_url, 'href': license_url, 'page': page_spec})
        return {'state': 'mismatch', 'href': license_url, 'note': note, 'page': page_spec, 'text': main.inner_text()}
    return {'state': 'confirmed', 'href': license_url, 'note': note, 'page': page_spec, 'text': main.inner_text()}
