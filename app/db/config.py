# app/db/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class SQLiteConfig(BaseSettings):
    """
    Configuration schema for SQLite database.

    Attributes
    ----------
    db_path : str, optional
        Path to the SQLite database file.
    echo : bool, optional
        Enables or disables SQL statement logging to stdout.
        Useful for debugging during development; should be `False` in production.
        Default is `False`.
    autocommit : bool, optional
        Controls whether SQLAlchemy sessions automatically commit transactions.
        When `False`, explicit `commit()` calls are required.
        Default is `False`.
    autoflush : bool, optional
        Controls whether pending ORM changes are automatically flushed before queries.
        When `False`, flushing is manual, giving full control over side effects.
        Default is `False`.
    expire_on_commit : bool, optional
        Determines whether ORM objects are expired (i.e., their attributes detached from the session)
        immediately after a transaction is committed.
        
        When `True` (SQLAlchemy's default), all loaded attributes of ORM instances are marked as "expired"
        upon `session.commit()`. Any subsequent access to these attributes triggers an implicit
        database refresh (lazy load) to ensure data consistency. While safe in synchronous contexts,
        this behavior is **incompatible with asynchronous applications** when serializing ORM objects
        after commit: Pydantic's `model_validate()` is a purely synchronous function and cannot
        perform the required `await`-based I/O to reload expired attributes. This results in a
        `MissingGreenlet` error during attribute access.
        
        Therefore, in async applications, this setting **must be `False`** to preserve attribute values post-commit and 
        allow safe serialization of ORM objects into Pydantic response models.
        
        Default is `False`.

    Notes:
    ------
    1. Automatically loads settings from a `.env` file in the current working directory
       using a module-specific prefix specified.
    2. The `.env` file must use UTF-8 encoding. 
    3. Variable names are case-insensitive.
    4. Any extra (unrecognized) variables are silently ignored.
    5. The configuration is immutable after instantiation.
    6. During instantiation, values are resolved in the following order of precedence 
       (from highest to lowest priority):
        1. **Explicitly passed arguments** — values provided directly to the constructor.
        2. **Environment variables** — including those loaded from the `.env` file,
        prefixed according to the subclass's `env_prefix`.
        3. **Code-defined defaults** — fallback values specified as field defaults
        in the class definition.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
        env_prefix="SQLITE_"
    )

    db_path: str
    echo: bool = False
    autocommit: bool = False
    autoflush: bool = False
    expire_on_commit: bool = False

    @property
    def sync_connection_url(self) -> str:
        """
        Build synchronous SQLite connection URL from the configured database path.

        Returns
        -------
        str
            Connection URL compatible with SQLAlchemy's synchronous SQLite backend.
        """

        return f"sqlite:///{self.db_path}"
    
    @property
    def async_connection_url(self) -> str:
        """
        Build asynchronous SQLite connection URL from the configured database path.

        Returns
        -------
        str
            Connection URL compatible with SQLAlchemy's asynchronous SQLite backend.
        """

        return f"sqlite+aiosqlite:///{self.db_path}"


# Initialize SQLite configuration singleton
# Since SQLite database settings are static for the application's lifetime
# and any configuration changes require a full application restart,
# it is safe to instantiate the config once at module level and reuse
# it throughout the application as a singleton.
sqlite_config = SQLiteConfig()