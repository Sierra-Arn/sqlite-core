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
   Context-managed database session factory (synchronous or asynchronous) that guarantees:
   - Automatic transaction rollback on exception,
   - Proper session closure regardless of outcome,
   - Isolation of database state per request or operation.

2. **`repositories/`**  
   Implements CRUD operations and model-specific queries.

3. **`services/`**  
   Validates overall application rules and coordinates repository operations within a single transaction.

## **III. `migrations/`**

Alembic directory that manages database schema changes and table modifications. Contains migration files, configuration, and version control for database structure evolution.