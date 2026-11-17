"""Candidate review of observed entry facts, never a completed transaction."""

def review_entries(entries):
    material = []
    for entry in entries:
        detail = entry['detail_fact']
        material.append({'material_key': detail['business_key'], 'directory_media': entry['catalog_fact']['media_state'],
                         'source_image': None, 'license_state': 'unconfirmed'})
    return material
