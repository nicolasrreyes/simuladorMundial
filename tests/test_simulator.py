import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.repositories.metrics_repository import MetricsRepository


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    MetricsRepository().clear_last_tournament()
    with TestClient(app) as test_client:
        yield test_client
    MetricsRepository().clear_last_tournament()
    Base.metadata.drop_all(bind=engine)


def assert_valid_group_draw(teams):
    grouped = {group: [] for group in "ABCDEFGH"}
    for team in teams:
        grouped[team["group"]].append(team)

    assert len(teams) == 32
    assert set(grouped.keys()) == set("ABCDEFGH")
    for group_teams in grouped.values():
        confederations = [team["confederation"] for team in group_teams]
        assert len(group_teams) == 4
        assert len(confederations) == len(set(confederations))


def test_startup_autogenerates_32_teams_with_players(client):
    response = client.get("/teams")

    assert response.status_code == 200
    teams = response.json()
    assert_valid_group_draw(teams)
    assert all(len(team["players"]) == 23 for team in teams)


def test_draw_groups_returns_valid_distribution_without_repeated_confederations(client):
    response = client.post("/simulator/draw")

    assert response.status_code == 200
    assert_valid_group_draw(response.json())


def test_draw_groups_rejects_impossible_confederation_distribution(client):
    teams = client.get("/teams").json()
    for team in teams[:9]:
        update = client.put(f"/teams/{team['id']}", json={"confederation": "UEFA"})
        assert update.status_code == 200

    response = client.post("/simulator/draw")

    assert response.status_code == 409
    assert "confederacion" in response.json()["detail"].lower()


def test_run_simulator_returns_complete_tournament_structure_and_stats(client):
    response = client.post("/simulator/run")

    assert response.status_code == 200
    data = response.json()
    assert data["champion"]
    assert len(data["groups"]) == 8
    assert [len(round_data["matches"]) for round_data in data["bracket"]] == [8, 4, 2, 1]
    assert [round_data["name"] for round_data in data["bracket"]] == [
        "Octavos",
        "Cuartos",
        "Semifinal",
        "Final",
    ]
    assert data["best_player"]["player"]
    assert data["best_player"]["score"] >= 0
    assert "penalties" in data
    assert data["top_scorers"]
    assert data["top_assisters"]

    for group in data["groups"]:
        assert len(group["matches"]) == 6
        assert len(group["standings"]) == 4
        assert len(group["qualified"]) == 2
        assert sum(row["played"] for row in group["standings"]) == 12


def test_dashboard_metrics_match_last_simulation(client):
    tournament = client.post("/simulator/run").json()
    metrics_response = client.get("/metrics/dashboard")

    assert metrics_response.status_code == 200
    metrics = metrics_response.json()
    total_goals = sum(
        match["home_goals"] + match["away_goals"]
        for group in tournament["groups"]
        for match in group["matches"]
    )
    total_goals += sum(
        match["home_goals"] + match["away_goals"]
        for round_data in tournament["bracket"]
        for match in round_data["matches"]
    )
    total_matches = sum(len(group["matches"]) for group in tournament["groups"]) + sum(
        len(round_data["matches"]) for round_data in tournament["bracket"]
    )

    assert metrics["champion"] == tournament["champion"]
    assert metrics["golden_boot"]["player"] == tournament["top_scorers"][0]["player"]
    assert metrics["golden_boot"]["team"] == tournament["top_scorers"][0]["team"]
    assert metrics["golden_boot"]["goals"] == tournament["top_scorers"][0]["goals"]
    assert metrics["total_goals"] == total_goals
    assert metrics["total_matches"] == total_matches
    assert metrics["goals_per_match_average"] == round(total_goals / total_matches, 2)


def test_dashboard_metrics_require_previous_simulation(client):
    assert client.get("/metrics/dashboard").status_code == 404

    client.post("/simulator/run")
    assert client.get("/metrics/dashboard").status_code == 200

    client.post("/simulator/draw")
    response = client.get("/metrics/dashboard")

    assert response.status_code == 404
    assert "simulacion" in response.json()["detail"].lower()


