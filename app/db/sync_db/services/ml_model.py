# app/db/sync_db/services/ml_model.py
from typing import Type
from .base import BaseService
from ..repositories import MLModelRepository
from ...models import MLModel
from ...schemas import MLModelRequestCreate, MLModelRequestUpdate


class MLModelService(BaseService[MLModel, MLModelRequestCreate, MLModelRequestUpdate, MLModelRepository]):
    """
    Business service for managing `MLModel` entities with strict enforcement of domain invariants.

    This service ensures that:
        - Model names are globally unique (immutable business identifiers),
        - No two models can share the same name, even across different devices,
        - Creation attempts with duplicate names are rejected early with a clear error.

    Attributes
    ----------
    repository_class : Type[MLModelRepository]
        Returns the repository responsible for `MLModel` data access.
    """

    @property
    def repository_class(self) -> Type[MLModelRepository]:
        """Return the repository class used for ML model data operations."""
        return MLModelRepository

    def _validate_create(self, obj_data: MLModelRequestCreate, repository: MLModelRepository) -> None:
        """
        Enforce uniqueness of the model name across the entire registry.

        Since `name` serves as the immutable business identifier, duplicate names
        would violate the system's ability to unambiguously reference models.
        This validation prevents such conflicts at creation time.

        Parameters
        ----------
        obj_data : MLModelRequestCreate
            The validated creation payload containing the proposed model name.
        repository : MLModelRepository
            An active repository instance for performing lookup operations.

        Raises
        ------
        ValueError
            If a model with the same `name` already exists in the database.
        """
        
        existing_model = repository.get_by_name(obj_data.name)
        if existing_model is not None:
            raise ValueError(f"ML model with name '{obj_data.name}' already exists")