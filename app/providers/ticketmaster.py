import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.types import Game


MLB_TEAMS = {
    "Arizona Diamondbacks",
    "Atlanta Braves",
    "Baltimore Orioles",
    "Boston Red Sox",
    "Chicago Cubs",
    "Chicago White Sox",
    "Cincinnati Reds",
    "Cleveland Guardians",
    "Colorado Rockies",
    "Detroit Tigers",
    "Houston Astros",
    "Kansas City Royals",
    "Los Angeles Angels",
    "Los Angeles Dodgers",
    "Miami Marlins",
    "Milwaukee Brewers",
    "Minnesota Twins",
    "New York Mets",
    "New York Yankees",
    "Athletics",
    "Philadelphia Phillies",
    "Pittsburgh Pirates",
    "San Diego Padres",
    "San Francisco Giants",
    "Seattle Mariners",
    "St. Louis Cardinals",
    "Tampa Bay Rays",
    "Texas Rangers",
    "Toronto Blue Jays",
    "Washington Nationals",
}

EXCLUDED_EVENT_TERMS = [
    "tours:",
    "tour",
    "world baseball classic",
    "pinstripe pass",
    "senior stroll",
    "giveaway",
    "post-game",
    "bobblehead",
    "theme ticket",
    "special event",
]

TEAM_ALIASES = {
    "A's": "Athletics",
    "Oakland Athletics": "Athletics",
}


class TicketmasterApiError(Exception):
    pass


class TicketmasterClient:
    BASE_URL = "https://app.ticketmaster.com/discovery/v2"

    def __init__(self, api_key: str | None = None, timeout: float = 20.0) -> None:
        self.api_key = api_key or os.getenv("TICKETMASTER_API_KEY")
        self.timeout = timeout

        if not self.api_key:
            raise TicketmasterApiError("Missing TICKETMASTER_API_KEY")

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        query = {"apikey": self.api_key, **params}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.BASE_URL}{path}", params=query)

        if response.status_code == 401:
            raise TicketmasterApiError("Invalid Ticketmaster API key")

        if response.status_code == 404:
            raise TicketmasterApiError("Ticketmaster event not found")

        if response.status_code >= 400:
            raise TicketmasterApiError(
                f"Ticketmaster API error {response.status_code}: {response.text}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise TicketmasterApiError("Ticketmaster returned invalid JSON") from exc

    async def get_mlb_games(
        self,
        *,
        days_ahead: int = 10,
        country_code: str = "US",
        page: int = 0,
        size: int = 50,
        team: str | None = None,
    ) -> list[Game]:
        now_utc = datetime.now(timezone.utc)
        end_utc = now_utc + timedelta(days=days_ahead)

        params: dict[str, Any] = {
            "countryCode": country_code,
            "classificationName": "Baseball",
            "keyword": team or "MLB",
            "startDateTime": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endDateTime": end_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sort": "date,asc",
            "size": size,
            "page": page,
        }

        payload = await self._get("/events.json", params)
        events = payload.get("_embedded", {}).get("events", [])

        games: list[Game] = []
        for event in events:
            normalized = self._normalize_event(event)
            if normalized is not None:
                games.append(normalized)

        return games

    async def get_event(self, event_id: str) -> Game:
        payload = await self._get(f"/events/{event_id}.json", {})
        normalized = self._normalize_event(payload)

        if normalized is None:
            raise TicketmasterApiError("Event exists but is not a valid MLB matchup")

        return normalized

    def _normalize_event(self, event: dict[str, Any]) -> Game | None:
        event_id = str(event.get("id") or "").strip()
        event_name = str(event.get("name") or "").strip()

        if not event_id or not event_name:
            return None

        if self._should_exclude_event(event_name):
            return None

        home_team, away_team = self._extract_teams(event_name, event)

        if not self._is_valid_mlb_matchup(home_team, away_team):
            return None

        venue = self._extract_venue(event)

        dates = event.get("dates", {}).get("start", {})
        local_date = dates.get("localDate")
        local_time = dates.get("localTime")

        if local_date and local_time:
            event_date = f"{local_date}T{local_time}"
        elif local_date:
            event_date = f"{local_date}T00:00:00"
        else:
            event_date = None

        return Game(
            event_id=event_id,
            league="MLB",
            home_team=home_team,
            away_team=away_team,
            event_name=event_name,
            event_date=event_date,
            venue=venue,
            ticketmaster_url=event.get("url"),
        )

    def _should_exclude_event(self, event_name: str) -> bool:
        lowered = event_name.lower()
        return any(term in lowered for term in EXCLUDED_EVENT_TERMS)

    def _extract_teams(
        self,
        event_name: str,
        event: dict[str, Any],
    ) -> tuple[str, str]:
        cleaned = re.sub(r"\s+", " ", event_name).strip()

        patterns = [
            r"^(?P<away>.+?)\s+at\s+(?P<home>.+?)$",
            r"^(?P<away>.+?)\s+vs\.?\s+(?P<home>.+?)$",
            r"^(?P<away>.+?)\s+v\.?\s+(?P<home>.+?)$",
        ]

        for pattern in patterns:
            match = re.match(pattern, cleaned, flags=re.IGNORECASE)
            if match:
                away_team = self._clean_team_name(match.group("away"))
                home_team = self._clean_team_name(match.group("home"))
                return home_team, away_team

        attractions = event.get("_embedded", {}).get("attractions", [])
        names = [
            self._clean_team_name(a.get("name", ""))
            for a in attractions
            if a.get("name")
        ]

        if len(names) >= 2:
            return names[1], names[0]

        return "TBD", "TBD"

    def _clean_team_name(self, name: str) -> str:
        name = re.sub(r"\*.*?\*", "", name)
        name = re.sub(r":.*$", "", name)
        name = re.sub(r"\(.*?\)", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        return TEAM_ALIASES.get(name, name)

    def _is_valid_mlb_matchup(self, home_team: str, away_team: str) -> bool:
        return home_team in MLB_TEAMS and away_team in MLB_TEAMS

    def _extract_venue(self, event: dict[str, Any]) -> str:
        venues = event.get("_embedded", {}).get("venues", [])
        if venues and venues[0].get("name"):
            return str(venues[0]["name"]).strip()
        return "Unknown Venue"