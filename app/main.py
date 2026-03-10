import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.sample_data import GAMES, TICKET_LISTINGS, VENDORS
from app.scrapers import SCRAPERS
from app.types import (
    EventSummaryResponse,
    Game,
    GamesResponse,
    GameSort,
    ScrapeCompareRequest,
    SectionGroupSummary,
    TicketListing,
    TicketsResponse,
    TicketSort,
    VendorLowestPrice,
)

app = FastAPI(
    title="Sports Ticket Data API",
    description="Backend-first API for normalized sports game and ticket listing data.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"


def parse_event_date(value: str) -> datetime:
    return datetime.fromisoformat(value)


def get_event_or_404(event_id: str) -> Game:
    event = next((game for game in GAMES if game.event_id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


def filter_games(
    league: str | None,
    team: str | None,
    venue: str | None,
    days: int | None,
    sort: GameSort,
    limit: int | None,
) -> list[Game]:
    results = list(GAMES)

    if league:
        league_lower = league.lower()
        results = [game for game in results if game.league.lower() == league_lower]

    if team:
        team_lower = team.lower()
        results = [
            game
            for game in results
            if team_lower in game.home_team.lower()
            or team_lower in game.away_team.lower()
            or team_lower in game.event_name.lower()
        ]

    if venue:
        venue_lower = venue.lower()
        results = [game for game in results if venue_lower in game.venue.lower()]

    if days is not None:
        now = datetime.now()
        results = [
            game
            for game in results
            if timedelta(0) <= (parse_event_date(game.event_date) - now) <= timedelta(days=days)
        ]

    if sort == "date":
        results.sort(key=lambda game: parse_event_date(game.event_date))
    elif sort == "home_team":
        results.sort(key=lambda game: game.home_team)
    elif sort == "away_team":
        results.sort(key=lambda game: game.away_team)
    elif sort == "venue":
        results.sort(key=lambda game: game.venue)

    if limit is not None:
        results = results[:limit]

    return results


def filter_tickets(
    event_id: str,
    vendor: str | None,
    section_group: str | None,
    section: str | None,
    min_quantity: int | None,
    min_price: float | None,
    max_price: float | None,
    sort: TicketSort,
) -> list[TicketListing]:
    results = [ticket for ticket in TICKET_LISTINGS if ticket.event_id == event_id]

    if vendor:
        vendor_lower = vendor.lower()
        results = [ticket for ticket in results if ticket.vendor.lower() == vendor_lower]

    if section_group:
        section_group_lower = section_group.lower()
        results = [
            ticket
            for ticket in results
            if ticket.section_group.lower() == section_group_lower
        ]

    if section:
        section_lower = section.lower()
        results = [
            ticket for ticket in results if section_lower in ticket.section.lower()
        ]

    if min_quantity is not None:
        results = [ticket for ticket in results if ticket.quantity >= min_quantity]

    if min_price is not None:
        results = [ticket for ticket in results if ticket.price >= min_price]

    if max_price is not None:
        results = [ticket for ticket in results if ticket.price <= max_price]

    if sort == "price_asc":
        results.sort(key=lambda ticket: ticket.price)
    elif sort == "price_desc":
        results.sort(key=lambda ticket: ticket.price, reverse=True)
    elif sort == "vendor":
        results.sort(key=lambda ticket: (ticket.vendor, ticket.price))
    elif sort == "section":
        results.sort(key=lambda ticket: (ticket.section_group, ticket.section, ticket.price))
    elif sort == "quantity_asc":
        results.sort(key=lambda ticket: (ticket.quantity, ticket.price))
    elif sort == "quantity_desc":
        results.sort(key=lambda ticket: (-ticket.quantity, ticket.price))

    return results


def build_event_summary(event: Game, listings: list[TicketListing]) -> EventSummaryResponse:
    vendor_prices: dict[str, list[float]] = defaultdict(list)
    vendor_counts: dict[str, int] = defaultdict(int)
    section_group_prices: dict[str, list[float]] = defaultdict(list)
    section_group_counts: dict[str, int] = defaultdict(int)

    for listing in listings:
        vendor_prices[listing.vendor].append(listing.price)
        vendor_counts[listing.vendor] += 1
        section_group_prices[listing.section_group].append(listing.price)
        section_group_counts[listing.section_group] += 1

    vendors = [
        VendorLowestPrice(
            vendor=vendor,
            lowest_price=min(prices),
            listing_count=vendor_counts[vendor],
        )
        for vendor, prices in vendor_prices.items()
    ]
    vendors.sort(key=lambda item: item.lowest_price)

    section_groups = [
        SectionGroupSummary(
            section_group=section_group,
            listing_count=section_group_counts[section_group],
            lowest_price=min(prices) if prices else None,
        )
        for section_group, prices in section_group_prices.items()
    ]
    section_groups.sort(key=lambda item: item.section_group)

    lowest_price = min((listing.price for listing in listings), default=None)
    highest_price = max((listing.price for listing in listings), default=None)

    return EventSummaryResponse(
        event=event,
        total_listings=len(listings),
        lowest_price=lowest_price,
        highest_price=highest_price,
        vendors=vendors,
        section_groups=section_groups,
    )


@app.get("/")
async def root():
    return {
        "name": "Sports Ticket Data API",
        "docs": "/docs",
        "viewer": "/viewer",
        "endpoints": [
            "/health",
            "/vendors",
            "/games",
            "/events/{event_id}",
            "/events/{event_id}/tickets",
            "/events/{event_id}/summary",
            "/scrape/compare",
        ],
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/viewer", response_class=FileResponse)
async def viewer():
    return FileResponse(STATIC_DIR / "viewer.html")


@app.get("/vendors")
async def get_vendors():
    return {"count": len(VENDORS), "vendors": VENDORS}


@app.get("/games", response_model=GamesResponse)
async def get_games(
    league: str | None = Query(None),
    team: str | None = Query(None),
    venue: str | None = Query(None),
    days: int | None = Query(None, ge=1, le=365),
    sort: GameSort = Query("date"),
    limit: int | None = Query(None, ge=1, le=100),
):
    games = filter_games(league, team, venue, days, sort, limit)
    return GamesResponse(league=league, count=len(games), games=games)


@app.get("/events/{event_id}", response_model=Game)
async def get_event(event_id: str):
    return get_event_or_404(event_id)


@app.get("/events/{event_id}/tickets", response_model=TicketsResponse)
async def get_event_tickets(
    event_id: str,
    vendor: str | None = Query(None),
    section_group: str | None = Query(None),
    section: str | None = Query(None),
    min_quantity: int | None = Query(None, ge=1, le=20),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    sort: TicketSort = Query("price_asc"),
):
    event = get_event_or_404(event_id)
    listings = filter_tickets(
        event_id=event_id,
        vendor=vendor,
        section_group=section_group,
        section=section,
        min_quantity=min_quantity,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
    )

    return TicketsResponse(
        event_id=event_id,
        event_name=event.event_name,
        count=len(listings),
        listings=listings,
        errors=[],
    )


@app.get("/events/{event_id}/summary", response_model=EventSummaryResponse)
async def get_event_summary(event_id: str):
    event = get_event_or_404(event_id)
    listings = filter_tickets(
        event_id=event_id,
        vendor=None,
        section_group=None,
        section=None,
        min_quantity=None,
        min_price=None,
        max_price=None,
        sort="price_asc",
    )
    return build_event_summary(event, listings)


@app.post("/scrape/compare", response_model=TicketsResponse)
async def scrape_compare(payload: ScrapeCompareRequest):
    if not payload.vendor_urls:
        raise HTTPException(status_code=400, detail="vendor_urls is required")

    tasks = []
    ordered_vendors: list[str] = []

    for vendor, event_url in payload.vendor_urls.items():
        normalized_vendor = vendor.lower().strip()
        scraper = SCRAPERS.get(normalized_vendor)

        if scraper is None:
            continue

        ordered_vendors.append(normalized_vendor)
        tasks.append(
            scraper.scrape_event(
                event_url=event_url,
                event_id=payload.event_id,
                event_name=payload.event_name,
            )
        )

    if not tasks:
        raise HTTPException(status_code=400, detail="No supported vendors were provided")

    results = await asyncio.gather(*tasks, return_exceptions=True)

    listings: list[TicketListing] = []
    errors: list[str] = []

    for vendor, result in zip(ordered_vendors, results):
        if isinstance(result, Exception):
            errors.append(f"{vendor}: {str(result)}")
        else:
            listings.extend(result)

    listings.sort(key=lambda item: item.price)

    resolved_event_name = payload.event_name or payload.event_id
    if listings:
        resolved_event_name = listings[0].event_name

    return TicketsResponse(
        event_id=payload.event_id,
        event_name=resolved_event_name,
        count=len(listings),
        listings=listings,
        errors=errors,
    )