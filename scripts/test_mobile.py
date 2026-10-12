"""Browser smoke tests at mobile, tablet and desktop widths; run after starting a local server."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

PAGES = ["index.html", "projects.html", "cv.html", "research.html", "projects/photoacoustic.html", "projects/burgers-rom.html", "projects/lorenz96.html", "projects/mixing.html", "projects/cylinder-flow.html"]
WIDTHS = [375, 768, 1280]
BASE = "http://127.0.0.1:8765/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        problems = []
        for width in WIDTHS:
            page = await browser.new_page(viewport={"width": width, "height": 850})
            for route in PAGES:
                response = await page.goto(BASE + route)
                if not response or response.status != 200:
                    problems.append(f"{route}: HTTP failure")
                    continue
                metrics = await page.evaluate("""() => ({
                    viewport: document.documentElement.clientWidth,
                    content: document.documentElement.scrollWidth,
                    main: document.querySelectorAll('main').length,
                    h1: document.querySelectorAll('h1').length,
                    unnamedButtons: [...document.querySelectorAll('button')].filter(b => !b.textContent.trim() && !b.getAttribute('aria-label')).length
                })""")
                if metrics["content"] > metrics["viewport"] + 1:
                    problems.append(f"{route} at {width}px: horizontal overflow {metrics}")
                if metrics["main"] != 1 or metrics["h1"] != 1 or metrics["unnamedButtons"]:
                    problems.append(f"{route} at {width}px: semantic failure {metrics}")
                if width == 375 and route == "index.html":
                    button = page.locator(".nav-hamburger")
                    await button.click()
                    if await button.get_attribute("aria-expanded") != "true":
                        problems.append("Mobile menu failed to open")
                    await page.keyboard.press("Escape")
                    if await button.get_attribute("aria-expanded") != "false":
                        problems.append("Mobile menu failed to close with Escape")
            await page.close()
        await browser.close()
        if problems:
            raise SystemExit("\n".join(problems))
        print(f"PASS: {len(PAGES)} pages at {len(WIDTHS)} viewport widths; mobile navigation and semantic smoke checks.")

asyncio.run(main())
