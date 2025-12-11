# app/db/models/ml_model.py
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .types import DeviceType, DeviceTypeSQL

# TYPE_CHECKING is a special constant that's True during type checking but False at runtime
# This prevents circular imports by only importing these types for type checking
if TYPE_CHECKING:
    from .ml_metric import MLMetric


class MLModel(Base):
    """
    Database model representing a registered machine learning model in the system.

    This class stores metadata about an ML model instance, including its unique identifier,
    target inference device, and associated performance metrics. It also establishes
    a one-to-many relationship with the `MLMetric` entity.

    Attributes
    ----------
    name : Mapped[str]
        Unique, human-readable identifier for the ML model. Must be 1-32 characters long. 
        Enforced as `UNIQUE` and `NOT NULL` at the database level.
    device : Mapped[DeviceType]
        Target device where the model is intended to run.
        Enforced as `NOT NULL` at the database level.
    ml_metrics : Mapped[list["MLMetric"]]
        Collection of performance and diagnostic metrics associated with this model.
        Managed via a one-to-many relationship with the `MLMetric` table.
        Configured with `cascade="all, delete-orphan"` to ensure that when an `MLModel`
        is deleted, all its dependent metrics are automatically removed from the database,
        preserving referential integrity.

    Notes
    -----
    The relationship to `MLMetric` is loaded lazily by default (per SQLAlchemy conventions).
    When querying metrics in bulk, explicitly join the ml_model relationship.
    """

    __tablename__ = 'ml_models'
        
    name: Mapped[str] = mapped_column(
        String(32),
        nullable = False,
        unique = True,
        comment = "ML model name (e.g., stub_model_v1, sapiens_pose)"
    )
    
    device: Mapped[DeviceType] = mapped_column(
        DeviceTypeSQL,
        nullable = False,
        comment = "Computation device target for model inference and tensor operations (e.g., CPU, CUDA)." 
    )
    
    ml_metrics: Mapped[list["MLMetric"]] = relationship(
        "MLMetric",
        back_populates = "ml_model",
        cascade = "all, delete-orphan"
    )

    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of the ML model instance.

        Returns
        -------
        str
            Concise, unambiguous representation suitable for logs, REPL, and test assertions.
        """
        
        return f"<MLModel(id={self.id}, name={self.name!r}, device={self.device})>"