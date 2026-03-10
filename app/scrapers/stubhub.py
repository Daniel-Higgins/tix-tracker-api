from playwright.async_api import Page

from app.scrapers.base import BaseScraper


class StubHubScraper(BaseScraper):
    vendor_name = "stubhub"

    card_selectors = (
        "[data-testid*='listing']",
        "[data-testid*='inventory']",
        "[class*='Listing']",
        "[class*='listing']",
        "article",
    )

    title_selectors = (
        "h1",
        "[data-testid*='event-title']",
        "[class*='EventTitle']",
        "[class*='eventTitle']",
    )

    async def after_goto(self, page: Page) -> None:
        await super().after_goto(page)

        for selector in [
            "[data-testid*='listings']",
            "[class*='ListingGrid']",
            "[class*='listingGrid']",
        ]:
            try:
                await page.locator(selector).first.wait_for(timeout=2000)
                break
            except Exception:
                continue