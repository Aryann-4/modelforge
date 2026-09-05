from __future__ import annotations

import asyncio
import os

os.environ.setdefault("MODELFORGE_DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.infrastructure.database.base import Base

# `sqlite+aiosqlite:///:memory:` creates a brand-new, empty database for every
# new DBAPI connection. SQLAlchemy's default pooling opens a fresh connection
# per checkout, so tables created on one connection are invisible on the
# next ("no such table"). StaticPool forces every checkout on an engine to
# reuse the SAME underlying connection -- the standard SQLAlchemy recipe for
# in-memory SQLite in tests.


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", future=True, poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def app_client(monkeypatch):
    """A fully wired FastAPI test client against an isolated in-memory DB."""
    from app.infrastructure.database import base as db_base

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", future=True, poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    monkeypatch.setattr(db_base, "engine", engine)
    monkeypatch.setattr(db_base, "SessionLocal", session_factory)

    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    await engine.dispose()
