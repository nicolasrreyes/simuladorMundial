from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate


class TeamRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Team]:
        return list(
            self.db.scalars(
                select(Team).options(selectinload(Team.players)).order_by(Team.group, Team.name)
            )
        )

    def get(self, team_id: int) -> Team | None:
        return self.db.scalar(
            select(Team).options(selectinload(Team.players)).where(Team.id == team_id)
        )

    def get_by_name(self, name: str) -> Team | None:
        return self.db.scalar(select(Team).where(Team.name == name))

    def create(self, payload: TeamCreate) -> Team:
        team = Team(**payload.model_dump())
        self.db.add(team)
        self.db.commit()
        self.db.refresh(team)
        return team

    def update(self, team: Team, payload: TeamUpdate) -> Team:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(team, field, value)
        self.db.commit()
        self.db.refresh(team)
        return team

    def delete(self, team: Team) -> None:
        self.db.delete(team)
        self.db.commit()
