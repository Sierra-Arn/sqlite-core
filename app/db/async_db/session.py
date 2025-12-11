# app/db/async_db/session.py
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from ..config import sqlite_config


engine = create_async_engine(
    sqlite_config.async_connection_url,
    echo=sqlite_config.echo,
    future=True
)
"""
Asynchronous SQLAlchemy database engine configured via application settings.

This engine provides the foundational connection interface for all asynchronous
ORM operations against the SQLite database.

Parameters
----------
url : str
    The SQLite connection URL.
echo : bool
    Controls whether all executed SQL statements are printed to stdout.
future : bool
    Enables SQLAlchemy 2.0-style API semantics, ensuring forward compatibility
    and consistent behavior across future versions.
"""

AsyncSessionLocal = async_sessionmaker(
    autocommit=sqlite_config.autocommit,
    autoflush=sqlite_config.autoflush,
    bind=engine,
    class_=AsyncSession,
)
"""
Asynchronous session factory configured according to application-wide database behavior policies.

Creates new SQLAlchemy `AsyncSession` instances whose transactional and flushing semantics
are dictated by the `SQLiteConfig` settings.

Parameters
----------
autocommit : bool
    If `True`, each operation is automatically committed.  
    **Not recommended** for production.
autoflush : bool
    If `True`, pending changes are automatically synchronized to the database before queries.  
    Disabling (`False`) gives explicit control.
bind : AsyncEngine
    The SQLAlchemy asynchronous engine to use for database connections.
class_ : type
    Specifies the session class to instantiate; here, `AsyncSession` for asynchronous operations.

Notes
-----
With `autocommit=False` and `autoflush=False`, the developer has full control over:
    - When pending changes become visible via `await session.flush()`.
    - When changes are permanently persisted via `await session.commit()`.
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