import asyncio
from playwright.async_api import async_playwright, Page, Browser
from app.config import settings
from app.automation.human_simulation import (
    simulate_human_mouse_movement,
    human_like_typing,
)


class BrowserManager:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Browser = None
        self.playwright = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=settings.BROWSER_LAUNCH_ARGS.split(","),
        )
        return self.browser

    async def get_page(self) -> Page:
        context = await self.browser.new_context(
            viewport={
                "width": settings.BROWSER_VIEWPORT_WIDTH,
                "height": settings.BROWSER_VIEWPORT_HEIGHT,
            },
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        )
        # In the future, apply stealth here
        page = await context.new_page()
        return page

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


async def scrape_page(url: str):
    manager = BrowserManager()
    await manager.start()
    page = await manager.get_page()
    await page.goto(url)
    content = await page.content()
    await manager.stop()
    return content
