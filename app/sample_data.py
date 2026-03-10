from app.types import Game, TicketListing

_RAW_GAMES = [
    {
        "event_id": "mlb-yankees-redsox-2026-03-12",
        "league": "mlb",
        "home_team": "New York Yankees",
        "away_team": "Boston Red Sox",
        "event_name": "Boston Red Sox at New York Yankees",
        "event_date": "2026-03-12T19:05:00",
        "venue": "Yankee Stadium",
        "price_boost": 24,
    },
    {
        "event_id": "mlb-dodgers-giants-2026-03-14",
        "league": "mlb",
        "home_team": "Los Angeles Dodgers",
        "away_team": "San Francisco Giants",
        "event_name": "San Francisco Giants at Los Angeles Dodgers",
        "event_date": "2026-03-14T19:10:00",
        "venue": "Dodger Stadium",
        "price_boost": 21,
    },
    {
        "event_id": "mlb-cubs-cardinals-2026-03-15",
        "league": "mlb",
        "home_team": "Chicago Cubs",
        "away_team": "St. Louis Cardinals",
        "event_name": "St. Louis Cardinals at Chicago Cubs",
        "event_date": "2026-03-15T14:20:00",
        "venue": "Wrigley Field",
        "price_boost": 18,
    },
    {
        "event_id": "mlb-braves-phillies-2026-03-16",
        "league": "mlb",
        "home_team": "Atlanta Braves",
        "away_team": "Philadelphia Phillies",
        "event_name": "Philadelphia Phillies at Atlanta Braves",
        "event_date": "2026-03-16T19:20:00",
        "venue": "Truist Park",
        "price_boost": 17,
    },
    {
        "event_id": "mlb-mets-padres-2026-03-17",
        "league": "mlb",
        "home_team": "New York Mets",
        "away_team": "San Diego Padres",
        "event_name": "San Diego Padres at New York Mets",
        "event_date": "2026-03-17T19:10:00",
        "venue": "Citi Field",
        "price_boost": 15,
    },
    {
        "event_id": "mlb-astros-rangers-2026-03-18",
        "league": "mlb",
        "home_team": "Houston Astros",
        "away_team": "Texas Rangers",
        "event_name": "Texas Rangers at Houston Astros",
        "event_date": "2026-03-18T20:10:00",
        "venue": "Minute Maid Park",
        "price_boost": 16,
    },
    {
        "event_id": "mlb-mariners-angels-2026-03-19",
        "league": "mlb",
        "home_team": "Seattle Mariners",
        "away_team": "Los Angeles Angels",
        "event_name": "Los Angeles Angels at Seattle Mariners",
        "event_date": "2026-03-19T18:40:00",
        "venue": "T-Mobile Park",
        "price_boost": 12,
    },
    {
        "event_id": "mlb-bluejays-orioles-2026-03-20",
        "league": "mlb",
        "home_team": "Toronto Blue Jays",
        "away_team": "Baltimore Orioles",
        "event_name": "Baltimore Orioles at Toronto Blue Jays",
        "event_date": "2026-03-20T19:07:00",
        "venue": "Rogers Centre",
        "price_boost": 13,
    },
    {
        "event_id": "mlb-brewers-reds-2026-03-21",
        "league": "mlb",
        "home_team": "Milwaukee Brewers",
        "away_team": "Cincinnati Reds",
        "event_name": "Cincinnati Reds at Milwaukee Brewers",
        "event_date": "2026-03-21T19:10:00",
        "venue": "American Family Field",
        "price_boost": 11,
    },
    {
        "event_id": "mlb-tigers-guardians-2026-03-22",
        "league": "mlb",
        "home_team": "Detroit Tigers",
        "away_team": "Cleveland Guardians",
        "event_name": "Cleveland Guardians at Detroit Tigers",
        "event_date": "2026-03-22T13:10:00",
        "venue": "Comerica Park",
        "price_boost": 10,
    },
    {
        "event_id": "mlb-dbacks-rockies-2026-03-23",
        "league": "mlb",
        "home_team": "Arizona Diamondbacks",
        "away_team": "Colorado Rockies",
        "event_name": "Colorado Rockies at Arizona Diamondbacks",
        "event_date": "2026-03-23T18:40:00",
        "venue": "Chase Field",
        "price_boost": 9,
    },
    {
        "event_id": "mlb-twins-royals-2026-03-24",
        "league": "mlb",
        "home_team": "Minnesota Twins",
        "away_team": "Kansas City Royals",
        "event_name": "Kansas City Royals at Minnesota Twins",
        "event_date": "2026-03-24T19:10:00",
        "venue": "Target Field",
        "price_boost": 8,
    },
    {
        "event_id": "mlb-athletics-mariners-2026-03-25",
        "league": "mlb",
        "home_team": "Athletics",
        "away_team": "Seattle Mariners",
        "event_name": "Seattle Mariners at Athletics",
        "event_date": "2026-03-25T19:05:00",
        "venue": "Oakland Coliseum",
        "price_boost": 8,
    },
    {
        "event_id": "mlb-nationals-marlins-2026-03-26",
        "league": "mlb",
        "home_team": "Washington Nationals",
        "away_team": "Miami Marlins",
        "event_name": "Miami Marlins at Washington Nationals",
        "event_date": "2026-03-26T18:45:00",
        "venue": "Nationals Park",
        "price_boost": 7,
    },
    {
        "event_id": "mlb-giants-padres-2026-03-27",
        "league": "mlb",
        "home_team": "San Francisco Giants",
        "away_team": "San Diego Padres",
        "event_name": "San Diego Padres at San Francisco Giants",
        "event_date": "2026-03-27T19:15:00",
        "venue": "Oracle Park",
        "price_boost": 14,
    },
    {
        "event_id": "mlb-dodgers-dbacks-2026-03-28",
        "league": "mlb",
        "home_team": "Los Angeles Dodgers",
        "away_team": "Arizona Diamondbacks",
        "event_name": "Arizona Diamondbacks at Los Angeles Dodgers",
        "event_date": "2026-03-28T19:10:00",
        "venue": "Dodger Stadium",
        "price_boost": 15,
    },
    {
        "event_id": "mlb-yankees-bluejays-2026-03-29",
        "league": "mlb",
        "home_team": "New York Yankees",
        "away_team": "Toronto Blue Jays",
        "event_name": "Toronto Blue Jays at New York Yankees",
        "event_date": "2026-03-29T13:35:00",
        "venue": "Yankee Stadium",
        "price_boost": 18,
    },
    {
        "event_id": "mlb-redsox-rays-2026-03-30",
        "league": "mlb",
        "home_team": "Boston Red Sox",
        "away_team": "Tampa Bay Rays",
        "event_name": "Tampa Bay Rays at Boston Red Sox",
        "event_date": "2026-03-30T19:10:00",
        "venue": "Fenway Park",
        "price_boost": 13,
    },
    {
        "event_id": "mlb-cubs-brewers-2026-03-31",
        "league": "mlb",
        "home_team": "Chicago Cubs",
        "away_team": "Milwaukee Brewers",
        "event_name": "Milwaukee Brewers at Chicago Cubs",
        "event_date": "2026-03-31T19:05:00",
        "venue": "Wrigley Field",
        "price_boost": 15,
    },
    {
        "event_id": "mlb-phillies-mets-2026-04-01",
        "league": "mlb",
        "home_team": "Philadelphia Phillies",
        "away_team": "New York Mets",
        "event_name": "New York Mets at Philadelphia Phillies",
        "event_date": "2026-04-01T18:40:00",
        "venue": "Citizens Bank Park",
        "price_boost": 16,
    },
]

