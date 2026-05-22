from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.team_repository import TeamRepository
from app.schemas.team import TeamCreate, TeamUpdate


class TeamService:
    def __init__(self, db: Session):
        self.repository = TeamRepository(db)

    def list_teams(self):
        return self.repository.list()

    def get_team(self, team_id: int):
        team = self.repository.get(team_id)
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
        return team

    def create_team(self, payload: TeamCreate):
        try:
            return self.repository.create(payload)
        except IntegrityError as exc:
            self.repository.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un equipo con ese nombre o codigo",
            ) from exc

    def update_team(self, team_id: int, payload: TeamUpdate):
        team = self.get_team(team_id)
        try:
            return self.repository.update(team, payload)
        except IntegrityError as exc:
            self.repository.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un equipo con ese nombre o codigo",
            ) from exc

    def delete_team(self, team_id: int) -> None:
        team = self.get_team(team_id)
        self.repository.delete(team)
