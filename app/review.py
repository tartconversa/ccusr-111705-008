"""只审阅已观察的详情入口，不把候选记录当作已完成的业务。"""

def review_entries(entries):
    material = []
    for entry in entries:
        detail = entry['detail_fact']
        material.append({'material_key': detail['business_key'], 'directory_media': entry['catalog_fact']['media_state'],
                         'source_image': None, 'license_state': 'unconfirmed'})
    return material
