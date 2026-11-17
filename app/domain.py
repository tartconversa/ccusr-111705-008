"""非遗联名商品页面的授权展示核验：目录卡片既有数据约定。"""
import re

def interpret_card(item):
    parts = item['summary'].split(' · ', 1)
    if len(parts) != 2:
        raise ValueError('卡片摘要格式无效')
    condition, observation = parts
    found = re.fullmatch(r"(?P<amount>已展示|待核对)", observation)
    if not found:
        raise ValueError('卡片状态未识别')
    amount = found.group('amount')
    return {'kind': 'collaboration', 'identity': item['id'], 'condition': condition, 'media_state': observation, 'state': int(amount) if amount.isdigit() else amount}

def interpret_entry(catalog_fact, signal):
    if signal['product'] != catalog_fact['identity'] or signal['material_variant'] != signal['variant']:
        raise ValueError('product material identity mismatch')
    return {'business_key': f"{signal['product']}:{signal['variant']}", 'variant': signal['variant'], 'material_variant': signal['material_variant']}

def interpret_observation(catalog_fact, spec, image_state, license_state):
    if spec['product'] != catalog_fact['identity']:
        raise ValueError('product material identity mismatch')
    return {'business_key': f"{spec['product']}:{spec['variant']}",
            'material_key': f"{spec['product']}:{spec['variant']}:r{spec['revision']}",
            'variant': spec['variant'], 'revision': spec['revision'],
            'image_state': image_state, 'license_state': license_state}
