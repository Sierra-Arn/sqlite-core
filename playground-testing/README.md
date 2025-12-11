## **Testing and Exploration**

Two Jupyter notebooks are provided for interactive experimentation with SQLite: one for synchronous workflows, another for asynchronous ones.

Additionally, you can always connect directly to the SQLite database and manually inspect the database state using standard SQLite commands like:

1. **Show current database:** [^1]
    ```sql
    .databases
    ``` 

2. **View all tables:** [^1]
    ```sql
    .tables
    ```

3. **View table structure:** [^1]
    ```sql
    .schema <table_name>
    ```
    
    Or for all tables:
    ```sql
    .schema
    ```

4. **View data in table:** [^1]
    ```sql
    SELECT * FROM <table_name> LIMIT 10;
    ```

5. **Export table to CSV:** [^1]
    ```sql
    .mode csv
    .output <file_name>.csv
    SELECT * FROM <table_name>;
    .output stdout
    ```

6. **Exit SQLite:**
    ```sql
    .quit
    ```

[^1]: SQLite dot commands (like .mode, .output) need to be executed separately from SQL statements, and they should each be on their own line.