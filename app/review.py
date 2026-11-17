"""只审阅已观察的详情入口，不把候选记录当作已完成的业务。"""

IMAGE_LABELS = {'loaded': '素材已加载', 'failed': '素材加载失败', 'cleared': '素材未提供',
                'pending': '懒加载未完成', 'placeholder': '封面占位图'}
LICENSE_LABELS = {'confirmed': '授权详情一致', 'withdrawn': '授权详情已撤回', 'external': '授权详情指向非授权站点',
                  'unavailable': '授权详情暂不可用', 'mismatch': '授权详情版本不一致'}
IMAGE_GAP_NOTE = '图像缺失仅记为素材缺口，不等于商品下架'

def review_entries(entries):
    material = []
    for entry in entries:
        detail = entry['detail_fact']
        material.append({'material_key': detail['business_key'], 'directory_media': entry['catalog_fact']['media_state'],
                         'source_image': None, 'license_state': 'unconfirmed'})
    return material

def review_observations(observations):
    """面向业务汇总采集记录：保留每次观察的来源与时刻，缺口连同原始页面出处一起列出。

    详情页可访问即说明商品页存在；图像缺失只记为素材缺口，不据此判定商品下架。
    """
    material = []
    for observation in observations:
        fact = observation['observation_fact']
        row = {'material_key': fact['material_key'], 'business_key': fact['business_key'],
               'observed_at': observation['observed_at'], 'source': observation['source'],
               'directory_media': observation['catalog_fact']['media_state'],
               'image_state': fact['image_state'], 'image_label': IMAGE_LABELS.get(fact['image_state'], fact['image_state']),
               'license_state': fact['license_state'], 'license_label': LICENSE_LABELS.get(fact['license_state'], fact['license_state']),
               'gaps': observation['gaps'], 'needs_follow_up': bool(observation['gaps']),
               'listing_state': 'page_reachable'}
        if fact['image_state'] != 'loaded':
            row['image_note'] = IMAGE_GAP_NOTE
        material.append(row)
    return material
