from pydantic import BaseModel


class GoldenBootMetric(BaseModel):
    player: str
    team: str
    goals: int


class DashboardMetrics(BaseModel):
    champion: str
    golden_boot: GoldenBootMetric
    goals_per_match_average: float
    total_goals: int
    total_matches: int
