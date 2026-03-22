# app/db/async_db/repositories/ml_model.py
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload, noload
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from ...models import MLModel


class MLModelRepository(BaseRepository[MLModel]):
    """
    Concrete repository for managing `MLModel` entity in the database (async version).
    This class extends the generic `BaseRepository` with model-specific functionality.

    Attributes
    ----------
    db : AsyncSession
        Active SQLAlchemy asynchronous session inherited from the base repository.
    model : Type[MLModel]
        Bound to the `MLModel` ORM class at initialization.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the ML model repository with a database session.

        Parameters
        ----------
        db : AsyncSession
            Active SQLAlchemy asynchronous session providing transactional context.
        """
        super().__init__(db=db, model=MLModel)

    async def create(self, obj_data: dict[str, Any]) -> MLModel:
        """
        Persist a new ML model to the database.

        Parameters
        ----------
        obj_data : dict[str, Any]
            Dictionary containing all required fields for the entity.

        Returns
        -------
        MLModel
            The newly created model instance, including auto-generated fields
            and an explicitly loaded (empty) ``ml_metrics`` collection.
        """
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        await self.db.flush()

        # Refresh with explicit attribute_names=["ml_metrics"] to eagerly load
        # the relationship alongside the standard column refresh.
        # Without this, ml_metrics remains in an unloaded state — any subsequent
        # synchronous access (e.g., Pydantic's model_validate) would trigger a
        # lazy load through SQLAlchemy's greenlet mechanism, resulting in
        # MissingGreenlet since Pydantic cannot call await internally.
        # For a newly created model this will always return an empty list [].
        await self.db.refresh(db_obj, attribute_names=["ml_metrics"])

        return db_obj

    async def get(
        self,
        obj_id: int,
        load_metrics: bool = False,
    ) -> MLModel | None:
        """
        Retrieve an ML model by its primary key.

        Uses eager loading — relationships are loaded explicitly within the same
        database round-trip, unlike lazy loading where they are fetched on first
        access. 

        ``selectinload`` issues a separate ``SELECT ... WHERE id IN (...)`` query
        to fetch all related metrics at once. ``noload`` explicitly marks the
        relationship as empty without any query, preventing accidental lazy access.

        Parameters
        ----------
        obj_id : int
            The unique identifier of the ML model to retrieve.
        load_metrics : bool, optional
            If True, eagerly load associated metrics via a separate SELECT IN query.
            If False, metrics are explicitly not loaded. Default is False.

        Returns
        -------
        MLModel or None
            The model instance if found; `None` if no record exists with the given ID.
        """
        stmt = select(MLModel).where(MLModel.id == obj_id)

        if load_metrics:
            stmt = stmt.options(selectinload(MLModel.ml_metrics))
        else:
            stmt = stmt.options(noload(MLModel.ml_metrics))

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        load_metrics: bool = False,
    ) -> list[MLModel]:
        """
        Retrieve a paginated list of all ML models.

        Uses eager loading — relationships are loaded explicitly within the same
        database round-trip, unlike lazy loading where they are fetched on first
        access.

        ``selectinload`` issues a separate ``SELECT ... WHERE id IN (...)`` query
        to fetch all related metrics at once. ``noload`` explicitly marks the
        relationship as empty without any query, preventing accidental lazy access.

        Parameters
        ----------
        skip : int, optional
            Number of records to skip (for pagination offset). Default is ``0``.
        limit : int, optional
            Maximum number of records to return. Default is ``100``.
        load_metrics : bool, optional
            If True, eagerly load associated metrics via a separate SELECT IN query.
            If False, metrics are explicitly not loaded. Default is False.

        Returns
        -------
        list[MLModel]
            A list of up to ``limit`` ML model instances, starting after ``skip`` records.
        """
        stmt = select(MLModel).offset(skip).limit(limit)

        if load_metrics:
            stmt = stmt.options(selectinload(MLModel.ml_metrics))
        else:
            stmt = stmt.options(noload(MLModel.ml_metrics))

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> MLModel | None:
        """
        Retrieve an ML model by its unique name, immutable business identifier.

        Parameters
        ----------
        name : str
            The unique name of the ML model (e.g., `"sapiens_pose_v2"`).
            Must exactly match a registered model name.

        Returns
        -------
        MLModel or None
            The model instance if found; `None` if no model with the given name exists.
        """
        stmt = select(MLModel).where(MLModel.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()