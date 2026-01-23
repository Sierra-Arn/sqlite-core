# app/db/sync_db/session.py
from typing import Generator
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ..config import sqlite_config


engine = create_engine(
    sqlite_config.sync_connection_url,
    echo=sqlite_config.echo,
    
    # Enables SQLAlchemy 2.0-style API semantics, ensuring forward compatibility
    # and consistent behavior across future versions.
    future=True
)
"""
Synchronous SQLAlchemy database engine configured via application settings.

This engine provides the foundational connection interface for all synchronous
ORM operations against the SQLite database.
"""

SessionLocal = sessionmaker(
    autocommit=sqlite_config.autocommit,
    autoflush=sqlite_config.autoflush,
    expire_on_commit=sqlite_config.expire_on_commit,
    bind=engine,
)
"""
Session factory configured according to application-wide database behavior policies.

Creates new SQLAlchemy `Session` instances whose transactional and flushing semantics
are dictated by the `SQLiteConfig` settings.
"""

@contextmanager
def get_sync_db_session() -> Generator[Session, None, None]:
    """
    Synchronous context manager for safe and automatic database session lifecycle management.

    Provides a scoped SQLAlchemy session that is:
    1. Automatically created upon entry,
    2. Yielded to the calling code block for use,
    3. Rolled back if an exception occurs during execution,
    4. Automatically closed upon exit (regardless of success or failure).

    This pattern ensures that database connections are never leaked and that
    partial or inconsistent state is never left in the database due to unhandled errors.

    Yields
    ------
    Session
        A new SQLAlchemy synchronous session instance, ready for ORM operations.

    Notes
    -----
    - The session **does not auto-commit**; the caller is responsible for calling
    `db.commit()` to persist changes. If omitted, changes are discarded on exit.
    - In the event of an exception, the session is rolled back to maintain data integrity,
    and the exception is re-raised to propagate the error.
    - The `finally` block is implicit in the context manager protocol and does not require
    explicit cleanup beyond `session.close()`, which is handled automatically by `with`.
    """
    
    with SessionLocal() as db:
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            pass