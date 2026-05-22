from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.player import Player
from app.schemas.player import PlayerCreate, PlayerUpdate


class PlayerRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, team_id: int | None = None) -> list[Player]:
        statement = select(Player).order_by(Player.team_id, Player.number)
        if team_id is not None:
            statement = statement.where(Player.team_id == team_id)
        return list(self.db.scalars(statement))

    def get(self, player_id: int) -> Player | None:
        return self.db.get(Player, player_id)

    def create(self, payload: PlayerCreate) -> Player:
        player = Player(**payload.model_dump())
        self.db.add(player)
        self.db.commit()
        self.db.refresh(player)
        return player

    def update(self, player: Player, payload: PlayerUpdate) -> Player:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(player, field, value)
        self.db.commit()
        self.db.refresh(player)
        return player

    def delete(self, player: Player) -> None:
        self.db.delete(player)
        self.db.commit()
