# app/db/sync_db/services/base.py
from typing import TypeVar, Generic, Type
from abc import ABC, abstractmethod
from ..session import get_sync_db_session
from ..repositories import BaseRepository
from ...types import ModelType, CreateSchemaType, UpdateSchemaType, ReadSchemaType


# Generic type variables with bounds to enforce architectural constraints
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, ReadSchemaType, RepositoryType],
    ABC
):
    """
    Abstract base service encapsulating standardized business logic patterns.

    This class provides a consistent interface for CRUD operations while enforcing:
        - Automatic database session management (via context manager),
        - Separation of concerns between business rules (service) and data access (repository),
        - Mandatory binding to a repository via the abstract `repository_class` property,
        - Mandatory binding to a read schema via the abstract `read_schema_class` property,
        - Direct conversion of ORM models to Pydantic read schemas using `model_validate`,
        - Extensible validation and post-processing via template hooks.

    Each concrete service **must** implement two abstract properties:
        - `repository_class`: Returns the repository type associated with this service,
        - `read_schema_class`: Returns the Pydantic schema type for read operations.

    The service assumes that:
        - All input data is pre-validated by Pydantic schemas,
        - Repository methods handle data persistence using plain dictionaries (not Pydantic objects),
        - Business rules (e.g., cross-field validation, state transitions) are implemented in hooks,
        - The `ReadSchemaType` is a Pydantic model with `model_config.from_attributes = True`.
    """

    @property
    @abstractmethod
    def repository_class(self) -> Type[RepositoryType]:
        """
        Return the repository class associated with this service.

        This property must be implemented by all concrete service subclasses.
        It defines which repository handles data persistence for this service.

        Returns
        -------
        Type[RepositoryType]
            The repository class bound to this service.
        """
        pass

    @property
    @abstractmethod
    def read_schema_class(self) -> Type[ReadSchemaType]:
        """
        Return the Pydantic schema class for read operations.

        This property must be implemented by all concrete service subclasses.
        It defines the schema used to serialize ORM objects into response models.

        Returns
        -------
        Type[ReadSchemaType]
            The Pydantic schema class used for serializing entities.
        """
        pass

    def create(self, obj_data: CreateSchemaType) -> ReadSchemaType:
        """
        Create a new entity with optional pre- and post-creation business logic.

        The method acquires a database session, invokes custom validation, delegates to the repository
        using a dictionary representation of the input schema, commits the transaction,
        and converts the resulting ORM object to a Pydantic read schema using `model_validate`.

        Parameters
        ----------
        obj_data : CreateSchemaType
            Validated creation payload containing all required fields.

        Returns
        -------
        ReadSchemaType
            The newly created and fully hydrated entity, including auto-generated fields,
            serialized as a Pydantic response schema.

        Raises
        ------
        ValueError
            If custom business validation fails.
        """

        with get_sync_db_session() as db:
            repository = self.repository_class(db)
            self._validate_create(obj_data, repository)
            orm_obj = repository.create(obj_data.model_dump())
            self._after_create(orm_obj, repository)
            db.commit()
            return self.read_schema_class.model_validate(orm_obj)

    def get(self, obj_id: int) -> ReadSchemaType | None:
        """
        Retrieve an entity by its primary key and return it as a read schema.

        Parameters
        ----------
        obj_id : int
            The unique identifier of the entity.

        Returns
        -------
        ReadSchemaType or None
            The entity serialized as a Pydantic schema if found; `None` otherwise.
        """

        with get_sync_db_session() as db:
            repository = self.repository_class(db)
            obj = repository.get(obj_id)
            return self.read_schema_class.model_validate(obj) if obj is not None else None

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ReadSchemaType]:
        """
        Retrieve a paginated list of all entities, serialized as read schemas.

        Parameters
        ----------
        skip : int, optional
            Number of records to skip (offset). Default is `0`.
        limit : int, optional
            Maximum number of records to return. Default is `100`.

        Returns
        -------
        list[ReadSchemaType]
            A list of entities, up to `limit` in size, each serialized as a Pydantic schema.
        """
        
        with get_sync_db_session() as db:
            repository = self.repository_class(db)
            objs = repository.get_all(skip=skip, limit=limit)
            return [self.read_schema_class.model_validate(obj) for obj in objs]

    def update(self, obj_id: int, obj_data: UpdateSchemaType) -> ReadSchemaType | None:
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
        ReadSchemaType or None
            The updated entity serialized as a Pydantic schema if it exists; `None` if not found.

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
            update_dict = obj_data.model_dump(exclude_unset=True)
            updated_obj = repository.update(obj_id, update_dict)
            if updated_obj is not None:
                self._after_update(updated_obj, repository)
                db.commit()
                return self.read_schema_class.model_validate(updated_obj)
            return None

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
                db.commit()
            return result

    # Template hooks: concrete services override only what they need

    def _validate_create(self, obj_data: CreateSchemaType, repository: RepositoryType) -> None:
        """
        Override to add custom validation logic before entity creation.

        Parameters
        ----------
        obj_data : CreateSchemaType
            The validated creation payload.
        repository : RepositoryType
            The repository instance for potential data access during validation.

        Raises
        ------
        ValueError
            If validation fails.
        """
        pass

    def _after_create(self, created_obj: ModelType, repository: RepositoryType) -> None:
        """
        Override to add custom logic after entity creation (e.g., emit event, update related entities).

        Parameters
        ----------
        created_obj : ModelType
            The newly created ORM object.
        repository : RepositoryType
            The repository instance for potential follow-up operations.
        """
        pass

    def _validate_update(self, obj_id: int, obj_data: UpdateSchemaType, existing_obj: ModelType, repository: RepositoryType) -> None:
        """
        Override to add custom validation logic before entity update.

        Parameters
        ----------
        obj_id : int
            Primary key of the entity being updated.
        obj_data : UpdateSchemaType
            The validated update payload.
        existing_obj : ModelType
            The current state of the entity before update.
        repository : RepositoryType
            The repository instance for potential data access during validation.

        Raises
        ------
        ValueError
            If validation fails.
        """
        pass

    def _after_update(self, updated_obj: ModelType, repository: RepositoryType) -> None:
        """
        Override to add custom logic after entity update.

        Parameters
        ----------
        updated_obj : ModelType
            The updated ORM object with new values.
        repository : RepositoryType
            The repository instance for potential follow-up operations.
        """
        pass

    def _validate_delete(self, obj_id: int, existing_obj: ModelType, repository: RepositoryType) -> None:
        """
        Override to add custom validation logic before entity deletion.

        Parameters
        ----------
        obj_id : int
            Primary key of the entity being deleted.
        existing_obj : ModelType
            The current state of the entity before deletion.
        repository : RepositoryType
            The repository instance for potential data access during validation.

        Raises
        ------
        ValueError
            If validation fails (e.g., entity has dependent relationships).
        """
        pass

    def _after_delete(self, obj_id: int, deleted_obj: ModelType, repository: RepositoryType) -> None:
        """
        Override to add custom logic after entity deletion (e.g., cleanup, cascade operations).

        Parameters
        ----------
        obj_id : int
            Primary key of the deleted entity.
        deleted_obj : ModelType
            The state of the entity before it was deleted.
        repository : RepositoryType
            The repository instance for potential follow-up operations.
        """
        pass