from app.schemas.simulator import TournamentResult


class MetricsRepository:
    _last_tournament: TournamentResult | None = None

    def save_last_tournament(self, tournament: TournamentResult) -> TournamentResult:
        self.__class__._last_tournament = tournament
        return tournament

    def get_last_tournament(self) -> TournamentResult | None:
        return self.__class__._last_tournament

    def clear_last_tournament(self) -> None:
        self.__class__._last_tournament = None
