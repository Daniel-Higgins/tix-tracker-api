from typing import Literal
from pydantic import BaseModel


class Game(BaseModel):
    event_id: str
    league: str
    home_team: str
    away_team: str
    event_name: str
    event_date: str
    venue: str


class TicketListing(BaseModel):
    vendor: str
    event_id: str
    event_name: str
    section: str
    section_group: str
    row: str
    quantity: int
    price: float
    currency: str
    listing_url: str


class GamesResponse(BaseModel):
    league: str | None = None
    count: int
    games: list[Game]


class TicketsResponse(BaseModel):
    event_id: str
    event_name: str
    count: int
    listings: list[TicketListing]
    errors: list[str]


class VendorLowestPrice(BaseModel):
    vendor: str
    lowest_price: float
    listing_count: int


class SectionGroupSummary(BaseModel):
    section_group: str
    listing_count: int
    lowest_price: float | None = None


class EventSummaryResponse(BaseModel):
    event: Game
    total_listings: int
    lowest_price: float | None = None
    highest_price: float | None = None
    vendors: list[VendorLowestPrice]
    section_groups: list[SectionGroupSummary]


class ScrapeCompareRequest(BaseModel):
    event_id: str
    event_name: str | None = None
    vendor_urls: dict[str, str]


GameSort = Literal["date", "home_team", "away_team", "venue"]
TicketSort = Literal[
    "price_asc",
    "price_desc",
    "vendor",
    "section",
    "quantity_asc",
    "quantity_desc",
]