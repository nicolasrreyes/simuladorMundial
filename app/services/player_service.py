from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.player_repository import PlayerRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.player import PlayerCreate, PlayerUpdate


class PlayerService:
    def __init__(self, db: Session):
        self.repository = PlayerRepository(db)
        self.team_repository = TeamRepository(db)

    def list_players(self, team_id: int | None = None):
        return self.repository.list(team_id=team_id)

    def get_player(self, player_id: int):
        player = self.repository.get(player_id)
        if player is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jugador no encontrado")
        return player

    def create_player(self, payload: PlayerCreate):
        self._ensure_team_exists(payload.team_id)
        return self.repository.create(payload)

    def update_player(self, player_id: int, payload: PlayerUpdate):
        player = self.get_player(player_id)
        if payload.team_id is not None:
            self._ensure_team_exists(payload.team_id)
        return self.repository.update(player, payload)

    def delete_player(self, player_id: int) -> None:
        player = self.get_player(player_id)
        self.repository.delete(player)

    def _ensure_team_exists(self, team_id: int) -> None:
        if self.team_repository.get(team_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
