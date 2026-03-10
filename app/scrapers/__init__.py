from app.scrapers.seatgeek import SeatGeekScraper
from app.scrapers.stubhub import StubHubScraper
from app.scrapers.vividseats import VividSeatsScraper

SCRAPERS = {
    "stubhub": StubHubScraper(),
    "seatgeek": SeatGeekScraper(),
    "vividseats": VividSeatsScraper(),
}