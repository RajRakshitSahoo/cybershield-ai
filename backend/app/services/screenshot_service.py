"""
Website screenshot capture.

Uses the microlink.io public screenshot API (no API key required for light,
non-commercial use) to avoid bundling a headless-Chromium/Playwright install
in the base image. For self-hosted, key-free screenshots in production,
swap `_microlink_shot()` for a local Playwright call -- see the commented
alternative below.
"""
import requests

REQUEST_TIMEOUT = 10


def _microlink_shot(url: str, is_mobile: bool) -> str | None:
    try:
        params = {
            "url": url,
            "screenshot": "true",
            "meta": "false",
            "embed": "screenshot.url",
        }
        if is_mobile:
            params["viewport.width"] = "390"
            params["viewport.height"] = "844"
            params["viewport.isMobile"] = "true"
        else:
            params["viewport.width"] = "1440"
            params["viewport.height"] = "900"
        resp = requests.get("https://api.microlink.io", params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", {}).get("screenshot", {}).get("url")
    except Exception:
        pass
    return None

    # --- Local Playwright alternative (uncomment if Chromium is installed) ---
    # from playwright.sync_api import sync_playwright
    # with sync_playwright() as p:
    #     browser = p.chromium.launch()
    #     page = browser.new_page(viewport={"width": 390, "height": 844} if is_mobile
    #                              else {"width": 1440, "height": 900})
    #     page.goto(url, timeout=8000)
    #     path = f"/tmp/{hash(url)}_{is_mobile}.png"
    #     page.screenshot(path=path)
    #     browser.close()
    #     return path


def capture_screenshots(url: str) -> dict:
    return {
        "desktop": _microlink_shot(url, is_mobile=False),
        "mobile": _microlink_shot(url, is_mobile=True),
    }
