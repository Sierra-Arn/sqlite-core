# app/db/schemas/ml_model.py
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