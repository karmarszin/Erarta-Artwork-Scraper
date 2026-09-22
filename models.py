# models.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, func, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pathlib import Path

class Base(DeclarativeBase):
    pass

class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    artworks: Mapped[List["Artwork"]] = relationship(back_populates="artist")

class Artwork(Base):
    __tablename__ = "artworks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(1024), unique=True, nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(500))
    artist_id: Mapped[Optional[int]] = mapped_column(ForeignKey("artists.id", ondelete="SET NULL"))
    artist: Mapped[Optional["Artist"]] = relationship(back_populates="artworks")

    price: Mapped[Optional[float]] = mapped_column(Float)
    size: Mapped[Optional[str]] = mapped_column(String(100))
    year: Mapped[Optional[int]] = mapped_column(Integer)
    art_type: Mapped[Optional[str]] = mapped_column(String(100))
    genre: Mapped[Optional[str]] = mapped_column(String(100))
    technique: Mapped[Optional[str]] = mapped_column(String(200))
    baguette: Mapped[Optional[str]] = mapped_column(String(50))

    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)  # pending, done, error
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "art_market.db"

engine = create_engine(f"sqlite:///{DB_PATH}")

def init_db():
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA journal_mode = WAL;")
        conn.exec_driver_sql("PRAGMA foreign_keys = ON;")
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("Создана база данных art_market.db", DB_PATH)