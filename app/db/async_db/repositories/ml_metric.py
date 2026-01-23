# app/db/async_db/repositories/ml_metric.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from ...models import MLMetric


class MLMetricRepository(BaseRepository[MLMetric]):
    """
    Concrete repository for managing `MLMetric` entity in the database (async version).
    This class extends the generic `BaseRepository` with model-specific functionality.

    Attributes
    ----------
    db : AsyncSession
        Active SQLAlchemy asynchronous session inherited from the base repository.
    model : Type[MLMetric]
        Bound to the `MLMetric` ORM class at initialization.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the ML metric repository with a database session.

        Parameters
        ----------
        db : AsyncSession
            Active SQLAlchemy asynchronous session providing transactional context.
        """

        super().__init__(db=db, model=MLMetric)

    async def get_by_model_id_and_name(self, model_id: int, metric_name: str) -> MLMetric | None:
        """
        Retrieve an ML metric by its unique pair of `(model_id, metric_name)`, immutable business identifier.

        Parameters
        ----------
        model_id : int
            Primary key of the associated ML model.
        metric_name : str
            Name of the metric (e.g., `"accuracy"`, `"f1_score"`).

        Returns
        -------
        MLMetric or None
            The metric instance if found; `None` if no such metric exists for the given model.
        """
        
        stmt = select(MLMetric).where(
            MLMetric.ml_model_id == model_id,
            MLMetric.name == metric_name
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()