from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.simulator import TournamentResult
from app.schemas.team import TeamWithPlayers
from app.services.metrics_service import MetricsService
from app.services.simulator_service import SimulatorService


router = APIRouter(prefix="/simulator", tags=["Simulador"])


@router.post("/run", response_model=TournamentResult)
def run_simulator(db: Session = Depends(get_db)):
    tournament = SimulatorService(db).run()
    return MetricsService().save_tournament(tournament)


@router.post("/draw", response_model=list[TeamWithPlayers])
def draw_groups(db: Session = Depends(get_db)):
    MetricsService().clear_tournament()
    return SimulatorService(db).draw_groups()
