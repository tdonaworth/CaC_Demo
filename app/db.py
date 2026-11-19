"""Persistence: SQLAlchemy Core. SQLite locally/in tests, Postgres (RDS) in AWS."""
from datetime import datetime, timezone

from sqlalchemy import (Column, DateTime, Integer, MetaData, String, Table, Text,
                        create_engine, insert, select, delete)

metadata = MetaData()
notes = Table(
    "notes", metadata,
    Column("id", Integer, primary_key=True),
    Column("owner", String(64), nullable=False),
    Column("body", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


def make_engine(url: str):
    engine = create_engine(url, pool_pre_ping=True)
    metadata.create_all(engine)
    return engine


def add_note(engine, owner: str, body: str) -> dict:
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        res = conn.execute(insert(notes).values(owner=owner, body=body, created_at=now))
        return {"id": res.inserted_primary_key[0], "owner": owner, "body": body,
                "created_at": now.isoformat()}


def list_notes(engine, owner: str) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(select(notes).where(notes.c.owner == owner).order_by(notes.c.id))
        return [{"id": r.id, "owner": r.owner, "body": r.body,
                 "created_at": r.created_at.isoformat()} for r in rows]


def delete_note(engine, owner: str, note_id: int) -> bool:
    with engine.begin() as conn:
        res = conn.execute(delete(notes).where(notes.c.id == note_id, notes.c.owner == owner))
        return res.rowcount > 0


def ping(engine) -> bool:
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return True
    except Exception:
        return False
