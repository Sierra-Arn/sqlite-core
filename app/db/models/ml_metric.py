# app/db/models/ml_metric.py
from typing import TYPE_CHECKING
from sqlalchemy import String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

# TYPE_CHECKING is a special constant that's True during type checking but False at runtime
# This prevents circular imports by only importing these types for type checking
if TYPE_CHECKING:
    from .ml_model import MLModel


class MLMetric(Base):
    """
    Database model representing a single performance metric associated with an ML model.
    
    This class stores a single named numerical metric associated with an ML model instance. 
    Each metric is uniquely identified within the scope of its parent model via a composite uniqueness constraint.
    It also establishes a many-to-one relationship with the `MLModel` entity, 
    ensuring each metric is explicitly tied to its source model.

    Attributes
    ----------
    ml_model_id : Mapped[int]
        Foreign key referencing the `id` of the associated `MLModel`.
        Enforced as `NOT NULL` at the database level and tied to the `ml_models` table 
        with `ON DELETE CASCADE`, ensuring automatic cleanup when the parent model is removed.
    name : Mapped[str]
        Descriptive identifier for the metric type. Must be 1-32 characters long.
        Enforced as `NOT NULL` at the database level.
    value : Mapped[float]
        Numerical value of the metric at the time of recording.
        Must be a finite real number (NaN and infinity are not enforced at the DB level but
        should be validated at the application layer).
        Enforced as `NOT NULL` at the database level.
    ml_model : Mapped["MLModel"]
        Many-to-one relationship linking this metric to its parent ML model.
        Enables bidirectional navigation from metric -> model (via this attribute)
        and from model -> metrics (via `ml_model.ml_metrics`).

    Notes
    -----
    - A composite unique constraint (`uix_model_metric`) ensures that a given metric name
    (e.g., `accuracy`) can appear at most once per model, preventing accidental duplication
    while allowing the same metric name across different models.

    - The relationship to MLModel is lazy-loaded by default (per SQLAlchemy conventions).
    When querying metrics in bulk, explicitly join the ml_model relationship.
    """

    __tablename__ = 'ml_metrics'
    __table_args__ = (UniqueConstraint('ml_model_id', 'name', name = 'uix_model_metric'),)
    
    ml_model_id: Mapped[int] = mapped_column(
        ForeignKey("ml_models.id", ondelete='CASCADE'),
        nullable = False,
        comment = "Primary key identifier of the ML model"
    )
    
    name: Mapped[str] = mapped_column(
        String(32),
        nullable = False,
        comment = "Metric name (e.g., accuracy, f1_score)"
    )
    
    value: Mapped[float] = mapped_column(
        Float,
        nullable = False,
        comment = "Numerical value of the metric"
    )
    
    ml_model: Mapped["MLModel"] = relationship(
        back_populates = "ml_metrics"
    )