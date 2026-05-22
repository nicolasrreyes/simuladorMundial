from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.team import TeamCreate, TeamRead, TeamUpdate, TeamWithPlayers
from app.services.team_service import TeamService


router = APIRouter(prefix="/teams", tags=["Equipos"])


@router.get("", response_model=list[TeamWithPlayers])
def list_teams(db: Session = Depends(get_db)):
    return TeamService(db).list_teams()


@router.get("/{team_id}", response_model=TeamWithPlayers)
def get_team(team_id: int, db: Session = Depends(get_db)):
    return TeamService(db).get_team(team_id)


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(payload: TeamCreate, db: Session = Depends(get_db)):
    return TeamService(db).create_team(payload)


@router.put("/{team_id}", response_model=TeamRead)
def update_team(team_id: int, payload: TeamUpdate, db: Session = Depends(get_db)):
    return TeamService(db).update_team(team_id, payload)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    TeamService(db).delete_team(team_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