def test_run_simulator_player_statistics_are_consistent_with_match_events(client):
    data = client.post("/simulator/run").json()

    match_goals = sum(
        match["home_goals"] + match["away_goals"]
        for group in data["groups"]
        for match in group["matches"]
    )
    match_goals += sum(
        match["home_goals"] + match["away_goals"]
        for round_data in data["bracket"]
        for match in round_data["matches"]
    )
    event_goals = sum(
        len(match["goals"])
        for group in data["groups"]
        for match in group["matches"]
    )
    event_goals += sum(
        len(match["goals"])
        for round_data in data["bracket"]
        for match in round_data["matches"]
    )
    scorer_goals = sum(player["goals"] for player in data["top_scorers"])
    event_assists = sum(
        1
        for group in data["groups"]
        for match in group["matches"]
        for goal in match["goals"]
        if goal["assistant"]
    )
    event_assists += sum(
        1
        for round_data in data["bracket"]
        for match in round_data["matches"]
        for goal in match["goals"]
        if goal["assistant"]
    )
    assists = sum(player["assists"] for player in data["top_assisters"])
    scorer_phase_goals = sum(player["group_goals"] + player["knockout_goals"] for player in data["top_scorers"])
    assister_phase_assists = sum(
        player["group_assists"] + player["knockout_assists"] for player in data["top_assisters"]
    )

    assert match_goals == event_goals
    assert event_goals == scorer_goals
    assert event_assists == assists
    assert scorer_goals == scorer_phase_goals
    assert assists == assister_phase_assists


def test_penalty_summary_matches_knockout_matches(client):
    data = client.post("/simulator/run").json()

    knockout_penalties = [
        (round_data["name"], match)
        for round_data in data["bracket"]
        for match in round_data["matches"]
        if match["decided_by"] == "penales"
    ]

    assert len(data["penalties"]) == len(knockout_penalties)
    for penalty in data["penalties"]:
        assert penalty["round"] in {"Octavos", "Cuartos", "Semifinal", "Final"}
        assert penalty["winner"] != penalty["loser"]
        assert penalty["winner"] in {penalty["home_team"], penalty["away_team"]}
        assert penalty["loser"] in {penalty["home_team"], penalty["away_team"]}


def test_teams_crud_happy_path(client):
    create_response = client.post(
        "/teams",
        json={
            "name": "Test FC",
            "country_code": "TFC",
            "confederation": "TEST",
            "group": "A",
            "coach": "Test Coach",
        },
    )
    assert create_response.status_code == 201
    team_id = create_response.json()["id"]

    get_response = client.get(f"/teams/{team_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test FC"

    update_response = client.put(
        f"/teams/{team_id}",
        json={"coach": "Updated Coach", "confederation": "DEMO"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["coach"] == "Updated Coach"
    assert update_response.json()["confederation"] == "DEMO"

    delete_response = client.delete(f"/teams/{team_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/teams/{team_id}").status_code == 404


def test_teams_crud_errors(client):
    payload = {
        "name": "Duplicado FC",
        "country_code": "DFC",
        "confederation": "TEST",
        "group": "A",
        "coach": "Coach",
    }
    assert client.post("/teams", json=payload).status_code == 201

    duplicate_response = client.post("/teams", json=payload)
    invalid_response = client.post("/teams", json={**payload, "name": "Grupo Malo", "group": "Z"})

    assert duplicate_response.status_code == 409
    assert invalid_response.status_code == 422
    assert client.get("/teams/999999").status_code == 404


def test_players_crud_happy_path(client):
    team_id = client.get("/teams").json()[0]["id"]
    create_response = client.post(
        "/players",
        json={
            "first_name": "Demo",
            "last_name": "Player",
            "position": "Delantero",
            "number": 10,
            "team_id": team_id,
        },
    )
    assert create_response.status_code == 201
    player_id = create_response.json()["id"]

    list_response = client.get(f"/players?team_id={team_id}")
    assert list_response.status_code == 200
    assert any(player["id"] == player_id for player in list_response.json())

    update_response = client.put(f"/players/{player_id}", json={"number": 11})
    assert update_response.status_code == 200
    assert update_response.json()["number"] == 11

    delete_response = client.delete(f"/players/{player_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/players/{player_id}").status_code == 404


def test_players_crud_errors(client):
    invalid_team_response = client.post(
        "/players",
        json={
            "first_name": "Sin",
            "last_name": "Equipo",
            "position": "Arquero",
            "number": 1,
            "team_id": 999999,
        },
    )
    invalid_number_response = client.post(
        "/players",
        json={
            "first_name": "Numero",
            "last_name": "Malo",
            "position": "Defensor",
            "number": 100,
            "team_id": client.get("/teams").json()[0]["id"],
        },
    )

    assert invalid_team_response.status_code == 404
    assert invalid_number_response.status_code == 422
    assert client.get("/players/999999").status_code == 404
