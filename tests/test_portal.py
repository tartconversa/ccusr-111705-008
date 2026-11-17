import unittest
from playwright.sync_api import sync_playwright
from test_browser import BrowserBaselineTest
from app.site import DATA

class PortalInteractionTest(BrowserBaselineTest):
    def test_browser_business_interaction(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(self.origin + "detail?id=" + DATA["items"][0]["id"], wait_until="domcontentloaded")
                page.locator('#variant').select_option('蓝色款');page.locator('#gallery-next').click();page.locator('#gallery-state').get_by_text('蓝色款：规格素材').wait_for();page.locator('#revoke').click();self.assertIn('授权撤回',page.locator('#license').inner_text())
            finally:
                browser.close()
