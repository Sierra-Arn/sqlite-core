# app/db/sync_db/services/base.py
from typing import TypeVar, Generic, Type
from abc import ABC, abstractmethod
from ..session import get_sync_db_session
from ..repositories import BaseRepository
from ...types import ModelType, CreateSchemaType, UpdateSchemaType


# Generic type variables with bounds to enforce architectural constraints
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, RepositoryType], ABC):
    """
    Abstract base service encapsulating standardized business logic patterns.

    This class provides a consistent interface for CRUD operations while enforcing:
        - Automatic database session management (via context manager),
        - Separation of concerns between business rules (service) and data access (repository),
        - Extensible validation and post-processing via template hooks.

    Each concrete service is bound to a specific repository type, ensuring type safety
    and eliminating runtime misconfiguration. The service assumes that:
        - All input data is pre-validated by Pydantic schemas,
        - Repository methods handle data persistence and constraints,
        - Business rules (e.g., cross-field validation, state transitions) are implemented in hooks.

    Attributes
    ----------
    repository_class : Type[RepositoryType]
        The repository class responsible for data access. Must be provided by concrete subclasses.
    """

    @property
    @abstractmethod
    def repository_class(self) -> Type[RepositoryType]:
        """
        Return the repository class associated with this service.

        This property replaces a traditional dependency injection constructor to:
            - Enforce a fixed, compile-time binding between service and repository,
            - Eliminate boilerplate in service instantiation (e.g., `MLModelService()` vs `MLModelService(repo_class)`),
            - Provide strong static typing guarantees,
            - Align with the principle that a service intrinsically "knows" its data layer.

        Concrete services must implement this property to return their specific repository type.
        """
        pass

    def create(self, obj_data: CreateSchemaType) -> ModelType:
        """
        Create a new entity with optional pre- and post-creation business logic.

        The method acquires a database session, invokes custom validation, delegates to the repository,
        and ensures session cleanup. It assumes the input schema is already validated by Pydantic.

        Parameters
        ----------
        obj_data : CreateSchemaType
            Validated creation payload containing all required fields.

        Returns
        -------
        ModelType
            The newly created and fully hydrated entity, including auto-generated fields.

        Raises
        ------
        ValueError
            If custom business validation fails.
        """
        
        with get_sync_db_session() as db:
            repository = self.repository_class(db)
            self._validate_create(obj_data, repository)
            created_obj = repository.create(obj_data)
            self._after_create(created_obj, repository)
            return created_obj

    def get(self, obj_id: int) -> ModelType | None:
        """
        Retrieve an entity by its primary key.

        Parameters
        ----------
        obj_id : int
            The unique identifier of the entity.

        Returns
        -------
        ModelType or None
            The entity if found; `None` otherwise.
        """
        
        with get_sync_db_session() as db:
            repository = self.repository_class(db)
            return repository.get(obj_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        Retrieve a paginated list of all entities.

        Parameters
        ----------
        skip : int, optional
            Number of records to skip (offset). Default is `0`.
        limit : int, optional
            Maximum number of records to return. Default is `100`.

        Returns
        -------
        list[ModelType]
            A list of entities, up to `limit` in size.
        """
        
        with get_sync_db_session() as db:
            repository = self.repository_class(db)
            return repository.get_all(skip=skip, limit=limit)

    def update(self, obj_id: int, obj_data: UpdateSchemaType) -> ModelType | None:
        """
        Update an existing entity with optional pre- and post-update business logic.

        Because update schemas contain only mutable, non-identifying fields,
        all provided values are applied unconditionally. The method first verifies
        that the entity exists before proceeding.

        Parameters
        ----------
        obj_id : int
            Primary key of the entity to update.
        obj_data : UpdateSchemaType
            Validated update payload containing new values for mutable fields.

        Returns
        -------
        ModelType or None
            The updated entity if it exists; `None` if not found.

        Raises
        ------
        ValueError
            If custom validation fails.
        """

        with get_sync_db_session() as db:
            repository = self.repository_class(db)
            existing_obj = repository.get(obj_id)
            if existing_obj is None:
                return None

            self._validate_update(obj_id, obj_data, existing_obj, repository)
            updated_obj = repository.update(obj_id, obj_data)
            if updated_obj is not None:
                self._after_update(updated_obj, repository)
            return updated_obj

    def delete(self, obj_id: int) -> bool:
        """
        Delete an entity by its primary key with optional pre- and post-deletion logic.

        Parameters
        ----------
        obj_id : int
            Primary key of the entity to delete.

        Returns
        -------
        bool
            `True` if the entity was found and deleted; `False` if not found.

        Raises
        ------
        ValueError
            If custom validation fails.
        """

        with get_sync_db_session() as db:
            repository = self.repository_class(db)
            existing_obj = repository.get(obj_id)
            if existing_obj is None:
                return False

            self._validate_delete(obj_id, existing_obj, repository)
            result = repository.delete(obj_id)
            if result:
                self._after_delete(obj_id, existing_obj, repository)
            return result

    # Template hooks: concrete services override only what they need

    def _validate_create(self, obj_data: CreateSchemaType, repository: RepositoryType) -> None:
        """Override to add custom validation before creation."""
        pass

    def _after_create(self, created_obj: ModelType, repository: RepositoryType) -> None:
        """Override to add custom validation after creation."""
        pass

    def _validate_update(self, obj_id: int, obj_data: UpdateSchemaType, existing_obj: ModelType, repository: RepositoryType) -> None:
        """Override to add custom validation before update."""
        pass

    def _after_update(self, updated_obj: ModelType, repository: RepositoryType) -> None:
        """Override to add custom validation update."""
        pass

    def _validate_delete(self, obj_id: int, existing_obj: ModelType, repository: RepositoryType) -> None:
        """Override to add custom validation before deletion."""
        pass

    def _after_delete(self, obj_id: int, deleted_obj: ModelType, repository: RepositoryType) -> None:
        """Override to add custom validation deletion."""
        pass