import json
import sqlite3
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from test_browser import BrowserBaselineTest
from app.capture import observe_detail
from app.records import save_observations, read_observations
from app.review import review_observations

class ObservationTest(BrowserBaselineTest):
    def test_observation_links_spec_carousel_and_license_with_provenance(self):
        observation = observe_detail(self.origin, 'ip-01')
        self.assertEqual(observation['spec'], {'product': 'ip-01', 'variant': '红色款', 'material_variant': '红色款', 'revision': '1'})
        self.assertEqual(observation['material']['state'], 'loaded')
        self.assertIn('revision=1', observation['material']['image_url'])
        self.assertEqual(observation['license']['state'], 'confirmed')
        self.assertEqual(observation['license']['page'], {'product': 'ip-01', 'variant': '红色款', 'revision': '1'})
        self.assertEqual(observation['gaps'], [])
        self.assertIn('detail?id=ip-01', observation['source'])
        self.assertTrue(observation['observed_at'])
        self.assertEqual(observation['observation_fact']['material_key'], 'ip-01:红色款:r1')

    def test_variants_and_revisions_stay_separate_rows(self):
        red = observe_detail(self.origin, 'ip-01')
        blue = observe_detail(self.origin, 'ip-01', '蓝色款')
        self.assertEqual(blue['spec']['revision'], '2')
        self.assertNotEqual(red['observation_fact']['material_key'], blue['observation_fact']['material_key'])
        with TemporaryDirectory() as directory:
            database = Path(directory) / 'observations.sqlite3'
            self.assertEqual(save_observations(database, [red, blue, blue]), 3)
            rows = read_observations(database)
            self.assertEqual(len(rows), 3)
            self.assertEqual(len({row['observation_fact']['material_key'] for row in rows}), 2)
            with sqlite3.connect(database) as db:
                self.assertEqual(db.execute('SELECT count(*) FROM observations').fetchone()[0], 3)
            review = review_observations(rows)
            self.assertEqual(len(review), 3)
            for row in review:
                self.assertEqual(row['listing_state'], 'page_reachable')
                self.assertEqual(row['directory_media'], '已展示')

    def test_unpublished_variant_material_gap_is_not_delisting(self):
        observation = observe_detail(self.origin, 'ip-03', '典藏款')
        self.assertEqual(observation['material']['state'], 'failed')
        self.assertIn('revision=2', observation['material']['image_url'])
        kinds = {gap['kind'] for gap in observation['gaps']}
        self.assertIn('material_load_failed', kinds)
        self.assertIn('license_unavailable', kinds)
        for gap in observation['gaps']:
            self.assertIn('detail?id=ip-03', gap['source'])
        (row,) = review_observations([observation])
        self.assertTrue(row['needs_follow_up'])
        self.assertEqual(row['listing_state'], 'page_reachable')
        self.assertNotIn('delisted', json.dumps(row))
        self.assertIn('不等于商品下架', row['image_note'])

    def test_withdrawn_license_is_gap_with_source(self):
        observation = observe_detail(self.origin, 'ip-05')
        self.assertEqual(observation['license']['state'], 'withdrawn')
        (gap,) = [gap for gap in observation['gaps'] if gap['kind'] == 'license_withdrawn']
        self.assertIn('detail?id=ip-05', gap['source'])
        (row,) = review_observations([observation])
        self.assertEqual(row['license_state'], 'withdrawn')
        self.assertTrue(row['needs_follow_up'])

    def test_external_license_link_is_recorded_not_followed(self):
        observation = observe_detail(self.origin, 'ip-04')
        self.assertEqual(observation['license']['state'], 'external')
        self.assertNotIn('page', observation['license'])
        (gap,) = [gap for gap in observation['gaps'] if gap['kind'] == 'license_external']
        self.assertIn('example.invalid', gap['href'])
        self.assertIn('detail?id=ip-04', gap['source'])

    def test_observe_rejects_non_local_origin(self):
        with self.assertRaises(ValueError):
            observe_detail('https://example.com/', 'ip-01')

if __name__ == '__main__': unittest.main()
