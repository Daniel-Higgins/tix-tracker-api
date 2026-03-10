from playwright.async_api import Page

from app.scrapers.base import BaseScraper


class SeatGeekScraper(BaseScraper):
    vendor_name = "seatgeek"

    card_selectors = (
        "[data-testid*='listing']",
        "[data-testid*='offer']",
        "[class*='Listing']",
        "[class*='listing']",
        "article",
        "li",
    )

    title_selectors = (
        "h1",
        "[data-testid*='event-title']",
        "[class*='EventTitle']",
        "[class*='title']",
    )

    async def after_goto(self, page: Page) -> None:
        await super().after_goto(page)

        for selector in [
            "[data-testid*='listing']",
            "[class*='listing']",
            "[class*='offer']",
        ]:
            try:
                await page.locator(selector).first.wait_for(timeout=2000)
                break
            except Exception:
                continue