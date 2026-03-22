# app/db/schemas/ml_metric.py
import math
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .base import IDMixin, TimestampMixin


class MLMetricBaseMixin(BaseModel):
    """
    Mixin providing core identity fields for ML metric schemas.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Unique identifier for the ML model metric. Must be 1-32 characters long."
    )

    ml_model_id: int = Field(
        ...,
        description="ID of the associated ML model. Must reference an existing model in the registry."
    )


class ValueMixin:
    """
    Mixin providing a finite float value field.
    """

    value: float = Field(
        ...,
        description = (
            "Numerical value of the metric. Must be a finite real number."
        )
    )

    @field_validator("value")
    @classmethod
    def value_must_be_finite(cls, v: float) -> float:
        if math.isnan(v):
            raise ValueError("Metric value must not be NaN")
        if math.isinf(v):
            raise ValueError("Metric value must not be infinite")
        return v


class MLMetricRequestCreate(MLMetricBaseMixin, ValueMixin, BaseModel):
    """Request schema for registering a new performance metric for an ML model via the REST API."""

    model_config = ConfigDict(
        extra = "forbid",
        json_schema_extra = {
            "examples": [
                {
                    "name": "accuracy",
                    "value": 0.95,
                    "ml_model_id": 1
                },
                {
                    "name": "f1_score",
                    "value": 0.876,
                    "ml_model_id": 5
                }
            ]
        }
    )


class MLMetricRequestUpdate(ValueMixin, BaseModel):
    """
    Request schema for updating the numerical value of an existing ML metric via the REST API.

    A metric's identity is defined by the combination of its `name` and `ml_model_id` — this pair
    forms a unique key in the system. Neither component can be changed, because altering
    a unique identifier is logically equivalent to creating a new entity. That's why if a metric needs a different
    identity, I force explicit deletion of the old metric and creation of a new one.
    This ensures clarity and prevents ambiguous references.

    The only updatable field is the value, which is a non-identifying property.

    Notes
    -----
    The model identifier is not included in this schema, as it is passed in the URL path 
    in accordance with RESTful design principles. The request body contains only the fields to be modified.
    """

    model_config = ConfigDict(
        extra = "forbid",
        json_schema_extra = {
            "examples": [
                {
                    "value": 0.96
                },
                {
                    "value": 45.2
                }
            ]
        }
    )


class MLMetricResponse(IDMixin, TimestampMixin, MLMetricBaseMixin, ValueMixin, BaseModel):
    """
    Response schema representing a fully hydrated machine learning performance metric.

    This schema is used to serialize an `MLMetric` ORM instance for API responses.
    It includes both user-provided fields and system-managed metadata.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "accuracy",
                    "value": 0.95,
                    "ml_model_id": 1,
                    "created_at": "2026-01-23T10:00:00Z",
                    "updated_at": "2026-01-23T10:00:00Z"
                },
                {
                    "id": 2,
                    "name": "f1_score",
                    "value": 0.876,
                    "ml_model_id": 5,
                    "created_at": "2026-01-23T11:30:00Z",
                    "updated_at": "2026-01-23T11:30:00Z"
                }
            ]
        }
    )