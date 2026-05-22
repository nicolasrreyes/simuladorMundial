from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    country_code: Mapped[str] = mapped_column(String(3), unique=True, index=True, nullable=False)
    confederation: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    group: Mapped[str] = mapped_column(String(1), index=True, nullable=False)
    coach: Mapped[str] = mapped_column(String(100), nullable=False)

    players: Mapped[list["Player"]] = relationship(
        "Player",
        back_populates="team",
        cascade="all, delete-orphan",
    )
