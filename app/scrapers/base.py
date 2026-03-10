import os
import re
from abc import ABC
from typing import Iterable
from urllib.parse import urljoin

from playwright.async_api import Locator, Page, async_playwright

from app.types import TicketListing


class BaseScraper(ABC):
    vendor_name = "base"
    max_cards = 250

    card_selectors: tuple[str, ...] = (
        "[data-testid*='listing']",
        "[class*='listing']",
        "[class*='Listing']",
        "article",
        "li",
    )

    title_selectors: tuple[str, ...] = (
        "h1",
        "[data-testid*='event-title']",
        "[class*='eventTitle']",
        "[class*='EventTitle']",
    )

    def headless(self) -> bool:
        return os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"

    def timeout_ms(self) -> int:
        return int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "45000"))

    async def scrape_event(
        self,
        event_url: str,
        event_id: str,
        event_name: str | None = None,
    ) -> list[TicketListing]:
        listings: list[TicketListing] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless())
            page = await browser.new_page()
            page.set_default_timeout(self.timeout_ms())

            await page.goto(event_url, wait_until="domcontentloaded", timeout=self.timeout_ms())
            await self.after_goto(page)

            resolved_event_name = event_name or await self.extract_event_name(page) or event_id
            cards = await self.find_cards(page)
            count = await cards.count()

            for index in range(min(count, self.max_cards)):
                card = cards.nth(index)
                text = await self.safe_inner_text(card)

                if not text:
                    continue

                price = self.extract_price(text)
                if price is None:
                    continue

                section = self.extract_section(text)
                row = self.extract_row(text)
                quantity = self.extract_quantity(text)
                section_group = self.infer_section_group(section)
                listing_url = await self.extract_listing_url(card, event_url)

                listings.append(
                    TicketListing(
                        vendor=self.vendor_name,
                        event_id=event_id,
                        event_name=resolved_event_name,
                        section=section or "",
                        section_group=section_group,
                        row=row or "",
                        quantity=quantity,
                        price=price,
                        currency="USD",
                        listing_url=listing_url,
                    )
                )

            await browser.close()

        return self.dedupe_and_sort(listings)

    async def after_goto(self, page: Page) -> None:
        await page.wait_for_timeout(2000)
        await self.dismiss_common_banners(page)

        for _ in range(3):
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(600)

    async def dismiss_common_banners(self, page: Page) -> None:
        dismiss_texts = [
            "Accept",
            "Accept All",
            "I Accept",
            "Got it",
            "Close",
        ]

        for text in dismiss_texts:
            try:
                button = page.get_by_role("button", name=re.compile(text, re.IGNORECASE))
                if await button.count() > 0:
                    await button.first.click(timeout=1000)
                    await page.wait_for_timeout(300)
            except Exception:
                pass

    async def extract_event_name(self, page: Page) -> str:
        for selector in self.title_selectors:
            try:
                locator = page.locator(selector)
                if await locator.count() > 0:
                    text = (await locator.first.inner_text()).strip()
                    if text:
                        return text
            except Exception:
                continue
        return ""

    async def find_cards(self, page: Page) -> Locator:
        best_selector = self.card_selectors[0]
        best_count = 0

        for selector in self.card_selectors:
            try:
                locator = page.locator(selector)
                count = await locator.count()
                if count > best_count:
                    best_selector = selector
                    best_count = count
            except Exception:
                continue

        return page.locator(best_selector)

    async def extract_listing_url(self, card: Locator, event_url: str) -> str:
        try:
            link = await card.locator("a").first.get_attribute("href")
            if link:
                return urljoin(event_url, link)
        except Exception:
            pass
        return event_url

    async def safe_inner_text(self, locator: Locator) -> str:
        try:
            return (await locator.inner_text()).strip()
        except Exception:
            return ""

    def extract_price(self, text: str) -> float | None:
        patterns = [
            r"\$([0-9,]+(?:\.[0-9]{2})?)",
            r"from\s+\$([0-9,]+(?:\.[0-9]{2})?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return float(match.group(1).replace(",", ""))

        return None

    def extract_row(self, text: str) -> str:
        patterns = [
            r"\bRow\s*[:#-]?\s*([A-Za-z0-9-]+)\b",
            r"\bR\s*[:#-]?\s*([A-Za-z0-9-]+)\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def extract_quantity(self, text: str) -> int:
        patterns = [
            r"\b([0-9]+)\s*tickets?\b",
            r"\bqty\s*[:#-]?\s*([0-9]+)\b",
            r"\bquantity\s*[:#-]?\s*([0-9]+)\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return int(match.group(1))

        return 1

    def extract_section(self, text: str) -> str:
        patterns = [
            r"\bSection\s*[:#-]?\s*([A-Za-z0-9 &.-]+?)(?:\s+Row|\s+\$|\s+[0-9]+\s+tickets?|$)",
            r"\bSec(?:tion)?\s*[:#-]?\s*([A-Za-z0-9 &.-]+?)(?:\s+Row|\s+\$|\s+[0-9]+\s+tickets?|$)",
            r"\b(Field\s+[A-Za-z0-9-]+)\b",
            r"\b(Dugout Club\s+[A-Za-z0-9-]+)\b",
            r"\b(Club\s+[A-Za-z0-9-]+)\b",
            r"\b(Lower Box\s+[A-Za-z0-9-]+)\b",
            r"\b(Main Level\s+[A-Za-z0-9-]+)\b",
            r"\b(Bleachers\s+[A-Za-z0-9-]+)\b",
            r"\b(Right Field Pavilion\s+[A-Za-z0-9-]+)\b",
            r"\b(Upper Reserve\s+[A-Za-z0-9-]+)\b",
            r"\b(Top Deck\s+[A-Za-z0-9-]+)\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def infer_section_group(self, section: str) -> str:
        section_lower = section.lower()

        if any(term in section_lower for term in ["field", "dugout"]):
            return "Field Level"
        if "club" in section_lower:
            return "Club Level"
        if any(term in section_lower for term in ["lower", "main level", "box"]):
            return "Lower Bowl"
        if any(term in section_lower for term in ["bleacher", "pavilion", "outfield"]):
            return "Outfield"
        if any(term in section_lower for term in ["upper", "top deck", "reserve", "deck"]):
            return "Upper Deck"

        return "General"

    def dedupe_and_sort(self, listings: Iterable[TicketListing]) -> list[TicketListing]:
        seen: set[tuple[str, str, str, str, float, int]] = set()
        output: list[TicketListing] = []

        for listing in listings:
            key = (
                listing.vendor,
                listing.event_id,
                listing.section,
                listing.row,
                listing.price,
                listing.quantity,
            )
            if key in seen:
                continue
            seen.add(key)
            output.append(listing)

        output.sort(key=lambda item: item.price)
        return output