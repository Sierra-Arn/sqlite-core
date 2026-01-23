# app/db/async_db/session.py
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from ..config import sqlite_config


engine = create_async_engine(
    sqlite_config.async_connection_url,
    echo=sqlite_config.echo,
    
    # Enables SQLAlchemy 2.0-style API semantics, ensuring forward compatibility
    # and consistent behavior across future versions.
    future=True
)
"""
Asynchronous SQLAlchemy database engine configured via application settings.

This engine provides the foundational connection interface for all asynchronous
ORM operations against the SQLite database.
"""

AsyncSessionLocal = async_sessionmaker(
    autocommit=sqlite_config.autocommit,
    autoflush=sqlite_config.autoflush,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=sqlite_config.expire_on_commit
)
"""
Asynchronous session factory configured according to application-wide database behavior policies.

Creates new SQLAlchemy `AsyncSession` instances whose transactional and flushing semantics
are dictated by the `SQLiteConfig` settings.
"""

@asynccontextmanager
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous context manager for safe and automatic database session lifecycle management.

    Provides a scoped SQLAlchemy asynchronous session that is:
    1. Automatically created upon entry,
    2. Yielded to the calling code block for use,
    3. Rolled back if an exception occurs during execution,
    4. Automatically closed upon exit (regardless of success or failure).

    This pattern ensures that database connections are never leaked and that
    partial or inconsistent state is never left in the database due to unhandled errors.

    Yields
    ------
    AsyncSession
        A new SQLAlchemy asynchronous session instance, ready for ORM operations.

    Notes
    -----
    - The session **does not auto-commit**; the caller is responsible for calling
    `await db.commit()` to persist changes. If omitted, changes are discarded on exit.
    - In the event of an exception, the session is rolled back to maintain data integrity,
    and the exception is re-raised to propagate the error.
    - The `finally` block is implicit in the async context manager protocol and does not require
    explicit cleanup beyond `session.close()`, which is handled automatically by `async with`.
    """
    
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise
        finally:
            pass