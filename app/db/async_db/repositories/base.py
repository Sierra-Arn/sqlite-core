# app/db/async_db/repositories/base.py
from typing import Generic, Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...types import ModelType, CreateSchemaType, UpdateSchemaType


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic base repository implementing standardized CRUD operations for SQLAlchemy models.

    This class enforces a consistent data access pattern across all entities in the application.
    It assumes that:
        - Creation and update payloads are provided via Pydantic schemas.
        - Update schemas contain only mutable, non-identifying fields.
        - Primary keys and composite identities are immutable.
        - All database interactions occur within a managed transactional session.
        - Transaction lifecycle (commit/rollback/close) is handled externally.

    Child classes specialize this repository by binding concrete model and schema types.

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

    async def create(self, obj_data: CreateSchemaType) -> ModelType:
        """
        Persist a new entity to the database using data from a validated creation schema.

        The method converts the Pydantic schema into a model instance, persists it,
        and refreshes to obtain database-generated values (e.g., `id`, `created_at`).

        Parameters
        ----------
        obj_data : CreateSchemaType
            Validated creation payload containing all required fields for the entity.

        Returns
        -------
        ModelType
            The newly created model instance, including auto-generated fields.
        """

        db_obj = self.model(**obj_data.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
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

    async def update(self, obj_id: int, obj_data: UpdateSchemaType) -> ModelType | None:
        """
        Update an existing entity with new values from a validated update schema.

        This method assumes that the update schema contains only fields that are mutable.

        Parameters
        ----------
        obj_id : int
            Primary key of the entity to update.
        obj_data : UpdateSchemaType
            Validated update payload containing only the new values for mutable fields.

        Returns
        -------
        ModelType or None
            The updated entity if it exists; `None` if no entity matches `obj_id`.
        """
        
        db_obj = await self.get(obj_id)
        if db_obj is None:
            return None

        update_data = obj_data.model_dump()
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await self.db.commit()
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
        await self.db.commit()
        return True