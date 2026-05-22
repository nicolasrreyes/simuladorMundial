from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.player import PlayerCreate, PlayerRead, PlayerUpdate
from app.services.player_service import PlayerService


router = APIRouter(prefix="/players", tags=["Jugadores"])


@router.get("", response_model=list[PlayerRead])
def list_players(team_id: int | None = None, db: Session = Depends(get_db)):
    return PlayerService(db).list_players(team_id=team_id)


@router.get("/{player_id}", response_model=PlayerRead)
def get_player(player_id: int, db: Session = Depends(get_db)):
    return PlayerService(db).get_player(player_id)


@router.post("", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
def create_player(payload: PlayerCreate, db: Session = Depends(get_db)):
    return PlayerService(db).create_player(payload)


@router.put("/{player_id}", response_model=PlayerRead)
def update_player(player_id: int, payload: PlayerUpdate, db: Session = Depends(get_db)):
    return PlayerService(db).update_player(player_id, payload)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    PlayerService(db).delete_player(player_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
