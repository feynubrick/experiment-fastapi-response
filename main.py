from enum import Enum
from pydantic import BaseModel
from datetime import date

from fastapi import FastAPI


class ImperialUnit(BaseModel):
    feets: float = 0

class MetricUnit(BaseModel):
    meters: float = 0

class Unit(str, Enum):
    imperial = "imperial"
    metric = "metric"

class TeamId(str, Enum):
    liverpool = "liverpool"
    man_utd = "man_utd"
    man_city = "man_city"
    chelsea = "chelsea"

class EnglishTeamBase(BaseModel):
    name: str
    city: str

class EnglishTeamForDB(EnglishTeamBase):
    id: TeamId

class EnglishTeamForResponse(EnglishTeamBase):
    pass

class EnglishPlayer(BaseModel):
    name: str
    height: ImperialUnit | MetricUnit
    position: str
    birth_date: date
    teams: list[TeamId]

def feets_to_metric(value: ImperialUnit) -> MetricUnit:
    CONVERSION_RATE = 1 / 3.2808399
    return MetricUnit(meters=value.feets * CONVERSION_RATE)

app = FastAPI()

database = {
    "players": [
        EnglishPlayer(name="Steven Gerrard", height=ImperialUnit(feets=6) , position="Midfielder", birth_date=date(1980, 5, 30), teams=[TeamId.liverpool]),
        EnglishPlayer(name="Wayne Rooney", height=ImperialUnit(feets=5.9), position="Forward", birth_date=date(1985, 10, 24), teams=[TeamId.man_utd]),
        EnglishPlayer(name="Frank Lampard", height=ImperialUnit(feets=6), position="Midfielder", birth_date=date(1978, 6, 20), teams=[TeamId.chelsea, TeamId.man_city]),
        EnglishPlayer(name="Michael Owen", height=ImperialUnit(feets=5.8), position="Forward", birth_date=date(1979, 12, 14), teams=[TeamId.liverpool, TeamId.man_utd]),
    ],
    "teams": [
        EnglishTeamForDB(id=TeamId.liverpool, name="Liverpool FC", city="Liverpool"),
        EnglishTeamForDB(id=TeamId.man_utd, name="Manchester United", city="Manchester"),
        EnglishTeamForDB(id=TeamId.chelsea, name="Chelsea FC", city="London"),
        EnglishTeamForDB(id=TeamId.man_city, name="Manchester City", city="Manchester"),
    ]
}


def get_team(team_id: TeamId):
    for team in database["teams"]:
        if team.id == team_id:
            return team

class EnglishPlayerForResponse(EnglishPlayer):
    teams: list[EnglishTeamForResponse]

@app.get("/legends/", response_model=list[EnglishPlayerForResponse])
async def get_lengend_players(unit: Unit = Unit.imperial) -> list[EnglishPlayerForResponse]:
    players = []
    for player in database["players"]:
        player_data = player.dict()
        teams = [get_team(team_id) for team_id in player_data["teams"]]
        player_data["teams"] = teams

        players.append(EnglishPlayerForResponse(**player_data))

    if unit == Unit.metric:
        for player in players:
            player.height = feets_to_metric(player.height)
            print(player.height)
    print(players)
    return players
