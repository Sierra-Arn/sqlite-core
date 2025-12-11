# app/db/schemas/ml_metric.py
import math
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MLMetricRequestCreate(BaseModel):
    """Request schema for registering a new performance metric for an ML model via the REST API."""

    name: str = Field(
        ...,
        min_length = 1,
        max_length = 32,
        description = (
            "Name of the metric. Must be 1-32 characters long."
        )
    )

    value: float = Field(
        ...,
        description = (
            "Numerical value of the metric. Must be a finite real number."
        )
    )

    ml_model_id: int = Field(
        ...,
        description = "ID of the associated ML model. Must reference an existing model in the registry."
    )

    @field_validator("value")
    @classmethod
    def value_must_be_finite(cls, v: float) -> float:
        if math.isnan(v):
            raise ValueError("Metric value must not be NaN")
        if math.isinf(v):
            raise ValueError("Metric value must not be infinite")
        return v

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


class MLMetricRequestUpdate(BaseModel):
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

    value: float = Field(
        ...,
        description = (
            "New numerical value of the metric. Must be a finite real number."
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