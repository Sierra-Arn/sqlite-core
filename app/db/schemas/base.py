# app/db/schemas/base.py
from datetime import datetime
from pydantic import Field


class IDMixin:
    """
    Mixin providing a surrogate primary key field for read schemas.
    """

    id: int = Field(
        ...,
        description="Unique surrogate identifier assigned by the database."
    )


class TimestampMixin:
    """
    Mixin providing audit timestamp fields for read schemas.
    Reflects server-generated timestamps managed by the database.
    """
    
    created_at: datetime = Field(
        ...,
        description="Timestamp when the record was first created in the database."
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the record was last modified."
    )