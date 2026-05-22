from pydantic import BaseModel, ConfigDict, Field


class PlayerBase(BaseModel):
    first_name: str = Field(min_length=2, max_length=80)
    last_name: str = Field(min_length=2, max_length=80)
    position: str = Field(min_length=2, max_length=40)
    number: int = Field(ge=1, le=99)


class PlayerCreate(PlayerBase):
    team_id: int


class PlayerUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=2, max_length=80)
    last_name: str | None = Field(default=None, min_length=2, max_length=80)
    position: str | None = Field(default=None, min_length=2, max_length=40)
    number: int | None = Field(default=None, ge=1, le=99)
    team_id: int | None = None


class PlayerRead(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
