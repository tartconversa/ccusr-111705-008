import unittest
from playwright.sync_api import sync_playwright
from test_browser import BrowserBaselineTest
from app.site import DATA
from app.capture import read_detail_entry
from app.records import save_detail_entries, read_detail_entries
from app.review import review_entries
from tempfile import TemporaryDirectory
from pathlib import Path
import sqlite3

class PortalInteractionTest(BrowserBaselineTest):
    def test_variant_material_and_revocation_propagate(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(self.origin + 'detail?id=' + DATA['items'][0]['id'])
                page.locator('#variant').select_option('蓝色款')
                self.assertEqual(page.locator('#material-revision').get_attribute('data-variant'), '蓝色款')
                page.locator('#gallery-next').click()
                page.locator('#material-revision').get_by_text('素材版本 2').wait_for()
                image_url = page.locator('#material').get_attribute('src')
                license_url = page.locator('#license').get_attribute('href')
                self.assertIn('variant=%E8%93%9D%E8%89%B2%E6%AC%BE', image_url)
                self.assertIn('revision=2', license_url)
                self.assertNotEqual(page.locator('#material').evaluate('(image) => image.naturalWidth'), 1)
                page.locator('#revoke').click()
                self.assertIsNone(page.locator('#material').get_attribute('src'))
                self.assertIsNone(page.locator('#license').get_attribute('href'))
                self.assertIn('授权已撤回', page.locator('#license-revision').inner_text())
                self.assertIn('授权待复核', page.locator('#material-revision').inner_text())
            finally:
                browser.close()
    def test_selected_business_state_reaches_receipt(self):
        initial = read_detail_entry(self.origin, DATA['items'][0]['id'])
        changed = read_detail_entry(self.origin, DATA['items'][0]['id'], '蓝色款')
        self.assertNotEqual(initial['detail_fact']['business_key'], changed['detail_fact']['business_key'])
        with TemporaryDirectory() as directory:
            database = Path(directory) / 'selected.sqlite3'
            save_detail_entries(database, [initial, changed])
            with sqlite3.connect(database) as db:
                self.assertEqual(db.execute('SELECT count(DISTINCT business_key) FROM detail_entries').fetchone()[0], 2)
            review = review_entries(read_detail_entries(database))
            self.assertEqual(len(review), 2)
            self.assertIn('unconfirmed' if 'unconfirmed' in str(review) else 'not_observed', str(review))
    def test_distinct_source_state_transitions(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(self.origin + 'detail?id=' + DATA['items'][0]['id'], wait_until='domcontentloaded')
                page.locator('#variant').select_option('蓝色款')
                page.locator('#gallery-next').click()
                page.locator('#material-revision').get_by_text('本地素材版本 2').wait_for()
                page.locator('#revoke').click()
                self.assertIn('授权待复核', page.locator('#material-revision').inner_text())
            finally:
                browser.close()
    def test_entry_visit_is_append_only_and_linked(self):
        entry = read_detail_entry(self.origin, DATA['items'][0]['id'])
        self.assertEqual(entry['catalog_fact']['identity'], entry['id'])
        self.assertIn('detail', entry['source'])
        self.assertIn(DATA['items'][0]['id'], entry['detail_fact']['business_key'])
        with TemporaryDirectory() as directory:
            database = Path(directory) / 'visits.sqlite3'
            save_detail_entries(database, [entry, entry])
            with sqlite3.connect(database) as db:
                self.assertEqual(db.execute('SELECT count(*) FROM detail_entries').fetchone()[0], 2)
                self.assertEqual(db.execute('SELECT count(DISTINCT business_key) FROM detail_entries').fetchone()[0], 1)

    def test_browser_business_interaction(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(self.origin + "detail?id=" + DATA["items"][0]["id"], wait_until="domcontentloaded")
                page.locator('#variant').select_option('蓝色款');page.locator('#gallery-next').click();page.locator('#gallery-state').get_by_text('蓝色款：规格素材').wait_for();page.locator('#revoke').click();self.assertIn('授权撤回',page.locator('#license').inner_text())
            finally:
                browser.close()
