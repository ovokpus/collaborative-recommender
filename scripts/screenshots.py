"""Capture README screenshots from the running stack (docker compose up)."""
from playwright.sync_api import sync_playwright

OUT = "docs/screenshots"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1360, "height": 900})
    pg.goto("http://localhost:8080")
    pg.locator(".rec .dist").first.wait_for(timeout=30000)
    pg.wait_for_timeout(800)
    pg.screenshot(path=f"{OUT}/web-recommendations.png", full_page=True)
    pg.select_option("select", index=42)
    pg.locator("input[type=range]").fill("30")
    pg.wait_for_timeout(2500)
    pg.screenshot(path=f"{OUT}/web-other-user.png", full_page=True)
    pg.goto("http://localhost:8000/docs")
    pg.get_by_text("/recommendations/{user_name}").first.wait_for()
    pg.screenshot(path=f"{OUT}/api-docs.png", full_page=True)
    b.close()
