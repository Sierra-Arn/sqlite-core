# app/db/models/base.py
from datetime import datetime
from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """
    Base declarative model class for all SQLAlchemy ORM models in the application.

    This class serves as the foundation for all database entities, providing:
    1. A standardized auto-incrementing primary key (`id`),
    2. Automatic creation timestamp (`created_at`),
    3. Automatic last-modification timestamp (`updated_at`).

    It follows SQLAlchemy 2.0's declarative syntax using `Mapped` annotations and leverages
    database-side functions for timestamp management to ensure consistency and reduce application-side logic.

    The class is intentionally schema-agnostic to align with microservice architectural principles:
    - Each service owns its dedicated database (database-per-service pattern),
    - Database objects reside in the default schema,
    - Explicit schema qualification is omitted to simplify deployment and migrations.

    Attributes
    ----------
    id : Mapped[int]
        Surrogate primary key for the record.
        Automatically assigned as a monotonically increasing integer upon insertion.
    created_at : Mapped[datetime]
        Timestamp indicating when the record was first inserted.
        Set automatically by the database using the current time at insert time.
        Value remains immutable after creation.
    updated_at : Mapped[datetime]
        Timestamp indicating the last time the record was modified.
        Initialized to the creation time and automatically updated to the current time
        on every `UPDATE` operation via database-level triggers or column defaults.

    Notes
    -----
    - All child models inherit these three columns by default.
    - Timestamps are managed entirely by the database engine (not the application),
      ensuring accuracy even under concurrent or time-skewed client conditions.
    - This base class assumes a single-tenant, single-schema deployment model typical
      in containerized microservices.
    """

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
        autoincrement=True,
        # comment parameter adds documentation directly to the database column (visible in DB schema)
        comment="Primary key identifier"
    )

    # Automatically set creation timestamp using database function
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),  # Database sets this value on insert
        comment="Record creation timestamp"
    )
    
    # Automatically updated timestamp that changes on every update
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),        # Updates automatically when row changes
        comment="Last update timestamp"
    )