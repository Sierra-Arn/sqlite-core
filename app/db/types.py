# app/db/types.py
from typing import TypeVar
from pydantic import BaseModel
from .models import Base


ModelType = TypeVar("ModelType", bound = Base)
"""
Generic type variable representing any SQLAlchemy ORM model that inherits from `Base`.

Notes
-----
This type variable enables a type-safe generic repository pattern:
- Repository or service classes can be written once and reused across different models.
- Static type checkers can infer correct input/output types.
- Refactoring and maintenance become safer and more predictable.
- The `bound = Base` constraint ensures that only valid ORM models (i.e., subclasses of the application's declarative base) 
can be substituted for this type parameter.
"""


CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
"""
Generic type variable representing any Pydantic model used for creating new entities.

Notes
-----
This type variable enables a type-safe generic repository pattern:
- Repository or service classes can be written once and reused across different models.
- Static type checkers can infer correct input/output types.
- Refactoring and maintenance become safer and more predictable.
- The `bound = BaseModel` constraint guarantees compatibility with Pydantic's validation,
serialization, and schema generation features.
"""


UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
"""
Generic type variable representing any Pydantic model used for updating existing entities.

Notes
-----
This type variable enables a type-safe generic repository pattern:
- Repository or service classes can be written once and reused across different models.
- Static type checkers can infer correct input/output types.
- Refactoring and maintenance become safer and more predictable.
- The `bound = BaseModel` constraint guarantees compatibility with Pydantic's validation,
serialization, and schema generation features.
"""