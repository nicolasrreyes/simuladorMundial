import random
from dataclasses import dataclass
from itertools import combinations
from math import exp

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team
from app.repositories.team_repository import TeamRepository
from app.schemas.simulator import (
    GoalEvent,
    GroupResult,
    GroupStanding,
    KnockoutRound,
    MatchResult,
    PenaltyShootout,
    PlayerStatistic,
    TournamentResult,
)


DEFAULT_TEAMS = [
    ("Francia", "FRA", "UEFA"), ("Espana", "ESP", "UEFA"),
    ("Argentina", "ARG", "CONMEBOL"), ("Inglaterra", "ENG", "UEFA"),
    ("Portugal", "POR", "UEFA"), ("Brasil", "BRA", "CONMEBOL"),
    ("Paises Bajos", "NED", "UEFA"), ("Marruecos", "MAR", "CAF"),
    ("Belgica", "BEL", "UEFA"), ("Alemania", "GER", "UEFA"),
    ("Croacia", "CRO", "UEFA"), ("Colombia", "COL", "CONMEBOL"),
    ("Senegal", "SEN", "CAF"), ("Mexico", "MEX", "CONCACAF"),
    ("Estados Unidos", "USA", "CONCACAF"), ("Uruguay", "URU", "CONMEBOL"),
    ("Japon", "JPN", "AFC"), ("Iran", "IRN", "AFC"),
    ("Ecuador", "ECU", "CONMEBOL"), ("Corea del Sur", "KOR", "AFC"),
    ("Australia", "AUS", "AFC"), ("Argelia", "ALG", "CAF"),
    ("Egipto", "EGY", "CAF"), ("Canada", "CAN", "CONCACAF"),
    ("Panama", "PAN", "CONCACAF"), ("Costa de Marfil", "CIV", "CAF"),
    ("Paraguay", "PAR", "CONMEBOL"), ("Tunez", "TUN", "CAF"),
    ("Congo DR", "COD", "CAF"), ("Uzbekistan", "UZB", "AFC"),
    ("Qatar", "QAT", "AFC"), ("Sudafrica", "RSA", "CAF"),
]

POSITIONS = ["Arquero", "Defensor", "Mediocampista", "Delantero"]

# Perfiles aproximados basados en ranking FIFA masculino del 1 de abril de 2026,
# historial mundialista y favoritismo publico/mercado consultado en mayo de 2026.
TEAM_PROFILES = {
    "Francia": {"rank": 1, "titles": 2, "semis": 7, "champion_probability": 0.16},
    "Espana": {"rank": 2, "titles": 1, "semis": 2, "champion_probability": 0.18},
    "Argentina": {"rank": 3, "titles": 3, "semis": 6, "champion_probability": 0.11},
    "Inglaterra": {"rank": 4, "titles": 1, "semis": 3, "champion_probability": 0.14},
    "Portugal": {"rank": 5, "titles": 0, "semis": 2, "champion_probability": 0.08},
    "Brasil": {"rank": 6, "titles": 5, "semis": 11, "champion_probability": 0.11},
    "Paises Bajos": {"rank": 7, "titles": 0, "semis": 5, "champion_probability": 0.05},
    "Marruecos": {"rank": 8, "titles": 0, "semis": 1, "champion_probability": 0.025},
    "Belgica": {"rank": 9, "titles": 0, "semis": 2, "champion_probability": 0.03},
    "Alemania": {"rank": 10, "titles": 4, "semis": 13, "champion_probability": 0.07},
    "Croacia": {"rank": 11, "titles": 0, "semis": 3, "champion_probability": 0.025},
    "Colombia": {"rank": 12, "titles": 0, "semis": 0, "champion_probability": 0.035},
    "Senegal": {"rank": 13, "titles": 0, "semis": 0, "champion_probability": 0.015},
    "Mexico": {"rank": 14, "titles": 0, "semis": 0, "champion_probability": 0.012},
    "Estados Unidos": {"rank": 15, "titles": 0, "semis": 1, "champion_probability": 0.02},
    "Uruguay": {"rank": 16, "titles": 2, "semis": 5, "champion_probability": 0.025},
    "Japon": {"rank": 17, "titles": 0, "semis": 0, "champion_probability": 0.012},
    "Iran": {"rank": 18, "titles": 0, "semis": 0, "champion_probability": 0.006},
    "Ecuador": {"rank": 19, "titles": 0, "semis": 0, "champion_probability": 0.01},
    "Corea del Sur": {"rank": 20, "titles": 0, "semis": 1, "champion_probability": 0.008},
    "Australia": {"rank": 21, "titles": 0, "semis": 0, "champion_probability": 0.005},
    "Argelia": {"rank": 22, "titles": 0, "semis": 0, "champion_probability": 0.006},
    "Egipto": {"rank": 23, "titles": 0, "semis": 0, "champion_probability": 0.006},
    "Canada": {"rank": 24, "titles": 0, "semis": 0, "champion_probability": 0.01},
    "Panama": {"rank": 25, "titles": 0, "semis": 0, "champion_probability": 0.003},
    "Costa de Marfil": {"rank": 26, "titles": 0, "semis": 0, "champion_probability": 0.006},
    "Paraguay": {"rank": 27, "titles": 0, "semis": 0, "champion_probability": 0.006},
    "Tunez": {"rank": 28, "titles": 0, "semis": 0, "champion_probability": 0.003},
    "Congo DR": {"rank": 29, "titles": 0, "semis": 0, "champion_probability": 0.002},
    "Uzbekistan": {"rank": 30, "titles": 0, "semis": 0, "champion_probability": 0.003},
    "Qatar": {"rank": 31, "titles": 0, "semis": 0, "champion_probability": 0.003},
    "Sudafrica": {"rank": 32, "titles": 0, "semis": 0, "champion_probability": 0.003},
}


