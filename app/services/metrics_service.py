from fastapi import HTTPException, status

from app.repositories.metrics_repository import MetricsRepository
from app.schemas.metrics import DashboardMetrics, GoldenBootMetric
from app.schemas.simulator import TournamentResult


class MetricsService:
    def __init__(self):
        self.repository = MetricsRepository()

    def save_tournament(self, tournament: TournamentResult) -> TournamentResult:
        return self.repository.save_last_tournament(tournament)

    def clear_tournament(self) -> None:
        self.repository.clear_last_tournament()

    def get_dashboard_metrics(self) -> DashboardMetrics:
        tournament = self.repository.get_last_tournament()
        if tournament is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay una simulacion ejecutada para calcular metricas",
            )

        total_goals = self._count_total_goals(tournament)
        total_matches = self._count_total_matches(tournament)
        golden_boot = tournament.top_scorers[0]
        return DashboardMetrics(
            champion=tournament.champion,
            golden_boot=GoldenBootMetric(
                player=golden_boot.player,
                team=golden_boot.team,
                goals=golden_boot.goals,
            ),
            goals_per_match_average=round(total_goals / total_matches, 2) if total_matches else 0,
            total_goals=total_goals,
            total_matches=total_matches,
        )

    def _count_total_goals(self, tournament: TournamentResult) -> int:
        group_goals = sum(
            match.home_goals + match.away_goals
            for group in tournament.groups
            for match in group.matches
        )
        knockout_goals = sum(
            match.home_goals + match.away_goals
            for round_data in tournament.bracket
            for match in round_data.matches
        )
        return group_goals + knockout_goals

    def _count_total_matches(self, tournament: TournamentResult) -> int:
        return sum(len(group.matches) for group in tournament.groups) + sum(
            len(round_data.matches) for round_data in tournament.bracket
        )
