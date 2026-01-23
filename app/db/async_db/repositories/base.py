# app/db/async_db/repositories/base.py
from typing import Generic, Type, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...types import ModelType


class BaseRepository(Generic[ModelType]):
    """
    Generic base repository implementing standardized CRUD operations for SQLAlchemy models (async version).

    This class enforces a consistent data access pattern across all entities in the application.
    It assumes that:
        - Creation and update payloads are provided as plain dictionaries (typically derived from validated Pydantic schemas).
        - Update dictionaries contain only mutable, non-identifying fields.
        - Primary keys and composite identities are immutable.
        - All database interactions occur within a managed transactional session.
        - Transaction lifecycle (commit/rollback/close) is handled externally.
        - Internal methods may call `session.flush()` and `session.refresh()` as needed
          to synchronize state with the database (e.g., to obtain generated IDs or updated values).

    Child classes specialize this repository by binding a concrete model type.

    Attributes
    ----------
    db : AsyncSession
        Active SQLAlchemy async session for database interaction.
        Managed externally and injected at construction time.
    model : Type[ModelType]
        SQLAlchemy ORM model class associated with this repository.
    """

    def __init__(self, db: AsyncSession, model: Type[ModelType]) -> None:
        """
        Initialize the repository with a database session and model type.

        Parameters
        ----------
        db : AsyncSession
            Active SQLAlchemy async session providing transactional context and connection management.
        model : Type[ModelType]
            The SQLAlchemy ORM model class this repository operates on.
        """

        self.db = db
        self.model = model

    async def create(self, obj_data: dict[str, Any]) -> ModelType:
        """
        Persist a new entity to the database using data from a dictionary.

        Parameters
        ----------
        obj_data : dict[str, Any]
            Dictionary containing all required fields for the entity.

        Returns
        -------
        ModelType
            The newly created model instance, including auto-generated fields.
        """

        db_obj = self.model(**obj_data)
        self.db.add(db_obj)

        # Flush the pending INSERT statement to the database.
        # This sends the SQL to the DB engine so that the row is physically created,
        # enabling database-generated values (e.g., from server_default) to be set.
        # While refresh() would internally trigger a flush if needed, we call flush()
        # explicitly here for full transparency and deterministic control over when
        # the SQL is executed.
        await self.db.flush()

        # Refresh the instance by re-fetching it from the database using its primary key.
        # This is required because the base model defines 'created_at' and 'updated_at'
        # with server_default=func.now(), meaning their actual values are assigned
        # by the database during INSERT and are not available in the ORM object until
        # a SELECT reloads them. Without refresh(), these fields would remain None
        # or stale, leading to incomplete data in API responses.
        # Note: refresh() internally calls flush() if the object is dirty, but since
        # we already flushed above, this call purely ensures the object reflects the
        # true persisted state from the database.
        await self.db.refresh(db_obj)

        return db_obj

    async def get(self, obj_id: int) -> ModelType | None:
        """
        Retrieve an entity by its primary key.

        Parameters
        ----------
        obj_id : int
            The unique identifier of the entity to retrieve.

        Returns
        -------
        ModelType or None
            The entity if found; `None` if no record exists with the given ID.
        """
        
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        Retrieve a paginated list of all entities of this type.

        Parameters
        ----------
        skip : int, optional
            Number of records to skip (for pagination offset). Default is `0`.
        limit : int, optional
            Maximum number of records to return. Default is `100`.

        Returns
        -------
        list[ModelType]
            A list of up to `limit` entities, starting after `skip` records.
        """
        
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, obj_id: int, obj_data: dict[str, Any]) -> ModelType | None:
        """
        Update an existing entity with new values from a dictionary.
        Only fields explicitly provided in the dictionary are modified.

        Parameters
        ----------
        obj_id : int
            Primary key of the entity to update.
        obj_data : dict[str, Any]
            Dictionary containing only the new values for mutable fields.

        Returns
        -------
        ModelType or None
            The updated entity if it exists; `None` if no entity matches `obj_id`.
        """
        
        db_obj = await self.get(obj_id)
        if db_obj is None:
            return None

        for field, value in obj_data.items():
            setattr(db_obj, field, value)

        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, obj_id: int) -> bool:
        """
        Remove an entity from the database by its primary key.

        Parameters
        ----------
        obj_id : int
            Primary key of the entity to delete.

        Returns
        -------
        bool
            `True` if the entity was found and deleted; `False` if no such entity exists.
        """
        
        db_obj = await self.get(obj_id)
        if db_obj is None:
            return False

        await self.db.delete(db_obj)
        return True