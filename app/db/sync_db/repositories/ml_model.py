# app/db/sync_db/repositories/ml_model.py
from sqlalchemy import select
from sqlalchemy.orm import Session
from .base import BaseRepository
from ...models import MLModel


class MLModelRepository(BaseRepository[MLModel]):
    """
    Concrete repository for managing `MLModel` entity in the database. 
    This class extends the generic `BaseRepository` with model-specific functionality.

    Attributes
    ----------
    db : Session
        Active SQLAlchemy session inherited from the base repository.
    model : Type[MLModel]
        Bound to the `MLModel` ORM class at initialization.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the ML model repository with a database session.

        Parameters
        ----------
        db : Session
            Active SQLAlchemy session providing transactional context.
            Typically injected via a dependency (e.g., FastAPI) or context manager.
        """
        
        super().__init__(db = db, model = MLModel)

    def get_by_name(self, name: str) -> MLModel | None:
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

        Notes
        -----
        Unlike `get(id)`, this method is not used for updates or deletions via primary key,
        but is essential for registration validation (e.g., ensuring no duplicate names on create).
        """
        
        stmt = select(MLModel).where(MLModel.name == name)
        return self.db.execute(stmt).scalar_one_or_none()