# Database connection (SQLite file). Swap the URL for PostgreSQL in production.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("sqlite:///./assets.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():  # FastAPI dependency: one DB session per request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
