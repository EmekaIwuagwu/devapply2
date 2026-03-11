import asyncio
import random
from playwright.async_api import Page


async def simulate_human_mouse_movement(page: Page, target_selector: str):
    """Simulate non-linear mouse movement to a target."""
    try:
        element = await page.wait_for_selector(target_selector)
        box = await element.bounding_box()
        if box:
            center_x = box["x"] + box["width"] / 2
            center_y = box["y"] + box["height"] / 2

            # Simulate jittery movement towards target
            await page.mouse.move(
                center_x + random.randint(-10, 10), center_y + random.randint(-10, 10)
            )
            await asyncio.sleep(random.uniform(0.1, 0.5))
            await page.mouse.click(center_x, center_y)
    except Exception as e:
        print(f"Mouse simulation error: {e}")


async def human_like_typing(page: Page, selector: str, text: str):
    """Type text with variable speed and occasional pauses."""
    await page.focus(selector)
    for char in text:
        await page.type(selector, char, delay=random.randint(50, 150))
        if random.random() < 0.1:  # 10% chance of a longer pause
            await asyncio.sleep(random.uniform(0.5, 1.5))
