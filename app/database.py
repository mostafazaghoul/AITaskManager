"""Database engine, session factory, and FastAPI session dependency.

Defaults to a local SQLite file but honours ``DATABASE_URL`` so the app
can be pointed at PostgreSQL (or any SQLAlchemy-supported database)
without code changes.
"""
import os
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DEFAULT_DATABASE_URL: str = "sqlite:///./todo.db"
DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# ``check_same_thread=False`` lets FastAPI use the SQLite connection from
# multiple threads; it is ignored by other database backends.
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Iterator[Session]:
    """Yield a database session scoped to a single request.

    Yields:
        An open SQLAlchemy ``Session`` that is always closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database_tables() -> None:
    """Create all tables defined on ``Base`` if they do not already exist.

    Returns:
        None.
    """
    Base.metadata.create_all(bind=engine)