GAMES: list[Game] = [
    Game(
        event_id=game["event_id"],
        league=game["league"],
        home_team=game["home_team"],
        away_team=game["away_team"],
        event_name=game["event_name"],
        event_date=game["event_date"],
        venue=game["venue"],
    )
    for game in _RAW_GAMES
]

VENDORS = ["stubhub", "seatgeek", "vividseats"]

SECTION_TEMPLATES = [
    {
        "vendor": "stubhub",
        "section": "Field 12",
        "section_group": "Field Level",
        "row": "C",
        "quantity": 2,
        "base_price": 189,
    },
    {
        "vendor": "vividseats",
        "section": "Dugout Club 8",
        "section_group": "Club Level",
        "row": "B",
        "quantity": 2,
        "base_price": 245,
    },
    {
        "vendor": "seatgeek",
        "section": "Lower Box 109",
        "section_group": "Lower Bowl",
        "row": "14",
        "quantity": 2,
        "base_price": 96,
    },
    {
        "vendor": "stubhub",
        "section": "Main Level 132",
        "section_group": "Lower Bowl",
        "row": "21",
        "quantity": 4,
        "base_price": 118,
    },
    {
        "vendor": "vividseats",
        "section": "Club 205",
        "section_group": "Club Level",
        "row": "7",
        "quantity": 2,
        "base_price": 128,
    },
    {
        "vendor": "seatgeek",
        "section": "Bleachers 39",
        "section_group": "Outfield",
        "row": "18",
        "quantity": 4,
        "base_price": 58,
    },
    {
        "vendor": "stubhub",
        "section": "Right Field Pavilion 301",
        "section_group": "Outfield",
        "row": "11",
        "quantity": 2,
        "base_price": 52,
    },
    {
        "vendor": "vividseats",
        "section": "Upper Reserve 312",
        "section_group": "Upper Deck",
        "row": "9",
        "quantity": 4,
        "base_price": 44,
    },
    {
        "vendor": "seatgeek",
        "section": "Top Deck 425",
        "section_group": "Upper Deck",
        "row": "3",
        "quantity": 1,
        "base_price": 36,
    },
]

VENDOR_PRICE_ADJUSTMENT = {
    "stubhub": 8.0,
    "seatgeek": 0.0,
    "vividseats": -4.0,
}


def _build_ticket_listings() -> list[TicketListing]:
    listings: list[TicketListing] = []

    for game_index, game in enumerate(_RAW_GAMES):
        for template_index, template in enumerate(SECTION_TEMPLATES):
            vendor = template["vendor"]
            base_price = float(template["base_price"])
            game_price_boost = float(game["price_boost"])
            index_adjustment = float((game_index % 4) * 4)
            template_adjustment = float((template_index % 3) * 1.5)

            price = round(
                base_price
                + game_price_boost
                + VENDOR_PRICE_ADJUSTMENT[vendor]
                + index_adjustment
                + template_adjustment,
                2,
            )

            listings.append(
                TicketListing(
                    vendor=vendor,
                    event_id=game["event_id"],
                    event_name=game["event_name"],
                    section=template["section"],
                    section_group=template["section_group"],
                    row=template["row"],
                    quantity=int(template["quantity"]),
                    price=price,
                    currency="USD",
                    listing_url=f"https://example.com/{vendor}/{game['event_id']}/{template_index + 1}",
                )
            )

    return listings


TICKET_LISTINGS: list[TicketListing] = _build_ticket_listings()