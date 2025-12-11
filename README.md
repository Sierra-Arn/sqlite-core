# **SQLite Core**

*An educational project showcasing how to use SQLite with Python, covering both synchronous and asynchronous approaches.*

## **Project Structure**

```bash
sqlite-core/
├── app/                   # Main application code
├── .env.example           # Example environment variables file
├── pixi.lock              # Locked dependency versions for reproducible environments
├── pixi.toml              # Pixi project configuration: environments, dependencies, 
|                          # platforms and project-specific commands
└── playground-testing/    # Jupyter notebooks for playground testing
```

Each directory includes its own `README.md` with detailed information about its contents and usage, and every file contains comprehensive inline comments to explain the code.

## **Dependencies Overview**

- [pydantic-settings](https://github.com/pydantic/pydantic-settings) —  
A Pydantic-powered library for managing application configuration and environment variables with strong typing, validation, and seamless `.env` support.

- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) —  
The Python SQL toolkit and Object-Relational Mapper (ORM) used as the foundation for database modeling, querying, and transaction management in both synchronous and asynchronous contexts.

- [Alembic](https://github.com/sqlalchemy/alembic) —  
A lightweight database migration tool for SQLAlchemy, enabling structured, version-controlled evolution of the SQLite schema over time.

- **`sqlite3`** —  
Python’s built-in module for working with SQLite databases — no extra installation required.

- [aiosqlite](https://github.com/omnilib/aiosqlite) —  
An asynchronous wrapper around Python’s built-in `sqlite3` module, enabling non-blocking SQLite database operations.

### **Testing & Development Dependencies**

- [ipykernel](https://github.com/ipython/ipykernel) —  
The IPython kernel for Jupyter, enabling interactive notebook development and seamless integration with the project’s virtual environments.

- [sqlite](https://github.com/mackyle/sqlite) —  
The unofficial SQLite engine. While Python’s built-in `sqlite3` module handles all runtime database operations (which is why the SQLite engine is listed under "Testing & Development"), it lacks a very important feature for testing (at least for me): the ability to connect to the database via a command-line interface and inspect or query data using SQL-like commands. That’s why I install the full, unofficial SQLite engine — it includes a CLI tool that allows me to directly inspect, query, and manipulate the SQLite database file from the terminal — for example, to verify the schema structure or examine raw data.

## **Quick Start**

### **I. Prerequisites**

- [Pixi](https://pixi.sh/latest/) package manager.

> **Platform note**: All development and testing were performed on `linux-64`.  
> If you're using a different platform, you’ll need to:
> 1. Update the `platforms` list in the `pixi.toml` accordingly.
> 2. Ensure that platform-specific scripts are compatible with your operating system or replace them with equivalents.

### **II. Database Setup**

1. **Clone the repository**

    ```bash
    git clone https://github.com/Sierra-Arn/sqlite-core.git
    cd sqlite-core
    ```

2. **Install dependencies**
    
    ```bash
    pixi install --all
    ```

3. **Setup environment configuration**
    
    ```bash
    pixi run copy-env
    ```

4. **Create a database migration & Apply it**
    ```bash
    pixi run alembic-revision
    pixi run alembic-upgrade
    ```

### **III. Testing**

Once a database is ready, you can run and test the SQLite implementation with interactive Jupyter notebooks in `playground-testing/`. Additionally, you can open a SQLite shell to manually verify that everything is working correctly:

```bash
pixi run sqlite-shell
```

## **License**

This project is licensed under the [BSD-3-Clause License](LICENSE).