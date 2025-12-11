# app/db/sync_db/repositories/ml_metric.py
from sqlalchemy import select
from sqlalchemy.orm import Session
from .base import BaseRepository
from ...models import MLMetric
from ...schemas import MLMetricRequestCreate, MLMetricRequestUpdate


class MLMetricRepository(BaseRepository[MLMetric, MLMetricRequestCreate, MLMetricRequestUpdate]):
    """
    Concrete repository for managing `MLMetric` entity in the database.
    This class extends the generic `BaseRepository` with model-specific functionality.

    Attributes
    ----------
    db : Session
        Active SQLAlchemy session inherited from the base repository.
    model : Type[MLMetric]
        Bound to the `MLMetric` ORM class at initialization.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the ML metric repository with a database session.

        Parameters
        ----------
        db : Session
            Active SQLAlchemy session providing transactional context.
            Typically injected via a dependency (e.g., FastAPI) or context manager.
        """

        super().__init__(db, MLMetric)

    def get_by_model_id_and_name(self, model_id: int, metric_name: str) -> MLMetric | None:
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

        Notes
        -----
        Unlike `get(id)`, this method is not used for updates or deletions via primary key,
        but is essential for metric registration validation (e.g., ensuring no duplicate identificators on create).
        """
        
        stmt = select(MLMetric).where(
            MLMetric.ml_model_id == model_id,
            MLMetric.name == metric_name
        )
        return self.db.execute(stmt).scalar_one_or_none()