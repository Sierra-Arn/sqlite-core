# app/db/async_db/services/ml_metric.py
from typing import Type
from .base import BaseService
from ...models import MLMetric
from ...schemas import MLMetricRequestCreate, MLMetricRequestUpdate, MLMetricResponse
from ..repositories import MLMetricRepository, MLModelRepository


class MLMetricService(
    BaseService[MLMetric, MLMetricRequestCreate, MLMetricRequestUpdate, MLMetricResponse, MLMetricRepository]
):
    """
    Business service for managing `MLMetric` entities with referential integrity enforcement (async version).

    This service ensures that:
        - Every metric is associated with an existing `MLModel`,
        - The composite identity `(ml_model_id, name)` remains consistent with the database constraint,
        - Orphaned or dangling metrics cannot be created.
    """

    @property
    def repository_class(self) -> Type[MLMetricRepository]:
        """
        Return the repository class responsible for `MLMetric` data access.

        Returns
        -------
        Type[MLMetricRepository]
            The repository class bound to this service.
        """
        return MLMetricRepository

    @property
    def read_schema_class(self) -> Type[MLMetricResponse]:
        """
        Return the Pydantic schema class for serializing `MLMetric` entities.

        Returns
        -------
        Type[MLMetricResponse]
            The schema class used for read operations.
        """
        return MLMetricResponse

    async def _validate_create(self, obj_data: MLMetricRequestCreate, repository: MLMetricRepository) -> None:
        """
        Enforce referential integrity and uniqueness constraints before metric creation.

        Parameters
        ----------
        obj_data : MLMetricRequestCreate
            The validated creation payload containing `ml_model_id`.
        repository : MLMetricRepository
            An active repository instance (provides access to the shared async session via `repository.db`).

        Raises
        ------
        ValueError
            - If no `MLModel` exists with the provided `ml_model_id`, or
            - If a metric with the same `name` already exists for the specified model.
        """

        model_repo = MLModelRepository(repository.db)
        ml_model = await model_repo.get(obj_data.ml_model_id)
        if ml_model is None:
            raise ValueError(f"ML model with ID {obj_data.ml_model_id} does not exist")
        
        existing_metric = await repository.get_by_model_id_and_name(
            model_id=obj_data.ml_model_id,
            metric_name=obj_data.name
        )
        if existing_metric is not None:
            raise ValueError(
                f"Metric with name '{obj_data.name}' already exists for model ID {obj_data.ml_model_id}"
            )