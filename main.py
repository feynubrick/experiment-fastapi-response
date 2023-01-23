from enum import Enum
from pydantic import BaseModel
from datetime import date

from fastapi import FastAPI


class LengthInImperialUnit(BaseModel):
    feet: int = 0
    inch: float = 0

def feets_to_metric(length: LengthInImperialUnit) -> float:
    FEET_TO_INCH = 12
    INCH_TO_METER = 0.0254
    inch = length.feet * FEET_TO_INCH + length.inch
    return inch * INCH_TO_METER

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
    height: LengthInImperialUnit
    height_in_metric: float = 0
    position: str
    birth_date: date
    teams: list[TeamId]


app = FastAPI()

database = {
    "teams": [
        EnglishTeamForDB(id=TeamId.liverpool, name="Liverpool FC", city="Liverpool"),
        EnglishTeamForDB(id=TeamId.man_utd, name="Manchester United", city="Manchester"),
        EnglishTeamForDB(id=TeamId.chelsea, name="Chelsea FC", city="London"),
        EnglishTeamForDB(id=TeamId.man_city, name="Manchester City", city="Manchester"),
    ],
    "players": [
        EnglishPlayer(name="Steven Gerrard", height=LengthInImperialUnit(feet=6, inch=0), position="Midfielder", birth_date=date(1980, 5, 30), teams=[TeamId.liverpool]),
        EnglishPlayer(name="Wayne Rooney", height=LengthInImperialUnit(feet=5, inch=9), position="Forward", birth_date=date(1985, 10, 24), teams=[TeamId.man_utd]),
        EnglishPlayer(name="Frank Lampard", height=LengthInImperialUnit(feet=6, inch=0), position="Midfielder", birth_date=date(1978, 6, 20), teams=[TeamId.chelsea, TeamId.man_city]),
        EnglishPlayer(name="Michael Owen", height=LengthInImperialUnit(feet=5, inch=8), position="Forward", birth_date=date(1979, 12, 14), teams=[TeamId.liverpool, TeamId.man_utd]),
    ],
}


def get_team(team_id: TeamId):
    for team in database["teams"]:
        if team.id == team_id:
            return team

class EnglishPlayerForResponse(EnglishPlayer):
    teams: list[EnglishTeamForResponse]

@app.get("/legends/", response_model=list[EnglishPlayerForResponse])
async def get_lengend_players() -> list[EnglishPlayerForResponse]:
    players = []
    for player in database["players"]:
        player_data = player.dict()
        teams = [get_team(team_id) for team_id in player_data["teams"]]
        player_data["teams"] = teams
        player_data["height_in_metric"] = feets_to_metric(player.height)
        players.append(EnglishPlayerForResponse(**player_data))

    print(players)
    return players
