from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.providers.ticketmaster import TicketmasterApiError
from app.services.game_service import GameService
from app.types import Game, GamesResponse

app = FastAPI(
    title="Tix Tracker API",
    version="1.0.0",
    description="Backend API for MLB events and ticket aggregation",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game_service = GameService()


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Tix Tracker API is running"
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok"
    }


@app.get("/games", response_model=GamesResponse)
async def get_games(
    page: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    team: str | None = Query(None),
) -> GamesResponse:
    try:
        games = await game_service.get_games(
            page=page,
            limit=limit,
            team=team,
        )
    except TicketmasterApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return GamesResponse(
        league="MLB",
        count=len(games),
        games=games,
    )


@app.get("/events/{event_id}", response_model=Game)
async def get_event(event_id: str) -> Game:
    try:
        return await game_service.get_event(event_id)
    except TicketmasterApiError as exc:
        detail = str(exc)

        if "not found" in detail.lower():
            raise HTTPException(status_code=404, detail=detail) from exc

        if "not a valid mlb matchup" in detail.lower():
            raise HTTPException(status_code=404, detail=detail) from exc

        raise HTTPException(status_code=502, detail=detail) from exc