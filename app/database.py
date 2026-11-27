from collections.abc import Generator
from urllib.parse import parse_qs, urlsplit, urlunsplit
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from .config import settings


database_url = settings.database_url
connect_args = {"check_same_thread": False} if settings.is_sqlite else {}
if database_url.startswith("mysql://"):
    # منصة التطوير توفر DSN بصيغة mysql مع query خاص بـ Node؛ نحوله لموصل PyMySQL.
    parts = urlsplit(database_url)
    database_url = urlunsplit(("mysql+pymysql", parts.netloc, parts.path, "", parts.fragment))
    connect_args = {"ssl": {"check_hostname": False}}
engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
