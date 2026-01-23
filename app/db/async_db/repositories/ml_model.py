# app/db/async_db/repositories/ml_model.py
from sqlalchemy import select
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