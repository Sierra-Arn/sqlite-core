# app/db/models/types.py
from enum import StrEnum
from sqlalchemy import Enum as SQLEnum


class DeviceType(StrEnum):
    """
    Computation device target for model inference and tensor operations.

    Specifies the hardware backend on which tensors and models are executed.
    The selected device has direct implications for performance, memory usage,
    and system requirements.

    - ``"cpu"``: Executes computations on the central processing unit. 
    Universally available, requires no specialized hardware or drivers, 
    but significantly slower for large-scale deep learning workloads.
    - ``"cuda"``: Executes computations on an NVIDIA GPU using the CUDA runtime. 
    Offers orders-of-magnitude speedup for neural network inference and training, 
    but requires a CUDA-capable GPU and properly installed drivers and libraries.

    Notes
    -----
    - This enum inherits from `enum.StrEnum`, meaning each member is a native `str` instance.
    Therefore, it can be used directly in any context expecting a string
    without needing to access the `.value` attribute.

    - The string values are fixed and must not be changed without a corresponding
    database migration, as they are persisted in persistent storage.
    """

    CPU = "cpu"
    CUDA = "cuda"


DeviceTypeSQL = SQLEnum(
    DeviceType,
    name="device_type"
)
"""
SQLAlchemy-compatible enum type representing valid computation devices in the database.

This type maps the `DeviceType` Python enum to a persistent, named `ENUM` type in the
underlying relational database. It ensures data integrity by restricting
column values to only the predefined set of valid devices (`'cpu'` or `'cuda'`).

The named enum type (`device_type`) appears explicitly in the database schema, improving
introspectability, readability of migrations, and compatibility with database tooling.

Notes
-----
Schema consistency: Changing the members or string values of `DeviceType` requires
a corresponding database migration to alter the `device_type` enum, as existing data
must remain compatible.
"""