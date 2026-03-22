# app/db/async_db/services/ml_model.py
from typing import Type
from .base import BaseService
from ..session import get_async_db_session
from ..repositories import MLModelRepository
from ...models import MLModel
from ...schemas import MLModelRequestCreate, MLModelRequestUpdate, MLModelResponse


class MLModelService(
    BaseService[MLModel, MLModelRequestCreate, MLModelRequestUpdate, MLModelResponse, MLModelRepository]
):
    """
    Business service for managing `MLModel` entities with strict enforcement of domain invariants (async version).

    This service ensures that:
        - Model names are globally unique (immutable business identifiers),
        - No two models can share the same name, even across different devices,
        - Creation attempts with duplicate names are rejected early with a clear error.
    """

    @property
    def repository_class(self) -> Type[MLModelRepository]:
        """
        Return the repository class responsible for `MLModel` data access.

        Returns
        -------
        Type[MLModelRepository]
            The repository class bound to this service.
        """
        return MLModelRepository

    @property
    def read_schema_class(self) -> Type[MLModelResponse]:
        """
        Return the Pydantic schema class for serializing `MLModel` entities.

        Returns
        -------
        Type[MLModelResponse]
            The schema class used for read operations.
        """
        return MLModelResponse

    async def get(
        self,
        obj_id: int,
        load_metrics: bool = False,
    ) -> MLModelResponse | None:
        """
        Retrieve an ML model by its primary key.

        Parameters
        ----------
        obj_id : int
            The unique identifier of the ML model.
        load_metrics : bool, optional
            If True, eagerly load associated metrics. Default is False.

        Returns
        -------
        MLModelResponse or None
            The model serialized as a Pydantic schema if found; `None` otherwise.
        """
        async with get_async_db_session() as db:
            repository = self.repository_class(db)
            obj = await repository.get(obj_id, load_metrics=load_metrics)
            return self.read_schema_class.model_validate(obj) if obj is not None else None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        load_metrics: bool = False,
    ) -> list[MLModelResponse]:
        """
        Retrieve a paginated list of all ML models.

        Parameters
        ----------
        skip : int, optional
            Number of records to skip (offset). Default is ``0``.
        limit : int, optional
            Maximum number of records to return. Default is ``100``.
        load_metrics : bool, optional
            If True, eagerly load associated metrics for each model. Default is False.

        Returns
        -------
        list[MLModelResponse]
            A list of ML models, up to ``limit`` in size, each serialized as a Pydantic schema.
        """
        async with get_async_db_session() as db:
            repository = self.repository_class(db)
            objs = await repository.get_all(skip=skip, limit=limit, load_metrics=load_metrics)
            return [self.read_schema_class.model_validate(obj) for obj in objs]

    async def _validate_create(
        self,
        obj_data: MLModelRequestCreate,
        repository: MLModelRepository,
    ) -> None:
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
        existing_model = await repository.get_by_name(obj_data.name)
        if existing_model is not None:
            raise ValueError(f"ML model with name '{obj_data.name}' already exists")