@dataclass
class StandingAccumulator:
    team: Team
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against


@dataclass
class PlayerStatAccumulator:
    player: Player
    team: Team
    goals: int = 0
    assists: int = 0
    group_goals: int = 0
    knockout_goals: int = 0
    group_assists: int = 0
    knockout_assists: int = 0
    score: int = 0


class SimulatorService:
    def __init__(self, db: Session):
        self.db = db
        self.team_repository = TeamRepository(db)

    def run(self) -> TournamentResult:
        teams = self._ensure_world_cup_roster()
        if not self._groups_are_valid(teams):
            teams = self.draw_groups()
        stats = self._build_player_stats(teams)
        group_results, qualifiers_by_group = self._play_groups(teams, stats)
        bracket, penalties = self._play_knockout(qualifiers_by_group, stats)
        champion = bracket[-1].matches[0].winner or ""
        self._apply_team_performance_bonus(teams, champion, stats)
        ranked_stats = self._rank_player_stats(stats)
        return TournamentResult(
            champion=champion,
            groups=group_results,
            bracket=bracket,
            penalties=penalties,
            top_scorers=[
                item
                for item in sorted(ranked_stats, key=lambda item: (item.goals, item.assists, item.score), reverse=True)
                if item.goals > 0
            ],
            top_assisters=[
                item
                for item in sorted(ranked_stats, key=lambda item: (item.assists, item.goals, item.score), reverse=True)
                if item.assists > 0
            ],
            best_player=ranked_stats[0],
        )

    def draw_groups(self) -> list[Team]:
        teams = self._ensure_world_cup_roster()
        if len(teams) != 32:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El sorteo requiere exactamente 32 equipos",
            )

        drawn_groups = self._build_valid_draw(teams)
        for group_name, group_teams in drawn_groups.items():
            for team in group_teams:
                team.group = group_name
        self.db.commit()
        return self.team_repository.list()

    def _ensure_world_cup_roster(self) -> list[Team]:
        teams = self.team_repository.list()
        if len(teams) != 32:
            self._reset_and_seed_teams()
            teams = self.team_repository.list()
        return teams

    def _reset_and_seed_teams(self) -> None:
        self.db.query(Player).delete()
        self.db.query(Team).delete()
        for index, (name, code, confederation) in enumerate(DEFAULT_TEAMS):
            team = Team(
                name=name,
                country_code=code,
                confederation=confederation,
                group="A",
                coach=f"DT {name}",
            )
            self.db.add(team)
            self.db.flush()
            for number in range(1, 24):
                self.db.add(
                    Player(
                        first_name=f"Jugador{number}",
                        last_name=code,
                        position=POSITIONS[(number - 1) % len(POSITIONS)],
                        number=number,
                        team_id=team.id,
                    )
                )
        self.db.commit()
        self.draw_groups()

    def _build_valid_draw(self, teams: list[Team]) -> dict[str, list[Team]]:
        confederation_counts: dict[str, int] = {}
        for team in teams:
            confederation_counts[team.confederation] = confederation_counts.get(team.confederation, 0) + 1

        if any(amount > 8 for amount in confederation_counts.values()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede sortear: una confederacion tiene mas de 8 equipos",
            )

        ordered_teams = sorted(
            teams,
            key=lambda team: (confederation_counts[team.confederation], random.random()),
            reverse=True,
        )
        groups = {group: [] for group in "ABCDEFGH"}
        confederations_by_group = {group: set() for group in "ABCDEFGH"}

        def place_team(index: int) -> bool:
            if index == len(ordered_teams):
                return True

            team = ordered_teams[index]
            candidate_groups = list(groups.keys())
            random.shuffle(candidate_groups)
            candidate_groups.sort(key=lambda group: len(groups[group]))

            for group in candidate_groups:
                if len(groups[group]) >= 4 or team.confederation in confederations_by_group[group]:
                    continue
                groups[group].append(team)
                confederations_by_group[group].add(team.confederation)
                if place_team(index + 1):
                    return True
                groups[group].pop()
                confederations_by_group[group].remove(team.confederation)
            return False

        if not place_team(0):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se pudo generar un sorteo valido con las confederaciones actuales",
            )
        return groups

    def _groups_are_valid(self, teams: list[Team]) -> bool:
        grouped = {group: [team for team in teams if team.group == group] for group in "ABCDEFGH"}
        for group_teams in grouped.values():
            confederations = [team.confederation for team in group_teams]
            if len(group_teams) != 4 or len(confederations) != len(set(confederations)):
                return False
        return True

    def _play_groups(
        self,
        teams: list[Team],
        stats: dict[int, PlayerStatAccumulator],
    ) -> tuple[list[GroupResult], dict[str, list[Team]]]:
        grouped = {group: [team for team in teams if team.group == group] for group in "ABCDEFGH"}
        group_results: list[GroupResult] = []
        qualifiers_by_group: dict[str, list[Team]] = {}

        for group, group_teams in grouped.items():
            standings = {team.id: StandingAccumulator(team=team) for team in group_teams}
            matches: list[MatchResult] = []
            for home, away in combinations(group_teams, 2):
                home_goals, away_goals = self._simulate_match_goals(home, away)
                self._apply_group_result(standings[home.id], standings[away.id], home_goals, away_goals)
                goal_events = self._generate_goal_events(home, home_goals, stats, "group")
                goal_events.extend(self._generate_goal_events(away, away_goals, stats, "group"))
                matches.append(
                    MatchResult(
                        home_team=home.name,
                        away_team=away.name,
                        home_goals=home_goals,
                        away_goals=away_goals,
                        goals=sorted(goal_events, key=lambda event: event.minute),
                    )
                )

            ordered = sorted(
                standings.values(),
                key=lambda item: (item.points, item.goal_difference, item.goals_for, random.random()),
                reverse=True,
            )
            qualifiers = [ordered[0].team, ordered[1].team]
            qualifiers_by_group[group] = qualifiers
            group_results.append(
                GroupResult(
                    group=group,
                    matches=matches,
                    standings=[
                        GroupStanding(
                            team_id=item.team.id,
                            team=item.team.name,
                            played=item.played,
                            won=item.won,
                            drawn=item.drawn,
                            lost=item.lost,
                            goals_for=item.goals_for,
                            goals_against=item.goals_against,
                            goal_difference=item.goal_difference,
                            points=item.points,
                        )
                        for item in ordered
                    ],
                    qualified=[team.name for team in qualifiers],
                )
            )
        return group_results, qualifiers_by_group

    def _apply_group_result(
        self,
        home: StandingAccumulator,
        away: StandingAccumulator,
        home_goals: int,
        away_goals: int,
    ) -> None:
        home.played += 1
        away.played += 1
        home.goals_for += home_goals
        home.goals_against += away_goals
        away.goals_for += away_goals
        away.goals_against += home_goals

        if home_goals > away_goals:
            home.won += 1
            away.lost += 1
            home.points += 3
        elif away_goals > home_goals:
            away.won += 1
            home.lost += 1
            away.points += 3
        else:
            home.drawn += 1
            away.drawn += 1
            home.points += 1
            away.points += 1

    def _play_knockout(
        self,
        qualifiers_by_group: dict[str, list[Team]],
        stats: dict[int, PlayerStatAccumulator],
    ) -> tuple[list[KnockoutRound], list[PenaltyShootout]]:
        round_of_16_pairs = [
            (qualifiers_by_group["A"][0], qualifiers_by_group["B"][1]),
            (qualifiers_by_group["C"][0], qualifiers_by_group["D"][1]),
            (qualifiers_by_group["E"][0], qualifiers_by_group["F"][1]),
            (qualifiers_by_group["G"][0], qualifiers_by_group["H"][1]),
            (qualifiers_by_group["B"][0], qualifiers_by_group["A"][1]),
            (qualifiers_by_group["D"][0], qualifiers_by_group["C"][1]),
            (qualifiers_by_group["F"][0], qualifiers_by_group["E"][1]),
            (qualifiers_by_group["H"][0], qualifiers_by_group["G"][1]),
        ]
        rounds: list[KnockoutRound] = []
        penalties: list[PenaltyShootout] = []
        current_pairs = round_of_16_pairs
        for name in ["Octavos", "Cuartos", "Semifinal", "Final"]:
            matches = [self._play_knockout_match(home, away, stats, name) for home, away in current_pairs]
            rounds.append(KnockoutRound(name=name, matches=matches))
            penalties.extend(self._extract_penalty_shootouts(name, matches))
            winners_by_name = {team.name: team for pair in current_pairs for team in pair}
            winners = [winners_by_name[match.winner or ""] for match in matches]
            current_pairs = list(zip(winners[0::2], winners[1::2]))
        return rounds, penalties

    def _play_knockout_match(
        self,
        home: Team,
        away: Team,
        stats: dict[int, PlayerStatAccumulator],
        stage: str,
    ) -> MatchResult:
        home_goals, away_goals = self._simulate_match_goals(home, away)
        goal_events = self._generate_goal_events(home, home_goals, stats, stage)
        goal_events.extend(self._generate_goal_events(away, away_goals, stats, stage))
        decided_by = None
        if home_goals == away_goals:
            winner = self._weighted_winner(home, away)
            decided_by = "penales"
        else:
            winner = home if home_goals > away_goals else away
        return MatchResult(
            home_team=home.name,
            away_team=away.name,
            home_goals=home_goals,
            away_goals=away_goals,
            goals=sorted(goal_events, key=lambda event: event.minute),
            winner=winner.name,
            decided_by=decided_by,
        )

    def _simulate_match_goals(self, home: Team, away: Team) -> tuple[int, int]:
        home_strength = self._team_strength(home.name)
        away_strength = self._team_strength(away.name)
        home_goals = self._weighted_goal_count(home_strength, away_strength)
        away_goals = self._weighted_goal_count(away_strength, home_strength)
        return home_goals, away_goals

    def _weighted_goal_count(self, attack_strength: float, defense_strength: float) -> int:
        ratio = attack_strength / max(defense_strength, 0.01)
        base_weights = [0.19, 0.27, 0.24, 0.16, 0.09, 0.05]
        adjusted_weights = []
        for goals, weight in enumerate(base_weights):
            if goals == 0:
                adjusted = weight / max(ratio ** 0.45, 0.35)
            else:
                adjusted = weight * (ratio ** (goals * 0.24))
            adjusted_weights.append(adjusted)
        return random.choices(range(6), weights=adjusted_weights, k=1)[0]

    def _weighted_winner(self, home: Team, away: Team) -> Team:
        home_strength = self._team_strength(home.name)
        away_strength = self._team_strength(away.name)
        return random.choices([home, away], weights=[home_strength, away_strength], k=1)[0]

    def _team_strength(self, team_name: str) -> float:
        profile = TEAM_PROFILES.get(
            team_name,
            {"rank": 48, "titles": 0, "semis": 0, "champion_probability": 0.002},
        )
        rank_score = max(0, 50 - profile["rank"]) / 49
        history_score = min((profile["titles"] * 0.09) + (profile["semis"] * 0.018), 0.32)
        probability_score = min(profile["champion_probability"] * 2.6, 0.48)
        raw_strength = -0.2 + (rank_score * 1.25) + history_score + probability_score
        return 0.65 + (1.95 / (1 + exp(-raw_strength)))

    def _build_player_stats(self, teams: list[Team]) -> dict[int, PlayerStatAccumulator]:
        return {
            player.id: PlayerStatAccumulator(player=player, team=team)
            for team in teams
            for player in team.players
        }

    def _generate_goal_events(
        self,
        team: Team,
        goal_count: int,
        stats: dict[int, PlayerStatAccumulator],
        stage: str,
    ) -> list[GoalEvent]:
        events: list[GoalEvent] = []
        attacking_players = [player for player in team.players if player.position != "Arquero"] or team.players
        stage_weight = self._stage_weight(stage)

        for _ in range(goal_count):
            scorer = random.choice(attacking_players)
            possible_assisters = [player for player in attacking_players if player.id != scorer.id]
            assistant = random.choice(possible_assisters) if possible_assisters and random.random() < 0.82 else None
            minute = random.randint(1, 90)

            stats[scorer.id].goals += 1
            if stage == "group":
                stats[scorer.id].group_goals += 1
            else:
                stats[scorer.id].knockout_goals += 1
            stats[scorer.id].score += 4 + stage_weight
            if assistant is not None:
                stats[assistant.id].assists += 1
                if stage == "group":
                    stats[assistant.id].group_assists += 1
                else:
                    stats[assistant.id].knockout_assists += 1
                stats[assistant.id].score += 3 + stage_weight

            events.append(
                GoalEvent(
                    minute=minute,
                    stage="Fase de grupos" if stage == "group" else stage,
                    team=team.name,
                    scorer=self._player_name(scorer),
                    assistant=self._player_name(assistant) if assistant is not None else None,
                )
            )
        return events

    def _stage_weight(self, stage: str) -> int:
        return {
            "group": 0,
            "Octavos": 1,
            "Cuartos": 2,
            "Semifinal": 3,
            "Final": 5,
        }.get(stage, 0)

    def _apply_team_performance_bonus(
        self,
        teams: list[Team],
        champion: str,
        stats: dict[int, PlayerStatAccumulator],
    ) -> None:
        for team in teams:
            team_bonus = 4 if team.name == champion else 0
            for player in team.players:
                stats[player.id].score += team_bonus

    def _rank_player_stats(self, stats: dict[int, PlayerStatAccumulator]) -> list[PlayerStatistic]:
        return [
            PlayerStatistic(
                player_id=item.player.id,
                player=self._player_name(item.player),
                team=item.team.name,
                goals=item.goals,
                assists=item.assists,
                group_goals=item.group_goals,
                knockout_goals=item.knockout_goals,
                group_assists=item.group_assists,
                knockout_assists=item.knockout_assists,
                score=item.score,
            )
            for item in sorted(
                stats.values(),
                key=lambda stat: (stat.score, stat.goals, stat.assists, random.random()),
                reverse=True,
            )
        ]

    def _player_name(self, player: Player) -> str:
        return f"{player.first_name} {player.last_name}"

    def _extract_penalty_shootouts(self, round_name: str, matches: list[MatchResult]) -> list[PenaltyShootout]:
        shootouts: list[PenaltyShootout] = []
        for match in matches:
            if match.decided_by != "penales" or match.winner is None:
                continue
            loser = match.away_team if match.winner == match.home_team else match.home_team
            shootouts.append(
                PenaltyShootout(
                    round=round_name,
                    home_team=match.home_team,
                    away_team=match.away_team,
                    winner=match.winner,
                    loser=loser,
                    home_goals=match.home_goals,
                    away_goals=match.away_goals,
                )
            )
        return shootouts
