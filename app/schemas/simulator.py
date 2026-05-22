from pydantic import BaseModel, Field


class GoalEvent(BaseModel):
    minute: int
    stage: str
    team: str
    scorer: str
    assistant: str | None = None


class GroupStanding(BaseModel):
    team_id: int
    team: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


class MatchResult(BaseModel):
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    goals: list[GoalEvent] = Field(default_factory=list)
    winner: str | None = None
    decided_by: str | None = None


class PlayerStatistic(BaseModel):
    player_id: int
    player: str
    team: str
    goals: int
    assists: int
    group_goals: int
    knockout_goals: int
    group_assists: int
    knockout_assists: int
    score: int


class PenaltyShootout(BaseModel):
    round: str
    home_team: str
    away_team: str
    winner: str
    loser: str
    home_goals: int
    away_goals: int


class GroupResult(BaseModel):
    group: str
    matches: list[MatchResult]
    standings: list[GroupStanding]
    qualified: list[str]


class KnockoutRound(BaseModel):
    name: str
    matches: list[MatchResult]


class TournamentResult(BaseModel):
    champion: str
    groups: list[GroupResult]
    bracket: list[KnockoutRound]
    penalties: list[PenaltyShootout]
    top_scorers: list[PlayerStatistic]
    top_assisters: list[PlayerStatistic]
    best_player: PlayerStatistic
