# **Application Structure**

*This README provides a high-level architectural overview of the project: what each component is for and why it exists. For implementation details refer to the docstrings and comments inside each file.*

## **I. `db/` — The Database Layer**

1. **`config.py`**  
   Defines configuration schemas for SQLite using Pydantic Settings, loaded from `.env` with `SQLITE_` prefix.

2. **`models/`**  
   Contains SQLAlchemy 2.0 ORM models that represent the core domain entities: `'ml_models'` and `'ml_metrics'`.

3. **`schemas/`**  
   Contains Pydantic models that validate and structure incoming data before it is persisted to the database, ensuring data integrity and type safety.

4. **`types.py`**  
   Declares shared type aliases to enable generic, type-safe repository and service patterns.

5. **`sync_db/`**  
   Synchronous data access layer.

6. **`async_db/`**  
   Asynchronous data access layer.

## **II. `sync_db/` and `async_db/` — Dual Data Access Layers**

These directories provide **symmetrical implementations** of the same data access patterns — one for synchronous execution (`sync_db/`), and the other for asynchronous (`async_db/`). Both follow identical architectural boundaries but differ only in I/O model, enabling consistent logic across blocking and non-blocking contexts.

1. **`session.py`**  
   Provides a context-managed database session factory (synchronous or asynchronous) that guarantees:
   - Automatic transaction rollback on exception,
   - Proper session closure regardless of outcome,
   - Isolation of database state per operation.

2. **`repositories/`**  
   **Low-level data access components with zero business logic.**  
   Each repository provides methods to **persist, retrieve, update, and delete domain entities** using only:
   - **Plain Python dictionaries** (for input),
   - **SQLAlchemy ORM model instances** (for output).  
   Repositories do **not** validate data, enforce constraints, manage transactions, or interpret business rules. They are a thin abstraction over the ORM, exposing only safe, composable operations on single entity types. Crucially, **repositories never create or manage their own sessions** — they receive an active session from the caller.

3. **`services/`**  
   **The enforcement layer for domain invariants, transaction control, and cross-cutting validation.**  
   Services:
   - Accept **validated Pydantic models** as input,
   - Enforce **custom business rules** (e.g., uniqueness, referential integrity) via template hooks like `_validate_create`,
   - **Acquire and manage a database session** for the duration of the operation,
   - **Orchestrate one or more repositories** within a single transactional boundary,
   - Explicitly control **transaction lifecycle**: `commit()` on success, `rollback()` on error,
   - Ensure **proper session cleanup** (`close`) regardless of outcome,
   - Convert results into **Pydantic response models** — never raw ORM objects.  

   This design ensures that:
   - All input is pre-validated and typed,
   - Business logic is centralized and testable,
   - The output is always a well-defined, serializable data structure,
   - Transactional integrity is guaranteed across complex workflows.

## **III. `migrations/`**

Alembic directory that manages database schema changes and table modifications. Contains migration files, configuration, and version control for database structure evolution.