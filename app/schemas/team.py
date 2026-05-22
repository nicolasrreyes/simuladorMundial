from pydantic import BaseModel, ConfigDict, Field

from app.schemas.player import PlayerRead


class TeamBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    country_code: str = Field(min_length=2, max_length=3)
    confederation: str = Field(min_length=2, max_length=20)
    group: str = Field(min_length=1, max_length=1, pattern="^[A-H]$")
    coach: str = Field(min_length=2, max_length=100)


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    country_code: str | None = Field(default=None, min_length=2, max_length=3)
    confederation: str | None = Field(default=None, min_length=2, max_length=20)
    group: str | None = Field(default=None, min_length=1, max_length=1, pattern="^[A-H]$")
    coach: str | None = Field(default=None, min_length=2, max_length=100)


class TeamRead(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TeamWithPlayers(TeamRead):
    players: list[PlayerRead] = []
