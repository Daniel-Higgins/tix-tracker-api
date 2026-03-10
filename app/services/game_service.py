from app.providers.ticketmaster import TicketmasterClient
from app.types import Game


class GameService:
    def __init__(self) -> None:
        self.ticketmaster = TicketmasterClient()

    async def get_games(
        self,
        *,
        page: int = 0,
        limit: int = 50,
        team: str | None = None,
    ) -> list[Game]:
        return await self.ticketmaster.get_mlb_games(
            days_ahead=10,
            page=page,
            size=limit,
            team=team,
        )

    async def get_event(self, event_id: str) -> Game:
        return await self.ticketmaster.get_event(event_id)