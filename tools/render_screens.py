"""Renders the rebuilt app screens in tools/screens/ to the images shown on the site.

The screens are rebuilt by hand from the real applications, with fictional data.
Requires: pip install playwright pillow, and a Chrome or Chromium install.
Usage: python3 tools/render_screens.py   (run from the repository root)
"""
import io
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "tools" / "screens"
OUT = ROOT / "assets" / "screens"

DESKTOP = {"width": 832, "height": 520}
PHONE = {"width": 390, "height": 844}

SCREENS = {
    "portaal-desktop": DESKTOP,
    "portaal-mobile": PHONE,
    "werkbonnen-desktop": DESKTOP,
    "werkbonnen-mobile": PHONE,
    "kasboek-desktop": DESKTOP,
}

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel="chrome", args=["--allow-file-access-from-files"])
    for name, viewport in SCREENS.items():
        page = browser.new_page(viewport=viewport, device_scale_factor=2)
        page.goto((SOURCE / f"{name}.html").as_uri())
        page.wait_for_function("document.fonts.status === 'loaded'")
        Image.open(io.BytesIO(page.screenshot())).save(OUT / f"{name}.webp", quality=88, method=6)
        page.close()
        print(f"{name}.webp")
    browser.close()
