# app/db/schemas/ml_model.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from ..models import DeviceType


class MLModelRequestCreate(BaseModel):
    """Request schema for registering a new machine learning model via the REST API."""

    name: str = Field(
        ...,
        min_length = 1,
        max_length = 32,
        description = (
            "Unique identifier for the ML model. Must be 1-32 characters long."
        )
    )

    device: DeviceType = Field(
        ...,
        description = (
            "Target inference device where the model is expected to run. "
            "Valid values are `CPU` or `CUDA`. "
        )
    )

    model_config = ConfigDict(
        extra = "forbid",
        json_schema_extra = {
            "examples": [
                {
                    "name": "stub_model_v1",
                    "device": "CPU"
                },
                {
                    "name": "sapiens_pose",
                    "device": "CUDA"
                }
            ]
        }
    )


class MLModelRequestUpdate(BaseModel):
    """
    Request schema for updating mutable metadata of an existing ML model via the REST API.

    The model's `name` is its immutable unique identifier. It cannot be changed, because altering
    a unique identifier is logically equivalent to creating a new entity. That's why if a model needs a different
    name or identity, I force explicit deletion of the old model and creation of a new one.
    This ensures clarity and prevents ambiguous references.

    The only updatable field is the target inference device, which is a non-identifying property.

    Notes
    -----
    The model identifier is not included in this schema, as it is passed in the URL path 
    in accordance with RESTful design principles. The request body contains only the fields to be modified.
    """

    device: DeviceType = Field(
        ...,
        description=(
            "New target inference device (`CPU` or `CUDA`)."
        )
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "device": "CUDA"
                },
                {
                    "device": "CPU"
                }
            ]
        }
    )


class MLModelResponse(BaseModel):
    """
    Response schema representing a fully hydrated machine learning model entity.

    This schema is used to serialize an `MLModel` ORM instance for API responses.
    It includes both user-provided fields and system-managed metadata.
    """

    id: int = Field(
        ...,
        description="Unique surrogate identifier assigned by the database."
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Unique business identifier for the ML model."
    )

    device: DeviceType = Field(
        ...,
        description="Target inference device where the model is expected to run (`CPU` or `CUDA`)."
    )

    created_at: datetime = Field(
        ...,
        description="Timestamp when the model record was first created in the database."
    )

    updated_at: datetime = Field(
        ...,
        description="Timestamp when the model record was last modified."
    )

    model_config = ConfigDict(
        # Key setting for working with ORM objects
        from_attributes=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "sapiens_pose",
                    "device": "CUDA",
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z"
                }
            ]
        }
    )